"""The closed book table, with the published figures beside the reproduction.

PUBLISHED holds what Liquid publish for the LFM2 generation. They are quoted
here so a reproduction can be read against them in the same row, and they are
labelled with the model they belong to: the numbers in the LFM2 table are not
LFM2.5 numbers and putting an LFM2.5 result under a 43.43 that belongs to
LFM2-350M would be the kind of mismatch an external reader finds first.
"""
from __future__ import annotations

import argparse
import glob
import json
import os

# Liquid's published figures for the LFM2 generation, as supplied to this lane.
PUBLISHED = {
    ("LiquidAI/LFM2-350M", "mmlu"): 43.43,
    ("LiquidAI/LFM2-350M", "gsm8k"): 30.1,
    ("LiquidAI/LFM2-1.2B", "mmlu"): 55.23,
    ("LiquidAI/LFM2-1.2B", "gsm8k"): 58.3,
}

# What the LFM2.5 cards publish instead. No MMLU or GSM8K figure appears on
# them, so those cells have no published counterpart and are left empty rather
# than compared against a different generation's number.
LFM25_CARD = {
    "LiquidAI/LFM2.5-350M": {"GPQA Diamond": 30.64, "MMLU-Pro": 20.01,
                             "IFEval": 76.96},
}


def tbl(head, rows):
    w = [len(str(h)) for h in head]
    for r in rows:
        for i, c in enumerate(r):
            w[i] = max(w[i], len(str(c)))
    o = ["| " + " | ".join(str(h).ljust(w[i]) for i, h in enumerate(head))
         + " |",
         "| " + " | ".join("-" * w[i] for i in range(len(head))) + " |"]
    for r in rows:
        o.append("| " + " | ".join(str(c).ljust(w[i])
                                   for i, c in enumerate(r)) + " |")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/extern/bench")
    ap.add_argument("--out", default="results/extern/bench_summary.md")
    a = ap.parse_args()
    rows = []
    for f in sorted(glob.glob(f"{a.dir}/*.json")):
        d = json.load(open(f))
        pub = PUBLISHED.get((d["model"], d["task"]))
        if d["task"] == "gsm8k":
            acc, extra = d["strict_match"], f"flexible {d['flexible_extract']:.4f}"
            floor = 0.0
        else:
            acc, extra = d["acc"], f"norm {d['acc_norm']:.4f}"
            floor = d["floor"]
        rows.append([
            d["model"], d["task"], d.get("fmt", "-"), d.get("shots", "-"),
            d["n"], f"{floor:.4f}", f"{acc:.4f}", f"{acc * 100:.2f}",
            f"{pub:.2f}" if pub else "-",
            f"{acc * 100 - pub:+.2f}" if pub else "-", extra,
            f"{d.get('params_total', 0):,}" if d.get("params_total") else "-",
        ])
    md = ["# Public benchmarks, closed book", "",
          "Every cell states its own n and chance floor. Nothing is pooled "
          "across benchmarks. `published` is Liquid's figure for the model "
          "named in that row and is blank where that model's card publishes "
          "no such figure.", "",
          tbl(["model", "task", "format", "shots", "n", "floor", "acc",
               "acc %", "published", "delta", "other", "parameters"], rows)]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
