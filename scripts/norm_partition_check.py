"""The four outcomes must partition every scored row, and the gold must run.

`src/norm/neval.py` increments exact, malformed, refused and wrong from four
independent booleans, so a bug that set two of them on one item would inflate
one rate without anything else looking wrong. This requires the four to sum to
one on every shape of every split of every size on record, and requires
n_gold_executes to equal n, which is the denominator answer_ok is divided by.
"""

import glob
import json
import sys

bad = tot = 0
for p in sorted(glob.glob("results/norm/eval/*/summary.json")):
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
