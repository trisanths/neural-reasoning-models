"""Score one generation file, by operation family and never pooled across it.

The grader is `src.norm.cmpwork.grade.forced`, the same function the project's
own three systems are scored by, imported rather than reimplemented so the
strict rule cannot drift between the two sides of the comparison.

Two spans are scored for every generation and both are reported:

    answer   the answer span, which is what the model wrote after its reasoning
             block and after any "Answer:" marker. This is the headline.
    scan     the whole generation after the reasoning block. It is the more
             forgiving reading and it exists so that a low headline cannot be
             an artefact of the extraction.

A generation that never produced an answer span is counted in `unparseable`
and kept out of neither numerator nor denominator, because the denominator is
the item count and a model that failed to answer has still failed the item.
The rate is reported beside the accuracy so the two are legible apart.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
from collections import defaultdict

from src.extern.answer import answer_span
from src.norm.cmpwork.grade import forced


def cell(rows):
    n = len(rows)
    if not n:
        return None
    agg = defaultdict(float)
    for r in rows:
        sp = answer_span(r["raw"])
        f = forced(sp["span"], r["options"], r["gold"])
        g = forced(sp["rest"], r["options"], r["gold"])
        agg["strict"] += f["strict_correct"]
        agg["lenient"] += f["lenient_correct"]
        agg["hedge"] += f["hedged"]
        agg["none"] += f["named_none"]
        agg["scan_strict"] += g["strict_correct"]
        agg["scan_lenient"] += g["lenient_correct"]
        agg["floor"] += f["floor"]
        agg["unparseable"] += int(sp["state"] != "ok")
        agg["unterminated"] += int(sp["state"] == "unterminated_reasoning")
        agg["empty"] += int(sp["state"] == "empty")
        agg["new_tokens"] += r["n_new"]
    out = {"n": n}
    for k in ("strict", "lenient", "hedge", "none", "scan_strict",
              "scan_lenient", "floor", "unparseable", "unterminated", "empty"):
        out[k] = round(agg[k] / n, 4)
    out["mean_new_tokens"] = round(agg["new_tokens"] / n, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", nargs="+", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--samples", type=int, default=0)
    a = ap.parse_args()

    report = []
    for path in a.gen:
        rows = [json.loads(l) for l in gzip.open(path, "rt")]
        meta_p = path.replace(".jsonl.gz", ".meta.json")
        meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
        by = defaultdict(list)
        for r in rows:
            by[(r["family"], r["n_pages"])].append(r)
        rec = {"gen": os.path.basename(path),
               "model": meta.get("model"), "variant": meta.get("variant"),
               "options_shown": meta.get("options_shown"),
               "params_total": meta.get("params_total"),
               "quantization": meta.get("quantization"),
               "max_new_tokens": meta.get("max_new_tokens"),
               "all": cell(rows),
               "cells": {f"{fam}/p{pg}": cell(v)
                         for (fam, pg), v in sorted(by.items())}}
        if a.samples:
            rec["samples"] = []
            for r in rows[:a.samples]:
                sp = answer_span(r["raw"])
                rec["samples"].append(
                    {"id": r["id"], "gold": r["gold"],
                     "options": r["options"], "state": sp["state"],
                     "span": sp["span"][:200], "raw": r["raw"][:1200]})
        report.append(rec)

    txt = json.dumps(report, indent=2)
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        with open(a.out, "w") as fh:
            fh.write(txt)
    for rec in report:
        c = rec["all"]
        print(f"{rec['model']} {rec['variant']:8s} n={c['n']:5d} "
              f"strict={c['strict']:.4f} lenient={c['lenient']:.4f} "
              f"floor={c['floor']:.4f} hedge={c['hedge']:.4f} "
              f"none={c['none']:.4f} unparse={c['unparseable']:.4f} "
              f"scan={c['scan_strict']:.4f} tok={c['mean_new_tokens']:.0f}")
        for k, v in rec["cells"].items():
            print(f"    {k:12s} n={v['n']:5d} strict={v['strict']:.4f} "
                  f"lenient={v['lenient']:.4f} floor={v['floor']:.4f} "
                  f"hedge={v['hedge']:.4f} none={v['none']:.4f} "
                  f"unparse={v['unparseable']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
