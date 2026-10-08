"""Profile one training step setting and print the result as a json line.

Each invocation measures a single micro batch and accumulation setting in a
fresh process, so out of memory failures and torch.compile state never leak
between settings. The step mechanics copy src.train.trainer.Trainer.train:
bf16 autocast on cuda, loss divided by the accumulation count, a loss.item()
per micro batch, gradient clipping, then AdamW with the same parameter
grouping. Batches come from the same BatchLoader the real run uses.

Steps are counted in micro batches on the command line and converted to whole
optimizer steps, so the timed window always covers full optimizer steps.
Peak memory statistics reset after the warmup window, which also absorbs
torch.compile time when --compile is set.

An out of memory failure is a valid measurement. It is recorded in the json
line and the process exits 0, so a sweep over settings keeps going.

Usage:

    uv run python -m scripts.bench.profile --config configs/350m.yaml \
        --data ~/data/bench/shards --micro-batch 8 --grad-accum 8 \
        --out ~/data/bench/results.jsonl
"""

import argparse
import json
import time

import torch
import yaml

from src.train.data import BatchLoader, ShardReader
from src.train.model import ModelConfig, TransformerLM
from src.train.trainer import seed_everything


def build_argparser():
    parser = argparse.ArgumentParser(prog="python -m scripts.bench.profile")
    parser.add_argument("--config", required=True, help="yaml config path")
    parser.add_argument("--data", required=True, help="shard directory")
    parser.add_argument("--micro-batch", type=int, required=True)
    parser.add_argument("--grad-accum", type=int, required=True)
    parser.add_argument("--seq-len", type=int, default=None,
                        help="override model.max_seq_len")
    parser.add_argument("--warmup-micro", type=int, default=32,
                        help="micro batches before the timed window")
    parser.add_argument("--timed-micro", type=int, default=192,
                        help="micro batches inside the timed window")
    parser.add_argument("--compile", action="store_true",
                        help="wrap the model in torch.compile")
    parser.add_argument("--tag", default="", help="free text label")
    parser.add_argument("--out", default=None, help="append the json line here")
    return parser


def main(argv=None):
    args = build_argparser().parse_args(argv)
    assert torch.cuda.is_available(), "this benchmark requires a cuda device"

    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    if args.seq_len is not None:
        cfg["model"]["max_seq_len"] = args.seq_len
    seq_len = int(cfg["model"]["max_seq_len"])
    train_cfg = cfg["train"]
    seed = int(train_cfg.get("seed", 0))
    grad_clip = float(train_cfg.get("grad_clip", 1.0))
    accum = args.grad_accum

    seed_everything(seed)
    model = TransformerLM(ModelConfig(**cfg["model"])).to("cuda")
    model.train()
    run_model = torch.compile(model) if args.compile else model

    opt_cfg = cfg["optimizer"]
    decay, no_decay = [], []
    for param in model.parameters():
        if not param.requires_grad:
            continue
        (decay if param.dim() >= 2 else no_decay).append(param)
    optimizer = torch.optim.AdamW(
        [
            {"params": decay, "weight_decay": float(opt_cfg.get("weight_decay", 0.1))},
            {"params": no_decay, "weight_decay": 0.0},
        ],
        lr=float(opt_cfg["lr"]),
        betas=(float(opt_cfg.get("beta1", 0.9)), float(opt_cfg.get("beta2", 0.95))),
        eps=float(opt_cfg.get("eps", 1e-8)),
    )

    reader = ShardReader(args.data)
    loader = BatchLoader(reader, args.micro_batch, seq_len, seed=seed + 1)
    batch_iter = iter(loader)

    def opt_step():
        optimizer.zero_grad(set_to_none=True)
        step_loss = 0.0
        for _ in range(accum):
            inputs, targets = next(batch_iter)
            inputs = inputs.to("cuda", non_blocking=True)
            targets = targets.to("cuda", non_blocking=True)
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                _, loss = run_model(inputs, targets)
            (loss / accum).backward()
            step_loss += loss.item() / accum
        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()
        return step_loss

    warmup_steps = max(1, round(args.warmup_micro / accum))
    timed_steps = max(3, round(args.timed_micro / accum))
    result = {
        "tag": args.tag,
        "config": args.config,
        "micro_batch": args.micro_batch,
        "grad_accum": accum,
        "seq_len": seq_len,
        "compile": bool(args.compile),
        "params_total": model.num_params(non_embedding=False),
        "params_non_embedding": model.num_params(),
        "warmup_opt_steps": warmup_steps,
        "timed_opt_steps": timed_steps,
        "torch": torch.__version__,
        "device": torch.cuda.get_device_name(0),
    }
    phase = "warmup"
    try:
        start = time.time()
        for _ in range(warmup_steps):
            first_loss = opt_step()
        torch.cuda.synchronize()
        result["warmup_s"] = round(time.time() - start, 2)
        result["loss_first"] = round(first_loss, 4)

        phase = "timed"
        torch.cuda.reset_peak_memory_stats()
        start = time.time()
        for _ in range(timed_steps):
            last_loss = opt_step()
        torch.cuda.synchronize()
        elapsed = time.time() - start
        tokens = timed_steps * accum * args.micro_batch * seq_len
        result.update(
            {
                "ok": True,
                "elapsed_s": round(elapsed, 2),
                "tokens_per_s": round(tokens / elapsed, 1),
                "peak_alloc_gib": round(torch.cuda.max_memory_allocated() / 2**30, 2),
                "peak_reserved_gib": round(torch.cuda.max_memory_reserved() / 2**30, 2),
                "loss_last": round(last_loss, 4),
            }
        )
    except torch.cuda.OutOfMemoryError:
        result.update(
            {
                "ok": False,
                "error": f"OOM during {phase}",
                "peak_reserved_gib": round(torch.cuda.max_memory_reserved() / 2**30, 2),
            }
        )

    line = json.dumps(result)
    print(line)
    if args.out:
        with open(args.out, "a") as fh:
            fh.write(line + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
