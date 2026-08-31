"""Which prompt formulation to take to the full item set.

The choice is made over the formulations that hand the model no more than the
library system was handed. `options` prints the candidate list, which is more,
so it is reported as its own advantaged cell and is never what a matched row
is built from.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os

from src.extern.answer import answer_span
from src.norm.cmpwork.grade import forced

MATCHED = ("bare", "reader", "worked", "prefill")


def strict_of(path):
    rows = [json.loads(l) for l in gzip.open(path, "rt")]
    if not rows:
        return 0.0, 0
    s = 0
    for r in rows:
        sp = answer_span(r["raw"])
        s += forced(sp["span"], r["options"], r["gold"])["strict_correct"]
    return s / len(rows), len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dir", default="results/extern")
    ap.add_argument("--any", action="store_true",
                    help="allow the advantaged options variant to win")
    a = ap.parse_args()
    best, bs = None, -1.0
    for p in sorted(glob.glob(f"{a.dir}/sel_{a.model}_*.jsonl.gz")):
        v = os.path.basename(p)[len(f"sel_{a.model}_"):-len(".jsonl.gz")]
        if not a.any and v not in MATCHED:
            continue
        s, n = strict_of(p)
        print(f"{v}\t{s:.4f}\tn={n}", file=os.sys.stderr)
        if s > bs:
            best, bs = v, s
    print(best or "worked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
