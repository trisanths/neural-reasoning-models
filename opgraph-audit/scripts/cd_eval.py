"""Score rungs C and D over a depth grid that is chosen rather than fixed.

`scripts/vocab_eval.py` hard-codes sequential depth one to eight. Eight points
do not separate a flat curve from a slowly decaying one, so the grid here is an
argument. Everything else is the shared harness: the same worlds, the same
items, the same `plan_outputs` and `score_cell`, the same four conditions.

Two additions over the shared script, both of which cost decoding time and are
therefore switches rather than defaults.

`oracle_ops` is normally scored on the original page wording only, following the
original experiment. Induction quality differs across rungs on the paraphrase,
so a difference in `plan_execute@para` between two rungs is partly an induction
difference and partly a plan difference, and the original pairing cannot tell
them apart. `--para-conditions` runs the gold-operator conditions on the
paraphrase as well, which separates the two.

`oracle_both@para` costs no decoding at all, since both the plan and the
operators are gold, and gives a second harness check on the wording the harness
was not originally run against.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.ladder_run import (SlotDecoder, TokenGenerator, plan_outputs,
                                    score_cell)
from src.opgraph.run import Generator, induce_worlds, load_model
from src.opgraph.vocab import REPS, REP_OF_ARM
from src.train.tokenizer import load_tokenizer

DEFAULT_DEPTHS = ("sequential=1,2,3,4,5,6,7,8;breadth=1,2,3,4,5,6;"
                  "novel=2,3,4,5,6;sequential_paren=2,3,4,5,6;"
                  "same_page_pair=2;units=1")


def parse_depths(spec: str) -> dict:
    grid = {}
    for part in spec.split(";"):
        part = part.strip()
        if not part:
            continue
        kind, _, ds = part.partition("=")
        grid[kind.strip()] = [int(d) for d in ds.split(",") if d.strip()]
    return grid


def build_sets(grid, n, style):
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
    ap.add_argument("--max-new", type=int, default=320)
    ap.add_argument("--conditions",
                    default="plan_execute,oracle_plan,oracle_ops,oracle_both")
    ap.add_argument("--para-conditions",
                    default="plan_execute,oracle_plan",
                    help="which conditions to run on the paraphrased wording")
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
    want = set(args.conditions.split(","))
    want_para = set(c for c in args.para_conditions.split(",") if c)
    sets = {st: build_sets(grid, args.n, st) for st in styles}

    results: dict = {"config": vars(args), "rep": rep,
                     "grid": grid,
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

    t0 = time.time()
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

        for key, items in sorted(sets[st].items(), key=lambda kv: kv[0]):
            for name, gold_plan, gold_ops in conds:
                if name not in want:
                    continue
                if st != 0 and name not in want_para:
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
                      f"exact={cell.exact / max(1, cell.n):.3f} "
                      f"n={cell.n} [{time.time() - t0:.0f}s]", flush=True)
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
    results["wall_seconds"] = round(time.time() - t0, 1)
    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"[written] {args.out}")
    if bad:
        print(f"[STOP] oracle_both is not 1.000 in {len(bad)} cells: {bad[:8]}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
