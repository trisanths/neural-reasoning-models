"""Throughput and memory for the evidence cross-attention model.

Three measurements on one GPU, all at bf16 autocast with a full training
step (forward, backward, optimizer-free) so the numbers project to a real
run:

  1. The 350m-xattn config at bank sizes 64, 256, and 1024 chunks of 128
     tokens, in both pooled and token granularity: seconds per step, answer
     tokens per second, evidence tokens per second, peak memory.
  2. The standard 350m decoder from configs/350m.yaml reading the same
     evidence in its context window, at growing sequence lengths until it
     runs out of memory. This locates the context-length limit the
     concatenation approach actually hits on this GPU.
  3. A batch-size sweep at bank 256, which is what the recommended 8-GPU
     shape is derived from.

Usage:

    uv run python -m scripts.bench_evidence --out results/evidence-bench.json
"""

import argparse
import json
import time
from pathlib import Path

import torch
import yaml

from src.train.evidence_model import (EvidenceTransformerLM,
                                      config_from_yaml,
                                      cross_attention_flops)
from src.train.model import ModelConfig, TransformerLM

REPO_ROOT = Path(__file__).resolve().parents[1]
BANK_SIZES = [64, 256, 1024]
CONTEXT_LENGTHS = [2048, 4096, 8192, 16384, 32768, 65536, 131072]


def sync():
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def timed_step(fn, warmup: int = 2, repeats: int = 5) -> float:
    for _ in range(warmup):
        fn()
    sync()
    times = []
    for _ in range(repeats):
        sync()
        start = time.perf_counter()
        fn()
        sync()
        times.append(time.perf_counter() - start)
    return sorted(times)[len(times) // 2]


def peak_mb() -> float:
    return torch.cuda.max_memory_allocated() / 1024 ** 2


def bench_xattn(model_cfg, device, batch_size, seq_len, n_chunks, mode,
                answer_tokens_per_seq):
    torch.cuda.reset_peak_memory_stats()
    model = EvidenceTransformerLM(model_cfg).to(device)
    model.train()
    gen = torch.Generator(device=device).manual_seed(0)
    ids = torch.randint(0, model_cfg.vocab_size, (batch_size, seq_len),
                        device=device, generator=gen)
    ev = torch.randint(0, model_cfg.vocab_size,
                       (batch_size, n_chunks, model_cfg.chunk_len),
                       device=device, generator=gen)
    mask = torch.ones_like(ev, dtype=torch.bool)
    rel = torch.rand((batch_size, n_chunks), device=device, generator=gen)
    targets = ids.clone()
    targets[:, :seq_len - answer_tokens_per_seq] = -100

    def step():
        model.zero_grad(set_to_none=True)
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            _, loss = model(ids, ev, mask, rel, targets=targets, mode=mode)
        loss.backward()

    seconds = timed_step(step)
    evidence_tokens = batch_size * n_chunks * model_cfg.chunk_len
    answer_tokens = batch_size * answer_tokens_per_seq
    flops = cross_attention_flops(model_cfg, seq_len, n_chunks, mode)
    out = {
        "mode": mode,
        "batch_size": batch_size,
        "seq_len": seq_len,
        "n_chunks": n_chunks,
        "chunk_len": model_cfg.chunk_len,
        "evidence_tokens_per_step": evidence_tokens,
        "answer_tokens_per_step": answer_tokens,
        "seconds_per_step": round(seconds, 5),
        "evidence_tokens_per_s": round(evidence_tokens / seconds, 1),
        "answer_tokens_per_s": round(answer_tokens / seconds, 1),
        "peak_mem_mb": round(peak_mb(), 1),
        "fwd_tflops_per_seq": round(flops["total"] / 1e12, 4),
    }
    del model, ids, ev, mask, rel, targets
    torch.cuda.empty_cache()
    return out


def bench_standard_in_context(std_cfg: dict, device, seq_len, batch_size=1):
    """One training step of the plain decoder with seq_len tokens in context."""
    cfg = ModelConfig(**{**std_cfg, "max_seq_len": seq_len})
    torch.cuda.reset_peak_memory_stats()
    model = TransformerLM(cfg).to(device)
    model.train()
    gen = torch.Generator(device=device).manual_seed(0)
    ids = torch.randint(0, cfg.vocab_size, (batch_size, seq_len), device=device,
                        generator=gen)
    targets = ids.clone()

    def step():
        model.zero_grad(set_to_none=True)
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            _, loss = model(ids, targets)
        loss.backward()

    seconds = timed_step(step, warmup=1, repeats=3)
    out = {
        "seq_len": seq_len,
        "batch_size": batch_size,
        "seconds_per_step": round(seconds, 5),
        "tokens_per_s": round(batch_size * seq_len / seconds, 1),
        "peak_mem_mb": round(peak_mb(), 1),
        "equivalent_chunks_of_128": seq_len // 128,
    }
    del model, ids, targets
    torch.cuda.empty_cache()
    return out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(REPO_ROOT / "configs" / "350m-xattn.yaml"))
    parser.add_argument("--standard", default=str(REPO_ROOT / "configs" / "350m.yaml"))
    parser.add_argument("--seq-len", type=int, default=256,
                        help="working sequence length: question plus answer")
    parser.add_argument("--answer-tokens", type=int, default=64,
                        help="supervised tokens per sequence")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--batch-sweep", default="1,2,4,8",
                        help="batch sizes to sweep at bank 256")
    parser.add_argument("--banks", default=",".join(str(b) for b in BANK_SIZES))
    parser.add_argument("--skip-context", action="store_true")
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    if not torch.cuda.is_available():
        raise SystemExit("this bench needs a gpu")
    device = "cuda"

    with open(args.config) as fh:
        xcfg = yaml.safe_load(fh)
    with open(args.standard) as fh:
        scfg = yaml.safe_load(fh)
    model_cfg = config_from_yaml(xcfg["model"])

    report = {
        "gpu": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "config": Path(args.config).name,
        "seq_len": args.seq_len,
        "answer_tokens_per_seq": args.answer_tokens,
    }

    probe = EvidenceTransformerLM(model_cfg)
    report["params"] = probe.param_breakdown()
    standard = TransformerLM(ModelConfig(**scfg["model"]))
    report["standard_params"] = {
        "total": sum(p.numel() for p in standard.parameters()),
        "non_embedding": standard.num_params(non_embedding=True),
        "max_seq_len": scfg["model"]["max_seq_len"],
    }
    report["param_ratio"] = report["params"]["total"] / report["standard_params"]["total"]
    del probe, standard

    banks = [int(b) for b in args.banks.split(",")]
    report["xattn"] = []
    for mode in ("pooled", "tokens"):
        for n_chunks in banks:
            try:
                row = bench_xattn(model_cfg, device, args.batch_size, args.seq_len,
                                  n_chunks, mode, args.answer_tokens)
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                row = {"mode": mode, "n_chunks": n_chunks,
                       "batch_size": args.batch_size, "oom": True}
            report["xattn"].append(row)
            print(json.dumps(row), flush=True)

    report["batch_sweep"] = []
    for bs in [int(b) for b in args.batch_sweep.split(",")]:
        try:
            row = bench_xattn(model_cfg, device, bs, args.seq_len, 256, "pooled",
                              args.answer_tokens)
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            row = {"mode": "pooled", "n_chunks": 256, "batch_size": bs, "oom": True}
        report["batch_sweep"].append(row)
        print(json.dumps(row), flush=True)

    report["standard_in_context"] = []
    if not args.skip_context:
        for seq_len in CONTEXT_LENGTHS:
            try:
                row = bench_standard_in_context(scfg["model"], device, seq_len)
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                row = {"seq_len": seq_len, "oom": True,
                       "equivalent_chunks_of_128": seq_len // 128}
                report["standard_in_context"].append(row)
                print(json.dumps(row), flush=True)
                break
            report["standard_in_context"].append(row)
            print(json.dumps(row), flush=True)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as fh:
            json.dump(report, fh, indent=2)
        print(f"wrote {out_path}")
    return report


if __name__ == "__main__":
    main()
