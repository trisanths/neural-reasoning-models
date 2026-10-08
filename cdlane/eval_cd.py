"""Score rungs C (opcode) and D (typed) over a depth grid the shared harness does not reach.

This is scripts/vocab_eval.py with three changes, and nothing else:

  1. The depth grid is an argument rather than a module constant, so sequential
     and novel can be pushed past eight. The question generator takes any depth;
     what it cannot do is make every representation able to write the answer.
  2. oracle_ops and oracle_both are run on the paraphrased wording too. The
     shared harness runs them on the original wording only, following the
     original experiment. That leaves plan_execute@para confounded: a rung can
     look worse there because its induction is worse, not because its plan
     representation is worse. oracle_ops@para holds induction fixed at gold and
     moves only the wording, which separates the two.
  3. A cell whose gold plan cannot be written in this representation at all is
     recorded as unrepresentable instead of being scored. The typed form has a
     sixteen register file, so a twenty step plan has no encoding, and a zero
     there is a fact about the register file rather than about the model.

The decoding budget is set per cell from the measured gold length rather than
fixed, and both the budget and the gold length go into the output so the margin
can be audited. A budget that clips one depth and not another would read as
depth costing accuracy.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.ladder_run import (SlotDecoder, TokenGenerator, plan_outputs,
                                    score_cell)
from src.opgraph.run import Generator, induce_worlds, load_model
from src.opgraph.vocab import REPS, REP_OF_ARM, encode_plan
from src.train.tokenizer import load_tokenizer

DEFAULT_DEPTHS = ("sequential=1,2,3,4,5,6,7,8,10,12,14,16,20,24,32;"
                  "novel=2,3,4,5,6,8,12,16,24,32;"
                  "breadth=1,2,3,4,5,6;"
                  "sequential_paren=2,3,4,5,6")


def parse_depths(spec: str) -> dict:
    out = {}
    for part in spec.split(";"):
        part = part.strip()
        if not part:
            continue
        kind, ds = part.split("=", 1)
        out[kind.strip()] = [int(d) for d in ds.split(",") if d.strip()]
    return out


def build_sets(grid: dict, n: int, style: int) -> dict:
    sets = {}
    cache = {}
    for kind, depths in grid.items():
        for depth in depths:
            breadth = depth if kind == "breadth" else 3
            key = (kind, breadth)
            if key not in cache:
                cache[key] = eval_worlds(kind, n, breadth=breadth, style=style)
            sets[(kind, depth)] = [make_item(kind, w, depth, i)
                                   for i, w in enumerate(cache[key])]
    return sets


def gold_budget(rep, items, tok) -> dict:
    """Longest gold plan in this cell, and whether it can be written at all.

    Returns encodable=0 when no item in the cell has an encoding, which is the
    signature of a representational ceiling rather than a model failure.
    """
    longest = 0
    encodable = 0
    err = ""
    for it in items:
        try:
            obj = encode_plan(rep, it.plan, it.world.ops, it)
        except Exception as exc:
            if not err:
                err = f"{type(exc).__name__}: {exc}"[:120]
            continue
        encodable += 1
        text = obj if isinstance(obj, str) else " ".join(obj)
        longest = max(longest, len(tok.encode(" " + text)) + 1)
    return {"gold_longest_tokens": longest, "gold_encodable": encodable,
            "gold_of": len(items), "gold_encode_error": err}


def _tag(name: str, style: int) -> str:
    return name if style == 0 else name + "@para"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--rep", default=None, choices=list(REPS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--slot-batch-size", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--depths", default=DEFAULT_DEPTHS)
    ap.add_argument("--styles", default="0,1")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--min-max-new", type=int, default=320,
                    help="floor for the decoding budget, matching the ladder")
    ap.add_argument("--budget-slack", type=float, default=1.6,
                    help="budget is this multiple of the longest gold plan")
    ap.add_argument("--conditions",
                    default="plan_execute,oracle_plan,oracle_ops,oracle_both")
    ap.add_argument("--para-oracles", type=int, default=1,
                    help="1 runs oracle_ops and oracle_both on the paraphrase too")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, state = load_model(args.ckpt, device)
    rep = args.rep or REP_OF_ARM.get(state.get("arm", ""), None)
    if rep is None:
        raise SystemExit("cannot tell which representation this checkpoint is; "
                         "pass --rep")
    grid = parse_depths(args.depths)
    styles = [int(s) for s in args.styles.split(",")]
    want = args.conditions.split(",")
    sets = {st: build_sets(grid, args.n, st) for st in styles}

    results: dict = {"config": vars(args), "rep": rep,
                     "checkpoint": {k: state.get(k) for k in
                                    ("arm", "rep", "step", "tokens",
                                     "supervised_tokens", "examples",
                                     "reinit_tokens", "rounds")},
                     "budget": {}, "unrepresentable": []}

    ind_gen = Generator(model, tok, device, batch_size=args.batch_size)
    # One sampling stream for the whole run, as the shared harness does, so a
    # sampled number here is comparable with a sampled number from the other
    # rungs. The budget is a call argument, not a constructor argument, so it
    # can still vary per cell without disturbing the stream.
    gen = TokenGenerator(model, tok, device, batch_size=args.batch_size,
                         temperature=args.temperature, seed=0)
    slot_dec = SlotDecoder(model, tok, device, batch_size=args.slot_batch_size,
                           rounds=args.rounds)

    conds = (("plan_execute", False, False),
             ("oracle_plan", True, False),
             ("oracle_ops", False, True),
             ("oracle_both", True, True))

    for st in styles:
        worlds = {it.world.seed: it.world
                  for items in sets[st].values() for it in items}
        induced = induce_worlds(ind_gen, worlds, progress=1)
        stats = Counter()
        for ind in induced.values():
            stats["pages"] += ind.pages
            stats["pages_parsed"] += ind.parsed
            stats["gold_ops"] += ind.gold_count
            stats["induced_ops"] += len(ind.ops)
            stats["self_verified"] += ind.self_verified
            stats["exact_text"] += ind.exact
            stats["behavioural"] += ind.behavioural
        results[_tag("induction", st)] = dict(stats)
        print(f"[induction style={st}] {json.dumps(dict(stats))}", flush=True)

        for key, items in sorted(sets[st].items()):
            kind, depth = key
            bud = gold_budget(rep, items, tok)
            max_new = max(args.min_max_new,
                          int(args.budget_slack * bud["gold_longest_tokens"]) + 64)
            bud["max_new"] = max_new
            results["budget"][f"{kind}/{depth}/style{st}"] = bud
            if bud["gold_encodable"] == 0:
                results["unrepresentable"].append(
                    {"kind": kind, "depth": depth, "style": st,
                     "reason": bud["gold_encode_error"]})
                print(f"[skip] {kind} d={depth} style={st} has no encoding in "
                      f"{rep}: {bud['gold_encode_error']}", flush=True)
                continue
            for name, gold_plan, gold_ops in conds:
                if name not in want:
                    continue
                if st != 0 and name in ("oracle_ops", "oracle_both") \
                        and not args.para_oracles:
                    continue
                written, side = (None, None)
                if not gold_plan:
                    written, side = plan_outputs(rep, gen, slot_dec, items,
                                                 induced, gold_ops,
                                                 max_new=max_new)
                cell = score_cell(rep, items, written, induced,
                                  use_gold_plan=gold_plan,
                                  use_gold_ops=gold_ops, side=side)
                d = cell.as_dict()
                d["max_new"] = max_new
                d["gold_longest_tokens"] = bud["gold_longest_tokens"]
                d["gold_encodable"] = bud["gold_encodable"]
                results.setdefault(_tag(name, st), {}).setdefault(
                    kind, {})[str(depth)] = d
                print(f"[{_tag(name, st)}] {kind} d={depth} "
                      f"acc={cell.correct / max(1, cell.n):.3f} "
                      f"parse={cell.parsed / max(1, cell.n):.3f} "
                      f"typed={cell.typed / max(1, cell.n):.3f} "
                      f"exact={cell.exact / max(1, cell.n):.3f} "
                      f"n={cell.n} budget={max_new}", flush=True)
            with open(args.out, "w") as fh:
                json.dump(results, fh, indent=1)

    bad = []
    for tag in ("oracle_both", "oracle_both@para"):
        for k, cells in results.get(tag, {}).items():
            for d, c in cells.items():
                if c["acc"] < 1.0:
                    bad.append((tag, k, d, c["acc"]))
    results["oracle_both_all_one"] = not bad
    results["oracle_both_failures"] = bad
    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"[written] {args.out}")
    if bad:
        print(f"[STOP] oracle_both is not 1.000 in {len(bad)} cells: {bad[:6]}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
