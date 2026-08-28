"""Turn the raw eval JSON into the headline the experiment was run to get.

For every condition and every kind of composition it reports the accuracy at
each depth and the depth at which the condition falls below threshold, defined
as the largest depth d such that accuracy is at or above the threshold at every
depth up to and including d. A condition that is already below threshold at the
smallest depth measured gets 0.

It also reports which stage is responsible, by comparing the plan path against
its two oracle rescues: if oracle_ops is much higher than plan_execute the
induction is at fault, and if oracle_plan is much higher the composition is.
"""

from __future__ import annotations

import argparse
import json

BASE_ORDER = ["base_untrained_direct", "direct_all", "direct_oracle_page",
              "trace_all", "trace_oracle_page", "plan_execute", "oracle_plan",
              "oracle_ops", "oracle_both"]
ORDER = BASE_ORDER + [c + "@para" for c in BASE_ORDER
                      if c != "base_untrained_direct"]
HEADLINE = ["sequential", "breadth", "novel"]


def breakdown_depth(row: dict, threshold: float) -> int:
    depths = sorted((int(d) for d in row), key=int)
    best = 0
    for d in depths:
        if row[str(d)]["acc"] >= threshold:
            best = d
        else:
            break
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    with open(args.results) as fh:
        res = json.load(fh)

    kinds = [k for k in HEADLINE if any(k in res.get(c, {}) for c in ORDER)]
    extra = sorted({k for c in ORDER for k in res.get(c, {}) if k not in kinds})
    summary: dict = {"threshold": args.threshold, "breakdown_depth": {},
                     "accuracy": {}, "induction": res.get("induction", {})}

    for kind in kinds + extra:
        print(f"\n=== {kind} ===")
        widths = sorted({int(d) for c in ORDER for d in res.get(c, {}).get(kind, {})})
        print(f"{'condition':24s} " + " ".join(f"d{d:<5d}" for d in widths) + "  fails_after")
        for c in ORDER:
            row = res.get(c, {}).get(kind)
            if not row:
                continue
            cells = " ".join(f"{row[str(d)]['acc']:.3f}" if str(d) in row else "  .  "
                             for d in widths)
            bd = breakdown_depth(row, args.threshold)
            print(f"{c:24s} {cells}  {bd}")
            summary["breakdown_depth"].setdefault(kind, {})[c] = bd
            summary["accuracy"].setdefault(kind, {})[c] = {
                str(d): row[str(d)]["acc"] for d in widths if str(d) in row}

    for style_key in ("induction", "induction@para"):
        ind = res.get(style_key)
        if not ind:
            continue
        print(f"\n=== {style_key} over the eval worlds ===")
        summary.setdefault("induction_all", {})[style_key] = ind
        g = max(1, ind.get("gold_ops", 1))
        p = max(1, ind.get("pages", 1))
        o = max(1, ind.get("induced_ops", 1))
        print(f"pages parsed        {ind.get('pages_parsed', 0)}/{p} "
              f"= {ind.get('pages_parsed', 0) / p:.3f}")
        print(f"behaviourally right {ind.get('behavioural', 0)}/{g} "
              f"= {ind.get('behavioural', 0) / g:.3f}")
        print(f"exact text          {ind.get('exact_text', 0)}/{g} "
              f"= {ind.get('exact_text', 0) / g:.3f}")
        print(f"self verified       {ind.get('self_verified', 0)}/{o} "
              f"= {ind.get('self_verified', 0) / o:.3f}")

    print("\n=== why the plan path failed, by kind and depth ===")
    for kind in kinds + extra:
        row = res.get("plan_execute", {}).get(kind, {})
        for d in sorted(row, key=int):
            r = row[d].get("reasons")
            if r:
                print(f"{kind:18s} d={d:2s} " +
                      " ".join(f"{k}={v}" for k, v in sorted(r.items())))

    print("\n=== which stage is responsible ===")
    for kind in kinds:
        row_pe = res.get("plan_execute", {}).get(kind, {})
        row_op = res.get("oracle_plan", {}).get(kind, {})
        row_oo = res.get("oracle_ops", {}).get(kind, {})
        for d in sorted(row_pe, key=int):
            pe = row_pe[d]["acc"]
            ind_gain = row_oo.get(d, {}).get("acc", float("nan")) - pe
            plan_gain = row_op.get(d, {}).get("acc", float("nan")) - pe
            print(f"{kind:18s} d={d:2s} plan_execute={pe:.3f} "
                  f"gold_ops_gain={ind_gain:+.3f} gold_plan_gain={plan_gain:+.3f}")

    if args.out:
        with open(args.out, "w") as fh:
            json.dump(summary, fh, indent=1)
        print(f"\n[written] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
