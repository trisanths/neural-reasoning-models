"""Command line entry point.

Usage, one GPU:
  uv run python -m src.train.cli --config configs/smoke.yaml --data DIR \
      --out RUNDIR [--warmup-bin PATH] [--resume] [--loops N]

Usage, many GPUs:
  bash scripts/train_ddp.sh configs/1b.yaml DIR RUNDIR 4,5,6,7

The data directory must hold uint16 shards with an index.json, as produced by
src.train.data. When --warmup-bin is given and schedule.warmup_phase_steps is
positive, training front loads that many steps on the raw procgen stream
before switching to the shard data, per SPEC.md section 1 regime C.

Under torchrun this joins the process group before anything else, then seeds
the global generator before the model is built so every rank starts from the
same weights and a run is reproducible from train.seed alone. The global batch
in train.global_batch_size is sequences per optimizer step summed over ranks,
so adding ranks shortens each rank's accumulation instead of growing the batch.

A config with a lossmask section switches the main phase loader to the
weighted one in src/lossmask, which reads the tag stream beside the tokens and
hands the trainer a per token loss weight. The token stream, the seed, and the
sampled offsets are unchanged by that, so two runs differing only in
lossmask.weights read the same tokens in the same order.
"""

import argparse
from pathlib import Path

import yaml

from src.train.data import ArraySource, BatchLoader, ShardReader, load_procgen_bin
from src.train.distributed import destroy_distributed, init_distributed
from src.train.model import ModelConfig, TransformerLM
from src.train.trainer import Trainer, seed_everything


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="src.train.cli")
    parser.add_argument("--config", required=True, help="yaml config path")
    parser.add_argument("--data", required=True, help="shard directory with index.json")
    parser.add_argument("--out", required=True, help="run directory for checkpoints and logs")
    parser.add_argument("--warmup-bin", default=None, help="raw procgen .bin stream")
    parser.add_argument("--resume", action="store_true", help="resume from OUT/latest.pt")
    parser.add_argument("--device", default=None, help="cuda or cpu, default auto")
    parser.add_argument("--max-steps", type=int, default=None, help="override schedule.max_steps")
    parser.add_argument(
        "--micro-batch-size",
        type=int,
        default=None,
        help="override train.batch_size, the per rank micro batch",
    )
    parser.add_argument(
        "--grad-accum-steps",
        type=int,
        default=None,
        help="override the derived per rank accumulation, for benchmarking",
    )
    parser.add_argument(
        "--loops",
        type=int,
        default=None,
        help="override model.recurrent.loops, the depth dial on a recurrent config",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    info = init_distributed()
    try:
        return _run(args, info)
    finally:
        destroy_distributed()


def _run(args, info: dict) -> int:
    rank = info["rank"]

    def log(message: str) -> None:
        if rank == 0:
            print(message, flush=True)

    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    if args.max_steps is not None:
        cfg["schedule"]["max_steps"] = args.max_steps
    if args.loops is not None:
        if "recurrent" not in cfg["model"] or cfg["model"]["recurrent"] is None:
            raise SystemExit("--loops needs a config with a model.recurrent block")
        cfg["model"]["recurrent"]["loops"] = args.loops

    train_cfg = cfg["train"]
    seed = int(train_cfg.get("seed", 0))
    # Seed before the model exists so every rank draws the same initial
    # weights and a rerun of the same config reproduces the same run.
    seed_everything(seed)

    model = TransformerLM(ModelConfig(**cfg["model"]))
    device = args.device if args.device is not None else info["device"]
    trainer = Trainer(
        model,
        cfg,
        args.out,
        device=device,
        micro_batch_size=args.micro_batch_size,
        grad_accum_steps=args.grad_accum_steps,
    )
    plan = trainer.plan
    seq_len = int(cfg["model"]["max_seq_len"])
    log(f"model params {model.num_params(non_embedding=False):,} "
        f"({model.num_params():,} non embedding), device {trainer.device}")
    log(f"batch plan: {plan.describe()}, "
        f"{plan.tokens_per_step(seq_len):,} tokens per optimizer step")
    stated = train_cfg.get("global_batch_size")
    if stated is not None and int(stated) != plan.global_batch_size:
        log(f"note: command line overrides moved the global batch from the config's "
            f"{int(stated)} sequences to {plan.global_batch_size}")
    if model.cfg.recurrent is not None:
        details = model.describe()
        log(f"recurrence on: {model.cfg.n_layers} unique layers, {details['loops']} loops, "
            f"effective depth {details['effective_depth']}")

    if args.resume:
        latest = Path(args.out) / "latest.pt"
        if latest.exists():
            trainer.load_checkpoint(latest)
            log(f"resumed at step {trainer.step}")

    batch_size = plan.micro_batch_size
    world_size = plan.world_size

    warmup_phase_steps = int(cfg["schedule"].get("warmup_phase_steps", 0))
    if args.warmup_bin is not None and trainer.step < warmup_phase_steps:
        source = ArraySource(load_procgen_bin(args.warmup_bin))
        loader = BatchLoader(
            source, batch_size, seq_len, seed=seed, rank=rank, world_size=world_size
        )
        log(f"warm up phase to step {warmup_phase_steps} on {args.warmup_bin}")
        trainer.train(loader, until_step=warmup_phase_steps)

    # Opt in by config. Without a lossmask section this is the plain loader
    # it has always been, and a lossmask section on untagged data trains the
    # control arm rather than failing.
    lossmask_cfg = cfg.get("lossmask")
    if lossmask_cfg is None:
        reader = ShardReader(args.data)
        loader = BatchLoader(
            reader, batch_size, seq_len, seed=seed + 1, rank=rank, world_size=world_size
        )
    else:
        from src.lossmask.shards import TaggedShardReader, WeightedBatchLoader
        from src.lossmask.tags import describe_weights, weight_table

        table = weight_table(lossmask_cfg.get("weights"))
        reader = TaggedShardReader(args.data)
        loader = WeightedBatchLoader(
            reader, batch_size, seq_len, table,
            seed=seed + 1, rank=rank, world_size=world_size
        )
        log(f"loss masking on, weights {describe_weights(table)}"
            + ("" if reader.tagged else "; data carries no tags, so every "
                                        "token weighs one"))
    log(f"main phase on {reader.total_tokens:,} tokens from {args.data}, "
        f"rank {rank} reads [{loader.region_start:,}, {loader.region_end:,})")
    trainer.train(loader)
    log(f"done at step {trainer.step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
