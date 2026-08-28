"""Check the six plan representations before any GPU time is spent on them.

Four things are checked, over the whole evaluation grid rather than a handful
of hand written cases.

  round trip     the gold plan, written in the representation and read back, is
                 the same plan and executes to the same answer. This is what
                 oracle_both measures at eval time, so a failure here is a
                 broken harness and it should surface on a laptop, not after
                 eight hours of training
  obligations    the goal stack's obligations, replayed against the gold plan,
                 all close. An obligation the gold plan cannot discharge would
                 be unsatisfiable, and the decoder would grind against its step
                 cap instead of terminating
  typing         the gold plan is well typed under the inferred operator
                 signatures, for every kind and depth
  tokens         every reserved token this ladder uses survives an encode and
                 decode as one token
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.plan import answer_text, run_plan
from src.opgraph.vocab import (F_WIDTH, MAX_LIT, Obligations, REPS, RepError,
                               canonical, decode_plan, encode_plan,
                               rep_plan_prompt, rep_tokens, required_applications,
                               slot_fields, well_typed)

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 7, 8],
    "breadth": [1, 2, 3, 4, 5, 6],
    "novel": [2, 3, 4, 5, 6],
    "sequential_paren": [2, 3, 4, 5, 6],
    "same_page_pair": [2],
    "units": [1],
}


def grid_items(n: int, style: int):
    cache = {}
    for kind, depths in GRID.items():
        for depth in depths:
            breadth = depth if kind == "breadth" else 3
            key = (kind, breadth)
            if key not in cache:
                cache[key] = eval_worlds(kind, n, breadth=breadth, style=style)
            yield kind, depth, [make_item(kind, w, depth, i)
                                for i, w in enumerate(cache[key])]


def check_roundtrip(n: int, style: int) -> dict:
    out: dict = {}
    for kind, depth, items in grid_items(n, style):
        for rep in REPS:
            c = Counter()
            for it in items:
                c["n"] += 1
                try:
                    written = encode_plan(rep, it.plan, it.world.ops, it)
                except RepError as exc:
                    c["encode_failed"] += 1
                    c["why:" + str(exc)[:50]] += 1
                    continue
                try:
                    back = decode_plan(rep, written, it.world.ops)
                except Exception as exc:  # noqa: BLE001 - the point is to catch all
                    c["decode_failed"] += 1
                    c["why:" + type(exc).__name__ + ":" + str(exc)[:50]] += 1
                    continue
                if canonical(back) != canonical(it.plan):
                    c["plan_differs"] += 1
                    continue
                try:
                    v = run_plan(back, it.world.ops)
                except Exception as exc:  # noqa: BLE001
                    c["execute_failed"] += 1
                    c["why:" + str(exc)[:50]] += 1
                    continue
                if str(answer_text(v)).strip() != str(it.gold).strip():
                    c["wrong_answer"] += 1
                    continue
                c["ok"] += 1
            out.setdefault(rep, {})[f"{kind}/{depth}"] = dict(c)
    return out


def check_obligations(n: int, style: int) -> dict:
    """Replay each gold plan through the obligation state and see it close."""
    out: dict = {}
    for kind, depth, items in grid_items(n, style):
        c = Counter()
        for it in items:
            ops = it.world.ops
            ob = Obligations.for_item(it, ops)
            c["n"] += 1
            req = required_applications(it.text, ops)
            if req > len(it.plan.steps):
                c["required_over_gold"] += 1
            regs = {s.target: i for i, s in enumerate(it.plan.steps)}
            for i, s in enumerate(it.plan.steps):
                args = []
                for a in s.args:
                    if isinstance(a, str) and a in regs:
                        args.append(("reg", regs[a]))
                    else:
                        args.append(("val", a))
                ob.apply_step(i, args)
            if ob.resolved():
                c["resolved"] += 1
            else:
                c["unresolved"] += 1
                for g in ob.open_goals():
                    c["open:" + g.split()[0]] += 1
        out[f"{kind}/{depth}"] = dict(c)
    return out


def check_typing(n: int, style: int) -> dict:
    out: dict = {}
    for kind, depth, items in grid_items(n, style):
        c = Counter()
        for it in items:
            c["n"] += 1
            c["well_typed"] += int(well_typed(it.plan, it.world.ops))
        out[f"{kind}/{depth}"] = dict(c)
    return out


def check_tokens(tokenizer: str) -> dict:
    from src.train.tokenizer import load_tokenizer
    tok = load_tokenizer(tokenizer)
    names = sorted({t for rep in REPS for t in rep_tokens(rep)})
    bad = []
    for t in names:
        ids = tok.encode(t)
        if len(ids) != 1 or tok.decode(ids) != t:
            bad.append({"token": t, "ids": ids, "back": tok.decode(ids)})
    joined = "".join(names[:8])
    return {"tokens": len(names), "not_single_token": bad,
            "adjacent_roundtrip": tok.decode(tok.encode(joined)) == joined}


def check_lengths(tokenizer: str, n: int) -> dict:
    """Prompt and target token lengths per representation, so max_len is chosen
    with the numbers in front of it rather than by hope."""
    from src.train.tokenizer import load_tokenizer
    from src.opgraph.vocab import ROW_LEN
    tok = load_tokenizer(tokenizer)
    out: dict = {}
    for kind, depth, items in grid_items(n, 0):
        for rep in REPS:
            worst = out.setdefault(rep, {"prompt": 0, "target": 0, "total": 0})
            for it in items[:8]:
                p = len(tok.encode(rep_plan_prompt(rep, it.world.ops, it.text)))
                if rep == "slots":
                    t = 3 * ROW_LEN
                else:
                    t = len(tok.encode(" " + encode_plan(rep, it.plan,
                                                         it.world.ops, it)))
                worst["prompt"] = max(worst["prompt"], p)
                worst["target"] = max(worst["target"], t)
                worst["total"] = max(worst["total"], p + t)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--tokenizer", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--styles", default="0,1")
    args = ap.parse_args()

    report: dict = {}
    fails: list[str] = []
    for style in [int(s) for s in args.styles.split(",")]:
        rt = check_roundtrip(args.n, style)
        report[f"roundtrip_style{style}"] = rt
        for rep, cells in rt.items():
            for cell, c in cells.items():
                if c.get("ok", 0) != c["n"]:
                    fails.append(f"roundtrip {rep} {cell} style={style} {c}")
        ob = check_obligations(args.n, style)
        report[f"obligations_style{style}"] = ob
        for cell, c in ob.items():
            if c.get("resolved", 0) != c["n"]:
                fails.append(f"obligations {cell} style={style} {c}")
            if c.get("required_over_gold"):
                fails.append(f"required over gold {cell} style={style} {c}")
        ty = check_typing(args.n, style)
        report[f"typing_style{style}"] = ty
        for cell, c in ty.items():
            if c.get("well_typed", 0) != c["n"]:
                fails.append(f"typing {cell} style={style} {c}")

    if args.tokenizer:
        tk = check_tokens(args.tokenizer)
        report["tokens"] = tk
        if tk["not_single_token"] or not tk["adjacent_roundtrip"]:
            fails.append(f"tokens {tk}")
        report["lengths"] = check_lengths(args.tokenizer, args.n)

    report["failures"] = fails
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(report, fh, indent=1)
    print(json.dumps({k: v for k, v in report.items()
                      if k in ("tokens", "lengths")}, indent=1))
    print(f"[selftest] failures={len(fails)}")
    for f in fails[:20]:
        print("  " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
