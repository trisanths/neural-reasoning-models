"""Turn the ladder's raw JSON into the tables a reader actually needs.

Three tables. The depth shape per condition, because a rung that lifts depth two
and still collapses by depth eight has not addressed the horizon. The plan level
diagnostics, because the gap between a plan that parses and an answer that is
right is where the remaining failure sits. And the harness check, because
oracle_both below 1.000 anywhere means the representation is lossy and nothing
else on the page can be read.
"""

from __future__ import annotations

import argparse
import glob
import json
import os

CONDS = ["plan_execute", "oracle_plan", "oracle_ops", "oracle_both",
         "plan_execute@para", "oracle_plan@para"]


def load(paths):
    out = {}
    for p in sorted(paths):
        name = os.path.basename(p).replace(".json", "").replace("smoke_", "")
        out[name] = json.load(open(p))
    return out


def depth_table(res, kind, field="acc"):
    lines = []
    for cond in CONDS:
        row = res.get(cond, {}).get(kind)
        if not row:
            continue
        cells = " ".join(f"{d}:{row[d][field]:.3f}"
                         for d in sorted(row, key=int))
        lines.append(f"  {cond:22s} {cells}")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="results/ladder/smoke_*.json")
    ap.add_argument("--kinds", default="sequential,breadth,novel,units")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    runs = load(glob.glob(args.glob))
    if not runs:
        print(f"no files matched {args.glob}")
        return 1
    lines: list[str] = []
    summary = {}
    for name, res in runs.items():
        lines.append(f"\n===== {name}  rep={res.get('rep')} =====")
        ck = res.get("checkpoint", {})
        lines.append(f"  checkpoint: {json.dumps(ck)}")
        ob = res.get("oracle_both", {})
        bad = [(k, d, c["acc"]) for k, cells in ob.items()
               for d, c in cells.items() if c["acc"] < 1.0]
        lines.append(f"  oracle_both all 1.000: {not bad}"
                     + (f"  FAILURES {bad[:6]}" if bad else ""))
        for kind in args.kinds.split(","):
            if not any(kind in res.get(c, {}) for c in CONDS):
                continue
            lines.append(f"  -- {kind} accuracy")
            lines.extend(depth_table(res, kind, "acc"))
            lines.append(f"  -- {kind} plan parses")
            lines.extend(depth_table(res, kind, "plan_parses"))
            lines.append(f"  -- {kind} exactly the gold plan")
            lines.extend(depth_table(res, kind, "exact_gold_plan"))
        ind = res.get("induction", {})
        if ind:
            lines.append(f"  induction: {json.dumps(ind)}")
        extra = {}
        for cond in ("plan_execute", "oracle_ops"):
            for kind in args.kinds.split(","):
                for d, c in res.get(cond, {}).get(kind, {}).items():
                    if c.get("extra"):
                        extra[f"{cond}/{kind}/{d}"] = c["extra"]
        if extra:
            keys = sorted(extra)[:6]
            lines.append("  representation diagnostics:")
            for k in keys:
                lines.append(f"    {k}: {json.dumps(extra[k])}")
        summary[name] = {
            "oracle_both_all_one": not bad,
            "seq_parse": {d: c["plan_parses"] for d, c in
                          res.get("plan_execute", {}).get("sequential", {}).items()},
            "seq_acc": {d: c["acc"] for d, c in
                        res.get("plan_execute", {}).get("sequential", {}).items()},
        }
    text = "\n".join(lines)
    print(text)
    print("\n===== one line per run =====")
    for name, s in summary.items():
        print(f"{name:22s} oracle_both_ok={s['oracle_both_all_one']} "
              f"seq_parse={json.dumps(s['seq_parse'])}")
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
