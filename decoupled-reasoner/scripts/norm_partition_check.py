"""Two gates on every scored row, run before TRAIN.md is rebuilt.

The four outcomes must partition each row. `src/norm/neval.py` increments
exact, malformed, refused and wrong from four independent booleans, so a bug
that set two of them on one item would inflate one rate without anything else
looking wrong. n_gold_executes must equal n, because that is the denominator
answer_ok is divided by.

And every summary must be newer than the checkpoint it reports on. A rescore
against a stale record set has cost this project a retracted headline before.
"""

import glob
import json
import os
import sys

bad = tot = 0
for p in sorted(glob.glob("results/norm/eval/*/summary.json")):
    tag = os.path.basename(os.path.dirname(p))
    ck = "results/norm/train/ckpt_%s.pt" % tag
    if os.path.exists(ck) and os.path.getmtime(p) < os.path.getmtime(ck):
        bad += 1
        print("STALE", p, "is older than", ck)
    d = json.load(open(p))
    for sp, v in d["splits"].items():
        for mode, g in v["modes"].items():
            for sh, r in g["by_shape"].items():
                tot += 1
                s4 = round(r["exact"] + r["malformed"] + r["refused"]
                           + r["wrong"], 4)
                if abs(s4 - 1.0) > 0.0002 or r["n_gold_executes"] != r["n"]:
                    bad += 1
                    print("BAD", p, sp, mode, sh, s4,
                          r["n_gold_executes"], r["n"])
print("rows", tot, "bad", bad)
sys.exit(1 if bad else 0)
