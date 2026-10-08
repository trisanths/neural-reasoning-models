"""Prove the plan parser and executor handle every length this lane trains on.

The cap in `src.opgraph.plan` was 32. A plan longer than that raised
`plan too long`, which every scorer here records as a parse failure. A depth
curve built on top of that would be a parse-rate curve wearing a depth curve's
clothes, so the cap is raised first and the raise is checked rather than
assumed.

For each length the check builds a real evaluation item at that depth, from the
same generators the sweep trains and scores with, then:

  serialize -> parse -> execute -> compare the executed value to the item's gold

It also re-runs the parse under the old cap, so the record shows which lengths
the old cap actually rejected rather than asserting it, and it measures the
tokenized length of the longest prompt-plus-plan at each depth, which is what
decides the training `--max-len` and the decode budget.
"""

from __future__ import annotations

import argparse
import json
import sys

from src.opgraph import plan as planmod
from src.opgraph.data import eval_worlds, make_item, plan_prompt
from src.opgraph.opdef import OpError
from src.opgraph.plan import (PlanError, answer_text, parse_plan, run_plan,
                              serialize_plan)


def norm(s) -> str:
    return str(s).strip().strip(".").strip().lower()


def check_depth(kind: str, depth: int, n: int, tok=None) -> dict:
    worlds = eval_worlds(kind, n, breadth=3, style=0)
    items = [make_item(kind, w, depth, i) for i, w in enumerate(worlds)]
    rec = {"kind": kind, "depth": depth, "n": n}
    gold_steps = set()
    parsed = executed = matched = 0
    round_trip = 0
    errs: list[str] = []
    tok_lens: list[int] = []
    for it in items:
        gold_steps.add(len(it.plan.steps))
        text = serialize_plan(it.plan)
        if tok is not None:
            tok_lens.append(len(tok.encode(plan_prompt(it.world.ops, it.text)))
                            + len(tok.encode(text)))
        try:
            p = parse_plan(text)
        except PlanError as exc:
            errs.append(f"parse:{exc}")
            continue
        parsed += 1
        round_trip += int(serialize_plan(p) == text)
        try:
            v = run_plan(p, it.world.ops)
        except (PlanError, OpError) as exc:
            errs.append(f"exec:{exc}")
            continue
        executed += 1
        matched += int(norm(answer_text(v)) == norm(it.gold))
    rec.update({
        "gold_steps": sorted(gold_steps),
        "parse_ok": parsed, "round_trip": round_trip,
        "exec_ok": executed, "value_matches_gold": matched,
        "all_ok": parsed == executed == matched == round_trip == n,
        "errors": errs[:3],
    })
    if tok_lens:
        rec["tokens_max"] = max(tok_lens)
        rec["tokens_mean"] = round(sum(tok_lens) / len(tok_lens), 1)
    return rec


def under_cap(cap: int, kind: str, depth: int, n: int) -> dict:
    """How many items of this depth the given parser cap accepts."""
    old = planmod.MAX_STEPS
    planmod.MAX_STEPS = cap
    try:
        worlds = eval_worlds(kind, n, breadth=3, style=0)
        ok = 0
        msg = ""
        for i, w in enumerate(worlds):
            it = make_item(kind, w, depth, i)
            try:
                parse_plan(serialize_plan(it.plan))
                ok += 1
            except PlanError as exc:
                msg = str(exc)
        return {"cap": cap, "depth": depth, "parsed": ok, "n": n, "error": msg}
    finally:
        planmod.MAX_STEPS = old


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--max", type=int, default=64)
    ap.add_argument("--tokenizer", default="")
    args = ap.parse_args()

    tok = None
    if args.tokenizer:
        from src.train.tokenizer import load_tokenizer
        tok = load_tokenizer(args.tokenizer)

    out = {"max_steps": planmod.MAX_STEPS, "checks": [], "old_cap": []}
    depths = list(range(1, args.max + 1))
    bad = []
    for d in depths:
        for kind in ("sequential", "sequential_paren"):
            if kind == "sequential_paren" and d < 2:
                continue
            r = check_depth(kind, d, args.n, tok)
            out["checks"].append(r)
            if not r["all_ok"]:
                bad.append(f"{kind}@{d}")
    for d in (32, 33, 40, 48, 64):
        out["old_cap"].append(under_cap(32, "sequential", d, args.n))

    out["all_ok"] = not bad
    out["failed"] = bad
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)

    seq = [c for c in out["checks"] if c["kind"] == "sequential"]
    print(json.dumps({
        "max_steps": out["max_steps"],
        "depths_checked": f"{depths[0]}..{depths[-1]}",
        "items_per_cell": args.n,
        "all_ok": out["all_ok"],
        "failed": bad,
        "tokens_max_at_max_depth": seq[-1].get("tokens_max"),
        "old_cap_32": {str(r["depth"]): f"{r['parsed']}/{r['n']}"
                       for r in out["old_cap"]},
        "written": args.out,
    }, indent=1))
    return 0 if out["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
