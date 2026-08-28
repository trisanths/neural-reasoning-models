"""Score one rung of the plan-representation ladder.

The four conditions are the ones the original experiment used, so a rung is
directly comparable to the plan_execute and oracle_plan numbers it is measured
against.

  plan_execute  the model induces every operator and writes the plan
  oracle_plan   the gold plan, written in this representation and read back,
                with the model's own induced operators
  oracle_ops    the model writes the plan over gold operators
  oracle_both   gold plan and gold operators, which must come out at 1.000 or
                the representation is lossy and every other number here is
                meaningless

Both page wordings are run. Gold operators do not depend on the wording, so
oracle_ops and oracle_both are scored on the original wording only, exactly as
the original harness did.

Greedy and sampled decoding are both available and both should be reported: on
this project a greedy decode has produced false zeros where the behaviour was
present but not the argmax.
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
from src.opgraph.vocab import REPS, REP_OF_ARM
from src.train.tokenizer import load_tokenizer

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 7, 8],
    "breadth": [1, 2, 3, 4, 5, 6],
    "novel": [2, 3, 4, 5, 6],
    "sequential_paren": [2, 3, 4, 5, 6],
    "same_page_pair": [2],
    "units": [1],
}


def build_sets(kinds, n, style):
    sets = {}
    cache = {}
    for kind in kinds:
        for depth in GRID[kind]:
            breadth = depth if kind == "breadth" else 3
            key = (kind, breadth)
            if key not in cache:
                cache[key] = eval_worlds(kind, n, breadth=breadth, style=style)
            sets[(kind, depth)] = [make_item(kind, w, depth, i)
                                   for i, w in enumerate(cache[key])]
    return sets


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
    ap.add_argument("--kinds", default=",".join(GRID))
    ap.add_argument("--styles", default="0,1")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-new", type=int, default=192)
    ap.add_argument("--conditions",
                    default="plan_execute,oracle_plan,oracle_ops,oracle_both")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, state = load_model(args.ckpt, device)
    rep = args.rep or REP_OF_ARM.get(state.get("arm", ""), None)
    if rep is None:
        raise SystemExit("cannot tell which representation this checkpoint is; "
                         "pass --rep")
    kinds = args.kinds.split(",")
    styles = [int(s) for s in args.styles.split(",")]
    want = args.conditions.split(",")
    sets = {st: build_sets(kinds, args.n, st) for st in styles}

    results: dict = {"config": vars(args), "rep": rep,
                     "checkpoint": {k: state.get(k) for k in
                                    ("arm", "rep", "step", "tokens",
                                     "supervised_tokens", "examples",
                                     "reinit_tokens", "rounds")}}

    ind_gen = Generator(model, tok, device, batch_size=args.batch_size)
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

        for key, items in sets[st].items():
            for name, gold_plan, gold_ops in conds:
                if name not in want:
                    continue
                if st != 0 and name in ("oracle_ops", "oracle_both"):
                    continue
                written, side = (None, None)
                if not gold_plan:
                    written, side = plan_outputs(rep, gen, slot_dec, items,
                                                 induced, gold_ops,
                                                 max_new=args.max_new)
                cell = score_cell(rep, items, written, induced,
                                  use_gold_plan=gold_plan,
                                  use_gold_ops=gold_ops, side=side)
                results.setdefault(_tag(name, st), {}).setdefault(
                    key[0], {})[str(key[1])] = cell.as_dict()
                print(f"[{_tag(name, st)}] {key[0]} d={key[1]} "
                      f"acc={cell.correct / max(1, cell.n):.3f} "
                      f"parse={cell.parsed / max(1, cell.n):.3f} "
                      f"typed={cell.typed / max(1, cell.n):.3f} "
                      f"exact={cell.exact / max(1, cell.n):.3f}", flush=True)
            with open(args.out, "w") as fh:
                json.dump(results, fh, indent=1)

    ob = results.get("oracle_both", {})
    bad = [(k, d, c["acc"]) for k, cells in ob.items()
           for d, c in cells.items() if c["acc"] < 1.0]
    results["oracle_both_all_one"] = not bad
    results["oracle_both_failures"] = bad
    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"[written] {args.out}")
    if bad:
        print(f"[STOP] oracle_both is not 1.000 in {len(bad)} cells: {bad[:6]}")
        return 2
    return 0


def _tag(name: str, style: int) -> str:
    return name if style == 0 else name + "@para"


if __name__ == "__main__":
    raise SystemExit(main())
