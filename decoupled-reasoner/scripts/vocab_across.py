"""Put the rungs of the ladder side by side, at one decoding temperature.

Three things a per-rung dump cannot show.

The shape in depth for every rung in one place, so a rung that lifts depth two
and still collapses by depth eight is visible as such rather than as a good
number at one depth.

The fraction of the measured gap each rung recovers. The ceiling is that rung's
own oracle_plan, where the plan is gold and the model still induces every
operator itself. The floor is the english rung, which is the closest to the
prose the model already writes and is what the ladder is measured against. A
rung that recovers none of the gap has changed the spelling and nothing else.

The harness check. oracle_both has to be 1.000 in every cell of every rung. A
representation that loses information shows up there and nowhere else, and if
it is not 1.000 no other number on the page can be read.
"""

from __future__ import annotations

import argparse
import glob
import json
import os

RUNGS = ["english", "symbolic", "opcode", "typed", "goalstack", "slots"]

# The smallest ceiling-to-floor span worth turning into a fraction.
MIN_SPAN = 0.25


def load(pattern: str, tag: str) -> dict:
    out = {}
    for p in sorted(glob.glob(pattern)):
        base = os.path.basename(p)
        if not base.endswith(f"_{tag}.json"):
            continue
        rep = base.replace("smoke_", "").replace(f"_{tag}.json", "")
        out[rep] = json.load(open(p))
    return out


def cells(res: dict, cond: str, kind: str) -> dict:
    return res.get(cond, {}).get(kind, {})


def depths(runs: dict, kind: str) -> list[str]:
    seen: dict[str, None] = {}
    for res in runs.values():
        for cond in ("plan_execute", "oracle_plan"):
            for d in cells(res, cond, kind):
                seen[d] = None
    return sorted(seen, key=int)


def row(res: dict, cond: str, kind: str, ds: list[str], field: str) -> str:
    out = []
    for d in ds:
        c = cells(res, cond, kind).get(d)
        out.append("  .  " if c is None else f"{c[field]:.2f} ")
    return "".join(out)


def n_of(res: dict, kind: str) -> str:
    for cond in ("plan_execute", "oracle_plan", "oracle_both"):
        for c in cells(res, cond, kind).values():
            return str(c["n"])
    return "?"


def recovered(res: dict, floor: dict, kind: str, d: str) -> float | None:
    """Fraction of this rung's own measured gap that the rung recovers."""
    hi = cells(res, "oracle_plan", kind).get(d)
    lo = cells(floor, "plan_execute", kind).get(d)
    me = cells(res, "plan_execute", kind).get(d)
    if hi is None or lo is None or me is None:
        return None
    span = hi["acc"] - lo["acc"]
    # A fraction of a gap that is not there is not a number worth printing. At
    # small n a span of one or two items turns a single disagreement into a
    # ratio of several, which reads as a large effect and is not one.
    if span < MIN_SPAN:
        return None
    return (me["acc"] - lo["acc"]) / span


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="results/ladder/smoke_*.json")
    ap.add_argument("--tag", default="greedy", help="greedy or sampled")
    ap.add_argument("--kinds", default="sequential,breadth,novel,units")
    ap.add_argument("--floor", default="english",
                    help="the rung the gap is measured from")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    runs = load(args.glob, args.tag)
    if not runs:
        print(f"no {args.tag} files matched {args.glob}")
        return 1
    order = [r for r in RUNGS if r in runs] + \
            [r for r in sorted(runs) if r not in RUNGS]
    lines: list[str] = [f"===== {args.tag} ====="]

    missing = [r for r in RUNGS if r not in runs]
    if missing:
        lines.append(f"rungs with no {args.tag} result: {', '.join(missing)}")

    lines.append("")
    lines.append("-- harness check, oracle_both must be 1.000 everywhere")
    for rep in order:
        ob = runs[rep].get("oracle_both", {})
        bad = [(k, d, c["acc"]) for k, cs in ob.items()
               for d, c in cs.items() if c["acc"] < 1.0]
        ck = runs[rep].get("checkpoint", {})
        lines.append(f"  {rep:10s} oracle_both_ok={not bad:1} "
                     f"cells={sum(len(cs) for cs in ob.values()):3d} "
                     f"step={ck.get('step')} reinit={ck.get('reinit_tokens')}"
                     + (f"  FAILURES {bad[:4]}" if bad else ""))

    for kind in args.kinds.split(","):
        ds = depths(runs, kind)
        if not ds:
            continue
        head = "".join(f"{d:^5s}" for d in ds)
        lines.append("")
        lines.append(f"-- {kind}, accuracy   depth {head}")
        for cond in ("plan_execute", "oracle_plan", "oracle_ops",
                     "plan_execute@para", "oracle_plan@para"):
            if not any(cells(runs[r], cond, kind) for r in order):
                continue
            for rep in order:
                if not cells(runs[rep], cond, kind):
                    continue
                lines.append(f"  {rep:10s} {cond:18s} "
                             f"{row(runs[rep], cond, kind, ds, 'acc')}"
                             f" n={n_of(runs[rep], kind)}")
            lines.append("")
        lines.append(f"-- {kind}, plan parses   depth {head}")
        for rep in order:
            if not cells(runs[rep], "plan_execute", kind):
                continue
            lines.append(f"  {rep:10s} {'plan_execute':18s} "
                         f"{row(runs[rep], 'plan_execute', kind, ds, 'plan_parses')}")
        lines.append("")
        lines.append(f"-- {kind}, parseable but wrong   depth {head}")
        for rep in order:
            if not cells(runs[rep], "plan_execute", kind):
                continue
            lines.append(f"  {rep:10s} {'plan_execute':18s} "
                         f"{row(runs[rep], 'plan_execute', kind, ds, 'parsed_but_wrong')}")

        floor = runs.get(args.floor)
        if floor is not None:
            lines.append("")
            lines.append(f"-- {kind}, fraction of the gap recovered over "
                         f"{args.floor}   depth {head}")
            lines.append(f"   blank where the ceiling and the floor are within "
                         f"{MIN_SPAN} of each other, which is not a gap.")
            for rep in order:
                vals = []
                for d in ds:
                    v = recovered(runs[rep], floor, kind, d)
                    vals.append("  .  " if v is None else f"{v:+.2f}")
                lines.append(f"  {rep:10s} {'':18s} " + " ".join(vals))

    ds = depths(runs, "sequential")
    if ds:
        lines.append("")
        lines.append("-- sequential decay shape, plan_execute")
        lines.append("   last_depth_above_half is the deepest d with accuracy at "
                     "or above 0.5 at every depth up to d.")
        lines.append("   per_depth_factor is the geometric mean of "
                     "acc(d+1)/acc(d) over the pairs where acc(d) is above zero.")
        for rep in order:
            cs = cells(runs[rep], "plan_execute", "sequential")
            if not cs:
                continue
            accs = [cs[d]["acc"] for d in ds if d in cs]
            last = 0
            for i, a in enumerate(accs):
                if a >= 0.5:
                    last = int(ds[i])
                else:
                    break
            ratios = [accs[i + 1] / accs[i] for i in range(len(accs) - 1)
                      if accs[i] > 0]
            if ratios:
                prod = 1.0
                for r in ratios:
                    prod *= r
                fac = prod ** (1.0 / len(ratios))
            else:
                fac = float("nan")
            lines.append(f"  {rep:10s} last_depth_above_half={last} "
                         f"per_depth_factor={fac:.3f} over {len(ratios)} pairs")

    lines.append("")
    lines.append("-- representation diagnostics, plan_execute only")
    for rep in order:
        for kind in args.kinds.split(","):
            for d, c in sorted(cells(runs[rep], "plan_execute", kind).items(),
                               key=lambda kv: int(kv[0])):
                if c.get("extra"):
                    lines.append(f"  {rep:10s} {kind}/{d}: "
                                 f"{json.dumps(c['extra'])}")
    text = "\n".join(lines)
    print(text)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
