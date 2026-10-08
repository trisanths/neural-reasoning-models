"""Key position in the training draw, per shape, counted off the draw itself.

The frame bank has key position as one of its axes, but what the network saw
is the draw and not the bank. Seven shapes score exactly 0.0000 on the
value-first half of the held-out sentence mode, and whether that is a hole in
the draw or a failure that survives the draw is the difference between a data
problem and a representational one. This counts it.
"""
import gzip
import json
import os
from collections import Counter

ROOT = os.path.expanduser("~/decoupled-reasoner")
ZERO_ON_VALUE_FIRST = ("lookup", "inverse", "iterate", "compose", "exclusion",
                       "sum_chain", "precedence")

c = Counter()
n = 0
for line in gzip.open(os.path.join(ROOT, "data/norm/train.meta.jsonl.gz"),
                      "rt"):
    d = json.loads(line)
    c[(d["shape"], d["fid"].split(".")[2])] += 1
    n += 1

rows = []
head = "shape".ljust(18) + "key_first".rjust(10) + "value_first".rjust(13) \
    + "value_first share".rjust(19) + "  zero on value_first"
print("training items in the draw:", n)
print(head)
print("-" * len(head))
for sh in sorted({k[0] for k in c}):
    kf = c[(sh, "key_first")]
    vf = c[(sh, "value_first")]
    t = kf + vf
    mark = "YES" if sh in ZERO_ON_VALUE_FIRST else ""
    print(sh.ljust(18) + f"{kf:10d}" + f"{vf:13d}"
          + f"{vf / t:19.4f}" + "  " + mark)
    rows.append({"shape": sh, "key_first": kf, "value_first": vf,
                 "n": t, "value_first_share": round(vf / t, 6),
                 "scores_zero_on_value_first": sh in ZERO_ON_VALUE_FIRST})

out = os.path.join(ROOT, "results/system/keypos_train_draw.json")
with open(out, "w") as fh:
    json.dump({"source": os.path.join(ROOT, "data/norm/train.meta.jsonl.gz"),
               "n_training_items": n, "axis": "fid field 2",
               "per_shape": rows}, fh, indent=1)
print("wrote", out)
