"""Does the fine tuning draw show the operand roles in both orders.

The transposed-operand test fine tunes on `data/norm/grid_train.npz` and then
asks the rung to read a page whose operand roles are swapped. If those 1,024
grids only ever list their nine key pairs in one order, the failure is a hole
in that draw. If they carry both, it is not.

`canonical` is `src/norm/cmpwork/xmode.py:canonical_order`: row major over the
symbols in their order of first appearance, which is the layout the failing
emissions use.
"""
import json
import os
from collections import Counter

ROOT = os.path.expanduser("~/decoupled-reasoner")


def canonical_order(keys):
    syms = []
    for a, b in keys:
        for s in (a, b):
            if s not in syms:
                syms.append(s)
    return [(a, b) for a in syms for b in syms]


def keys_of(prog):
    out = []
    for d in prog["defs"]:
        for k, _ in d.get("entries", []):
            if isinstance(k, dict) and "$tuple" in k:
                out.append(tuple(k["$tuple"]))
    return out


for name in ("grid_train", "grid_both"):
    path = os.path.join(ROOT, f"data/norm/{name}.meta.jsonl")
    if not os.path.exists(path):
        print(name, "missing")
        continue
    c = Counter()
    n = 0
    for line in open(path):
        d = json.loads(line)
        prog = d.get("prog")
        if not prog:
            continue
        ks = keys_of(prog)
        if len(ks) < 4:
            continue
        n += 1
        c["canonical" if ks == canonical_order(ks) else "other"] += 1
    print(f"{name}: {n} pages  " + json.dumps(dict(c)))

out = os.path.join(ROOT, "results/system/grid_key_order.json")
res = {}
for name in ("grid_train", "grid_both"):
    path = os.path.join(ROOT, f"data/norm/{name}.meta.jsonl")
    if not os.path.exists(path):
        continue
    c = Counter()
    for line in open(path):
        d = json.loads(line)
        prog = d.get("prog")
        if not prog:
            continue
        ks = keys_of(prog)
        if len(ks) < 4:
            continue
        c["canonical" if ks == canonical_order(ks) else "other"] += 1
    res[name] = dict(c)
with open(out, "w") as fh:
    json.dump({"source": "data/norm/grid_*.meta.jsonl",
               "definition": "canonical is src/norm/cmpwork/xmode.py:"
                             "canonical_order, row major over the symbols in "
                             "their order of first appearance",
               "counts": res}, fh, indent=1)
print("wrote", out)
