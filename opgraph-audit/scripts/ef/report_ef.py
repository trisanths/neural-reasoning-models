"""Read the E and F result files and write the tables the report needs.

Nothing is computed here that is not in the JSON. What this adds is the shape
in depth, the fraction of the recorded gap each cell recovers, and the
plan-level diagnostics side by side with the answer accuracy, so the place
where a rung loses an item is visible rather than inferred.
"""

from __future__ import annotations

import argparse
import json
import math
import os

# The original operator-graph arms, at the settings this sweep matches, as
# recorded in src/opgraph/README.md. These are the floor the ladder is scored
# against: the gap is from this plan_execute up to the rung's own oracle_plan.
FLOOR = {
    ("sequential", 0): {1: 1.000, 2: 0.480, 3: 0.500, 4: 0.020,
                        5: 0.033, 6: 0.020, 7: 0.007, 8: 0.013},
    ("sequential", 1): {1: 0.600, 2: 0.313, 3: 0.293, 4: 0.007, 5: 0.027,
                        6: 0.020, 7: 0.007, 8: 0.007},
    ("novel", 0): {2: 0.013, 3: 0.013, 4: 0.013, 5: 0.013, 6: 0.013},
}
MIN_SPAN = 0.25
COND = ["plan_execute", "oracle_plan", "oracle_ops", "oracle_both"]


def tag(name, style):
    return name if style == 0 else name + "@para"


def cells(res, name, style, kind):
    return res.get(tag(name, style), {}).get(kind, {})


def fmt(x, w=6):
    return "  n/a " if x is None else f"{x:{w}.3f}"


def depth_table(res, name, style, kind, depths, field="acc"):
    c = cells(res, name, style, kind)
    return [c[str(d)][field] if str(d) in c else None for d in depths]


def decay(depths, accs):
    """A single exponential fitted to whatever is not zero, and its residual.

    Reported with the raw points beside it. A fit over a curve that is flat at
    one and then falls off a cliff is not a description of the curve, so the
    cliff depth is reported too and the fit is only worth reading when the
    residual is small.
    """
    pts = [(d, a) for d, a in zip(depths, accs)
           if a is not None and a > 0.0]
    if len(pts) < 3:
        return None
    xs = [p[0] for p in pts]
    ys = [math.log(max(p[1], 1e-3)) for p in pts]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    half = math.log(0.5) / b if b < 0 else None
    first_zero = next((d for d, v in zip(depths, accs)
                       if v is not None and v == 0.0), None)
    return {"rate_per_depth": b, "r2": r2, "half_life": half,
            "first_zero_depth": first_zero, "points": len(pts)}


def gap(res, name, style, kind, d):
    floor = FLOOR.get((kind, style), {}).get(d)
    hi = cells(res, "oracle_plan", style, kind).get(str(d))
    me = cells(res, name, style, kind).get(str(d))
    if floor is None or hi is None or me is None:
        return None
    span = hi["acc"] - floor
    if span < MIN_SPAN:
        return None
    return (me["acc"] - floor) / span


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    lines: list[str] = []
    w = lines.append

    for path in args.files:
        if not os.path.exists(path):
            w(f"missing {path}")
            continue
        res = json.load(open(path))
        rep = res["rep"]
        temp = res["config"]["temperature"]
        label = f"{rep} @ temperature {temp}"
        w("=" * 78)
        w(f"{label}   {os.path.basename(path)}")
        ck = res["checkpoint"]
        w(f"checkpoint step={ck.get('step')} examples={ck.get('examples')} "
          f"supervised_tokens={ck.get('supervised_tokens')} "
          f"reinit_tokens={ck.get('reinit_tokens')}")
        w(f"oracle_both all 1.000: {res.get('oracle_both_all_one')}"
          + ("" if res.get("oracle_both_all_one") else
             f"  FAILURES {res.get('oracle_both_failures')[:8]}"))
        for st in (0, 1):
            ind = res.get(tag("induction", st))
            if ind:
                w(f"induction style={st}: {json.dumps(ind)}")
        grid = res["grid"]

        conds = [c for c in COND if tag(c, 0) in res]
        extra = sorted(k for k in res
                       if k.startswith("plan_execute_") and "@para" not in k)
        for kind, depths in grid.items():
            for st in (0, 1):
                if not cells(res, "plan_execute", st, kind):
                    continue
                w("")
                wording = "original" if st == 0 else "paraphrase"
                w(f"-- {kind}, {wording} page wording")
                hdr = "depth      " + "".join(f"{d:>7d}" for d in depths)
                w(hdr)
                for name in conds + extra:
                    if st != 0 and name in ("oracle_ops", "oracle_both"):
                        continue
                    row = depth_table(res, name, st, kind, depths)
                    if all(v is None for v in row):
                        continue
                    w(f"{name:<11s}" + "".join(fmt(v) for v in row))
                ns = depth_table(res, "plan_execute", st, kind, depths, "n")
                w("n          " + "".join("  n/a " if v is None else f"{v:>7d}"
                                          for v in ns))
                for field in ("plan_parses", "well_typed", "exact_gold_plan",
                              "parsed_but_wrong"):
                    row = depth_table(res, "plan_execute", st, kind, depths,
                                      field)
                    if all(v is None for v in row):
                        continue
                    w(f"{field:<11s}" + "".join(fmt(v) for v in row))
                gr = [gap(res, "plan_execute", st, kind, d) for d in depths]
                if any(v is not None for v in gr):
                    w("gap_recov  " + "".join(fmt(v) for v in gr))
                fit = decay(depths, depth_table(res, "plan_execute", st, kind,
                                                depths))
                if fit:
                    w(f"fit plan_execute: rate={fit['rate_per_depth']:+.3f}/depth"
                      f" r2={fit['r2']:.3f} half_life="
                      + ("n/a" if fit["half_life"] is None
                         else f"{fit['half_life']:.1f}")
                      + f" first_zero_depth={fit['first_zero_depth']}")
                fit = decay(depths, depth_table(res, "oracle_plan", st, kind,
                                                depths))
                if fit:
                    w(f"fit oracle_plan:  rate={fit['rate_per_depth']:+.3f}/depth"
                      f" r2={fit['r2']:.3f} first_zero_depth="
                      f"{fit['first_zero_depth']}")

        # The condition-specific diagnostics, which live in "extra".
        for st in (0, 1):
            for kind in grid:
                c = cells(res, "plan_execute", st, kind)
                keys = sorted({k for d in c.values()
                               for k in d.get("extra", {})})
                if not keys:
                    continue
                w("")
                w(f"-- {kind} extras, style {st}")
                depths = grid[kind]
                w("depth      " + "".join(f"{d:>9d}" for d in depths))
                for k in keys:
                    if k == "bind_replacements":
                        continue
                    row = [c[str(d)]["extra"].get(k) if str(d) in c else None
                           for d in depths]
                    cellstr = []
                    for v in row:
                        if v is None:
                            cellstr.append("      n/a")
                        elif isinstance(v, float):
                            cellstr.append(f"{v:9.3f}")
                        else:
                            cellstr.append(f"{v:>9}")
                    w(f"{k:<26s}" + "".join(cellstr))
                for d in depths:
                    br = c.get(str(d), {}).get("extra", {}).get(
                        "bind_replacements")
                    if br:
                        w(f"  d={d} bind replacements: {json.dumps(br)}")
        w("")
    with open(args.out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[:0]))
    print(f"[written] {args.out}  ({len(lines)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
