"""Turn the per-arm summaries into the ceiling tables.

Three tables come out of this, in the order they decide the question.

  emitted plan length against the training ceiling, which is the direct
  measurement: if the test ceiling tracks the training ceiling the first
  hypothesis holds, if it sits near three whatever the training ceiling the
  second does, and if it tracks and then stops there is a real horizon and
  this prints where it is

  answer accuracy by condition, kind and depth, each cell with its
  denominator and the majority-answer rate that stands in for a chance floor

  relational breadth one to six, which a plan-length ceiling should not move
"""

from __future__ import annotations

import argparse
import json
import os


def load(paths: dict) -> dict:
    out = {}
    for arm, p in paths.items():
        with open(p) as fh:
            out[arm] = json.load(fh)
    return out


def cells(summary, cond=None, style=None, temp=None, kind=None):
    for key, c in summary["cells"].items():
        if cond and c["cond"] != cond:
            continue
        if style is not None and c["style"] != style:
            continue
        if temp is not None and abs(c["temperature"] - temp) > 1e-9:
            continue
        if kind and c["kind"] != kind:
            continue
        yield key, c


def table(arms, summaries, field, cond, kind, style, temp, depths):
    rows = []
    head = f"{'arm':>8} | " + " ".join(f"{d:>7}" for d in depths)
    rows.append(head)
    rows.append("-" * len(head))
    for arm in arms:
        s = summaries.get(arm)
        if not s:
            continue
        by_depth = {c["depth"]: c for _, c in
                    cells(s, cond=cond, style=style, temp=temp, kind=kind)}
        cs = []
        for d in depths:
            c = by_depth.get(d)
            v = c.get(field) if c else None
            cs.append("      ." if v is None else f"{v:>7.3f}"
                      if isinstance(v, float) else f"{v:>7}")
        rows.append(f"{arm:>8} | " + " ".join(cs))
    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summaries", required=True,
                    help="arm=path,arm=path,...")
    ap.add_argument("--out", required=True)
    ap.add_argument("--kind", default="sequential")
    ap.add_argument("--cond", default="oracle_ops")
    ap.add_argument("--style", type=int, default=0)
    ap.add_argument("--temp", type=float, default=0.0)
    args = ap.parse_args()

    paths = {}
    for chunk in args.summaries.split(","):
        if not chunk.strip():
            continue
        a, p = chunk.split("=")
        if os.path.exists(p):
            paths[a] = p
    summaries = load(paths)
    arms = list(paths)

    depths = sorted({c["depth"] for s in summaries.values()
                     for _, c in cells(s, cond=args.cond, kind=args.kind,
                                       style=args.style, temp=args.temp)})
    out = []
    for field in ("emit_steps_mean", "emit_steps_max", "acc", "parse_rate",
                  "well_typed_rate", "exact_gold_rate", "shape_match_rate",
                  "operands_match_rate", "emit_symbols_mean",
                  "symbol_collapse_rate", "hit_cap_rate", "empty_rate",
                  "majority_gold_rate", "n"):
        out.append(f"\n### {field}  cond={args.cond} kind={args.kind} "
                   f"style={args.style} temp={args.temp}")
        out.append(table(arms, summaries, field, args.cond, args.kind,
                         args.style, args.temp, depths))
    text = "\n".join(out)
    with open(args.out, "w") as fh:
        fh.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
