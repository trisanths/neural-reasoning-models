"""Turn the rung A and rung B result files into one report.

The gap a rung is scored against is the one the original experiment measured:
the floor is the opgraph arm's own plan_execute, the model writing the plan in
that arm's notation, and the ceiling is oracle_plan, the plan supplied with the
operator still induced by the model. Both are read cell by cell out of
`results/opgraph.json`, the original arm's own result file at the same
settings, rather than retyped from prose. Where the ceiling is not above the
floor by at least MIN_SPAN there is no gap to recover and the fraction is left
blank; that happens at relational breadth four and above, where plan_execute
beats oracle_plan.
"""

from __future__ import annotations

import argparse
import json
import math
import os

MIN_SPAN = 0.25
KINDS = ["sequential", "sequential_paren", "novel", "breadth",
         "same_page_pair", "units"]
CONDS = ["plan_execute", "oracle_plan", "oracle_ops", "oracle_both"]
TAGS = ["main_greedy", "main_sampled", "deep_greedy", "deep_sampled"]


def load(path):
    with open(path) as fh:
        return json.load(fh)


def cell(res, cond, style, kind, depth):
    tag = cond if style == 0 else cond + "@para"
    return res.get(tag, {}).get(kind, {}).get(str(depth))


def depths(res, cond, style, kind):
    tag = cond if style == 0 else cond + "@para"
    return sorted((int(k) for k in res.get(tag, {}).get(kind, {})))


class Reference:
    """The original opgraph arm, cell by cell, as floor and ceiling."""

    def __init__(self, paths):
        self.src = []
        self.d = {}
        self.clash = []
        for p in paths:
            if not p or not os.path.exists(p):
                continue
            r = load(p)
            self.src.append(p)
            for cond in ("plan_execute", "oracle_plan"):
                for style, tag in ((0, cond), (1, cond + "@para")):
                    for kind, cells in r.get(tag, {}).items():
                        for dk, c in cells.items():
                            k = (cond, style, kind, int(dk))
                            # The recorded grid wins where the two overlap, and
                            # the overlap is kept as a check rather than
                            # silently resolved: the deep floor run repeats
                            # sequential depth 8, which has to land on the
                            # number already on record or the pairing is wrong.
                            if k in self.d:
                                self.clash.append((k, self.d[k], c["acc"]))
                            else:
                                self.d[k] = c["acc"]

    def get(self, cond, style, kind, depth):
        return self.d.get((cond, style, kind, depth))

    def gap(self, acc, style, kind, depth):
        lo = self.get("plan_execute", style, kind, depth)
        hi = self.get("oracle_plan", style, kind, depth)
        if lo is None or hi is None or hi - lo < MIN_SPAN:
            return None, lo, hi
        return (acc - lo) / (hi - lo), lo, hi


def fit_decay(ds, accs):
    """Least squares on log accuracy, plus a flat and a cliff verdict.

    One exponent cannot tell a flat curve from one that falls off a cliff, so
    the fitted rate is reported next to the largest one-step drop and the total
    spread, and the verdict is taken from those.
    """
    out = {"n_points_fit": 0, "span": round(max(accs) - min(accs), 4),
           "max_step_drop": 0.0, "at": None, "decay_lambda": None,
           "half_life_depths": None, "r2": None, "fit_over_depths": None}
    for i in range(1, len(ds)):
        drop = accs[i - 1] - accs[i]
        if drop > out["max_step_drop"]:
            out["max_step_drop"] = round(drop, 4)
            out["at"] = f"{ds[i-1]}to{ds[i]}"
    pts = [(d, a) for d, a in zip(ds, accs) if a >= 0.005]
    out["n_points_fit"] = len(pts)
    if len(pts) >= 3:
        xs = [d for d, _ in pts]
        ys = [math.log(a) for _, a in pts]
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        slope = sxy / sxx if sxx else 0.0
        inter = my - slope * mx
        ss_t = sum((y - my) ** 2 for y in ys)
        ss_r = sum((y - (inter + slope * x)) ** 2 for x, y in zip(xs, ys))
        out["decay_lambda"] = round(-slope, 4)
        out["half_life_depths"] = (round(math.log(2) / -slope, 3)
                                   if slope < -1e-9 else None)
        out["r2"] = round(1 - ss_r / ss_t, 4) if ss_t > 1e-12 else None
        out["fit_over_depths"] = f"{min(xs)} to {max(xs)}"
    if out["span"] <= 0.10:
        out["verdict"] = "flat"
    elif out["max_step_drop"] >= 0.40:
        out["verdict"] = f"cliff {out['at']}"
    else:
        out["verdict"] = "decaying"
    return out


ROWS = [("n", "n"), ("acc", "acc"), ("gap recovered", "gap"),
        ("plan parses", "plan_parses"), ("well typed", "well_typed"),
        ("exact gold plan", "exact_gold_plan"),
        ("parsed but wrong, over n", "parsed_but_wrong"),
        ("parsed but wrong, given a parse", "wrong_given_parse")]


def table(res, ref, cond, style, kind):
    ds = depths(res, cond, style, kind)
    if not ds:
        return []
    out = ["| depth | " + " | ".join(str(d) for d in ds) + " |",
           "|---|" + "---|" * len(ds)]
    for label, key in ROWS:
        vals = []
        for d in ds:
            c = cell(res, cond, style, kind, d)
            if c is None:
                vals.append("")
            elif key == "gap":
                g, _, _ = ref.gap(c["acc"], style, kind, d)
                vals.append("" if g is None else f"{g:.3f}")
            elif key == "wrong_given_parse":
                p = c["plan_parses"]
                vals.append("" if p <= 0 else f"{c['parsed_but_wrong'] / p:.3f}")
            elif key == "n":
                vals.append(str(c["n"]))
            else:
                vals.append(f"{c[key]:.3f}")
        out.append(f"| {label} | " + " | ".join(vals) + " |")
    return out


def ref_rows(ref, style, kind, ds):
    lo = [ref.get("plan_execute", style, kind, d) for d in ds]
    hi = [ref.get("oracle_plan", style, kind, d) for d in ds]
    if all(v is None for v in lo) and all(v is None for v in hi):
        return []
    f = lambda v: "" if v is None else f"{v:.3f}"  # noqa: E731
    return [f"| reference floor, opgraph plan_execute | "
            + " | ".join(f(v) for v in lo) + " |",
            f"| reference ceiling, opgraph oracle_plan | "
            + " | ".join(f(v) for v in hi) + " |"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/ladder_ab")
    ap.add_argument("--reference", default="results/opgraph.json")
    ap.add_argument("--reference-deep", default=None)
    ap.add_argument("--out", default="src/opgraph/VOCAB_AB.md")
    ap.add_argument("--summary", default="results/ladder_ab/SUMMARY.txt")
    args = ap.parse_args()

    ref = Reference([args.reference, args.reference_deep])
    runs = {}
    for arm in ("english", "symbolic"):
        for tag in TAGS:
            p = os.path.join(args.dir, f"{arm}_{tag}.json")
            if os.path.exists(p):
                runs[(arm, tag)] = load(p)

    o: list[str] = []
    o.append("# Rungs A and B of the plan representation ladder")
    o.append("")
    o.append("Rung A writes the plan as English sentences. Rung B writes it as "
             "single letter registers over operator slots spelled in ordinary "
             "vocabulary. Neither uses a reserved token and neither redraws an "
             "embedding row, so both have the same parameter count as the base "
             "checkpoint and differ from the original opgraph arm in the plan "
             "half of the training stream and in nothing else.")
    o.append("")
    o.append("## What was run")
    o.append("")
    o.append("Both rungs are fine tuned from `ckpt/base350.pt` with `--steps "
             "8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000`, the "
             "settings the original arms used, over the same world seeds in the "
             "same shuffled order, with a byte identical induction half. "
             "Checkpoints are in `runs/ladder_ab/`, raw cells in "
             "`results/ladder_ab/`.")
    o.append("")
    for arm in ("english", "symbolic"):
        r = runs.get((arm, "main_greedy")) or runs.get((arm, "main_sampled"))
        if r:
            ck = r["checkpoint"]
            o.append(f"- {arm}: {ck['examples']} training examples, "
                     f"{ck['tokens']} tokens seen, {ck['supervised_tokens']} "
                     f"supervised, {ck['reinit_tokens']} embedding rows "
                     f"redrawn, checkpoint at step {ck['step']}.")
    o.append("")
    o.append("The gap each cell is scored against comes from "
             f"`{args.reference}`, the original opgraph arm's own result file "
             "at the same settings and the same n. The floor is that arm's "
             "plan_execute and the ceiling is its oracle_plan, cell by cell. "
             "Where the ceiling is not at least "
             f"{MIN_SPAN} above the floor there is no gap and the fraction is "
             "blank; that is the whole of relational breadth four and above, "
             "where the recorded plan_execute of 0.420 beats the recorded "
             "oracle_plan of 0.000.")
    if args.reference_deep:
        o.append("")
        o.append("The recorded grid stops at sequential depth eight, so the "
                 "floor past eight is measured rather than assumed: "
                 f"`{args.reference_deep}` runs `runs/opgraph.pt`, the arm that "
                 "set the floor, over the same items at depths 8, 16 and 32 in "
                 "that arm's own plan notation. Depth 8 is repeated there as a "
                 "check on the pairing.")
        o.append("")
        if ref.clash:
            o.append("| overlapping cell | on record | re-run |")
            o.append("|---|---|---|")
            for (cond, style, kind, d), a, b in ref.clash:
                w = "original" if style == 0 else "paraphrase"
                o.append(f"| {kind} {cond} {w} depth {d} | {a:.4f} | {b:.4f} |")
        else:
            o.append("No overlapping cell between the two reference files.")
    o.append("")
    o.append("## Harness check, oracle_both")
    o.append("")
    ok_all = True
    for (arm, tag) in sorted(runs):
        r = runs[(arm, tag)]
        good = r.get("oracle_both_all_one")
        bad = r.get("oracle_both_failures") or []
        if good is None:
            ok_all = False
            o.append(f"- {arm} {tag}: run did not reach the oracle_both check")
            continue
        ok_all = ok_all and bool(good)
        o.append(f"- {arm} {tag}: oracle_both is 1.000 in every cell: {good}"
                 + (f", failures {bad[:6]}" if bad else ""))
    o.append("")
    o.append("## The decoding budget")
    o.append("")
    o.append("The main grid runs at `--max-new 320`, the shared number. The "
             "deep sequential tail runs at 512, because rung A's gold plan at "
             "sequential depth 32 is 443 tokens where rung B's is 228. Depth 8 "
             "is measured again inside the deep grid at 512, so any difference "
             "at depth 8 between the two grids is the budget and not the "
             "depth. Depth 32 is the deepest cell either rung can express at "
             "all: rung A numbers results with ordinals one through thirty two "
             "and rung B names registers A to Z then a to f.")
    o.append("")
    for (arm, tag) in sorted(runs):
        r = runs[(arm, tag)]
        cl = r.get("budget_clipped_cells", [])
        o.append(f"- {arm} {tag}: max_new {r['config']['max_new']}, cells whose "
                 f"gold plan does not fit: {cl if cl else 'none'}")

    for arm in ("english", "symbolic"):
        title = "A, english" if arm == "english" else "B, symbolic"
        o.append("")
        o.append(f"## Rung {title}")
        for tag in TAGS:
            r = runs.get((arm, tag))
            if r is None:
                continue
            o.append("")
            o.append(f"### {tag.replace('_', ' ')}, temperature "
                     f"{r['config']['temperature']}")
            for style, wording in ((0, "original wording"),
                                   (1, "paraphrased wording")):
                for kind in KINDS:
                    for cond in CONDS:
                        if style == 1 and cond in ("oracle_ops", "oracle_both"):
                            continue
                        rows = table(r, ref, cond, style, kind)
                        if not rows:
                            continue
                        o.append("")
                        o.append(f"#### {kind}, {cond}, {wording}")
                        o.append("")
                        o.extend(rows)
                        if cond == "plan_execute":
                            o.extend(ref_rows(ref, style, kind,
                                              depths(r, cond, style, kind)))
            o.append("")
            o.append("#### shape in depth")
            o.append("")
            o.append("| series | verdict | span | largest one step drop | "
                     "decay lambda | half life in depths | r2 | fit over |")
            o.append("|---|---|---|---|---|---|---|---|")
            for style, wording in ((0, "original"), (1, "paraphrase")):
                for kind in ("sequential", "novel", "breadth",
                             "sequential_paren"):
                    for cond in CONDS:
                        if style == 1 and cond in ("oracle_ops", "oracle_both"):
                            continue
                        ds = depths(r, cond, style, kind)
                        if len(ds) < 3:
                            continue
                        accs = [cell(r, cond, style, kind, d)["acc"] for d in ds]
                        f = fit_decay(ds, accs)
                        o.append(f"| {kind} {cond} {wording} | {f['verdict']} | "
                                 f"{f['span']} | {f['max_step_drop']} at "
                                 f"{f['at']} | {_s(f['decay_lambda'])} | "
                                 f"{_s(f['half_life_depths'])} | "
                                 f"{_s(f['r2'])} | {_s(f['fit_over_depths'])} |")
            o.append("")
            o.append("#### induction, the same stream for both rungs")
            o.append("")
            o.append("| wording | pages | pages parsed | gold ops | induced ops "
                     "| self verified | exact text | behavioural |")
            o.append("|---|---|---|---|---|---|---|---|")
            for style, wording in ((0, "original"), (1, "paraphrase")):
                s = r.get("induction" if style == 0 else "induction@para")
                if not s:
                    continue
                o.append(f"| {wording} | {s.get('pages', 0)} | "
                         f"{s.get('pages_parsed', 0)} | {s.get('gold_ops', 0)} | "
                         f"{s.get('induced_ops', 0)} | "
                         f"{s.get('self_verified', 0)} | "
                         f"{s.get('exact_text', 0)} | "
                         f"{s.get('behavioural', 0)} |")
            o.append("")
            o.append("#### sample plans")
            o.append("")
            for kind, d in (("sequential", 8), ("sequential", 2),
                            ("novel", 2), ("breadth", 5)):
                c = cell(r, "plan_execute", 0, kind, d)
                if c and c.get("samples"):
                    o.append(f"- {kind} depth {d}, plan_execute: "
                             f"`{c['samples'][0][:300]}`")

    o.append("")
    o.append("## Where the rungs stand against each other")
    o.append("")
    for style, wording in ((0, "original"), (1, "paraphrase")):
        for kind in ("sequential", "novel", "breadth"):
            base = runs.get(("english", "main_greedy"))
            if base is None:
                continue
            ds = depths(base, "plan_execute", style, kind)
            if not ds:
                continue
            o.append("")
            o.append(f"#### {kind}, {wording}, plan_execute accuracy")
            o.append("")
            o.append("| series | " + " | ".join(str(d) for d in ds) + " |")
            o.append("|---|" + "---|" * len(ds))
            o.append("| opgraph arm on record | " + " | ".join(
                _f(ref.get("plan_execute", style, kind, d)) for d in ds) + " |")
            for arm in ("english", "symbolic"):
                for tag in ("main_greedy", "main_sampled"):
                    r = runs.get((arm, tag))
                    if r is None:
                        continue
                    row = []
                    for d in ds:
                        c = cell(r, "plan_execute", style, kind, d)
                        row.append("" if c is None else f"{c['acc']:.3f}")
                    o.append(f"| {arm} {tag.split('_')[1]} | "
                             + " | ".join(row) + " |")
            o.append("| opgraph arm oracle_plan, the ceiling | " + " | ".join(
                _f(ref.get("oracle_plan", style, kind, d)) for d in ds) + " |")

    with open(args.out, "w") as fh:
        fh.write("\n".join(o) + "\n")

    s: list[str] = [f"reference files: {ref.src}",
                    f"oracle_both 1.000 in every scored cell: {ok_all}"]
    for arm in ("english", "symbolic"):
        for tag in TAGS:
            r = runs.get((arm, tag))
            if r is None:
                s.append(f"{arm} {tag}: MISSING")
                continue
            for style in (0, 1):
                for kind in ("sequential", "breadth", "novel"):
                    ds = depths(r, "plan_execute", style, kind)
                    if not ds:
                        continue
                    s.append(f"{arm} {tag} style{style} {kind} d={ds}")
                    for cond in CONDS:
                        if style == 1 and cond in ("oracle_ops", "oracle_both"):
                            continue
                        cs = [cell(r, cond, style, kind, d) for d in ds]
                        if any(c is None for c in cs):
                            continue
                        s.append(f"   {cond:12s} acc  "
                                 + " ".join(f"{c['acc']:.3f}" for c in cs))
                        if cond == "plan_execute":
                            s.append("   " + " " * 12 + " prs  "
                                     + " ".join(f"{c['plan_parses']:.3f}"
                                                for c in cs))
                            s.append("   " + " " * 12 + " gap  "
                                     + " ".join(
                                         _f(ref.gap(c["acc"], style, kind, d)[0])
                                         for c, d in zip(cs, ds)))
    with open(args.summary, "w") as fh:
        fh.write("\n".join(s) + "\n")
    print("\n".join(s))
    print(f"[written] {args.out}")
    return 0


def _s(v):
    return "" if v is None else str(v)


def _f(v):
    return "" if v is None else f"{v:.3f}"


if __name__ == "__main__":
    raise SystemExit(main())
