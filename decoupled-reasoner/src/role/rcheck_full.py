"""The pair invariant over the whole training file, counted, not sampled.

The sample check reads the text and the structure out of a sidecar that the
training file does not carry. It does not need to. The target side is the
structure written in slot indices, and each member has its own slot table, so
deserialising both targets against their own tables gives two structures in
surface symbols that must be equal for a real pair. That check runs on every
row of the file rather than on a sample of it.

Five counts per file, and every one of them is over all 600,000 slots of two:
the frame ids differ in the key position field and in no other field, the pair
runs key-first then value-first, the two structures are equal, the two invented
word sets are equal, and the two gold targets differ, which is the part a
positional reader cannot satisfy at once.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter

from src.norm import ndata
from src.norm.ntok import deserialize

AXIS = int(sys.argv[2]) if len(sys.argv) > 2 else 2
path = sys.argv[1] if len(sys.argv) > 1 else "data/role/paired_train"
_, outs, _, ooff = ndata.load_split(path)
meta = ndata.load_meta(path)
_, ov = ndata._vocab()
c = Counter()
for k in range(0, len(meta), 2):
    a, b = meta[k], meta[k + 1]
    c["slots of two"] += 1
    if not a.get("paired", True):
        c["independent, the axis does not reach this shape"] += 1
        c["independent|" + a["shape"]] += 1
        continue
    c["pairs"] += 1
    c["pairs|" + a["shape"]] += 1
    fa, fb = a["fid"].split("."), b["fid"].split(".")
    c["fid differs in the axis field and nowhere else"] += int(
        [i for i in range(5) if fa[i] != fb[i]] == [AXIS])
    c["ordered key_first then value_first"] += int(
        (fa[AXIS], fb[AXIS]) == ("key_first", "value_first")) if AXIS == 2 \
        else 0
    c["same shape"] += int(a["shape"] == b["shape"])
    c["same invented words"] += int({s.lower() for s in a["slots"]}
                                    == {s.lower() for s in b["slots"]})
    ta = outs[ooff[k] + 1:ooff[k + 1] - 1].tolist()
    tb = outs[ooff[k + 1] + 1:ooff[k + 2] - 1].tolist()
    c["gold targets differ"] += int(ta != tb)
    c["gold targets differ|" + a["shape"]] += int(ta != tb)
    pa = deserialize(ov.decode(ta), a["slots"])
    pb = deserialize(ov.decode(tb), b["slots"])
    c["same structure"] += int(pa == pb)

rep = {"file": os.path.abspath(path), "axis_field": AXIS,
       "counts": {k: v for k, v in sorted(c.items()) if "|" not in k},
       "by_shape": {k: v for k, v in sorted(c.items()) if "|" in k}}
for k, v in rep["counts"].items():
    print(f"{k:52s} {v}")
dest = os.path.join("results/role",
                    "pairs_" + os.path.basename(path) + ".json")
os.makedirs("results/role", exist_ok=True)
with open(dest, "w") as fh:
    json.dump(rep, fh, indent=1)
print("wrote", os.path.abspath(dest))
