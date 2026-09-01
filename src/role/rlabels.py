"""Which invented word of a page is a key and which is a value, read off gold.

The auxiliary arm needs a per token role target and the training file does not
carry the structure that wrote it, only the token ids on both sides. The target
side is enough: it is the structure, written in the closed output vocabulary,
and `src/norm/ntok.py:deserialize` turns it back into a `Program` exactly. The
surface spellings are not needed for this, so the slot table handed to
`deserialize` is the slot names themselves and the program comes back written
in `W0..W63`, which is already the index the input side uses.

A word can be both. A compose chain uses its middle level as the value of one
table and the key of the next, so the label is two independent bits rather than
one three way choice, and `both` is a real cell rather than a collision.

Written as (n_items, 64) uint8, bit 0 key and bit 1 value, aligned row for row
with the split's own `.npz`. Slot indices past the item's own slot count stay
zero and are never read, because the input side never emits them.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter

import numpy as np

from src.norm import ndata
from src.norm.ntok import MAX_SLOTS, SLOT_TOKENS, deserialize

KEY = 1
VALUE = 2


def roles(prog):
    """(key symbols, value symbols) of one structure, as lowercase sets."""
    keys, vals = set(), set()

    def k_(v):
        if isinstance(v, str):
            keys.add(v.lower())
        elif isinstance(v, tuple):
            for part in v:
                k_(part)

    def v_(v):
        if isinstance(v, str):
            vals.add(v.lower())
        elif isinstance(v, tuple):
            for part in v:
                v_(part)

    for d in prog.defs:
        if d.kind == "table":
            for k, v in d.entries:
                k_(k)
                v_(v)
            v_(d.default)
        elif d.kind == "bands":
            for lab in d.labels:
                v_(lab)
        elif d.kind == "rule":
            v_(d.general)
            for k, v in d.exceptions:
                k_(k)
                v_(v)
        elif d.kind == "weights":
            for k, _ in d.entries:
                k_(k)
    return keys, vals


NAMES = tuple(s.lower() for s in SLOT_TOKENS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    _, outs, _, ooff = ndata.load_split(a.split)
    _, ov = ndata._vocab()
    n = len(ooff) - 1
    lab = np.zeros((n, MAX_SLOTS), dtype=np.uint8)
    idx = {s: i for i, s in enumerate(NAMES)}
    c = Counter()
    t0 = time.time()
    for i in range(n):
        toks = ov.decode(outs[ooff[i] + 1:ooff[i + 1] - 1].tolist())
        try:
            prog = deserialize(toks, list(SLOT_TOKENS))
        except Exception as exc:                    # a gold target must parse
            raise RuntimeError(f"item {i} of {a.split}: {exc}")
        keys, vals = roles(prog)
        row = lab[i]
        for s in keys:
            row[idx[s]] |= KEY
        for s in vals:
            row[idx[s]] |= VALUE
        c["named"] += len(keys | vals)
    dest = a.out or (a.split + ".roles.npy")
    np.save(dest, lab)
    flat = lab.reshape(-1)
    rep = {"split": os.path.abspath(a.split), "labels": os.path.abspath(dest),
           "n_items": int(n), "bit0": "key", "bit1": "value",
           "n_slots_named_by_the_structure": int(c["named"]),
           "cells_over_all_64_slots": {
               "zero": int((flat == 0).sum()), "key_only": int((flat == 1).sum()),
               "value_only": int((flat == 2).sum()), "both": int((flat == 3).sum())},
           "seconds": round(time.time() - t0, 1)}
    with open(dest + ".json", "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
