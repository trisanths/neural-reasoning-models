"""Pages whose operand roles are transposed after training.

The sharpest test on record in this project put the same question to a
checkpoint on a page whose operand roles had been swapped, and the checkpoint
followed the identity it had learned on 678 of 678 items and the page on 0.
`src/audit/VERDICT.md` check 8 is that test.

The structure language's analogue of a non-commutative binary operator is a
`Table` whose keys are pairs drawn from one symbol set, which the frame grammar
writes as the `pair` question shape: one line per ordered pair. Transposing the
operand roles swaps the two operands on every line and leaves the values where
they are, so the page states the swapped rule on all nine lines and nothing else
about the page moves. The question is byte identical in the two versions.

Every item is emitted twice, tagged `original` and `transposed`, and carries
both answers:

    gold   what the page in front of the reader says
    alt    what the other version of the page says

An item is kept only where the two differ, which drops the diagonal cells and
any symmetric pair, and only where the answer cannot be echoed out of the
question, which is the same pair of filters the original test applied.
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

SPLITS = ("train", "qframe", "lexicon", "mode", "mixed")
WIDTH = 3


def pair_case(fid: str, seed: int):
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
    tbl = Table(name, tuple(ent))
    ai, bi = rng.sample(range(WIDTH), 2)
    x, y = syms[ai], syms[bi]
    tp = Table(name, tuple(((b, a), v) for (a, b), v in tbl.entries))
    po = assemble("pair", tables=[tbl], inputs=(("x", x), ("y", y)))
    pt = assemble("pair", tables=[tp], inputs=(("x", x), ("y", y)))
    return po, pt


def build(split: str, fids, n: int, seed0: int):
    fids = sorted(fids)
    out, tries, i = [], 0, 0
    while len(out) < n and tries < n * 25:
        tries += 1
        fid = fids[i % len(fids)]
        i += 1
        seed = seed0 + tries * 7919
        try:
            po, pt = pair_case(fid, seed)
            do = render.render(po, fid, seed % 5)
            dt = render.render(pt, fid, seed % 5)
        except Exception:
            continue
        ro, rt = run(po), run(pt)
        if not (ro.ok and rt.ok) or ro.text == rt.text:
            continue                      # not distinguishable
        if do["question"] != dt["question"]:
            continue                      # the edit must not touch the ask
        qwords = set(do["question"].lower().split())
        if ro.text.lower() in qwords or rt.text.lower() in qwords:
            continue                      # copyable out of the question
        cs = candidates(po)
        if cs is None or len(cs) < 2:
            continue
        opts = sorted(str(c) for c in cs)
        if ro.text not in opts or rt.text not in opts:
            continue
        pid = f"{split}/{len(out)//2}"
        base = {"split": split, "fid": fid, "shape": "pair", "seed": seed,
                "options": opts, "pair_id": pid}
        out.append(dict(base, id=f"{pid}/original",
                        version="original", gold=ro.text, alt=rt.text,
                        pages=list(do["pages"]), question=do["question"],
                        text=do["text"], prog=program_json(po)))
        out.append(dict(base, id=f"{pid}/transposed",
                        version="transposed", gold=rt.text, alt=ro.text,
                        pages=list(dt["pages"]), question=dt["question"],
                        text=dt["text"], prog=program_json(pt)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=20260831)
    ap.add_argument("--out", default="results/norm/compare/x_items.jsonl.gz")
    a = ap.parse_args()
    sp = ndata.split_frames()
    rows = []
    for split in SPLITS:
        got = build(split, sp[split], a.n, a.seed)
        rows.extend(got)
        print(f"{split:10s} {len(got):5d} rows ({len(got)//2} pairs)", flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with gzip.open(a.out, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump({"n_rows": len(rows), "rows_per_split": a.n,
                   "grid_width": WIDTH, "seed": a.seed}, fh, indent=2)
    print(json.dumps({"n_rows": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
