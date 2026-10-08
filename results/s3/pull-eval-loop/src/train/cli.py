"""Command line entry point.

Usage:
  uv run python -m src.train.cli --config configs/smoke.yaml --data DIR \
      --out RUNDIR [--warmup-bin PATH] [--resume]

The data directory must hold uint16 shards with an index.json, as produced by
src.train.data. When --warmup-bin is given and schedule.warmup_phase_steps is
positive, training front loads that many steps on the raw procgen stream
before switching to the shard data, per SPEC.md section 1 regime C.
"""

import argparse
from pathlib import Path

import yaml

from src.train.data import ArraySource, BatchLoader, ShardReader, load_procgen_bin
from src.train.model import ModelConfig, TransformerLM
from src.train.trainer import Trainer


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="src.train.cli")
    parser.add_argument("--config", required=True, help="yaml config path")
    parser.add_argument("--data", required=True, help="shard directory with index.json")
    parser.add_argument("--out", required=True, help="run directory for checkpoints and logs")
    parser.add_argument("--warmup-bin", default=None, help="raw procgen .bin stream")
    parser.add_argument("--resume", action="store_true", help="resume from OUT/latest.pt")
    parser.add_argument("--device", default=None, help="cuda or cpu, default auto")
    parser.add_argument("--max-steps", type=int, default=None, help="override schedule.max_steps")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    if args.max_steps is not None:
        cfg["schedule"]["max_steps"] = args.max_steps

    model = TransformerLM(ModelConfig(**cfg["model"]))
    trainer = Trainer(model, cfg, args.out, device=args.device)
    print(f"model params {model.num_params(non_embedding=False):,} "
          f"({model.num_params():,} non embedding), device {trainer.device}")

    if args.resume:
        latest = Path(args.out) / "latest.pt"
        if latest.exists():
            trainer.load_checkpoint(latest)
            print(f"resumed at step {trainer.step}")

    train_cfg = cfg["train"]
    batch_size = int(train_cfg["batch_size"])
    seq_len = int(cfg["model"]["max_seq_len"])
    seed = int(train_cfg.get("seed", 0))

    warmup_phase_steps = int(cfg["schedule"].get("warmup_phase_steps", 0))
    if args.warmup_bin is not None and trainer.step < warmup_phase_steps:
        source = ArraySource(load_procgen_bin(args.warmup_bin))
        loader = BatchLoader(source, batch_size, seq_len, seed=seed)
        print(f"warm up phase to step {warmup_phase_steps} on {args.warmup_bin}")
        trainer.train(loader, until_step=warmup_phase_steps)

    reader = ShardReader(args.data)
    loader = BatchLoader(reader, batch_size, seq_len, seed=seed + 1)
    print(f"main phase on {reader.total_tokens:,} tokens from {args.data}")
    trainer.train(loader)
    print(f"done at step {trainer.step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
