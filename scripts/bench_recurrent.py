"""Throughput and peak memory for looped depth, on one GPU.

Each case runs a few warm up optimizer steps and then times a measured window,
reporting tokens per second and torch.cuda.max_memory_allocated. Cases vary the
loop count, the backprop truncation depth, and gradient checkpointing, so the
cost of every gradient setting is measured rather than argued.

  uv run python scripts/bench_recurrent.py --config configs/350m-loop.yaml \
      --loops 1,2,4,8 --compile --out bench.json

--baseline additionally times configs/350m.yaml for the same batch shape.
"""

import argparse
import copy
import gc
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

import torch
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
# Runnable as scripts/bench_recurrent.py, which puts scripts/ on the path
# rather than the repo root.
sys.path.insert(0, str(REPO_ROOT))

from src.train.model import ModelConfig, TransformerLM  # noqa: E402
from src.train.trainer import Trainer  # noqa: E402


def make_batch(vocab: int, batch: int, seq_len: int, device: str, seed: int = 3):
    gen = torch.Generator().manual_seed(seed)
    tokens = torch.randint(0, vocab, (batch, seq_len + 1), generator=gen)
    return (
        tokens[:, :-1].contiguous().to(device),
        tokens[:, 1:].contiguous().to(device),
    )


def run_case(
    cfg: dict,
    label: str,
    device: str,
    batch: int,
    seq_len: int,
    accum: int,
    compile_model: bool,
    warmup_steps: int,
    measure_steps: int,
    loops: int | None = None,
) -> dict:
    cfg = copy.deepcopy(cfg)
    cfg["model"]["max_seq_len"] = seq_len
    if loops is not None and cfg["model"].get("recurrent"):
        cfg["model"]["recurrent"]["loops"] = loops
        # A fixed loop count per case, so the timing is not an average over a
        # sampled range and dynamo compiles one graph.
        cfg["model"]["recurrent"]["train_loop_sampling"] = None
    cfg["train"] = dict(cfg["train"])
    cfg["train"].update(
        {
            "batch_size": batch,
            "grad_accum_steps": accum,
            "ckpt_interval": 0,
            "log_interval": 10**9,
            "compile": compile_model,
        }
    )
    cfg["schedule"] = dict(cfg["schedule"])
    cfg["schedule"]["max_steps"] = warmup_steps + measure_steps
    cfg["schedule"]["warmup_steps"] = 1

    model_cfg = ModelConfig(**cfg["model"])
    model = TransformerLM(model_cfg)
    describe = model.describe()
    out_dir = Path(tempfile.mkdtemp(prefix="bench_recurrent_"))
    trainer = Trainer(model, cfg, out_dir, device=device)
    # Trainer writes a checkpoint whenever it reaches its target step. A 1.5 GiB
    # torch.save inside the timed window would swamp the measurement, so the
    # bench turns saving off.
    trainer.save_checkpoint = lambda name=None: None

    tokens_per_step = batch * seq_len * accum
    data = make_batch(model_cfg.vocab_size, batch, seq_len, device)

    def batches():
        while True:
            yield data

    result = {
        "label": label,
        "params_total": describe["params_total"],
        "params_non_embedding": describe["params_non_embedding"],
        "unique_layers": describe["unique_layers"],
        "loops": describe["loops"],
        "effective_depth": describe["effective_depth"],
        "batch": batch,
        "seq_len": seq_len,
        "grad_accum": accum,
        "tokens_per_step": tokens_per_step,
        "compiled": compile_model,
        "recurrent": describe["recurrent"],
    }
    try:
        trainer.train(batches(), until_step=warmup_steps)
        if device == "cuda":
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        trainer.train(batches(), until_step=warmup_steps + measure_steps)
        if device == "cuda":
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        result["seconds_per_step"] = elapsed / measure_steps
        result["tokens_per_second"] = tokens_per_step * measure_steps / elapsed
        if device == "cuda":
            result["peak_mem_gib"] = torch.cuda.max_memory_allocated() / 2**30
        result["ok"] = True
    except Exception as exc:
        # An out of memory raised inside a compiled backend arrives wrapped, so
        # the case is recorded by what the message says rather than by its type.
        text = str(exc)
        result["ok"] = False
        result["oom"] = "out of memory" in text.lower()
        result["error"] = f"{type(exc).__name__}: {text[:200]}"
    finally:
        del trainer, model
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
        shutil.rmtree(out_dir, ignore_errors=True)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/350m-loop.yaml")
    parser.add_argument("--baseline", default=None, help="second config to time for comparison")
    parser.add_argument("--loops", default="1,2,4,8")
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--seq-len", type=int, default=4096)
    parser.add_argument("--accum", type=int, default=1)
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--warmup-steps", type=int, default=3)
    parser.add_argument("--measure-steps", type=int, default=6)
    parser.add_argument("--grad-checkpoint", default="on", choices=["on", "off", "both"])
    parser.add_argument("--backprop-last-k", default="", help="comma separated k values to sweep at --sweep-loops")
    parser.add_argument("--sweep-loops", type=int, default=8, help="loop count for the backprop_last_k sweep")
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    with open(REPO_ROOT / args.config) as fh:
        loop_cfg = yaml.safe_load(fh)

    loop_counts = [int(v) for v in args.loops.split(",") if v]
    ckpt_modes = {"on": [True], "off": [False], "both": [True, False]}[args.grad_checkpoint]

    results = []
    if args.baseline:
        with open(REPO_ROOT / args.baseline) as fh:
            base_cfg = yaml.safe_load(fh)
        row = run_case(
            base_cfg, f"baseline {Path(args.baseline).stem}", device, args.batch,
            args.seq_len, args.accum, args.compile, args.warmup_steps, args.measure_steps,
        )
        results.append(row)
        print(json.dumps(row))

    for use_ckpt in ckpt_modes:
        for loops in loop_counts:
            cfg = copy.deepcopy(loop_cfg)
            cfg["model"]["recurrent"]["grad_checkpoint"] = use_ckpt
            row = run_case(
                cfg, f"loops={loops} ckpt={'on' if use_ckpt else 'off'}", device, args.batch,
                args.seq_len, args.accum, args.compile, args.warmup_steps,
                args.measure_steps, loops=loops,
            )
            results.append(row)
            print(json.dumps(row))

    for k in [int(v) for v in args.backprop_last_k.split(",") if v]:
        cfg = copy.deepcopy(loop_cfg)
        cfg["model"]["recurrent"]["backprop_last_k"] = k
        cfg["model"]["recurrent"]["grad_checkpoint"] = ckpt_modes[0]
        row = run_case(
            cfg, f"loops={args.sweep_loops} last_k={k} ckpt={'on' if ckpt_modes[0] else 'off'}",
            device, args.batch, args.seq_len, args.accum, args.compile,
            args.warmup_steps, args.measure_steps, loops=args.sweep_loops,
        )
        results.append(row)
        print(json.dumps(row))

    if args.out:
        Path(args.out).write_text(json.dumps(results, indent=2))
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
