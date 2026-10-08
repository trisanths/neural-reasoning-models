"""How far the held-out frames really are from the training frames.

A withheld frame is only withheld to the extent that no training frame reads
it. `src/norm/nsearch.py` measures whether the reference parser can read a
held-out item with some training frame's templates; this measures which
training frame that is, and on how many of the five frame axes it differs from
the item's own. A held-out item read by a frame one axis away is a small step;
one that every training frame refuses is the real thing.

Written to `results/norm/nsearch/band.json`.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter

from src.norm import ndata, neval
from src.norm.parse import parse

AXES = ("lexicon", "mode", "key_pos", "qform", "scope_pos")
SPLITS = ("qframe", "lexicon", "mode", "mixed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--out", default="results/norm/nsearch/band.json")
    ap.add_argument("--n", type=int, default=140)
    ap.add_argument("--splits", default=",".join(SPLITS))
    a = ap.parse_args()

    train_fids = ndata.split_frames()["train"]
    report = {"n_train_frames": len(train_fids), "n_per_split": a.n,
              "splits": {}}
    for sp in a.splits.split(","):
        items = neval.load_eval(os.path.join(a.data, sp), a.n)
        c = Counter()
        for it in items:
            hit = None
            for fid in train_fids:
                pp = parse(it["text"], fid)
                if pp.ok:
                    hit = fid
                    break
            if hit is None:
                c["refused_by_all"] += 1
                continue
            a_, b_ = it["fid"].split("."), hit.split(".")
            diff = tuple(ax for ax, x, y in zip(AXES, a_, b_) if x != y)
            c["|".join(diff) or "identical"] += 1
        report["splits"][sp] = {"n": len(items), "counts": dict(c)}
        print(sp, json.dumps(dict(c)), flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(report, fh, indent=1)
    print("wrote", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
