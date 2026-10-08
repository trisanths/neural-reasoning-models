"""What the value-first failures of the held-out sentence mode are made of.

A reader that is confused by an unfamiliar sentence could emit a stream that is
not a structure, and the interpreter would decline. A reader that applies the
wrong binding emits a well-formed structure that runs to the wrong answer. The
categories are disjoint, so counting them says which of the two this is.
"""
import gzip
import json
import os
from collections import Counter

ROOT = os.path.expanduser("~/decoupled-reasoner")
SEVEN = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
         "precedence")
CATS = ("exact", "wrong", "refused", "malformed")
out = {}
for tag in ("l45", "xl93"):
    p = os.path.join(ROOT, f"results/system/eval/{tag}/"
                           "records_mode_greedy.jsonl.gz")
    if not os.path.exists(p):
        continue
    c = Counter()
    with gzip.open(p, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            if r["shape"] not in SEVEN:
                continue
            kp = r["fid"].split(".")[2]
            c[(kp, "n")] += 1
            for cat in CATS:
                if r[cat]:
                    c[(kp, cat)] += 1
    print("===", tag, "the seven shapes, held-out sentence mode")
    for kp in ("key_first", "value_first"):
        n = c[(kp, "n")]
        cells = "  ".join(f"{cat} {c[(kp, cat)]:4d} ({c[(kp, cat)] / n:.4f})"
                          for cat in CATS)
        print(f"  {kp:12s} n={n:4d}  {cells}")
    out[tag] = {f"{a}|{b}": v for (a, b), v in c.items()}
dest = os.path.join(ROOT, "results/system/failcat_mode_seven.json")
with open(dest, "w") as fh:
    json.dump({"shapes": list(SEVEN),
               "source": "results/system/eval/*/records_mode_greedy.jsonl.gz",
               "cells": out}, fh, indent=1)
print("wrote", dest)
