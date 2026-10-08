"""Tables for rungs C and D: raw accuracy, gap recovered, plan diagnostics, decay.

The gap is the one the original experiment measured. Its floor is that
experiment's plan_execute, which is the prose plan the ladder is trying to
improve on, and its ceiling is this rung's own oracle_plan, which is the same
model reading the same pages with only the plan supplied. A rung that recovers
none of the gap has changed the spelling and nothing else.

The floor is only known where the original experiment published it: sequential
depth one to eight on both wordings, and novel on the original wording. Cells
without a published floor print raw accuracy and a blank fraction rather than a
fraction against a floor that was never measured.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os

# The original experiment, as registered before this ladder was built.
FLOOR = {
    ("sequential", 0): {"1": 1.000, "2": 0.480, "3": 0.500, "4": 0.020,
                        "5": 0.033, "6": 0.020, "7": 0.007, "8": 0.013},
    ("sequential", 1): {"1": 0.600, "2": 0.313, "3": 0.293, "4": 0.007,
                        "5": 0.027, "6": 0.020, "7": 0.007, "8": 0.007},
    ("novel", 0): {str(d): 0.013 for d in (2, 3, 4, 5, 6, 8, 12, 16, 24, 32)},
    ("breadth", 0): {"4": 0.420},
}
MIN_SPAN = 0.25
FIELDS = ("acc", "plan_parses", "well_typed", "exact_gold_plan",
          "parsed_but_wrong")


def dkey(d: str) -> int:
    return int(d)


def cells(res: dict, tag: str, kind: str) -> dict:
    return res.get(tag, {}).get(kind, {})


def all_depths(res: dict, kind: str, tags: list) -> list:
    ds: set = set()
    for t in tags:
        ds |= set(cells(res, t, kind))
    return sorted(ds, key=dkey)


def fit_decay(ds: list, accs: list) -> dict:
    """Shape of one curve in depth: flat, cliffed, or decaying with a rate."""
    pts = [(d, a) for d, a in zip(ds, accs) if a is not None]
    if len(pts) < 3:
        return {"shape": "too few points"}
    vals = [a for _, a in pts]
    span = max(vals) - min(vals)
    drops = [(pts[i][0], pts[i + 1][0], vals[i] - vals[i + 1])
             for i in range(len(pts) - 1)]
    worst = max(drops, key=lambda t: t[2]) if drops else None
    out: dict = {"span": round(span, 4), "first": round(vals[0], 4),
                 "last": round(vals[-1], 4)}
    if worst:
        out["largest_single_step_drop"] = {
            "from_depth": worst[0], "to_depth": worst[1],
            "drop": round(worst[2], 4)}
    pos = [(d, a) for d, a in pts if a > 0.005]
    if len(pos) >= 3:
        n = len(pos)
        sx = sum(d for d, _ in pos)
        sy = sum(math.log(a) for _, a in pos)
        sxx = sum(d * d for d, _ in pos)
        sxy = sum(d * math.log(a) for d, a in pos)
        den = n * sxx - sx * sx
        if den:
            slope = (n * sxy - sx * sy) / den
            lam = -slope
            out["decay_per_depth"] = round(lam, 4)
            if lam > 1e-6:
                out["half_life_depths"] = round(math.log(2) / lam, 2)
            out["fit_over_depths"] = [d for d, _ in pos]
    if span <= 0.10:
        out["shape"] = "flat"
    elif worst and worst[2] >= 0.40:
        out["shape"] = "cliff"
    else:
        out["shape"] = "decaying"
    return out


def table(res: dict, tags: list, kind: str, field: str) -> list:
    ds = all_depths(res, kind, tags)
    if not ds:
        return []
    head = "  ".join(f"{d:>6s}" for d in ds)
    lines = [f"   {'condition':<20s} {head}"]
    for t in tags:
        c = cells(res, t, kind)
        if not c:
            continue
        row = "  ".join(
            (f"{c[d][field]:6.3f}" if d in c and field in c[d] else "     .")
            for d in ds)
        lines.append(f"   {t:<20s} {row}")
    ns = cells(res, tags[0], kind)
    if ns:
        nrow = "  ".join(f"{ns[d]['n']:6d}" if d in ns else "     ." for d in ds)
        lines.append(f"   {'n':<20s} {nrow}")
    return lines


def recovered(res: dict, kind: str, style: int) -> list:
    tag_pe = "plan_execute" if style == 0 else "plan_execute@para"
    tag_op = "oracle_plan" if style == 0 else "oracle_plan@para"
    pe, op = cells(res, tag_pe, kind), cells(res, tag_op, kind)
    floor = FLOOR.get((kind, style), {})
    ds = sorted(set(pe) & set(op), key=dkey)
    if not ds:
        return []
    head = "  ".join(f"{d:>6s}" for d in ds)
    out = [f"   {'':<20s} {head}"]
    raw = "  ".join(f"{pe[d]['acc']:6.3f}" for d in ds)
    ceil = "  ".join(f"{op[d]['acc']:6.3f}" for d in ds)
    fl = "  ".join((f"{floor[d]:6.3f}" if d in floor else "     .") for d in ds)
    frac = []
    for d in ds:
        if d not in floor:
            frac.append("     .")
            continue
        lo, hi = floor[d], op[d]["acc"]
        if hi - lo < MIN_SPAN:
            frac.append("     .")
            continue
        frac.append(f"{(pe[d]['acc'] - lo) / (hi - lo):6.3f}")
    out.append(f"   {'floor (original)':<20s} {fl}")
    out.append(f"   {'plan_execute (raw)':<20s} {raw}")
    out.append(f"   {'ceiling oracle_plan':<20s} {ceil}")
    out.append(f"   {'gap recovered':<20s} {'  '.join(frac)}")
    return out


def one(path: str, lines: list) -> dict:
    with open(path) as fh:
        res = json.load(fh)
    rep = res.get("rep", "?")
    temp = res.get("config", {}).get("temperature", "?")
    ck = res.get("checkpoint", {})
    lines.append("")
    lines.append("=" * 78)
    lines.append(f"{rep}   temperature {temp}   step {ck.get('step')}   "
                 f"reinit rows {ck.get('reinit_tokens')}")
    lines.append(f"file {os.path.basename(path)}")
    lines.append("=" * 78)

    ob = res.get("oracle_both_failures", [])
    lines.append(f"oracle_both is 1.000 everywhere: "
                 f"{res.get('oracle_both_all_one')}"
                 + (f"   failures {ob[:6]}" if ob else ""))
    un = res.get("unrepresentable", [])
    if un:
        lines.append(f"cells with no encoding in this representation: {len(un)}")
        for u in un[:8]:
            lines.append(f"   {u['kind']} d={u['depth']} style={u['style']}  "
                         f"{u['reason']}")
    for st in (0, 1):
        ind = res.get("induction" if st == 0 else "induction@para")
        if ind:
            lines.append(f"induction style={st}: {json.dumps(ind)}")

    summary: dict = {"rep": rep, "temperature": temp, "cells": [],
                     "shape": {}, "oracle_both_all_one":
                     res.get("oracle_both_all_one")}
    kinds = ["sequential", "novel", "breadth", "sequential_paren"]
    for st, suf in ((0, ""), (1, "@para")):
        tags = [t + suf for t in ("plan_execute", "oracle_plan",
                                  "oracle_ops", "oracle_both")]
        tags = [t for t in tags if res.get(t)]
        for kind in kinds:
            if not any(cells(res, t, kind) for t in tags):
                continue
            wording = "original" if st == 0 else "paraphrase"
            lines.append("")
            lines.append(f"-- {kind}, {wording} wording, accuracy")
            lines.extend(table(res, tags, kind, "acc"))
            lines.append(f"-- {kind}, {wording} wording, gap recovered")
            lines.extend(recovered(res, kind, st) or ["   (no published floor)"])
            for field in ("plan_parses", "well_typed", "exact_gold_plan",
                          "parsed_but_wrong"):
                lines.append(f"-- {kind}, {wording} wording, {field}")
                lines.extend(table(res, tags, kind, field))
            for t in tags:
                c = cells(res, t, kind)
                if len(c) < 3:
                    continue
                ds = sorted(c, key=dkey)
                sh = fit_decay([dkey(d) for d in ds], [c[d]["acc"] for d in ds])
                summary["shape"][f"{t}/{kind}"] = sh
                lines.append(f"   shape {t:<20s} {json.dumps(sh)}")
            for t in tags:
                for d, c in sorted(cells(res, t, kind).items(), key=lambda kv: dkey(kv[0])):
                    row = {"condition": t, "kind": kind,
                           "wording": wording, "depth": dkey(d), "n": c["n"]}
                    row.update({f: c.get(f) for f in FIELDS})
                    if "declarations_agree" in c:
                        row["declarations_agree"] = c["declarations_agree"]
                    if "extra" in c:
                        row["extra"] = c["extra"]
                    summary["cells"].append(row)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="results/ladder_cd/*.json")
    ap.add_argument("--out", default="results/ladder_cd/REPORT_CD.txt")
    ap.add_argument("--summary", default="results/ladder_cd/summary_cd.json")
    args = ap.parse_args()
    lines: list = []
    summaries = []
    for path in sorted(glob.glob(args.glob)):
        if os.path.basename(path).startswith("summary"):
            continue
        try:
            summaries.append(one(path, lines))
        except Exception as exc:
            lines.append(f"[skip] {path}: {type(exc).__name__}: {exc}")
    text = "\n".join(lines)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        fh.write(text + "\n")
    with open(args.summary, "w") as fh:
        json.dump(summaries, fh, indent=1)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
