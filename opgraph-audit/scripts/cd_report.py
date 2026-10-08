"""Read the rung C and rung D result files and print what the sweep was for.

Three things the raw json does not say on its own.

The fraction of the gap recovered. The floor is the opgraph arm's own
plan_execute, the number this ladder exists to move, recorded in the original
experiment at n=150 per cell. The ceiling is the rung's own oracle_plan, where
the plan is gold and the model still induces every operator itself. A cell is
blank when the two are within MIN_SPAN of each other, because a fraction of a
gap that is not there reads as a large effect and is not one, and blank past
depth eight on the sequential and novel families because the original
experiment did not measure a floor there.

The shape in depth. A rung that lifts depth two and collapses by depth eight
has not moved the horizon. Reported as an exponential fit over the depths where
accuracy is positive, alongside the constant fit, so flat and decaying are
distinguishable rather than asserted.

The plan-level diagnostics next to the answers. The gap between a plan that
parses and an answer that is right is where the remaining failure sits.
"""

from __future__ import annotations

import argparse
import json
import math
import os

MIN_SPAN = 0.25

# The opgraph arm, n=150 per cell, from the original experiment. This is the
# floor the ladder is measured against. Nothing past depth eight was measured,
# and a floor that was not measured is not invented here.
FLOOR = {
    ("sequential", 0): {1: 0.480, 2: 0.227, 3: 0.127, 4: 0.020,
                        5: 0.020, 6: 0.007, 7: 0.013, 8: 0.013},
    ("sequential", 1): {1: 0.187, 2: 0.047, 3: 0.053, 4: 0.033,
                        5: 0.007, 6: 0.007, 7: 0.000, 8: 0.000},
}
# plan_execute in the opgraph arm, which is the arm this ladder replaces.
FLOOR_PE = {
    ("sequential", 0): {1: 1.000, 2: 0.480, 3: 0.500, 4: 0.020,
                        5: 0.033, 6: 0.020, 7: 0.007, 8: 0.013},
    ("sequential", 1): {1: 0.600, 2: 0.313, 3: 0.293, 4: 0.007,
                        5: 0.027, 6: 0.020, 7: 0.007, 8: 0.007},
    ("novel", 0): {2: 0.013, 3: 0.013, 4: 0.013, 5: 0.013, 6: 0.013},
}


def cells(res, cond, kind):
    return res.get(cond, {}).get(kind, {})


def depths(res, kind):
    seen = {}
    for cond in ("plan_execute", "oracle_plan", "oracle_ops", "oracle_both",
                 "plan_execute@para", "oracle_plan@para"):
        for d in cells(res, cond, kind):
            seen[d] = None
    return sorted(seen, key=int)


def fit_decay(ds, accs):
    """Exponential fit over the positive points, against a constant fit."""
    pts = [(d, a) for d, a in zip(ds, accs) if a > 0]
    if len(pts) < 3:
        return None
    xs = [float(d) for d, _ in pts]
    ys = [math.log(a) for _, a in pts]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    b = my - k * mx
    pred = [math.exp(b + k * x) for x in xs]
    obs = [a for _, a in pts]
    mo = sum(obs) / len(obs)
    sst = sum((o - mo) ** 2 for o in obs)
    sse = sum((o - p) ** 2 for o, p in zip(obs, pred))
    r2 = 1 - sse / sst if sst > 0 else float("nan")
    # A constant fit over the same points, so flat has something to beat.
    sse_const = sst
    return {"per_depth_factor": math.exp(k), "decay_rate": -k,
            "a0": math.exp(b), "r2_exponential": r2,
            "sse_exponential": sse, "sse_constant": sse_const,
            "points": len(pts),
            "half_life_depths": (math.log(0.5) / k) if k < 0 else None}


def shape_line(ds, accs):
    last = 0
    for d, a in zip(ds, accs):
        if a >= 0.5:
            last = int(d)
        else:
            break
    drops = [(round(accs[i] - accs[i + 1], 3), f"{ds[i]}->{ds[i + 1]}")
             for i in range(len(accs) - 1)]
    biggest = max(drops, key=lambda t: t[0]) if drops else (0.0, "-")
    fit = fit_decay(ds, accs)
    txt = (f"last_depth_at_or_above_0.5={last} "
           f"largest_single_step_drop={biggest[0]:.3f} at {biggest[1]}")
    if fit:
        txt += (f" | exp fit: per_depth_factor={fit['per_depth_factor']:.3f} "
                f"r2={fit['r2_exponential']:.3f} "
                f"sse_exp={fit['sse_exponential']:.4f} vs "
                f"sse_const={fit['sse_constant']:.4f} "
                f"over {fit['points']} positive points")
    else:
        txt += " | too few positive points for a fit"
    return txt, fit


def recovered(res, kind, style, d):
    floor = FLOOR_PE.get((kind, style), {}).get(int(d))
    if floor is None:
        return None
    cond_pe = "plan_execute" if style == 0 else "plan_execute@para"
    cond_op = "oracle_plan" if style == 0 else "oracle_plan@para"
    hi = cells(res, cond_op, kind).get(d)
    me = cells(res, cond_pe, kind).get(d)
    if hi is None or me is None:
        return None
    span = hi["acc"] - floor
    if span < MIN_SPAN:
        return None
    return (me["acc"] - floor) / span


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/cd")
    ap.add_argument("--reps", default="opcode,typed")
    ap.add_argument("--tags", default="greedy,sampled")
    ap.add_argument("--kinds",
                    default="sequential,breadth,novel,sequential_paren,"
                            "same_page_pair,units")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lines: list[str] = []
    summary: dict = {}
    for tag in args.tags.split(","):
        for rep in args.reps.split(","):
            path = os.path.join(args.dir, f"{rep}_{tag}.json")
            if not os.path.exists(path):
                lines.append(f"### {rep} {tag}: no result file at {path}")
                continue
            res = json.load(open(path))
            ck = res.get("checkpoint", {})
            lines.append("")
            lines.append(f"===== {rep} / {tag} =====")
            lines.append(f"checkpoint step={ck.get('step')} arm={ck.get('arm')} "
                         f"reinit_tokens={ck.get('reinit_tokens')} "
                         f"supervised_tokens={ck.get('supervised_tokens')}")
            for st in (0, 1):
                ind = res.get("induction" if st == 0 else "induction@para")
                if ind:
                    lines.append(f"induction style={st}: {json.dumps(ind)}")

            bad = res.get("oracle_both_failures") or []
            lines.append(f"oracle_both all 1.000: {not bad}"
                         + (f"  FAILURES {bad[:8]}" if bad else ""))

            for kind in args.kinds.split(","):
                ds = depths(res, kind)
                if not ds:
                    continue
                head = "".join(f"{d:>7s}" for d in ds)
                lines.append("")
                lines.append(f"-- {kind}   depth {head}")
                for cond in ("plan_execute", "oracle_plan", "oracle_ops",
                             "oracle_both", "plan_execute@para",
                             "oracle_plan@para", "oracle_ops@para",
                             "oracle_both@para"):
                    cs = cells(res, cond, kind)
                    if not cs:
                        continue
                    row = "".join(f"{cs[d]['acc']:>7.3f}" if d in cs
                                  else "      ." for d in ds)
                    ns = {cs[d]["n"] for d in cs}
                    lines.append(f"   acc  {cond:20s}{row}   n={sorted(ns)}")
                for field in ("plan_parses", "well_typed", "exact_gold_plan",
                              "parsed_but_wrong", "declarations_agree"):
                    for cond in ("plan_execute", "plan_execute@para",
                                 "oracle_ops"):
                        cs = cells(res, cond, kind)
                        if not cs or field not in next(iter(cs.values())):
                            continue
                        row = "".join(f"{cs[d][field]:>7.3f}" if d in cs
                                      else "      ." for d in ds)
                        lines.append(f"   {field[:9]:9s} {cond:15s}{row}")
                for st, cond in ((0, "plan_execute"), (1, "plan_execute@para")):
                    vals = []
                    any_v = False
                    for d in ds:
                        v = recovered(res, kind, st, d)
                        if v is None:
                            vals.append("      .")
                        else:
                            vals.append(f"{v:>+7.3f}")
                            any_v = True
                    if any_v:
                        lab = "gap_recovered" + ("@para" if st else "")
                        lines.append(f"   {lab:26s}" + "".join(vals))
                        summary.setdefault(f"{rep}/{tag}", {})[
                            f"{kind}/style{st}/gap_recovered"] = {
                                d: recovered(res, kind, st, d) for d in ds}

                for cond in ("plan_execute", "oracle_plan",
                             "plan_execute@para", "oracle_plan@para"):
                    cs = cells(res, cond, kind)
                    if not cs:
                        continue
                    accs = [cs[d]["acc"] for d in ds if d in cs]
                    dd = [d for d in ds if d in cs]
                    txt, fit = shape_line(dd, accs)
                    lines.append(f"   shape {cond:20s}{txt}")
                    if fit:
                        summary.setdefault(f"{rep}/{tag}", {})[
                            f"{kind}/{cond}/fit"] = fit

                for cond in ("plan_execute", "plan_execute@para"):
                    cs = cells(res, cond, kind)
                    for d in ds:
                        if d in cs and cs[d].get("reasons"):
                            lines.append(f"   why   {cond:20s} d={d:<3s} "
                                         f"{json.dumps(cs[d]['reasons'])}")
                for cond in ("plan_execute", "plan_execute@para"):
                    cs = cells(res, cond, kind)
                    for d in ds:
                        if d in cs and cs[d].get("extra"):
                            lines.append(f"   extra {cond:20s} d={d:<3s} "
                                         f"{json.dumps(cs[d]['extra'])}")

    text = "\n".join(lines)
    with open(args.out, "w") as fh:
        fh.write(text + "\n")
    with open(args.out.replace(".txt", "") + "_summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
