"""The reference parser on each split's own withheld group, by key position.

The same control the first split has: if the parser reads those items exactly,
the binding is in the text and unambiguous there, so whatever the network does
with them is about the network. Runs on the CPU against no checkpoint.

usage: parsercheck2.py DATADIR GROUP [GROUP ...]
"""
import json
import os
import sys
from collections import Counter

from src.norm import neval
from src.norm.parse import parse

ROOT = os.path.expanduser("~/decoupled-reasoner")
SEVEN = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
         "precedence")


def main():
    data = sys.argv[1]
    groups = sys.argv[2:] or ["train_frames_eval", "mode"]
    name = os.path.basename(data)
    out = {}
    for split in groups:
        items = neval.load_eval(os.path.join(ROOT, data, split), 0)
        c = Counter()
        for it in items:
            kp = it["fid"].split(".")[2]
            pp = parse(it["text"], it["fid"])
            ok = bool(pp.ok) and pp.program == it["prog"]
            c[(kp, "n")] += 1
            c[(kp, "exact")] += ok
            c[(it["shape"], kp, "n")] += 1
            c[(it["shape"], kp, "exact")] += ok
        print(f"=== {name} / {split}  ({len(items)} items)")
        for kp in ("key_first", "value_first"):
            n = c[(kp, "n")]
            if n:
                print(f"  all shapes  {kp:12s} {c[(kp, 'exact')]} of {n} = "
                      f"{c[(kp, 'exact')] / n:.4f}")
        lo = None
        for sh in SEVEN:
            n = c[(sh, "value_first", "n")]
            if n:
                r = c[(sh, "value_first", "exact")] / n
                lo = r if lo is None else min(lo, r)
        if lo is not None:
            print(f"  lowest of the seven shapes on value_first: {lo:.4f}")
        out[split] = {"|".join(map(str, k)): v for k, v in c.items()}
    dest = os.path.join(ROOT, f"results/system/parser_{name}.json")
    with open(dest, "w") as fh:
        json.dump({"data": data,
                   "parser": "src/norm/parse.py, exact program equality",
                   "splits": out}, fh, indent=1)
    print("wrote", dest)


if __name__ == "__main__":
    main()
