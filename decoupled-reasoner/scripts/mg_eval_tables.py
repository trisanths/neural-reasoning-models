"""Turn a strict-regrade report into the markdown tables `EVAL.md` prints.

Kept so the document can be rebuilt from the json rather than transcribed.
"""

from __future__ import annotations

import argparse
import json
import math


def f(x, nd=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.{nd}f}"


COLS = [("floor", "chance"), ("shipped", "acc_shipped"),
        ("forced", "acc_forced"), ("first", "acc_first"),
        ("c_shipped", "corrected_shipped"), ("c_forced", "corrected_forced"),
        ("hedge", "hedge_rate"), ("none", "none_named_rate"),
        ("rounds", "mean_rounds"), ("any_ret", "any_retrieval"),
        ("well_formed", "well_formed"), ("degen", "degenerate_query_rate"),
        ("ans_in_ret", "answer_in_retrieved"),
        ("ans_in_lib", "answer_in_library")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--match", default="", help="substring the cell key must hold")
    ap.add_argument("--exclude", default="", help="substring the key must not hold")
    ap.add_argument("--macro", action="store_true")
    args = ap.parse_args()

    with open(args.report, encoding="utf-8") as fh:
        rep = json.load(fh)
    cells = rep["cells"] if "cells" in rep else rep

    keys = [k for k in cells
            if (not args.match or args.match in k)
            and (not args.exclude or args.exclude not in k)]
    head = "| cell | nQ | nR | " + " | ".join(c for c, _ in COLS) + " |"
    rule = "| --- | ---: | ---: | " + " | ".join("---:" for _ in COLS) + " |"
    print(head)
    print(rule)
    for k in sorted(keys):
        c = cells[k]
        vals = " | ".join(f(c.get(field)) for _, field in COLS)
        print(f"| {k} | {c['n_questions']} | {c['n_rollouts']} | {vals} |")

    if args.macro and rep.get("macro"):
        print()
        print("| macro cell | grader | cells | macro_acc | macro_floor | "
              "corrected_of_macro | macro_of_corrected |")
        print("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
        for k, m in sorted(rep["macro"].items()):
            if args.match and args.match not in k:
                continue
            for which, v in m.items():
                if not v:
                    continue
                print(f"| {k} | {which} | {v['cells']} | "
                      f"{f(v['macro_accuracy'], 4)} | {f(v['macro_chance'], 4)} | "
                      f"{f(v['corrected_of_macro'], 4)} | "
                      f"{f(v['macro_of_corrected'], 4)} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
