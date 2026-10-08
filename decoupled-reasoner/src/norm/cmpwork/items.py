"""One item set that all three systems answer, with the option set attached.

An item is a structure drawn by `src/norm/gen.py`, written into one corpus
frame by `src/norm/render.py`, and the answer the interpreter computes for it.
The option set is `src/norm/neval.py:candidates`, the values the plan's last
step could have returned. An item is kept only when that set holds the gold
answer and has at least two members, so the chance floor is 1/len(options) and
is real rather than assumed. Shapes whose answer is an integer the page never
states are dropped by that rule, which removes `apply_n` and `sum_chain`.

Frames come from `src/norm/ndata.py:split_frames`, the same partition the
normalizer trained under, so a held-out frame here is held out there.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random

from src.norm import gen, ndata, render
from src.norm.interp import run
from src.norm.lang import program_json
from src.norm.neval import candidates

SHAPES = ("lookup", "lookup_general", "classify", "inverse", "compose",
          "iterate", "pair", "priority", "exclusion", "lookup_then_band",
          "band_then_lookup", "precedence")

SPLITS = ("train", "qframe", "lexicon", "mode", "mixed")


def build(split: str, fids, shape: str, n: int, seed0: int):
    """n items of one shape in one split, frames cycled in sorted order."""
    fids = sorted(fids)
    out = []
    tries = 0
    i = 0
    while len(out) < n and tries < n * 20:
        tries += 1
        fid = fids[i % len(fids)]
        i += 1
        seed = seed0 + tries * 7919
        try:
            p = gen.make_for(fid, shape, seed)
            d = render.render(p, fid, preamble_level=(seed % 5))
        except Exception:
            continue
        r = run(p)
        if not r.ok or not r.text:
            continue
        cs = candidates(p)
        if cs is None or len(cs) < 2 or r.text not in cs:
            continue
        out.append({
            "id": f"{split}/{shape}/{len(out)}",
            "split": split, "fid": fid, "shape": shape, "seed": seed,
            "preamble": seed % 5,
            "pages": list(d["pages"]), "question": d["question"],
            "text": d["text"], "prog": program_json(p),
            "gold": r.text, "options": sorted(str(c) for c in cs),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260831)
    ap.add_argument("--out", default="results/norm/compare/items.jsonl.gz")
    a = ap.parse_args()

    sp = ndata.split_frames()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    rows = []
    for split in SPLITS:
        for shape in SHAPES:
            got = build(split, sp[split], shape, a.n, a.seed)
            rows.extend(got)
            print(f"{split:10s} {shape:18s} {len(got):4d}", flush=True)
    with gzip.open(a.out, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    meta = {"n_items": len(rows), "n_per_cell": a.n, "seed": a.seed,
            "shapes": list(SHAPES), "splits": list(SPLITS),
            "frames_per_split": {k: len(v) for k, v in sp.items()}}
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
