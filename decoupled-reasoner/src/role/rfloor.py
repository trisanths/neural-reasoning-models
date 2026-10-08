"""The floor and the ceiling of each key position cell, with no model involved.

Every cell in the report is a fraction of a few thousand items and needs both
ends stated. The floor is `src/norm/neval.py`'s modal-by-shape baseline: the
most frequent gold target for the item's own shape, emitted for every item of
that shape. Slot ids are positional, so on the fixed arity shapes that floor is
not near zero and quoting an exact match without it would flatter every arm.
The ceiling is `src/norm/parse.py`, the hand written reference parser, which is
handed the frame id the network never sees.

Neither depends on which arm is being scored, so this runs once and every arm's
table cites the same numbers.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter

from src.norm import ndata, neval
from src.norm.parse import parse

SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode")
SEVEN = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
         "precedence")


def main():
    data = sys.argv[1] if len(sys.argv) > 1 else "data/norm"
    _, ov = ndata._vocab()
    out = {}
    for sp in SPLITS:
        items = neval.load_eval(os.path.join(data, sp), 7000)
        golds = [it["gold_ids"][1:-1].tolist() for it in items]
        modal = neval.modal_by_shape(items, golds)
        c = Counter()
        for it, g in zip(items, golds):
            kp = it["fid"].split(".")[2]
            mr = neval.classify_emission(ov.decode(list(modal[it["shape"]])),
                                         it["slots"], it["prog"])
            pp = parse(it["text"], it["fid"])
            ok = bool(pp.ok) and pp.program == it["prog"]
            for cell in (kp, f"{kp}|seven" if it["shape"] in SEVEN else None):
                if cell is None:
                    continue
                c[(cell, "n")] += 1
                c[(cell, "modal_shape_exact")] += int(mr["exact"])
                c[(cell, "parser_exact")] += int(ok)
        out[sp] = {}
        for cell in ("key_first", "value_first", "key_first|seven",
                     "value_first|seven"):
            n = c[(cell, "n")]
            if not n:
                continue
            out[sp][cell] = {
                "n": n,
                "modal_shape_floor": round(c[(cell, "modal_shape_exact")] / n, 4),
                "parser_exact": round(c[(cell, "parser_exact")] / n, 4)}
        print(sp, json.dumps(out[sp]), flush=True)
    os.makedirs("results/role", exist_ok=True)
    dest = "results/role/floors.json"
    with open(dest, "w") as fh:
        json.dump({"data": os.path.abspath(data),
                   "floor": "src/norm/neval.py modal_by_shape, the most "
                            "frequent gold target for the item's own shape",
                   "ceiling": "src/norm/parse.py, exact program equality, "
                              "given the frame id",
                   "seven": list(SEVEN), "cells": out}, fh, indent=1)
    print("wrote", os.path.abspath(dest))


if __name__ == "__main__":
    main()
