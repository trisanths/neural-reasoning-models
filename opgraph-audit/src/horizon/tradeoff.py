"""Paraphrase induction against the training ceiling, across every arm.

Reads the persisted ceiling artifacts and nothing else. Every number carries
its denominator. Accuracy carries the empirical chance floor for its own cell,
which is that cell's majority gold answer rate, and both macro aggregation
orders are reported because they differ.

  strict   an item whose plan failed to parse, or whose induced operator table
           could not execute the plan, counts as wrong. This is the forced
           choice score.
  lenient  those items are dropped from the denominator instead. The gap
           between the two is the size of the abstention channel.

usage: python3 -m src.horizon.tradeoff --glob 'results/ceiling/full_*.json'
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from collections import Counter, defaultdict

SEQ = "sequential"


def arm_ceiling(arm: str):
    m = re.match(r"d(\d+)s(\d+)", arm)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def load(paths):
    out = {}
    for p in sorted(paths):
        d = json.load(open(p))
        arm = d["config"]["arm"] or os.path.basename(p)
        d["_path"] = p
        d["_mtime"] = os.path.getmtime(p)
        out[arm] = d
    return out


def cells_for(d, cond, style, temp, kind):
    got = {}
    for k, c in d["cells"].items():
        if (c["cond"] == cond and c["style"] == style
                and abs(c["temperature"] - temp) < 1e-9 and c["kind"] == kind):
            got[c["depth"]] = c
    return got


def corrected(cells):
    """Both macro aggregation orders, with their formulas.

    order A: chance-correct the pooled accuracy.
      A = (sum(correct)/sum(n) - sum(chance_c * n_c)/sum(n_c)) / (1 - same)
    order B: mean of the per cell chance-corrected values.
      B = mean_c (acc_c - chance_c) / (1 - chance_c)
    """
    if not cells:
        return None
    n = sum(c["n"] for c in cells)
    k = sum(c["correct"] for c in cells)
    ch = sum(c["majority_gold_rate"] * c["n"] for c in cells) / n
    acc = k / n
    a = (acc - ch) / (1 - ch) if ch < 1 else float("nan")
    per = []
    for c in cells:
        cc = c["majority_gold_rate"]
        per.append((c["acc"] - cc) / (1 - cc) if cc < 1 else float("nan"))
    b = sum(per) / len(per)
    return {"n": n, "correct": k, "acc": round(acc, 4),
            "chance": round(ch, 4), "macro_then_correct": round(a, 4),
            "correct_then_mean": round(b, 4), "cells": len(cells)}


def reason_table(recpath, arm, ceiling):
    """Strict and lenient accuracy, and the abstention channel, from records."""
    agg = defaultdict(Counter)
    if not os.path.exists(recpath):
        return {}
    for line in open(recpath):
        r = json.loads(line)
        if r["cond"] != "plan_execute" or r["kind"] != SEQ:
            continue
        band = "in_ceiling" if r["depth"] <= ceiling else "above_ceiling"
        key = (r["style"], r["temperature"], band)
        a = agg[key]
        a["n"] += 1
        a[r["reason"]] += 1
        a["correct"] += int(bool(r["correct"]))
    out = {}
    for (style, temp, band), a in sorted(agg.items()):
        answered = a["ok"] + a["wrong_value"]
        out[f"s{style}|t{temp}|{band}"] = {
            "n": a["n"],
            "correct": a["correct"],
            "strict_acc": round(a["correct"] / a["n"], 4) if a["n"] else None,
            "answered": answered,
            "lenient_acc": (round(a["correct"] / answered, 4)
                            if answered else None),
            "no_answer": a["n"] - answered,
            "no_answer_rate": round((a["n"] - answered) / a["n"], 4),
            "plan_parse_fail": a["plan_parse"],
            "execute_fail": a["execute"],
            "wrong_value": a["wrong_value"],
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="results/ceiling/full_*.json")
    ap.add_argument("--out", default="results/horizon/tradeoff.json")
    ap.add_argument("--md", default="results/horizon/TRADEOFF_TABLES.md")
    ap.add_argument("--records", action="store_true",
                    help="also walk the records jsonl for the reason split")
    args = ap.parse_args()

    runs = load(glob.glob(args.glob))
    if not runs:
        print("no runs matched")
        return 2
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    report = {"arms": {}, "generated_from": sorted(r["_path"]
                                                   for r in runs.values())}
    lines = []
    P = lines.append

    # harness check first. oracle_both must be 1.000 everywhere.
    P("## harness check")
    P("")
    P("| arm | oracle_both cells | min acc | verdict |")
    P("|---|---|---|---|")
    broken = []
    for arm, d in sorted(runs.items()):
        ob = [c for c in d["cells"].values() if c["cond"] == "oracle_both"]
        lo = min(c["acc"] for c in ob) if ob else None
        ok = lo is not None and lo >= 1.0
        if not ok:
            broken.append(arm)
        P(f"| {arm} | {len(ob)} | {lo} | {'ok' if ok else 'BROKEN'} |")
        report["arms"].setdefault(arm, {})["oracle_both_min"] = lo
        report["arms"][arm]["oracle_both_cells"] = len(ob)
    P("")

    # induction, the reading half, both wordings.
    P("## induction, both wordings")
    P("")
    P("Pages are operator definition pages. One induction pass per wording "
      "covers every world in the grid, so the denominator is the same in "
      "every arm.")
    P("")
    P("| arm | D | wording | pages parsed | rate | ops induced / gold | "
      "behaviourally correct / gold | rate | exact text / gold |")
    P("|---|---|---|---|---|---|---|---|---|")
    for arm, d in sorted(runs.items()):
        D, S = arm_ceiling(arm)
        for style in (0, 1):
            b = d.get(f"induction_style{style}")
            if not b:
                continue
            w = "trained" if style == 0 else "paraphrase"
            P(f"| {arm} | {D} | {w} | {b['pages_parsed']}/{b['pages']} | "
              f"{b['pages_parsed'] / b['pages']:.3f} | "
              f"{b['induced_ops']}/{b['gold_ops']} | "
              f"{b['behavioural']}/{b['gold_ops']} | "
              f"{b['behavioural'] / b['gold_ops']:.3f} | "
              f"{b['exact_text']}/{b['gold_ops']} |")
            report["arms"][arm][f"induction_style{style}"] = b
    P("")

    # the headline contrast.
    for temp in (0.0, 0.8):
        tag = "greedy" if temp == 0.0 else "sampled t=0.8"
        P(f"## plan_execute, sequential, at or below each arm's own ceiling "
          f"({tag})")
        P("")
        P("Cells are depths 1..D for that arm. Chance is the majority gold "
          "answer rate pooled over those cells.")
        P("")
        P("| arm | D | wording | cells | n | acc | chance | "
          "macro-then-correct | correct-then-mean |")
        P("|---|---|---|---|---|---|---|---|---|")
        for arm, d in sorted(runs.items()):
            D, S = arm_ceiling(arm)
            for style in (0, 1):
                cs = cells_for(d, "plan_execute", style, temp, SEQ)
                inb = [c for k, c in sorted(cs.items()) if k <= D]
                r = corrected(inb)
                if not r:
                    continue
                w = "trained" if style == 0 else "paraphrase"
                P(f"| {arm} | {D} | {w} | {r['cells']} | {r['n']} | "
                  f"{r['acc']:.3f} | {r['chance']:.3f} | "
                  f"{r['macro_then_correct']:.3f} | "
                  f"{r['correct_then_mean']:.3f} |")
                report["arms"][arm][f"inceiling_s{style}_t{temp}"] = r
        P("")

    # common depth band, so arms are compared on identical items.
    P("## plan_execute, sequential depths 1 to 3, identical items in every arm")
    P("")
    P("Depths 1 to 3 are at or below the ceiling of every arm from d3s1 up, "
      "so this contrast holds the item set fixed.")
    P("")
    P("| arm | wording | temp | n | acc | chance | macro-then-correct | "
      "correct-then-mean |")
    P("|---|---|---|---|---|---|---|---|")
    for arm, d in sorted(runs.items()):
        for style in (0, 1):
            for temp in (0.0, 0.8):
                cs = cells_for(d, "plan_execute", style, temp, SEQ)
                band = [c for k, c in sorted(cs.items()) if k <= 3]
                r = corrected(band)
                if not r:
                    continue
                w = "trained" if style == 0 else "paraphrase"
                P(f"| {arm} | {w} | {temp} | {r['n']} | {r['acc']:.3f} | "
                  f"{r['chance']:.3f} | {r['macro_then_correct']:.3f} | "
                  f"{r['correct_then_mean']:.3f} |")
                report["arms"][arm][f"d123_s{style}_t{temp}"] = r
    P("")

    # emitted structure, which is where the ceiling was visible.
    P("## emitted structure, sequential, plan_execute, greedy")
    P("")
    P("| arm | wording | depth | req steps | emit steps mean | emit steps max "
      "| emit distinct symbols | parse | well typed | exact gold | hedge | "
      "hit cap |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for arm, d in sorted(runs.items()):
        for style in (0, 1):
            cs = cells_for(d, "plan_execute", style, 0.0, SEQ)
            for depth in sorted(cs):
                c = cs[depth]
                w = "trained" if style == 0 else "paraphrase"
                P(f"| {arm} | {w} | {depth} | {c['req_steps_mean']} | "
                  f"{c['emit_steps_mean']} | {c['emit_steps_max']} | "
                  f"{c['emit_symbols_mean']} | {c['parse_rate']:.3f} | "
                  f"{c['well_typed_rate']:.3f} | {c['exact_gold_rate']:.3f} | "
                  f"{c['empty_rate']:.3f} | {c['hit_cap_rate']:.3f} |")
    P("")

    # per depth accuracy grid, both wordings.
    for temp in (0.0, 0.8):
        tag = "greedy" if temp == 0.0 else "sampled t=0.8"
        for style in (0, 1):
            w = "trained wording" if style == 0 else "paraphrase wording"
            P(f"## plan_execute accuracy by depth, {w}, {tag}")
            P("")
            depths = sorted({c["depth"] for d in runs.values()
                             for c in d["cells"].values()
                             if c["cond"] == "plan_execute"
                             and c["kind"] == SEQ and c["style"] == style})
            P("| arm | " + " | ".join(str(x) for x in depths) + " |")
            P("|---" * (len(depths) + 1) + "|")
            for arm, d in sorted(runs.items()):
                cs = cells_for(d, "plan_execute", style, temp, SEQ)
                row = []
                for x in depths:
                    c = cs.get(x)
                    row.append("." if c is None
                               else f"{c['emit_steps_mean']}/{c['acc']:.2f}")
                P(f"| {arm} | " + " | ".join(row) + " |")
            P("")
        P("")

    if args.records:
        P("## strict against lenient, and the abstention channel")
        P("")
        P("An item counts as answered when the plan parsed and the induced "
          "operator table ran it. plan_parse and execute failures produce no "
          "answer at all, so they are the abstention channel.")
        P("")
        P("| arm | cell | n | strict acc | answered | lenient acc | "
          "no answer | plan parse fail | execute fail |")
        P("|---|---|---|---|---|---|---|---|---|")
        for arm, d in sorted(runs.items()):
            D, S = arm_ceiling(arm)
            rt = reason_table(d.get("records", ""), arm, D)
            report["arms"][arm]["reasons"] = rt
            for k, v in rt.items():
                P(f"| {arm} | {k} | {v['n']} | {v['strict_acc']} | "
                  f"{v['answered']} | {v['lenient_acc']} | "
                  f"{v['no_answer']} ({v['no_answer_rate']:.3f}) | "
                  f"{v['plan_parse_fail']} | {v['execute_fail']} |")
        P("")

    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1)
    with open(args.md, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"[written] {args.out} {args.md}")
    if broken:
        print("[HARNESS BROKEN] oracle_both below 1.000 in arms: "
              + ", ".join(broken))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
