"""Can every head's plan representation hold every plan the sweep will ask for?

A head whose codec cannot express a plan is capped, and every number it then
produces measures the cap rather than the head. `oracle_both_roundtrip` in the
evaluation catches that, but only on the cells that were actually run and only
after a model has been trained. This runs the same question first, on the CPU,
over the whole evaluation grid at the denominator the sweep will use.

For each head and each cell it encodes the gold plan into that head's
representation, decodes it back to plan text, parses it with the same strict
parser the model output meets, executes it, and checks the answer against gold
and the serialised plan against the gold plan. Any failure is reported with the
cell and the reason, and the exit status is non zero.
"""

from __future__ import annotations

import argparse
import json
import sys

from src.opgraph.data import eval_items
from src.opgraph.plan import parse_plan, run_plan, serialize_plan
from src.opgraph.planheads import (HEADS, decode_plan_text, encode_plan,
                                   from_opcode_text, schema_for, to_opcode_text)

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 7, 8],
    "breadth": [1, 2, 3, 4, 5, 6],
    "novel": [2, 3, 4, 5, 6],
    "sequential_paren": [2, 3, 4, 5, 6],
    "same_page_pair": [2],
    "units": [1],
}


def roundtrip(head: str, item) -> str:
    """Plan text after a trip through this head's representation, or raise."""
    ops = item.world.ops
    gold = serialize_plan(item.plan)
    if head == "p1":
        return gold
    if head == "p2":
        return from_opcode_text(to_opcode_text(gold, ops), ops)
    schema = schema_for(head)
    return decode_plan_text(encode_plan(item.plan, ops, schema), ops, schema)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--styles", default="0,1")
    ap.add_argument("--out", default="results/planheads_codec_check.json")
    args = ap.parse_args()

    styles = [int(s) for s in args.styles.split(",")]
    report: dict = {"n": args.n, "styles": styles, "heads": {}}
    failures: list[dict] = []
    for style in styles:
        for kind, depths in GRID.items():
            for depth in depths:
                items = eval_items(kind, depth, args.n, style=style)
                for head in HEADS:
                    cell = report["heads"].setdefault(head, {}).setdefault(
                        f"style{style}", {}).setdefault(kind, {})
                    ok = 0
                    for item in items:
                        try:
                            text = roundtrip(head, item)
                            plan = parse_plan(text)
                            value = run_plan(plan, item.world.ops)
                            assert str(value) == item.gold, "answer changed"
                            assert (serialize_plan(plan)
                                    == serialize_plan(item.plan)), "plan changed"
                            ok += 1
                        except Exception as exc:
                            failures.append({
                                "head": head, "style": style, "kind": kind,
                                "depth": depth, "world": item.world.seed,
                                "reason": f"{type(exc).__name__}: {exc}"[:160],
                            })
                    cell[str(depth)] = {"n": len(items), "ok": ok}
    report["failures"] = failures[:200]
    report["failure_count"] = len(failures)
    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1)

    print(f"codec round trip over the evaluation grid, n={args.n} a cell")
    for head in HEADS:
        tot = ok = 0
        for block in report["heads"][head].values():
            for kd in block.values():
                for c in kd.values():
                    tot += c["n"]
                    ok += c["ok"]
        print(f"  {head:4s} {ok}/{tot} plans survive the round trip")
    if failures:
        print(f"\n{len(failures)} failures, first ten:")
        for f in failures[:10]:
            print("  " + json.dumps(f))
    print(f"[written] {args.out}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
