"""Training and evaluation examples for the shared domain grid.

`src/norm/gen.py` draws the `pair` shape with two disjoint symbol sets, one for
each key column, so no page it writes can state a non-commutative operation
over one domain. The transposed operand test needs exactly that page, and the
normalizer has never read one.

Nothing about the language or the seam is in the way: `serialize` and
`deserialize` round trip a shared domain grid, and the reference parser reads
it exactly. What is missing is the example. This module writes it, and
`ftune.py` measures how many of them the network needs.

Training grids come from training frames only. Evaluation grids come from every
frame group, so acquisition is measured on frames the network never trained on
as well as on frames it did.
"""
from __future__ import annotations

import argparse
import json
import os
import random

import numpy as np

from src.norm import gen, ndata, render
from src.norm.lang import program_json
from src.norm.ntok import TokenizeError, serialize
from src.norm.shapes import assemble
from src.norm.lang import Table

WIDTH = 3


def case(fid: str, seed: int, transpose: bool = False):
    rng = random.Random(seed)
    lex = gen.lexicon_for(fid, rng)
    syms = lex.words(WIDTH)
    cells = lex.words(WIDTH * WIDTH)
    name = lex.name()
    ent, t = [], 0
    for a in syms:
        for b in syms:
            ent.append(((a, b), cells[t]))
            t += 1
    if transpose:
        ent = [((b, a), v) for (a, b), v in ent]
    ai, bi = rng.sample(range(WIDTH), 2)
    return assemble("pair", tables=[Table(name, tuple(ent))],
                    inputs=(("x", syms[ai]), ("y", syms[bi])))


def example(fid: str, seed: int, transpose: bool = False):
    iv, ov = ndata._vocab()
    p = case(fid, seed, transpose)
    d = render.render(p, fid, seed % 5)
    try:
        ids, slots, n_unk = iv.encode(d["text"])
    except TokenizeError:
        return None
    if n_unk or len(ids) > ndata.MAX_IN:
        return None
    try:
        toks = serialize(p, slots)
    except TokenizeError:
        return None
    if len(toks) + 2 > ndata.MAX_OUT:
        return None
    return {"in": ids, "out": [ov.bos] + ov.encode(toks) + [ov.eos],
            "slots": slots, "prog": program_json(p), "fid": fid,
            "text": d["text"]}


def draw(fids, n: int, seed0: int, transpose: bool = False):
    fids = sorted(fids)
    out, tries, i = [], 0, 0
    while len(out) < n and tries < n * 20:
        tries += 1
        e = example(fids[i % len(fids)], seed0 + tries * 7919, transpose)
        i += 1
        if e is not None:
            out.append(e)
    return out


def save(path: str, rows):
    ins = np.concatenate([np.asarray(r["in"], dtype=np.int32) for r in rows])
    outs = np.concatenate([np.asarray(r["out"], dtype=np.int32) for r in rows])
    ioff = np.cumsum([0] + [len(r["in"]) for r in rows]).astype(np.int64)
    ooff = np.cumsum([0] + [len(r["out"]) for r in rows]).astype(np.int64)
    np.savez(path + ".npz", ins=ins, outs=outs, ioff=ioff, ooff=ooff)
    with open(path + ".meta.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps({"slots": r["slots"], "prog": r["prog"],
                                 "fid": r["fid"]}) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/norm/grid")
    ap.add_argument("--train", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=771)
    a = ap.parse_args()
    sp = ndata.split_frames()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    rows = draw(sp["train"], a.train, a.seed)
    save(a.out + "_train", rows)
    print("train grids", len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
