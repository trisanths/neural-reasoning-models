"""Prove that compiled training survives a sampled loop count.

Sampling the depth makes dynamo trace one graph per distinct loop count, and
its default recompile limit is 8. A range of [1, 8] sits exactly on that limit,
so without the raise the trainer performs in __init__ the recommended config
would fall back to eager partway through the first epoch and quietly lose the
compile speedup. This runs the real Trainer, compiled, on cuda, across a
sampling range wide enough to blow the default limit, and fails if dynamo
reports hitting it or if any loop count in the range never gets exercised.

  uv run python scripts/check_loop_sampling_compile.py

Small on purpose: it shares the dev GPU with other lanes.
"""

import io
import itertools
import json
import logging
import sys
import tempfile
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.train.model import ModelConfig, TransformerLM  # noqa: E402
from src.train.trainer import Trainer  # noqa: E402

LOOP_RANGE = [1, 8]
STEPS = 60


def build_cfg() -> dict:
    return {
        "model": {
            "vocab_size": 32768,
            "d_model": 512,
            "n_layers": 8,
            "n_heads": 8,
            "d_ff": 1408,
            "max_seq_len": 512,
            "recurrent": {
                "prelude_layers": 1,
                "core_layers": 5,
                "coda_layers": 2,
                "loops": 4,
                "loop_embedding": True,
                "train_loop_sampling": LOOP_RANGE,
                "grad_checkpoint": True,
                "inject_prelude": True,
            },
        },
        "optimizer": {"lr": 3.0e-4, "weight_decay": 0.1, "beta1": 0.9, "beta2": 0.95},
        "schedule": {"warmup_steps": 5, "max_steps": STEPS, "min_lr_ratio": 0.1},
        "train": {
            "batch_size": 2,
            "grad_accum_steps": 1,
            "grad_clip": 1.0,
            "seed": 1234,
            "log_interval": 1,
            "ckpt_interval": 0,
            "compile": True,
        },
    }


def main() -> int:
    if not torch.cuda.is_available():
        print("cuda is not available")
        return 1
    cfg = build_cfg()
    model_cfg = ModelConfig(**cfg["model"])
    model = TransformerLM(model_cfg)
    out_dir = Path(tempfile.mkdtemp(prefix="loop_sampling_"))
    trainer = Trainer(model, cfg, out_dir, device="cuda")
    trainer.save_checkpoint = lambda name=None: None

    from torch import _dynamo

    limit = _dynamo.config.recompile_limit
    print(f"recompile limit after Trainer init: {limit}")

    # dynamo reports hitting the limit through the logging module rather than
    # by raising, so the check has to read what it logged.
    captured = io.StringIO()
    handler = logging.StreamHandler(captured)
    dynamo_log = logging.getLogger("torch._dynamo")
    dynamo_log.addHandler(handler)

    gen = torch.Generator().manual_seed(4)
    tokens = torch.randint(
        0, model_cfg.vocab_size, (2, model_cfg.max_seq_len + 1), generator=gen
    )
    batch = (tokens[:, :-1].contiguous().cuda(), tokens[:, 1:].contiguous().cuda())
    losses = trainer.train(itertools.cycle([batch]), until_step=STEPS)
    dynamo_log.removeHandler(handler)

    records = [json.loads(line) for line in (out_dir / "loss.jsonl").read_text().splitlines()]
    seen = sorted({r["loops"] for r in records})
    text = captured.getvalue()
    hit_limit = "recompile_limit" in text or "cache_size_limit" in text

    print(f"steps: {len(losses)}, first loss {losses[0]:.4f}, last loss {losses[-1]:.4f}")
    print(f"loop counts exercised: {seen}")
    print(f"peak memory: {torch.cuda.max_memory_allocated() / 2**30:.2f} GiB")
    print(f"dynamo reported hitting its recompile limit: {hit_limit}")

    ok = True
    if limit <= LOOP_RANGE[1]:
        print(f"FAIL: recompile limit {limit} does not cover the sampling range")
        ok = False
    if seen != list(range(LOOP_RANGE[0], LOOP_RANGE[1] + 1)):
        print(f"FAIL: sampling never exercised every depth in {LOOP_RANGE}")
        ok = False
    if hit_limit:
        print("FAIL: dynamo fell back to eager on some loop count")
        print(text[:2000])
        ok = False
    if not all(torch.isfinite(torch.tensor(v)) for v in losses):
        print("FAIL: non finite loss")
        ok = False
    print("PASS" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
