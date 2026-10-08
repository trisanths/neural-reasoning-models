"""Turns results.json into a readable summary with the interpretation rules
that make the headline number meaningful.

The pipeline's accuracy is only informative relative to four other rows, so the
report states explicitly whether each control passed rather than leaving the
reader to compare numbers.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.flops import fmt  # noqa: E402

CHANCE = 0.5  # two candidates


def find(rows, needle):
    for r in rows:
        if needle in r["name"].lower():
            return r
    return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--out", default=None)
    a = p.parse_args()

    with open(a.results) as f:
        data = json.load(f)
    rows = data["rows"]

    lines = []
    w = max(len(r["name"]) for r in rows) + 2
    lines.append(f"{'configuration':<{w}} {'exact':>7} {'concept':>8} {'FLOPs/query':>12} {'rel':>7}")
    lines.append("-" * (w + 38))
    base = min(r["flops"] for r in rows)
    for r in rows:
        lines.append(
            f"{r['name']:<{w}} {r['exact']:>7.3f} {r['concept']:>8.3f} "
            f"{fmt(r['flops']):>12} {r['flops'] / base:>6.1f}x"
        )

    floor = find(rows, "floor")
    ceiling = find(rows, "ceiling")
    pipe = find(rows, "cross-model")
    rand = find(rows, "random big")

    lines.append("")
    lines.append("interpretation")
    lines.append("-" * 14)

    if ceiling and ceiling["concept"] < CHANCE + 0.05:
        lines.append(
            f"INCONCLUSIVE: the big model itself scores {ceiling['concept']:.3f}, at or near "
            f"chance ({CHANCE}). There is no capacity gap to close, so the pipeline "
            "number cannot be interpreted. Fix the ceiling before reading anything else."
        )
    elif pipe and floor and ceiling:
        gap = ceiling["concept"] - floor["concept"]
        closed = (pipe["concept"] - floor["concept"]) / gap if gap > 1e-6 else 0.0
        lines.append(
            f"gap to close: {floor['concept']:.3f} (small) -> {ceiling['concept']:.3f} (big)"
        )
        lines.append(
            f"pipeline at {pipe['concept']:.3f} closes {closed * 100:.0f}% of it, "
            f"at {pipe['flops'] / ceiling['flops']:.2f}x the big model's FLOPs "
            f"and {pipe['flops'] / floor['flops']:.2f}x the small model's"
        )
        c1_pass = None
        if rand:
            delta = pipe["concept"] - rand["concept"]
            c1_pass = delta > 0.03
            lines.append(
                f"[{'PASS' if c1_pass else 'FAIL'}] control 1 (random big model): "
                f"{rand['concept']:.3f} vs pipeline {pipe['concept']:.3f} "
                f"(delta {delta:+.3f}). "
                + ("The trained big model is contributing." if c1_pass
                   else "The big model is NOT contributing; an untrained network of "
                        "the same shape does just as well, so the projectors and the "
                        "small model's adapter account for the whole result.")
            )
        delta2 = pipe["concept"] - floor["concept"]
        c2_pass = delta2 > 0.03
        if c2_pass and c1_pass is False:
            # Beating the floor is not evidence of transfer once control 1 has
            # shown the big model is irrelevant -- the adapter explains it.
            note = (
                "The pipeline beats the small model, but control 1 already showed "
                "this is NOT the big model's capacity: it is the extra trainable "
                "adapter and projectors fitted on top of the frozen small model."
            )
        elif c2_pass:
            note = "The gain is capacity, not just extra sequential compute."
        else:
            note = "The gain is not attributable to the big model's capacity."
        lines.append(
            f"[{'PASS' if c2_pass else 'FAIL'}] control 2 (small model, same latent "
            f"steps): {floor['concept']:.3f} vs pipeline {pipe['concept']:.3f} "
            f"(delta {delta2:+.3f}). {note}"
        )
        if c1_pass is False:
            lines.append("")
            lines.append(
                "VERDICT: the cross-model latent handoff did NOT transfer reasoning. "
                "Diagnosis is in the stage-1 gate: driving the big model from "
                "projected small-model states drops it far below its native accuracy, "
                "so the thoughts it returns carry little of its own computation."
            )

    text = "\n".join(lines)
    print(text)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text + "\n")
        print(f"\nsaved -> {a.out}")


if __name__ == "__main__":
    main()
