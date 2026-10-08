"""Worker bodies for the data parallel tests.

These live outside the test module because torch.multiprocessing.spawn pickles
the entry point by qualified name, and a pytest collected module has no stable
one. Every worker runs a real gloo process group on cpu, so the tests exercise
DistributedDataParallel, no_sync and the logging all reduce without touching a
GPU that somebody else's training run is using.
"""

import json
import os
from pathlib import Path

import numpy as np
import torch

from src.train.data import ArraySource, BatchLoader
from src.train.distributed import destroy_distributed, init_distributed
from src.train.model import ModelConfig, TransformerLM
from src.train.trainer import Trainer, seed_everything

TINY_MODEL = {
    "vocab_size": 64,
    "d_model": 32,
    "n_layers": 2,
    "n_heads": 2,
    "d_ff": 64,
    "max_seq_len": 16,
}
SEQ_LEN = TINY_MODEL["max_seq_len"]
STREAM_TOKENS = 4096
DATA_SEED = 20260828


def tiny_cfg(global_batch_size: int = 4, micro_batch_size: int = 1, max_steps: int = 4,
             seed: int = 1234) -> dict:
    return {
        "model": dict(TINY_MODEL),
        "optimizer": {"lr": 1e-3, "weight_decay": 0.1, "beta1": 0.9, "beta2": 0.95, "eps": 1e-8},
        "schedule": {"warmup_steps": 0, "max_steps": max_steps, "min_lr_ratio": 0.1},
        "train": {
            "batch_size": micro_batch_size,
            "global_batch_size": global_batch_size,
            "grad_clip": 1.0,
            "seed": seed,
            "log_interval": 1,
            "ckpt_interval": 0,
        },
    }


def token_stream() -> np.ndarray:
    """The same synthetic corpus for every process in a test."""
    rng = np.random.default_rng(DATA_SEED)
    return rng.integers(0, TINY_MODEL["vocab_size"], size=STREAM_TOKENS, dtype=np.uint16)


def fixed_batches(count: int, batch_size: int, seed: int = 7) -> list:
    """A list of micro batches that every configuration can be handed, so a
    world of two accumulating twice sees exactly the sequences a world of one
    accumulating four times sees."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(count):
        arr = rng.integers(0, TINY_MODEL["vocab_size"], size=(batch_size, SEQ_LEN + 1),
                           dtype=np.int64)
        tensor = torch.from_numpy(arr)
        out.append((tensor[:, :-1].contiguous(), tensor[:, 1:].contiguous()))
    return out


def build_trainer(cfg: dict, out_dir, **kwargs) -> Trainer:
    seed_everything(int(cfg["train"]["seed"]))
    model = TransformerLM(ModelConfig(**cfg["model"]))
    return Trainer(model, cfg, str(out_dir), device="cpu", **kwargs)


def _enter_group(rank: int, world_size: int, port: int) -> dict:
    os.environ["RANK"] = str(rank)
    os.environ["LOCAL_RANK"] = str(rank)
    os.environ["WORLD_SIZE"] = str(world_size)
    os.environ["MASTER_ADDR"] = "127.0.0.1"
    os.environ["MASTER_PORT"] = str(port)
    torch.set_num_threads(1)
    return init_distributed(backend="gloo", device="cpu")


def _write(out_dir, rank: int, payload: dict) -> None:
    with open(Path(out_dir) / f"result-{rank}.json", "w") as fh:
        json.dump(payload, fh)


# ---------------- workers ----------------


def loss_worker(rank: int, world_size: int, port: int, out_dir: str, steps: int) -> None:
    """Train through the distributed path and record the logged losses."""
    _enter_group(rank, world_size, port)
    try:
        cfg = tiny_cfg(global_batch_size=4, micro_batch_size=1, max_steps=steps)
        trainer = build_trainer(cfg, Path(out_dir) / "run")
        loader = BatchLoader(
            ArraySource(token_stream()),
            trainer.plan.micro_batch_size,
            SEQ_LEN,
            seed=int(cfg["train"]["seed"]) + 1,
            rank=rank,
            world_size=world_size,
        )
        losses = trainer.train(loader, save_at_end=False)
        _write(out_dir, rank, {"losses": [repr(x) for x in losses],
                               "grad_accum_steps": trainer.grad_accum_steps})
    finally:
        destroy_distributed()


def nosync_worker(rank: int, world_size: int, port: int, out_dir: str) -> None:
    """One optimizer step over a fixed set of four micro batches, split evenly
    across ranks. The resulting parameters must match a single process run that
    accumulated all four."""
    _enter_group(rank, world_size, port)
    try:
        cfg = tiny_cfg(global_batch_size=4, micro_batch_size=1, max_steps=1)
        trainer = build_trainer(cfg, Path(out_dir) / "run")
        accum = trainer.grad_accum_steps
        every = fixed_batches(4, cfg["train"]["batch_size"])
        mine = every[rank * accum : (rank + 1) * accum]
        trainer.train(mine, until_step=1, save_at_end=False)
        torch.save(trainer.model.state_dict(), Path(out_dir) / f"params-{rank}.pt")
        _write(out_dir, rank, {"grad_accum_steps": accum})
    finally:
        destroy_distributed()


def comm_count_worker(rank: int, world_size: int, port: int, out_dir: str) -> None:
    """Count gradient bucket reductions per optimizer step at two different
    accumulation depths. no_sync means the two counts are equal."""
    _enter_group(rank, world_size, port)
    try:
        from torch.distributed.algorithms.ddp_comm_hooks import default_hooks

        counts = {}
        for accum in (1, 4):
            cfg = tiny_cfg(global_batch_size=accum * world_size, micro_batch_size=1, max_steps=1)
            cfg["train"].pop("grad_accum_steps", None)
            trainer = build_trainer(cfg, Path(out_dir) / f"run{accum}")
            seen = {"n": 0}

            def hook(state, bucket, seen=seen):
                seen["n"] += 1
                return default_hooks.allreduce_hook(state, bucket)

            trainer.ddp.register_comm_hook(None, hook)
            trainer.train(fixed_batches(accum, 1), until_step=1, save_at_end=False)
            counts[str(accum)] = seen["n"]
        _write(out_dir, rank, {"bucket_reductions": counts})
    finally:
        destroy_distributed()


def ckpt_write_worker(rank: int, world_size: int, port: int, out_dir: str, steps: int) -> None:
    """Train a few steps under DDP and leave a checkpoint behind. Rank zero
    also writes a wrapper prefixed copy, which is what a checkpoint written
    straight from the DistributedDataParallel object looks like."""
    _enter_group(rank, world_size, port)
    try:
        cfg = tiny_cfg(global_batch_size=4, micro_batch_size=1, max_steps=steps)
        run_dir = Path(out_dir) / "ddp_run"
        trainer = build_trainer(cfg, run_dir)
        loader = BatchLoader(
            ArraySource(token_stream()), trainer.plan.micro_batch_size, SEQ_LEN,
            seed=int(cfg["train"]["seed"]) + 1, rank=rank, world_size=world_size,
        )
        trainer.train(loader, save_at_end=False)
        trainer.save_checkpoint(name="ddp.pt", loader=loader)
        if rank == 0:
            torch.save(trainer.model.state_dict(), run_dir / "reference-params.pt")
            wrapped = torch.load(run_dir / "ddp.pt", map_location="cpu", weights_only=False)
            wrapped["model"] = trainer.ddp.state_dict()
            torch.save(wrapped, run_dir / "ddp-wrapped.pt")
        _write(out_dir, rank, {"step": trainer.step, "grad_accum_steps": trainer.grad_accum_steps})
    finally:
        destroy_distributed()


def ckpt_read_worker(rank: int, world_size: int, port: int, out_dir: str, ckpt_path: str) -> None:
    """Load a checkpoint written by a single GPU run into every rank of a
    distributed run and dump what each rank ended up holding."""
    _enter_group(rank, world_size, port)
    try:
        cfg = tiny_cfg(global_batch_size=4, micro_batch_size=1, max_steps=8)
        trainer = build_trainer(cfg, Path(out_dir) / "read_run")
        trainer.load_checkpoint(ckpt_path)
        torch.save(trainer.model.state_dict(), Path(out_dir) / f"loaded-{rank}.pt")
        _write(out_dir, rank, {"step": trainer.step})
    finally:
        destroy_distributed()
