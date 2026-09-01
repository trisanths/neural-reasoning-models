"""Where the collapse lives, by shape, and which shapes can show it at all.

Key position selects the `ASSOC` rule sentence and the `table_row` column
header and nothing else, so it does not reach every page, and a shape whose page
comes out byte identical in the two frames cannot show the effect either way.
Reporting all fourteen shapes in one average therefore dilutes the cells that
carry the finding with cells that could not carry it. Four groups, and the
grouping follows the templates rather than the scores:

    new keys      the page states rule lines whose key is a symbol appearing
                  for the first time, so the wording of that line is the only
                  thing saying which of the two words is the key
    seen keys     `band_then_lookup`, whose table keys are the band labels the
                  previous page already named, so the key is recoverable
                  without reading the rule line at all
    header only   `lookup_then_band`, where the axis reaches nothing but the
                  column header, and only in `table_row`
    out of reach  `apply_n`, `classify`, `lookup_general`, `pair`, whose pages
                  are byte identical in the two frames

Read off the record files, per key position, never pooled across it.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from collections import Counter

GROUPS = {
    "new keys": ("lookup", "inverse", "iterate", "compose", "exclusion",
                 "sum_chain", "precedence", "priority"),
    "seen keys": ("band_then_lookup",),
    "header only": ("lookup_then_band",),
    "out of reach": ("apply_n", "classify", "lookup_general", "pair"),
}
OF = {s: g for g, ss in GROUPS.items() for s in ss}
POS = ("key_first", "value_first")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", required=True)
    ap.add_argument("--split", default="mode")
    ap.add_argument("--eval", default="results/system/eval")
    ap.add_argument("--out", default="results/role")
    a = ap.parse_args()

    for tag in a.tags.split(","):
        rep = {"tag": tag, "split": a.split, "groups": {}, "shapes": {},
               "definition": {g: list(s) for g, s in GROUPS.items()}}
        print("=" * 74)
        print(f"{tag}   held-out split: {a.split}")
        for dm in ("greedy", "sampled"):
            p = os.path.join(a.eval, tag, f"records_{a.split}_{dm}.jsonl.gz")
            if not os.path.exists(p):
                continue
            c = Counter()
            with gzip.open(p, "rt") as fh:
                for line in fh:
                    r = json.loads(line)
                    kp = r["fid"].split(".")[2]
                    for cell in (r["shape"], OF[r["shape"]]):
                        c[(cell, kp, "n")] += 1
                        c[(cell, kp, "exact")] += int(r["exact"])
            rep["records_" + dm] = {
                "path": os.path.abspath(p),
                "mtime": time.strftime("%Y-%m-%d %H:%M:%S",
                                       time.gmtime(os.path.getmtime(p)))}
            print(f"  {dm}")
            print("    " + "group or shape".ljust(20)
                  + "key_first".rjust(20) + "value_first".rjust(20)
                  + "gap".rjust(9))
            for cell in list(GROUPS) + sorted(OF):
                if not c[(cell, "key_first", "n")]:
                    continue
                r = {}
                for kp in POS:
                    n = c[(cell, kp, "n")]
                    r[kp] = {"n": n,
                             "exact": round(c[(cell, kp, "exact")] / n, 4)}
                gap = r["key_first"]["exact"] - r["value_first"]["exact"]
                r["gap_key_first_minus_value_first"] = round(gap, 4)
                dest = rep["groups"] if cell in GROUPS else rep["shapes"]
                dest.setdefault(cell, {})[dm] = r
                mark = "  <" if cell in GROUPS else ""
                print("    " + cell.ljust(20)
                      + ("%.4f (n=%d)" % (r["key_first"]["exact"],
                                          r["key_first"]["n"])).rjust(20)
                      + ("%.4f (n=%d)" % (r["value_first"]["exact"],
                                          r["value_first"]["n"])).rjust(20)
                      + ("%+.4f" % gap).rjust(9) + mark)
        os.makedirs(a.out, exist_ok=True)
        d = os.path.join(a.out, f"shapes_{tag}_{a.split}.json")
        with open(d, "w") as fh:
            json.dump(rep, fh, indent=1)
        print("  wrote", os.path.abspath(d))


if __name__ == "__main__":
    main()
