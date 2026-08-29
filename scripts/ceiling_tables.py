"""The tables the ceiling question is decided on, as markdown.

Reads every arm summary written by `scripts/ceiling_eval.py` and prints, in
the order the question is decided:

  1. emitted plan length against required length, per arm, which is the direct
     measurement of the ceiling
  2. where each arm stops tracking, and the largest plan it ever wrote
  3. answer accuracy by condition, with denominators and the majority-answer
     rate that stands in for a chance floor
  4. novel composition: distinct symbols emitted against required, and how
     often the structure was right while the symbols collapsed
  5. relational breadth one to six, which a plan-length ceiling should not move
  6. structure under depth: operands, wiring and typing

Nothing is pooled across composition kind or wording.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re


def arm_depth(name: str) -> int:
    m = re.match(r"d(\d+)s(\d+)$", name)
    return int(m.group(1)) if m else -1


def arm_symbols(name: str) -> int:
    m = re.match(r"d(\d+)s(\d+)$", name)
    return int(m.group(2)) if m else -1


def load(pattern: str) -> dict:
    out = {}
    for p in sorted(glob.glob(pattern)):
        name = os.path.basename(p).split(".")[0]
        name = name.split("_", 1)[1] if "_" in name else name
        try:
            with open(p) as fh:
                out[name] = json.load(fh)
        except json.JSONDecodeError:
            print(f"<!-- {p} not valid json yet, skipped -->")
    return out


def order(names):
    return sorted(names, key=lambda n: (arm_symbols(n), arm_depth(n)))


def pick(summary, cond, kind, style, temp):
    got = {}
    for _, c in summary["cells"].items():
        if (c["cond"] == cond and c["kind"] == kind and c["style"] == style
                and abs(c["temperature"] - temp) < 1e-9):
            got[c["depth"]] = c
    return got


def fmt(v, spec="{:.3f}"):
    if v is None:
        return "."
    if isinstance(v, float):
        return spec.format(v)
    return str(v)


def table(summaries, field, cond, kind, style, temp, spec="{:.3f}"):
    depths = sorted({d for s in summaries.values()
                     for d in pick(s, cond, kind, style, temp)})
    if not depths:
        return "no cells\n"
    lines = ["| arm | " + " | ".join(str(d) for d in depths) + " |",
             "|---|" + "---|" * len(depths)]
    for name in order(summaries):
        row = pick(summaries[name], cond, kind, style, temp)
        cells = [fmt(row[d].get(field) if d in row else None, spec)
                 for d in depths]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def tracking_point(summaries, cond, kind, style, temp, tol=0.5):
    """The largest required depth an arm still matched in emitted length."""
    lines = ["| arm | training ceiling | tracks to | largest plan emitted | "
             "emitted at required 8 | emitted at required 32 |",
             "|---|---|---|---|---|---|"]
    for name in order(summaries):
        row = pick(summaries[name], cond, kind, style, temp)
        tracks = 0
        biggest = 0
        for d in sorted(row):
            m = row[d].get("emit_steps_mean")
            mx = row[d].get("emit_steps_max")
            if mx:
                biggest = max(biggest, mx)
            if m is not None and m >= d - tol:
                tracks = d
            elif m is not None:
                break
        e8 = row.get(8, {}).get("emit_steps_mean")
        e32 = row.get(32, {}).get("emit_steps_mean")
        lines.append(f"| {name} | {arm_depth(name)} | {tracks} | {biggest} | "
                     f"{fmt(e8)} | {fmt(e32)} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="/home/ec2-user/opg/results/ceiling/fast_*.json")
    ap.add_argument("--out", default="")
    ap.add_argument("--temp", type=float, default=0.0)
    ap.add_argument("--style", type=int, default=0)
    args = ap.parse_args()

    s = load(args.glob)
    if not s:
        print("no summaries")
        return 1
    o: list[str] = []
    w = o.append

    w(f"Summaries: {', '.join(order(s))}\n")
    w(f"Decoding: temperature {args.temp}, page wording style {args.style}\n")

    w("\n## 1. Emitted plan length against required, sequential, "
      "gold operators (composition isolated)\n")
    w("\nMean emitted steps. The column heading is the number of steps the "
      "question needs.\n")
    w(table(s, "emit_steps_mean", "oracle_ops", "sequential", args.style, args.temp))
    w("\nMax emitted steps over the cell.\n")
    w(table(s, "emit_steps_max", "oracle_ops", "sequential", args.style,
            args.temp, "{:.0f}"))
    w("\nDecoding hit the token budget (a truncated plan would read as a short "
      "plan, so this must stay at zero for the length numbers to mean "
      "anything).\n")
    w(table(s, "hit_cap_rate", "oracle_ops", "sequential", args.style, args.temp))

    w("\n## 2. Where each arm stops tracking\n")
    w(tracking_point(s, "oracle_ops", "sequential", args.style, args.temp))

    w("\n## 3. Answer accuracy, sequential\n")
    for cond in ("plan_execute", "oracle_plan", "oracle_ops", "oracle_both"):
        t = 0.0 if cond in ("oracle_plan", "oracle_both") else args.temp
        st = 0 if cond in ("oracle_ops", "oracle_both") else args.style
        w(f"\n{cond} (style {st}, temperature {t})\n")
        w(table(s, "acc", cond, "sequential", st, t))
    w("\nDenominator per cell\n")
    w(table(s, "n", "oracle_ops", "sequential", 0, args.temp, "{:.0f}"))
    w("\nMajority-answer rate, the empirical chance floor\n")
    w(table(s, "majority_gold_rate", "oracle_ops", "sequential", 0, args.temp))
    w("\nEmpty output rate, the hedge rate\n")
    w(table(s, "empty_rate", "oracle_ops", "sequential", 0, args.temp))

    w("\n## 4. Novel composition, two operators from two pages\n")
    w("\nDistinct operator symbols emitted (the question needs 2)\n")
    w(table(s, "emit_symbols_mean", "oracle_ops", "novel", 0, args.temp))
    w("\nStructure right, symbols collapsed onto fewer names than needed\n")
    w(table(s, "symbol_collapse_rate", "oracle_ops", "novel", 0, args.temp))
    w("\nAccuracy, gold operators, model plan\n")
    w(table(s, "acc", "oracle_ops", "novel", 0, args.temp))
    w("\nAccuracy, model induces and plans\n")
    w(table(s, "acc", "plan_execute", "novel", args.style, args.temp))
    w("\nEmitted plan length on novel\n")
    w(table(s, "emit_steps_mean", "oracle_ops", "novel", 0, args.temp))

    w("\n## 5. Relational breadth 1 to 6\n")
    for cond in ("plan_execute", "oracle_plan", "oracle_ops", "oracle_both"):
        t = 0.0 if cond in ("oracle_plan", "oracle_both") else args.temp
        st = 0 if cond in ("oracle_ops", "oracle_both") else args.style
        w(f"\n{cond} (style {st}, temperature {t})\n")
        w(table(s, "acc", cond, "breadth", st, t))

    w("\n## 6. Structure under depth, sequential, gold operators\n")
    w("\nPlan parse rate\n")
    w(table(s, "parse_rate", "oracle_ops", "sequential", 0, args.temp))
    w("\nWell typed rate\n")
    w(table(s, "well_typed_rate", "oracle_ops", "sequential", 0, args.temp))
    w("\nExact gold plan rate\n")
    w(table(s, "exact_gold_rate", "oracle_ops", "sequential", 0, args.temp))
    w("\nShape match: operands, ordering and register wiring right, symbols "
      "ignored\n")
    w(table(s, "shape_match_rate", "oracle_ops", "sequential", 0, args.temp))
    w("\nOperand multiset match\n")
    w(table(s, "operands_match_rate", "oracle_ops", "sequential", 0, args.temp))
    w("\nEmitted plan text containing the gold answer as a literal, a leakage "
      "check that should stay near zero\n")
    w(table(s, "contains_gold_rate", "oracle_ops", "sequential", 0, args.temp))

    text = "\n".join(o)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
