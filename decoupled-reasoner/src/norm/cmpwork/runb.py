"""System B: the hand-written frame-aware parser, in two conditions.

`b_oracle` is handed the item's own frame id, which is the condition
`src/norm/CORE.md` section 6 measures and the condition the published
frame-aware parser of `src/frames/parsers.py` runs in. It is the ceiling a
frame grammar reaches when it already covers the frame.

`b_train` is the same parser restricted to the 490 training frames, and is not
told which frame the text is in. It tries each training frame's pattern set in
sorted order and takes the first that reads the whole item. On a training frame
that is the frame itself. On a held-out frame it is whichever training frame's
templates happen to match, or a refusal when none do. This is what a parser
written for a fixed frame set does when text arrives from outside it, and it is
the honest form of "should fail on frames it was not written for".

Neither condition executes anything itself: both hand the structure to
`src/norm/interp.py`.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from multiprocessing import Pool

from src.norm import ndata
from src.norm.interp import run
from src.norm.parse import parse

_TRAIN = None


def train_fids():
    global _TRAIN
    if _TRAIN is None:
        _TRAIN = sorted(ndata.split_frames()["train"])
    return _TRAIN


def one(it):
    rec = {"id": it["id"], "split": it["split"], "shape": it["shape"],
           "fid": it["fid"], "gold": it["gold"], "options": it["options"]}
    p = parse(it["text"], it["fid"])
    if not p.ok:
        rec["b_oracle"] = {"read": 0, "answer": "", "reason": p.reason[:120]}
    else:
        r = run(p.program)
        rec["b_oracle"] = {"read": 1, "answer": r.text if r.ok else "",
                           "reason": "" if r.ok else r.reason[:120]}
    hit = None
    tried = 0
    for f in train_fids():
        tried += 1
        q = parse(it["text"], f)
        if q.ok:
            hit = (f, q)
            break
    if hit is None:
        rec["b_train"] = {"read": 0, "answer": "", "tried": tried,
                          "match_fid": "", "reason": "no training frame reads it"}
    else:
        f, q = hit
        r = run(q.program)
        rec["b_train"] = {"read": 1, "answer": r.text if r.ok else "",
                          "tried": tried, "match_fid": f,
                          "self": int(f == it["fid"]),
                          "reason": "" if r.ok else r.reason[:120]}
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="results/norm/compare/items.jsonl.gz")
    ap.add_argument("--out", default="results/norm/compare/b.jsonl.gz")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    items = [json.loads(l) for l in gzip.open(a.items, "rt")]
    if a.limit:
        items = items[:a.limit]
    train_fids()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    t0 = time.time()
    with Pool(a.procs) as pool:
        recs = pool.map(one, items, chunksize=8)
    with gzip.open(a.out, "wt") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    el = time.time() - t0
    print(json.dumps({"n": len(recs), "seconds": round(el, 1),
                      "per_item": round(el / max(len(recs), 1), 4),
                      "out": a.out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
