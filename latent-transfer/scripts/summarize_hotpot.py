"""Final HotpotQA table: accuracy beside per-query cost.

Accuracy alone does not carry the claim. The point of the architecture is to buy
most of the big model's reasoning for a fraction of its compute, so both numbers
have to appear together, and any configuration that was not measured has to say
so rather than render as blank.

Costs are analytic FLOPs at the measured HotpotQA shape (1403-token context,
6 latent steps, 16-token answer), from the same model used in pair_economics.py.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.pair_economics import QWEN, decode, prefill, step  # noqa: E402

L, K, DEC, COT = 1403, 6, 16, 60
S, B = QWEN["0.5B"], QWEN["7B"]


def small_only():
    return prefill(S, L) + decode(S, L, DEC)


def big_cot():
    return prefill(B, L) + decode(B, L, COT + DEC)


def big_latent():
    return prefill(B, L) + sum(step(B, L + i) for i in range(K)) + decode(B, L + K, DEC)


def pipeline(m):
    n = m or L
    return (
        prefill(S, L)
        + sum(step(S, L + i) for i in range(K))
        + decode(S, L + K, DEC)
        + prefill(B, n)
        + sum(step(B, n + i) for i in range(K))
        + 2 * (n * S.d * B.d + K * B.d * S.d)
    )


def acc(path, *keys):
    if not os.path.exists(path):
        return None
    d = json.load(open(path))
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "results/h200_hotpot"
    base = small_only()
    rows = [
        ("Qwen2.5-0.5B alone (latent)", acc(f"{root}/hp_small/metrics.json", "test", "exact"), base),
        ("Qwen2.5-7B alone (latent)", acc(f"{root}/hp_big/metrics.json", "test", "exact"), big_latent()),
        ("7B alone, explicit CoT (not run)", None, big_cot()),
        ("PIPELINE m=32, adapted receiver", acc(f"{root}/hp_pipe_m32/metrics.json", "test", "exact"), pipeline(32)),
        ("CONTROL random receiver", acc(f"{root}/hp_pipe_random/metrics.json", "test", "exact"), pipeline(32)),
    ]

    print(f"HotpotQA distractor, {L}-token contexts, 0.5B -> 7B")
    print("=" * 72)
    print(f"{'configuration':<36}{'exact':>9}{'TFLOPs':>10}{'x small':>10}")
    print("-" * 72)
    missing = []
    for name, a, f in rows:
        astr = f"{a:.4f}" if a is not None else "   --"
        if a is None:
            missing.append(name)
        print(f"{name:<36}{astr:>9}{f / 1e12:>10.2f}{f / base:>9.2f}x")
    print("-" * 72)

    if missing:
        print("\nNOT MEASURED (not zero):")
        for m in missing:
            print(f"  - {m}")

    small, big = rows[0][1], rows[1][1]
    pipe, ctrl = rows[3][1], rows[4][1]
    if None not in (small, big, pipe):
        gap = big - small
        closed = (pipe - small) / gap if abs(gap) > 1e-9 else float("nan")
        print(f"\nfloor {small:.4f} -> pipeline {pipe:.4f} -> ceiling {big:.4f}")
        print(f"gap closed: {closed:.0%}  at {pipeline(32) / base:.2f}x the small model's cost")
        print(f"cheaper than the 7B with CoT: {big_cot() / pipeline(32):.1f}x")
    if None not in (pipe, ctrl):
        d = pipe - ctrl
        # 500 test examples; a difference under ~0.045 is inside two standard
        # errors and should not be read as an effect.
        verdict = "REAL" if d > 0.045 else "NOT DISTINGUISHABLE from the control"
        print(f"\npipeline - random control: {d:+.4f}  -> {verdict}")


if __name__ == "__main__":
    main()
