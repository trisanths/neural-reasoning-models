"""Turn the raw eval JSON into the headline the experiment was run to get.

For every condition and every kind of composition it reports the accuracy at
each depth and the depth at which the condition falls below threshold, defined
as the largest depth d such that accuracy is at or above the threshold at every
depth up to and including d. A condition that is already below threshold at the
smallest depth measured gets 0.

It also reports which stage is responsible. The two oracle rescues do most of
that work: if oracle_ops is much higher than plan_execute the induction is at
fault, and if oracle_plan is much higher the composition is. One case needs the
failure reasons rather than the accuracies. When the gold plan cannot even run
against the induced operators, the reason counter for oracle_plan fills with
`execute` rather than `wrong_value`, which means the induced operator does not
have the signature the page states. That is an induction failure that would
otherwise be read off the accuracies as a planning failure, because both oracle
rescues drop together.
"""

from __future__ import annotations

import argparse
import json

BASE_ORDER = ["base_untrained_direct", "direct_all", "direct_oracle_page",
              "trace_all", "trace_oracle_page", "plan_execute", "oracle_plan",
              "oracle_ops", "step_plan_execute", "step_oracle_ops",
              "oracle_both"]
ORDER = BASE_ORDER + [c + "@para" for c in BASE_ORDER
                      if c != "base_untrained_direct"]
HEADLINE = ["sequential", "breadth", "novel"]


def wilson(k: int, n: int, z: float = 1.96):
    """Wilson score interval, so a 150 item cell carries its own error bar."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (round((c - half) / d, 4), round((c + half) / d, 4))


def breakdown_depth(row: dict, threshold: float) -> int:
    depths = sorted((int(d) for d in row), key=int)
    best = 0
    for d in depths:
        if row[str(d)]["acc"] >= threshold:
            best = d
        else:
            break
    return best


def signature_broken(cell: dict) -> bool:
    """True when this cell failed by refusing to run, not by running wrong.

    A plan that carries the right operator symbol but the wrong number of
    arguments cannot execute at all, so it lands in `execute` rather than in
    `wrong_value`. Half the cell is enough to call it.
    """
    reasons = cell.get("reasons") or {}
    total = sum(reasons.values())
    return total > 0 and reasons.get("execute", 0) >= 0.5 * total


def blame(pe, oo, op, ob, op_cell, threshold, margin=0.2):
    """Name the stage responsible for one cell, or '-' when nothing is."""
    if ob is not None and ob < threshold:
        return "executor"
    if pe >= threshold:
        return "-"
    if op_cell is not None and signature_broken(op_cell):
        return "induction/arity"
    ind_gain = (oo - pe) if oo is not None else float("-inf")
    plan_gain = (op - pe) if op is not None else float("-inf")
    if plan_gain >= margin and plan_gain > ind_gain:
        return "scheduler"
    if ind_gain >= margin:
        return "induction"
    if op is not None and oo is not None and max(ind_gain, plan_gain) < margin:
        return "both"
    return "unresolved"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True,
                    help="one path, or several separated by commas, merged in order")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    res: dict = {}
    for path in args.results.split(","):
        path = path.strip()
        with open(path) as fh:
            part = json.load(fh)
        for name, body in part.items():
            if name == "config":
                res.setdefault("config", {})[path] = body
            elif name.startswith("induction"):
                # counts, so halves of one grid add up
                slot = res.setdefault(name, {})
                for k, v in body.items():
                    slot[k] = slot.get(k, 0) + v
            elif isinstance(body, dict):
                slot = res.setdefault(name, {})
                for kind, cells in body.items():
                    slot.setdefault(kind, {}).update(cells)
            else:
                res[name] = body

    kinds = [k for k in HEADLINE if any(k in res.get(c, {}) for c in ORDER)]
    extra = sorted({k for c in ORDER for k in res.get(c, {}) if k not in kinds})
    summary: dict = {"threshold": args.threshold, "breakdown_depth": {},
                     "accuracy": {}, "blame": {},
                     "induction": res.get("induction", {})}

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
                str(d): {"acc": row[str(d)]["acc"], "n": row[str(d)]["n"],
                         "ci": wilson(round(row[str(d)]["acc"] * row[str(d)]["n"]),
                                      row[str(d)]["n"])}
                for d in widths if str(d) in row}

    for style_key in ("induction", "induction@para", "induction_step",
                      "induction_step@para"):
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

    print("\n=== how the plan path failed, by kind and depth ===")
    print(f"{'kind':18s} {'d':>2s}  {'condition':13s} reasons")
    for kind in kinds + extra:
        for cond in ("plan_execute", "oracle_plan"):
            row = res.get(cond, {}).get(kind, {})
            for d in sorted(row, key=int):
                r = row[d].get("reasons")
                if r:
                    print(f"{kind:18s} {d:>2s}  {cond:13s} " +
                          " ".join(f"{k}={v}" for k, v in sorted(r.items())))

    print("\n=== which stage is responsible ===")
    print(f"{'kind':18s} {'d':>2s}  {'plan_exec':>9s} {'gold_ops':>9s} "
          f"{'gold_plan':>9s}  stage")
    for kind in kinds + extra:
        row_pe = res.get("plan_execute", {}).get(kind, {})
        row_op = res.get("oracle_plan", {}).get(kind, {})
        row_oo = res.get("oracle_ops", {}).get(kind, {})
        row_ob = res.get("oracle_both", {}).get(kind, {})
        for d in sorted(row_pe, key=int):
            pe = row_pe[d]["acc"]
            oo = row_oo.get(d, {}).get("acc")
            op = row_op.get(d, {}).get("acc")
            ob = row_ob.get(d, {}).get("acc")
            who = blame(pe, oo, op, ob, row_op.get(d), args.threshold)
            summary["blame"].setdefault(kind, {})[d] = who
            gi = "     .   " if oo is None else f"{oo - pe:+9.3f}"
            gp = "     .   " if op is None else f"{op - pe:+9.3f}"
            print(f"{kind:18s} {d:>2s}  {pe:9.3f} {gi} {gp}  {who}")

    if args.out:
        with open(args.out, "w") as fh:
            json.dump(summary, fh, indent=1)
        print(f"\n[written] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
