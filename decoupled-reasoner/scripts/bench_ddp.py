"""Throughput and memory of the data parallel training path.

Runs the real Trainer over the real shard loader, throws away the first few
optimizer steps so compilation, allocator growth and NCCL warm up stay out of
the number, then times the rest. Prints one json line on rank zero.

  bash scripts/train_ddp.sh is the launcher for training; this uses torchrun
  directly because it takes its own flags:

  .venv/bin/python -m torch.distributed.run --nnodes=1 --nproc-per-node=4 \
      --rdzv-backend=c10d --rdzv-endpoint=127.0.0.1:29571 \
      scripts/bench_ddp.py --config configs/1b.yaml --data ~/data/regime_e3 \
      --micro-batch-size 2 --grad-accum-steps 2 --warmup 3 --steps 10

Tokens per second is global: sequences per optimizer step across every rank
times sequence length, divided by the wall clock of the timed steps. Peak
memory is the largest reserved bytes on any rank.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.train.data import BatchLoader, ShardReader  # noqa: E402
from src.train.distributed import (  # noqa: E402
    destroy_distributed,
    get_rank,
    get_world_size,
    init_distributed,
    is_distributed,
)
from src.train.model import ModelConfig, TransformerLM  # noqa: E402
from src.train.trainer import Trainer, seed_everything  # noqa: E402


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog="bench_ddp")
    parser.add_argument("--config", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", default=None, help="scratch run dir, default a temp dir")
    parser.add_argument("--micro-batch-size", type=int, default=None)
    parser.add_argument("--grad-accum-steps", type=int, default=None)
    parser.add_argument("--warmup", type=int, default=3, help="untimed optimizer steps")
    parser.add_argument("--steps", type=int, default=10, help="timed optimizer steps")
    parser.add_argument("--label", default="", help="free text carried into the json")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    info = init_distributed()
    try:
        return _run(args, info)
    finally:
        destroy_distributed()


def _run(args, info) -> int:
    rank, world_size = get_rank(), get_world_size()
    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    total_steps = args.warmup + args.steps
    cfg["schedule"]["max_steps"] = total_steps
    cfg["train"]["ckpt_interval"] = 0
    cfg["train"]["log_interval"] = 10**9

    seed = int(cfg["train"].get("seed", 0))
    seed_everything(seed)
    model = TransformerLM(ModelConfig(**cfg["model"]))
    params_total = model.num_params(non_embedding=False)
    params_non_emb = model.num_params()

    out_dir = args.out or os.path.join("/tmp", f"benchddp-{os.getpid()}-{rank}")
    trainer = Trainer(
        model,
        cfg,
        out_dir,
        device=info["device"],
        micro_batch_size=args.micro_batch_size,
        grad_accum_steps=args.grad_accum_steps,
    )
    plan = trainer.plan
    seq_len = int(cfg["model"]["max_seq_len"])
    reader = ShardReader(args.data)
    loader = BatchLoader(reader, plan.micro_batch_size, seq_len, seed=seed + 1,
                         rank=rank, world_size=world_size)

    trainer.train(loader, until_step=args.warmup, save_at_end=False)
    if trainer.on_cuda:
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
    if is_distributed():
        torch.distributed.barrier()

    start = time.time()
    trainer.train(loader, until_step=total_steps, save_at_end=False)
    if trainer.on_cuda:
        torch.cuda.synchronize()
    if is_distributed():
        torch.distributed.barrier()
    elapsed = time.time() - start

    peak_alloc = peak_reserved = 0.0
    if trainer.on_cuda:
        peak_alloc = torch.cuda.max_memory_allocated() / 1024**3
        peak_reserved = torch.cuda.max_memory_reserved() / 1024**3
    if is_distributed():
        stats = torch.tensor([peak_alloc, peak_reserved, elapsed], dtype=torch.float64,
                             device=trainer.device)
        torch.distributed.all_reduce(stats, op=torch.distributed.ReduceOp.MAX)
        peak_alloc, peak_reserved, elapsed = (float(x) for x in stats.tolist())

    tokens = plan.tokens_per_step(seq_len) * args.steps
    if rank == 0:
        record = {
            "label": args.label,
            "config": args.config,
            "world_size": world_size,
            "params_total": params_total,
            "params_non_embedding": params_non_emb,
            "seq_len": seq_len,
            "micro_batch_size": plan.micro_batch_size,
            "grad_accum_steps": plan.grad_accum_steps,
            "global_batch_size": plan.global_batch_size,
            "tokens_per_step": plan.tokens_per_step(seq_len),
            "timed_steps": args.steps,
            "elapsed_s": round(elapsed, 4),
            "s_per_step": round(elapsed / args.steps, 4),
            "tokens_per_s": round(tokens / elapsed, 1),
            "tokens_per_s_per_gpu": round(tokens / elapsed / world_size, 1),
            "peak_mem_alloc_gb": round(peak_alloc, 3),
            "peak_mem_reserved_gb": round(peak_reserved, 3),
        }
        print("BENCH " + json.dumps(record), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
