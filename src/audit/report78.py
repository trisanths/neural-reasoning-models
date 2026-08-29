"""Compact tables from the check 7 and check 8 result file."""

from __future__ import annotations

import json
import sys

TAGS = ["s0", "s2", "s3", "s4", "perm"]
CONDS = ["direct_all", "direct_oracle_page", "trace_all", "trace_oracle_page",
         "plan_execute", "oracle_plan", "oracle_ops", "oracle_both",
         "parser_all_wordings", "parser_trained_wording"]


def main() -> int:
    d = json.load(open(sys.argv[1]))
    depths = [str(x) for x in d["depths"]]
    print("n =", d["n"], " dropped from the transposed set:", d["dropped_from_perm"])
    print("\n=== check 7: accuracy by wording (page-implied gold) ===")
    for c in CONDS:
        if c not in d:
            continue
        for tag in TAGS:
            if tag not in d[c]:
                continue
            row = d[c][tag]
            cells = " ".join("%s:%.3f" % (k, row[k]["acc_page"])
                             for k in depths if k in row)
            ns = {row[k]["n"] for k in depths if k in row}
            print("%-24s %-5s %s   n=%s" % (c, tag, cells, sorted(ns)))
        print()
    print("=== check 8: page-implied against training-implied, transposed pages ===")
    for c in CONDS:
        if c not in d or "perm" not in d[c]:
            continue
        row = d[c]["perm"]
        p = " ".join("%s:%.3f" % (k, row[k]["acc_page"]) for k in depths if k in row)
        t = " ".join("%s:%.3f" % (k, row[k]["acc_train"]) for k in depths if k in row)
        print("%-24s page  %s" % (c, p))
        print("%-24s train %s" % ("", t))
    print("\n=== induction ===")
    for tag, s in d.get("induction", {}).items():
        print(tag, json.dumps(s))
    print("identity:", json.dumps(d.get("induction_identity", {})))
    print("\n=== induced samples on transposed pages ===")
    for s in d.get("induced_samples", [])[:6]:
        print(" ", s)
    print("\n=== plan-path failure reasons ===")
    for c in ("plan_execute", "oracle_plan"):
        for tag in TAGS:
            if c not in d or tag not in d[c]:
                continue
            for k in depths:
                if k in d[c][tag] and "reasons" in d[c][tag][k]:
                    print(c, tag, "d=" + k, d[c][tag][k]["reasons"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
