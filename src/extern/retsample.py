"""Hand check sample for the answer detector.

Prints, for a seeded random sample, the question, the gold answer, the
number of distractors the same test finds in the same text, and the
characters around the match. A detector that fires on a one word gold
that the page uses in an unrelated sentence would inflate the answer
present cell, so false positives are sampled as well as misses.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys

sys.path.insert(0, ".")
from src.extern.retpack import content_terms, norm  # noqa: E402


def window(hay, needle, pad=160):
    i = hay.find(needle)
    if i < 0:
        return ""
    return hay[max(0, i - pad):i + len(needle) + pad]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diag", default="results/extern/retdiag.json")
    ap.add_argument("--mode", default="hit")
    ap.add_argument("--pack", default="sequential")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    recs = [r for r in json.load(open(a.diag))["records"] if r.get("cached")]
    if a.mode == "any":
        sub = recs
    else:
        sub = [r for r in recs if r["mode"] == a.mode]
    rng = random.Random(a.seed)
    rng.shuffle(sub)
    print(f"# mode={a.mode} pool={len(sub)} sample={min(a.k, len(sub))} "
          f"seed={a.seed}")
    for r in sub[:a.k]:
        g = norm(r["gold"])
        print("=" * 78)
        print(f"{r['id']}  gold_terms={len(content_terms(r['gold']))} "
              f"gold_norm_len={len(g)}")
        print("Q:", " ".join(r["question"].split())[:220])
        print("gold:", r["gold"][:180])
        print("choices:", [c[:60] for c in r["choices"]])
        print("ctx flags:", json.dumps(r["ctx"][a.pack]))
        print("per page gold/soft/stem:",
              [(p["gold"], p["gold_soft"], p["stem"], p["n_distractors"],
                p["chars"]) for p in r["per_page"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
