"""What is the same and what differs inside a minimal pair.

A pair is only worth training on if it is minimal in the way it claims. Six
things are checked over every pair of the sample split, and the two that matter
are stated as counts rather than asserted: the frame ids differ in the key
position field and in nothing else, and the two gold targets differ, which is
what a positional reader cannot satisfy at once.
"""
import json
import random
import sys
from collections import Counter

from src.norm import ndata
from src.norm.lang import program_load
from src.norm.ntok import deserialize

split = sys.argv[1]
show = int(sys.argv[2]) if len(sys.argv) > 2 else 1
ins, outs, ioff, ooff = ndata.load_split(split)
meta = ndata.load_meta(split)
iv, ov = ndata._vocab()
c = Counter()
for k in range(0, len(meta), 2):
    a, b = meta[k], meta[k + 1]
    c["slots of two"] += 1
    if not a.get("paired", True):
        c["independent, the shape ignores key position"] += 1
        c["independent and identical text"] += int(a["text"] == b["text"])
        continue
    fa, fb = a["fid"].split("."), b["fid"].split(".")
    c["minimal pairs"] += 1
    c["fid differs only in field 2"] += int(
        [i for i in range(5) if fa[i] != fb[i]] == [2])
    c["key_first then value_first"] += int(
        (fa[2], fb[2]) == ("key_first", "value_first"))
    c["same shape"] += int(a["shape"] == b["shape"])
    pa, pb = program_load(a["prog"]), program_load(b["prog"])
    c["same structure"] += int(pa == pb)
    c["same invented words"] += int({s.lower() for s in a["slots"]}
                                    == {s.lower() for s in b["slots"]})
    c["different text"] += int(a["text"] != b["text"])
    ta = outs[ooff[k] + 1:ooff[k + 1] - 1].tolist()
    tb = outs[ooff[k + 1] + 1:ooff[k + 2] - 1].tolist()
    c["different gold target"] += int(ta != tb)
    c["same slot order"] += int([s.lower() for s in a["slots"]]
                                == [s.lower() for s in b["slots"]])
    c["target deserialises to the structure"] += int(
        deserialize(ov.decode(ta), a["slots"]) == pa
        and deserialize(ov.decode(tb), b["slots"]) == pb)
    c["target differs|" + a["shape"]] += int(ta != tb)
    c["pairs|" + a["shape"]] += 1
for k, v in sorted(c.items()):
    print(f"{k:44s} {v}")

rng = random.Random(0)
ks = [k for k in range(0, len(meta), 2)
      if meta[k]["shape"] == "lookup" and meta[k].get("paired", True)]
for k in rng.sample(ks, show):
    for j in (k, k + 1):
        m = meta[j]
        print("=" * 72)
        print(m["fid"], m["shape"])
        print(m["text"])
        print("slots:", " ".join(f"W{i}={s}" for i, s in
                                 enumerate(m["slots"])))
        print("target:", " ".join(
            ov.decode(outs[ooff[j] + 1:ooff[j + 1] - 1].tolist())))
