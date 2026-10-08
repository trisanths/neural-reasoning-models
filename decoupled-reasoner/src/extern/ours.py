"""Lift the project's own acquisition numbers out of the oneshot report.

The comparison tables put the external models beside the library system and
the project's reader, and both of those numbers are read from
`results/norm/oneshot/report.json` rather than copied out of ONESHOT.md, so
the two sides of every row come from record files.
"""
from __future__ import annotations

import argparse
import json

FAMS = ["a2c1", "a3c1", "a2c2", "a3c2"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="results/norm/oneshot/report.json")
    ap.add_argument("--out", default="results/extern/ours_oneshot.json")
    a = ap.parse_args()
    d = json.load(open(a.report))
    out = {}
    for f in FAMS:
        one = d["acq"].get(f"{f}|pages1|L", {})
        two = d["acq"].get(f"{f}|pages2|L", {})
        four = d["acq"].get(f"{f}|pages4|L", {})
        n1 = d["neural"].get(f"n_base_l|greedy|acq|{f}|pages1", {})
        n1s = d["neural"].get(f"n_base_l|sampled|acq|{f}|pages1", {})
        s1 = d["acq"].get(f"{f}|pages1|S1", {})
        s2 = d["acq"].get(f"{f}|pages1|S2", {})
        out[f] = {
            "n": one.get("n"), "floor": one.get("floor"),
            "L": one.get("strict"), "L2": two.get("strict"),
            "L4": four.get("strict"),
            "L_exact": one.get("structure_exact"),
            "N": n1.get("strict"), "N_sampled": n1s.get("strict"),
            "N_declined": n1.get("declined"), "N_none": n1.get("none"),
            "S1": s1.get("strict"), "S2": s2.get("strict"),
        }
    json.dump(out, open(a.out, "w"), indent=2)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
