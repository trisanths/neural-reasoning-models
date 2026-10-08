"""Tables for the depth by recurrence sweep.

The question this sweep exists to answer is the shape of the depth curve, so
the classifier that turns a curve into a word is written down here rather than
left to prose. Three outcomes are distinguished and never pooled:

  flat        the curve never falls below the threshold anywhere in the grid
  cliff@k     it first falls below the threshold at depth k, and k is where the
              measured token channel arms already fall
  moved@k     it first falls below the threshold at depth k, deeper than the
              token channel arms manage

A moved cliff and a flat curve mean different things about the architecture. A
moved cliff says a second bottleneck sits underneath the one that was removed.
A flat curve says the bottleneck was the whole story. Reporting one as the
other is the single most damaging error available here.

The fitted per depth decay is printed beside the label in every table, because
a cliff that moves two steps and a decay that halves are not the same claim and
the label alone cannot separate them.
"""

from __future__ import annotations

import argparse
import json
import math
import os

THRESH = 0.10

# The measured token channel arms, from results/opgraph_report.txt at n = 150,
# depths 1..8. They are what every latent number is compared against, so they
# are quoted rather than recomputed.
REFERENCE_DEPTHS = [1, 2, 3, 4, 5, 6, 7, 8]
REFERENCE = {
    "direct_all": [0.480, 0.227, 0.127, 0.020, 0.020, 0.007, 0.013, 0.013],
    "trace_all": [0.860, 0.460, 0.267, 0.027, 0.000, 0.000, 0.033, 0.000],
    "plan_execute": [1.000, 1.000, 1.000, 0.020, 0.033, 0.020, 0.040, 0.020],
    "oracle_plan": [1.0] * 8,
}
AR_CLIFF = 4        # where direct, trace and plan_execute all fall below 0.10


def crossing(depths, rates, thr=THRESH):
    for d, r in zip(depths, rates):
        if r is not None and r < thr:
            return d
    return None


def decay(depths, rates, floor=1e-3):
    pts = [(d, r) for d, r in zip(depths, rates) if r is not None and r > floor]
    if len(pts) < 2:
        return None
    xs = [float(d) for d, _ in pts]
    ys = [math.log(r) for _, r in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    var = sum((x - mx) ** 2 for x in xs)
    if var <= 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / var
    return math.exp(slope)


def half_life(depths, rates):
    """Depths per halving of the rate, from the fitted log linear decay.

    This is the column that stops a higher intercept being read as a longer
    horizon. A curve that starts at 1.000 instead of 0.480 crosses any fixed
    threshold later while decaying at exactly the same rate, and only the two
    numbers side by side say which happened.
    """
    d = decay(depths, rates)
    if d is None or d <= 0 or d >= 1:
        return None
    return math.log(0.5) / math.log(d)


def shape_label(depths, rates, thr=THRESH, ar_cliff=AR_CLIFF):
    live = [r for r in rates if r is not None]
    if not live or max(live) < thr:
        return "floor"
    k = crossing(depths, rates, thr)
    if k is None:
        return "flat"
    if k > ar_cliff:
        return f"moved@{k}"
    if k == ar_cliff:
        return f"cliff@{k}"
    return f"early@{k}"


def fmt(x, nd=3):
    return "-" if x is None else f"{x:.{nd}f}"


def load(path):
    with open(path) as fh:
        return json.load(fh)


def cells_of(doc, kind):
    return [c for c in doc["cells"] if c.get("kind") == kind]


def curve(doc, kind, key="greedy"):
    """rows keyed by R, columns by depth."""
    cs = cells_of(doc, kind)
    depths = sorted({c["depth"] for c in cs})
    rs = sorted({c["r_steps"] for c in cs})
    rates, cells = {}, {}
    for r in rs:
        row, rowc = [], []
        for d in depths:
            hit = [c for c in cs if c["r_steps"] == r and c["depth"] == d]
            row.append(hit[0].get(key) if hit else None)
            rowc.append(hit[0] if hit else None)
        rates[r] = row
        cells[r] = rowc
    return depths, rates, cells


def md(header, rows):
    out = ["| " + " | ".join(str(h) for h in header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def section_curve(doc, kind, title):
    depths, greedy, cells = curve(doc, kind, "greedy")
    _, sampled, _ = curve(doc, kind, "sampled_mean")
    _, anyc, _ = curve(doc, kind, "sampled_any")
    if not depths:
        return ""
    n = next(c["n"] for row in cells.values() for c in row if c)
    head = ["R"] + [f"d{d}" for d in depths] + ["shape", "decay/depth",
                                                "half life in depths"]
    rows = []
    for r in sorted(greedy):
        rows.append([r] + [fmt(x) for x in greedy[r]]
                    + [shape_label(depths, greedy[r]),
                       fmt(decay(depths, greedy[r]), 2),
                       fmt(half_life(depths, greedy[r]), 2)])
    parts = [f"{title}, greedy, n={n} per cell", "", md(head, rows), "",
             f"{title}, sampled mean of 2 draws at T=0.8, n={n}", "",
             md(["R"] + [f"d{d}" for d in depths],
                [[r] + [fmt(x) for x in sampled[r]] for r in sorted(sampled)]),
             "",
             f"{title}, either sampled draw correct, n={n}", "",
             md(["R"] + [f"d{d}" for d in depths],
                [[r] + [fmt(x) for x in anyc[r]] for r in sorted(anyc)]), ""]
    return "\n".join(parts)


def section_cost(doc, kind, title):
    depths, _, cells = curve(doc, kind)
    if not depths:
        return ""
    head = ["R", "reason fwd/ex", "decode fwd/ex", "prompt fwd/ex",
            "total fwd/ex", "reason ms/ex", "total ms/ex", "cells wall s"]
    rows = []
    for r in sorted(cells):
        cs = [c for c in cells[r] if c]
        if not cs:
            continue

        def g(k):
            return sum(c["cost"][k] for c in cs) / len(cs)

        rows.append([
            r, fmt(g("reason_passes_per_example"), 1),
            fmt(g("decode_passes_per_example"), 1),
            fmt(g("prompt_passes_per_example"), 1),
            fmt(g("reason_passes_per_example") + g("decode_passes_per_example")
                + g("prompt_passes_per_example"), 1),
            fmt(1000 * g("reason_seconds_per_example"), 2),
            fmt(1000 * g("total_seconds_per_example"), 2),
            fmt(sum(c["wall_seconds"] for c in cs), 1)])
    return "\n".join([f"{title}, compute per example, mean over the depths of "
                      f"the curve", "", md(head, rows), ""])


def section_plan(doc, kind, title):
    depths, _, cells = curve(doc, kind)
    rows = []
    for r in sorted(cells):
        for d, c in zip(depths, cells[r]):
            if not c or "plan" not in c:
                continue
            p = c["plan"]
            rows.append([r, d, p["n"], fmt(p["parse_rate"]),
                         fmt(p["well_typed_rate"]), fmt(p["exact_gold_rate"]),
                         fmt(p["mean_steps_written"], 1),
                         fmt(p["mean_steps_gold"], 1), fmt(c["greedy"])])
    if not rows:
        return ""
    return "\n".join([f"{title}, plan level diagnostics, greedy", "",
                      md(["R", "depth", "n", "parse", "well typed",
                          "exact gold", "steps written", "steps gold",
                          "executed correct"], rows), ""])


def section_reference():
    rows = []
    for name, rates in REFERENCE.items():
        rows.append([name] + [fmt(x) for x in rates]
                    + [shape_label(REFERENCE_DEPTHS, rates),
                       fmt(decay(REFERENCE_DEPTHS, rates), 2),
                       fmt(half_life(REFERENCE_DEPTHS, rates), 2)])
    return "\n".join(["Token channel arms, sequential, greedy, n=150, from "
                      "results/opgraph_report.txt", "",
                      md(["condition"] + [f"d{d}" for d in REFERENCE_DEPTHS]
                         + ["shape", "decay/depth", "half life in depths"],
                         rows), ""])


def section_matched(mdoc, title):
    """The token channel given a measured reasoning forward pass budget."""
    cs = mdoc["cells"]
    depths = sorted({c["depth"] for c in cs})
    budgets = sorted({c["budget"] for c in cs})
    rows = []
    for b in budgets:
        row = [f"{b:g}"]
        got = []
        for d in depths:
            hit = [c for c in cs if c["budget"] == b and c["depth"] == d]
            if not hit:
                row.append("-")
                continue
            c = hit[0]
            row.append(fmt(c["vote"]))
            got.append(c["extra_reason_passes_per_example"])
        row.append(f"{min(got):.0f}-{max(got):.0f}" if got else "-")
        row.append(str(hit[0]["samples"]) if hit else "-")
        rows.append(row)
    head = ["budget R"] + [f"d{d}" for d in depths] + ["achieved fwd/ex", "N"]
    out = [f"{title}, majority vote over N samples, n={mdoc['n']}", "",
           md(head, rows), ""]
    rows = []
    for b in budgets:
        row = [f"{b:g}"]
        for d in depths:
            hit = [c for c in cs if c["budget"] == b and c["depth"] == d]
            row.append(fmt(hit[0]["any"]) if hit else "-")
        rows.append(row)
    out += [f"{title}, oracle selection over N samples (the ceiling a selector "
            f"is working against), n={mdoc['n']}", "",
            md(["budget R"] + [f"d{d}" for d in depths], rows), ""]
    return "\n".join(out)


def frontier(docs, matched, depth, kind="sequential"):
    """Accuracy against reasoning forward passes at one depth, every condition."""
    rows = []
    for name, doc in docs:
        for c in cells_of(doc, kind):
            if c["depth"] != depth:
                continue
            rows.append([name, f"R={c['r_steps']}",
                         fmt(c["cost"]["reason_passes_per_example"], 1),
                         fmt(c["cost"]["reason_passes_per_example"]
                             + c["cost"]["decode_passes_per_example"], 1),
                         c["n"], fmt(c["greedy"]), fmt(c["sampled_mean"])])
    for name, doc in matched:
        seen = set()
        for c in doc["cells"]:
            if c["depth"] != depth or c.get("kind") != kind:
                continue
            if c["samples"] in seen:
                continue
            seen.add(c["samples"])
            rows.append([name, f"N={c['samples']}",
                         fmt(c["extra_reason_passes_per_example"], 1),
                         fmt(c["samples"]
                             * c["decode_passes_greedy_per_example"], 1),
                         c["n"], fmt(c["greedy"]), fmt(c["vote"])])
    rows.sort(key=lambda r: (r[0], float(r[2])))
    return "\n".join([f"Compute accuracy frontier at {kind} depth {depth}", "",
                      md(["condition", "setting", "reasoning fwd/ex",
                          "reasoning+decode fwd/ex", "n", "greedy",
                          "selected or sampled"], rows), ""])


def pairs(doc, mdoc, latent_name, ar_name, kind="sequential"):
    """The mandated comparison, one row per (depth, R).

    Each row puts the latent condition at R beside the token channel handed the
    same number of reasoning forward passes. If the token channel column is not
    lower, what R bought was test time compute and nothing else.
    """
    cs = cells_of(doc, kind)
    depths = sorted({c["depth"] for c in cs})
    rs = sorted({c["r_steps"] for c in cs})
    rows = []
    for d in depths:
        for r in rs:
            hit = [c for c in cs if c["depth"] == d and c["r_steps"] == r]
            if not hit:
                continue
            c = hit[0]
            m = [x for x in mdoc["cells"]
                 if x.get("kind") == kind and x["depth"] == d
                 and abs(x["budget"] - r) < 1e-9]
            mm = m[0] if m else None
            rows.append([
                d, r, c["n"], fmt(c["greedy"]), fmt(c["sampled_mean"]),
                fmt(c["cost"]["reason_passes_per_example"], 1),
                fmt(mm["greedy"]) if mm else "-",
                fmt(mm["vote"]) if mm else "-",
                fmt(mm["any"]) if mm else "-",
                (str(mm["samples"]) if mm else "-"),
                fmt(mm["extra_reason_passes_per_example"], 1) if mm else "-"])
    return "\n".join([
        f"{latent_name} against {ar_name} at matched reasoning compute, {kind}",
        "",
        md(["depth", "R", "n", f"{latent_name} greedy", f"{latent_name} sampled",
            "latent fwd/ex", f"{ar_name} greedy", f"{ar_name} vote",
            f"{ar_name} oracle of N", "N", f"{ar_name} fwd/ex"], rows), ""])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--latent", nargs="*", default=[],
                    help="name=path.json for a latent sweep result")
    ap.add_argument("--matched", nargs="*", default=[],
                    help="name=path.json for a matched compute control")
    ap.add_argument("--frontier-depths", default="1,2,3,4")
    ap.add_argument("--pair", nargs="*", default=[],
                    help="latent_name:ar_name, one matched compute table each")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    docs, matched = [], []
    for spec in args.latent:
        name, _, path = spec.partition("=")
        if os.path.exists(path):
            docs.append((name, load(path)))
    for spec in args.matched:
        name, _, path = spec.partition("=")
        if os.path.exists(path):
            matched.append((name, load(path)))

    parts = ["# Depth by recurrence sweep, raw tables", "",
             "Generated by src/latent/report.py. Every rate carries its "
             "denominator. Threshold for the shape label is "
             f"{THRESH:.2f}.", "", section_reference()]
    for name, doc in docs:
        parts.append(f"## {name}")
        parts.append(f"checkpoint `{doc['ckpt']}`, style {doc['style']}, "
                     f"n={doc.get('n')}, induced ops: {doc.get('induce')}")
        parts.append("")
        for kind, title in (("sequential", "Sequential depth"),
                            ("breadth", "Relational breadth"),
                            ("novel", "Novel composition")):
            parts.append(section_curve(doc, kind, f"{name} {title}"))
        parts.append(section_cost(doc, "sequential", f"{name} sequential"))
        parts.append(section_plan(doc, "sequential", f"{name} sequential"))
    for name, doc in matched:
        parts.append(f"## {name}")
        parts.append(section_matched(doc, name))
    dd = dict(docs)
    mm = dict(matched)
    for spec in args.pair:
        ln, _, an = spec.partition(":")
        if ln in dd and an in mm:
            parts.append(f"## {ln} against {an}")
            for kind in ("sequential", "novel"):
                parts.append(pairs(dd[ln], mm[an], ln, an, kind))
    for d in (int(x) for x in args.frontier_depths.split(",")):
        parts.append(frontier(docs, matched, d))

    text = "\n".join(p for p in parts if p is not None)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        fh.write(text + "\n")
    print(f"[done] -> {args.out} ({len(text)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
