"""Two independent checks on the role labels, and one page printed in full.

The labels come from the target token stream. The eval splits also carry the
structure itself in their sidecar, drawn before either was written, so the two
paths can be compared symbol for symbol. The printed page is there so a reader
can see the binding the labels claim and disagree with it.
"""
import json
import random
import sys

import numpy as np

from src.norm import ndata
from src.norm.lang import program_load
from src.norm.ntok import MAX_SLOTS
from src.role.rlabels import roles

split = sys.argv[1]
show = int(sys.argv[2]) if len(sys.argv) > 2 else 2
lab = np.load(split + ".roles.npy")
ins, outs, ioff, ooff = ndata.load_split(split)
meta = ndata.load_meta(split)
iv, ov = ndata._vocab()

bad = 0
for i in range(len(meta)):
    prog = program_load(meta[i]["prog"])
    keys, vals = roles(prog)
    for s, surf in enumerate(meta[i]["slots"]):
        want = (1 if surf.lower() in keys else 0) | (2 if surf.lower() in vals
                                                     else 0)
        if int(lab[i, s]) != want:
            bad += 1
print(f"disagreements against the sidecar structure: {bad} over {len(meta)} items")

over = 0
for i in range(len(meta)):
    a = ins[ioff[i]:ioff[i + 1]]
    sl = a[a >= iv.slot0] - iv.slot0
    if len(sl) and int(sl.max()) >= len(meta[i]["slots"]):
        over += 1
print(f"items whose input names a slot the sidecar does not have: {over}")

rng = random.Random(0)
idx = [i for i in range(len(meta)) if meta[i]["shape"] == "lookup"]
for i in rng.sample(idx, show):
    m = meta[i]
    print("=" * 70)
    print("fid", m["fid"], " shape", m["shape"])
    print(m["text"])
    print("-" * 70)
    names = {0: "neither", 1: "key", 2: "value", 3: "both"}
    for s, surf in enumerate(m["slots"]):
        print(f"  W{s:<3d} {surf:<16s} {names[int(lab[i, s])]}")
