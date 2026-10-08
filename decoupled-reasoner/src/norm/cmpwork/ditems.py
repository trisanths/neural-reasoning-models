"""A composition depth ladder whose page does not grow with the depth.

The `iterate` shape is one table read n times, so the page is a ring of fixed
width and the question states n. The plan is n `lookup` steps. Depth therefore
moves on its own axis: the text the reader is handed is the same length at
depth 48 as at depth 2, and only the plan gets longer.

Ring width is held at 49 for every depth, one more than the deepest question
asked. That is what makes the ladder a depth axis and not something else. A
ring narrower than the depth wraps, and a wrapped ring makes depth n and depth
n mod width the same answer, so a reader that ignored n and always walked eight
steps would be scored correct at depth 18 and at depth 28. The first version of
this ladder used width 10 and was aliased in exactly that way: it scored 1.000
at depth 12 with the structure wrong in every item, because the network walked
two steps and two steps is twelve steps on a ring of ten. At width 49 no two
depths in the ladder share an answer.

Holding the width fixed also holds the page fixed. The text handed to the
reader is the same length at depth 48 as at depth 2 and only the question's
number moves. `gen.py` draws n from 1 to 8 with a ring of n + 2, so a 49 row
ring is wider than anything the reader trained on, and that cost is measured by
the narrow companion ladder rather than assumed: `--width 0` reproduces the
generator's own width of max(4, n + 2) at every depth.

Depth 1 is not on the ladder. A one step plan is what `render.classify` calls
`lookup`, so the grammar writes it with the lookup question and it is not an
iterate item at all.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import random

from src.norm import gen, ndata, render
from src.norm.interp import run
from src.norm.lang import Table, program_json
from src.norm.neval import candidates
from src.norm.shapes import assemble

DEPTHS = (2, 3, 4, 6, 8, 12, 16, 17, 20, 24, 32, 48)
WIDTH = 49
SPLITS = ("train", "qframe", "lexicon", "mode", "mixed")


def case(fid: str, seed: int, n: int, width: int):
    rng = random.Random(seed)
    lex = gen.lexicon_for(fid, rng)
    name = lex.name()
    ring = lex.words(width)
    rng.shuffle(ring)
    t = Table(name, tuple((ring[i], ring[(i + 1) % width])
                          for i in range(width)))
    return assemble("iterate", tables=[t],
                    inputs=(("x", rng.choice(ring)),), n=n)


def build(split, fids, n_items, seed0, width0, depths):
    fids = sorted(fids)
    rows = []
    for depth in depths:
        width = width0 or max(4, depth + 2)
        got, tries, i = 0, 0, 0
        while got < n_items and tries < n_items * 20:
            tries += 1
            fid = fids[i % len(fids)]
            i += 1
            seed = seed0 + tries * 104729 + depth
            try:
                p = case(fid, seed, depth, width)
                d = render.render(p, fid, seed % 5)
            except Exception:
                continue
            r = run(p)
            if not r.ok or not r.text:
                continue
            cs = candidates(p)
            if cs is None or len(cs) < 2 or r.text not in cs:
                continue
            rows.append({"id": f"{split}/d{depth}/{got}", "split": split,
                         "shape": "iterate", "depth": depth, "fid": fid,
                         "seed": seed, "steps": len(p.steps),
                         "ring_width": width,
                         "pages": list(d["pages"]), "question": d["question"],
                         "text": d["text"], "prog": program_json(p),
                         "gold": r.text,
                         "options": sorted(str(c) for c in cs)})
            got += 1
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20260831)
    ap.add_argument("--splits", default="train,qframe,lexicon,mode,mixed")
    ap.add_argument("--width", type=int, default=WIDTH)
    ap.add_argument("--depths", default=",".join(str(d) for d in DEPTHS))
    ap.add_argument("--out", default="results/norm/compare/d_items.jsonl.gz")
    a = ap.parse_args()
    sp = ndata.split_frames()
    rows = []
    for split in a.splits.split(","):
        got = build(split, sp[split], a.n, a.seed, a.width,
                    tuple(int(x) for x in a.depths.split(",")))
        rows.extend(got)
        print(f"{split:10s} {len(got):5d}", flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with gzip.open(a.out, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump({"n_rows": len(rows), "depths": a.depths,
                   "ring_width": a.width or "max(4, depth + 2)",
                   "n_per_cell": a.n, "seed": a.seed}, fh, indent=2)
    print(json.dumps({"n_rows": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
