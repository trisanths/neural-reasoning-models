"""The hand-written parser on the value-first half of the held-out mode.

If the reference parser reads those pages exactly, the binding the network gets
wrong is present and unambiguous in the text, and the network's zero is about
the network. If the parser also stumbled there, the surface would be the
suspect instead. It is the control that decides which of the two the finding is
about, so it is counted on the same items, split the same way.

Runs on the CPU and touches no checkpoint.
"""
import json
import os
from collections import Counter

from src.norm import neval
from src.norm.parse import parse

ROOT = os.path.expanduser("~/decoupled-reasoner")
SEVEN = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
         "precedence")
out = {}
for split in ("train_frames_eval", "mode"):
    items = neval.load_eval(os.path.join(ROOT, "data/norm", split), 2800)
    c = Counter()
    for it in items:
        kp = it["fid"].split(".")[2]
        pp = parse(it["text"], it["fid"])
        ok = bool(pp.ok) and pp.program == it["prog"]
        c[(kp, "n")] += 1
        c[(kp, "exact")] += ok
        c[(it["shape"], kp, "n")] += 1
        c[(it["shape"], kp, "exact")] += ok
    print("===", split)
    for kp in ("key_first", "value_first"):
        n = c[(kp, "n")]
        print(f"  all shapes  {kp:12s} {c[(kp, 'exact')]} of {n} = "
              f"{c[(kp, 'exact')] / n:.4f}")
    for sh in SEVEN:
        n = c[(sh, "value_first", "n")]
        if n:
            print(f"  {sh:12s} value_first  "
                  f"{c[(sh, 'value_first', 'exact')]} of {n}")
    out[split] = {"|".join(k): v for k, v in c.items()}

dest = os.path.join(ROOT, "results/system/parser_by_keypos.json")
with open(dest, "w") as fh:
    json.dump({"parser": "src/norm/parse.py, exact program equality",
               "splits": out}, fh, indent=1)
print("wrote", dest)
