"""Composition depth, which the interpreter does not bound.

A plan is a list and executing it is a loop over that list, so depth 32768
costs what depth 2 costs per step and nothing extra for being deep. This lane
runs the same structure at rising depths against an independent reference
computed a different way, and times it.

Two existing limits are reported beside it, because the point is that they are
not inherited:

    src/opgraph/plan.py   MAX_STEPS 128. `parse_plan` refuses a longer plan.
    src/opgraph/opdef.py  MAX_DEPTH 64 on expression nesting, and its
                          evaluator recurses, so a deep body also risks the
                          Python stack. `src/norm/interp.py` walks an explicit
                          stack instead.

The measured comparison on record for the neural checkpoint is that it
collapsed by depth four. Nothing here runs a checkpoint.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

from src.norm.interp import Cannot, eval_expr, run
from src.norm.lang import Lit, Program, Ref, Step, Table
from src.norm.shapes import assemble
from src.opgraph import opdef, plan as opplan

DEPTHS = (2, 4, 8, 16, 48, 128, 512, 2048, 8192, 32768)


def ring_case(depth: int, width: int = 64, seed: int = 5):
    rng = random.Random(seed)
    nodes = [f"n{i}" for i in range(width)]
    rng.shuffle(nodes)
    t = Table("Ring", tuple((nodes[i], nodes[(i + 1) % width])
                            for i in range(width)))
    start = nodes[0]
    p = assemble("iterate", tables=[t], inputs=(("x", start),), n=depth)
    # The reference is computed a different way: index arithmetic on the ring
    # rather than a walk, so an error in the walk cannot be reproduced by it.
    return p, nodes[depth % width]


def opgraph_limit() -> dict:
    """Where src/opgraph/plan.py stops, measured rather than quoted."""
    out = {"MAX_STEPS": opplan.MAX_STEPS}
    for d in (opplan.MAX_STEPS, opplan.MAX_STEPS + 1, opplan.MAX_STEPS + 2):
        text = " ; ".join([f"t{i} = add 1 1" for i in range(1, d + 1)]
                          + [f"ans t{d}"])
        try:
            opplan.parse_plan(text)
            out[f"parse_plan_at_{d}"] = "accepted"
        except opplan.PlanError as exc:
            out[f"parse_plan_at_{d}"] = f"refused: {exc}"
    return out


def nested_expr(depth: int):
    e = opdef.Var("x")
    for _ in range(depth):
        e = opdef.Call("+", (e, 1))
    return e


def expr_limits() -> dict:
    out = {"opdef_MAX_DEPTH": opdef.MAX_DEPTH}
    for d in (64, 65, 1000, 100000):
        e = nested_expr(d)
        try:
            v = eval_expr(e, {"x": 0})
            out[f"norm_eval_at_{d}"] = f"ok, {v}"
        except (Cannot, RecursionError) as exc:
            out[f"norm_eval_at_{d}"] = f"{type(exc).__name__}: {exc}"
        if d <= 1000:
            try:
                v = opdef.eval_expr(e, {"x": 0})
                out[f"opdef_eval_at_{d}"] = f"ok, {v}"
            except (opdef.OpError, RecursionError) as exc:
                out[f"opdef_eval_at_{d}"] = f"{type(exc).__name__}: {exc}"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/norm/depth/summary.json")
    args = ap.parse_args()
    rows = []
    for d in DEPTHS:
        p, want = ring_case(d)
        t0 = time.perf_counter()
        r = run(p)
        dt = time.perf_counter() - t0
        rows.append({"depth": d, "steps": len(p.steps), "ok": r.ok,
                     "exact": bool(r.ok and r.value == want),
                     "seconds": round(dt, 6),
                     "us_per_step": round(dt * 1e6 / max(1, len(p.steps)), 3)})
    out = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "note": ("one ring walk per depth, against a reference computed by "
                 "index arithmetic rather than by walking"),
        "recursionlimit": sys.getrecursionlimit(),
        "plan_depth": rows,
        "exact_at_every_depth": all(r["exact"] for r in rows),
        "opgraph_plan": opgraph_limit(),
        "expression_nesting": expr_limits(),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
