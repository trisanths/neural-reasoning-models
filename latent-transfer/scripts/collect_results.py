"""Assembles every run into one table with cost alongside accuracy.

Accuracy without cost is meaningless here: the whole claim is that the pipeline
buys most of the big model's reasoning for a fraction of its compute. FLOPs come
from the same analytic model as scripts/pair_economics.py, evaluated at the
measured ProsQA shape.

Reports what is missing rather than omitting it, so a truncated run cannot be
mistaken for a complete one.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.pair_economics import QWEN, decode, prefill, step  # noqa: E402

L, K, DEC, COT = 400, 6, 8, 49


def flops_small_only(s):
    return prefill(s, L) + decode(s, L, DEC)


def flops_big_cot(b):
    return prefill(b, L) + decode(b, L, COT + DEC)


def flops_big_latent(b):
    return prefill(b, L) + sum(step(b, L + i) for i in range(K)) + decode(b, L + K, DEC)


def flops_pipeline(s, b, m):
    n = m if m else L
    return (
        prefill(s, L)
        + sum(step(s, L + i) for i in range(K))
        + decode(s, L + K, DEC)
        + prefill(b, n)
        + sum(step(b, n + i) for i in range(K))
        + 2 * (n * s.d * b.d + K * b.d * s.d)
    )


def read(path, *keys):
    if not os.path.exists(path):
        return None
    d = json.load(open(path))
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--runs", default="runs")
    p.add_argument("--small", default="0.5B")
    p.add_argument("--big", default="7B")
    p.add_argument("--out", default=None)
    a = p.parse_args()

    s, b = QWEN[a.small], QWEN[a.big]
    R = a.runs
    base = flops_small_only(s)

    rows = []
    rows.append(
        ("small alone (Coconut)", read(f"{R}/eval_small.json", "overall", "exact")
         or read(f"{R}/qwen05b/metrics.json", "test", "exact"), flops_small_only(s))
    )
    rows.append(
        ("big alone (Coconut)", read(f"{R}/eval_big.json", "overall", "exact")
         or read(f"{R}/qwen7b/metrics.json", "test", "exact"), flops_big_latent(b))
    )
    rows.append(("big alone (CoT baseline, not run)", None, flops_big_cot(b)))
    for m in (8, 32, 128):
        rows.append(
            (f"pipeline m={m}", read(f"{R}/pipe_m{m}/metrics.json", "test", "exact"),
             flops_pipeline(s, b, m))
        )
    rows.append(
        ("CONTROL random frozen receiver",
         read(f"{R}/pipe_random/metrics.json", "test", "exact"), flops_pipeline(s, b, 32))
    )

    print(f"ProsQA test accuracy and per-query cost  ({a.small} -> {a.big})")
    print("=" * 74)
    print(f"{'configuration':<36}{'exact':>9}{'TFLOPs':>10}{'x small':>10}")
    print("-" * 74)
    missing = []
    for name, acc, f in rows:
        astr = f"{acc:.4f}" if acc is not None else "   --"
        if acc is None:
            missing.append(name)
        print(f"{name:<36}{astr:>9}{f / 1e12:>10.2f}{f / base:>9.2f}x")
    print("-" * 74)

    if missing:
        print("\nNOT MEASURED (do not read these rows as zero):")
        for m in missing:
            print(f"  - {m}")

    small_acc = rows[0][1]
    big_acc = rows[1][1]
    pipe = next((r for r in rows if r[0] == "pipeline m=32"), None)
    if small_acc and big_acc and pipe and pipe[1]:
        gap = big_acc - small_acc
        closed = (pipe[1] - small_acc) / gap if abs(gap) > 1e-9 else float("nan")
        print(
            f"\nGap closed by the pipeline: {closed:.0%} "
            f"(small {small_acc:.3f} -> pipeline {pipe[1]:.3f} -> big {big_acc:.3f}) "
            f"at {pipe[2] / base:.2f}x the small model's cost"
        )

    if a.out:
        json.dump(
            {"rows": [{"name": n, "exact": acc, "flops": f} for n, acc, f in rows]},
            open(a.out, "w"), indent=2,
        )


if __name__ == "__main__":
    main()
