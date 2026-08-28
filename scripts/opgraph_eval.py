"""The depth curve for every condition, on worlds no arm was trained on.

Three kinds of composition are kept apart throughout, because they may have
different scaling laws and pooling them would hide that:

  sequential   one operator chained d times, written flat, associativity stated
  breadth      one procedure integrating b simultaneous conditions
  novel        a parenthesised expression that needs both operators, each of
               which was defined on its own page and shown only alone

Two further sets are reported but are not headline numbers: sequential_paren,
the notation the plan arm saw in training at depth two and three, and
same_page_pair, two operators taken from a single page.

Conditions, in the order they localise the failure:

  base_untrained_direct  the pretrained checkpoint, no fine tuning
  direct_all             fine tuned to answer, all four pages in context
  direct_oracle_page     fine tuned to answer, only the pages it needs
  trace_all              fine tuned to write the same decomposition out in
                         tokens and compute every step itself
  trace_oracle_page      the same, only the pages it needs
  plan_execute           induce, plan, execute
  oracle_plan            gold plan, induced operators, execute
  oracle_ops             gold operators, model plan, execute
  oracle_both            execution alone, which must come out at 1.000

Everything is run twice: once on the page wording every arm trained on, and
once on the same worlds with every page rewritten in different prose. The
paraphrase pass is what separates reading a page from matching a template.
Condition names from that pass carry a "@para" suffix.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.run import (Generator, induce_worlds, load_model, score_direct,
                             score_planned, score_trace)
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
    """(kind, depth) -> items, with worlds shared across the depths of a kind."""
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
    ap.add_argument("--direct-ckpt", required=True)
    ap.add_argument("--opgraph-ckpt", required=True)
    ap.add_argument("--trace-ckpt", default=None)
    ap.add_argument("--base-ckpt", default=None)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--kinds", default=",".join(GRID))
    ap.add_argument("--styles", default="0,1")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    kinds = args.kinds.split(",")
    styles = [int(s) for s in args.styles.split(",")]
    sets = {st: build_sets(kinds, args.n, st) for st in styles}
    results: dict = {"config": vars(args)}

    def tag(name, style):
        return name if style == 0 else name + "@para"

    direct, _ = load_model(args.direct_ckpt, device)
    gen = Generator(direct, tok, device, batch_size=args.batch_size)
    for st in styles:
        for key, items in sets[st].items():
            for name, oracle in (("direct_all", False),
                                 ("direct_oracle_page", True)):
                ok, outs = score_direct(gen, items, oracle)
                _record(results, tag(name, st), key, ok, samples=outs[:3])
    del direct, gen
    torch.cuda.empty_cache()

    if args.trace_ckpt:
        tr, _ = load_model(args.trace_ckpt, device)
        gt = Generator(tr, tok, device, batch_size=args.batch_size)
        for st in styles:
            for key, items in sets[st].items():
                for name, oracle in (("trace_all", False),
                                     ("trace_oracle_page", True)):
                    ok, outs = score_trace(gt, items, oracle)
                    _record(results, tag(name, st), key, ok, samples=outs[:3])
        del tr, gt
        torch.cuda.empty_cache()

    if args.base_ckpt:
        base, _ = load_model(args.base_ckpt, device)
        gb = Generator(base, tok, device, batch_size=args.batch_size)
        for key, items in sets[styles[0]].items():
            ok, outs = score_direct(gb, items, False)
            _record(results, "base_untrained_direct", key, ok, samples=outs[:3])
        del base, gb
        torch.cuda.empty_cache()

    opg, _ = load_model(args.opgraph_ckpt, device)
    gen = Generator(opg, tok, device, batch_size=args.batch_size)

    conds = (("plan_execute", False, False),
             ("oracle_plan", True, False),
             ("oracle_ops", False, True),
             ("oracle_both", True, True))
    for st in styles:
        worlds = {it.world.seed: it.world
                  for items in sets[st].values() for it in items}
        induced = induce_worlds(gen, worlds, progress=1)
        ind_stats = Counter()
        for ind in induced.values():
            ind_stats["pages"] += ind.pages
            ind_stats["pages_parsed"] += ind.parsed
            ind_stats["gold_ops"] += ind.gold_count
            ind_stats["induced_ops"] += len(ind.ops)
            ind_stats["self_verified"] += ind.self_verified
            ind_stats["exact_text"] += ind.exact
            ind_stats["behavioural"] += ind.behavioural
        results[tag("induction", st)] = dict(ind_stats)
        print(f"[induction style={st}]", json.dumps(dict(ind_stats)), flush=True)
        for key, items in sets[st].items():
            for name, gold_plan, gold_ops in conds:
                if st != 0 and name in ("oracle_ops", "oracle_both"):
                    continue  # gold operators do not depend on the wording
                ok, texts, reasons = score_planned(gen, items, induced,
                                                   use_gold_plan=gold_plan,
                                                   use_gold_ops=gold_ops)
                _record(results, tag(name, st), key, ok, samples=texts[:3],
                        reasons=dict(Counter(reasons)))
        with open(args.out, "w") as fh:
            json.dump(results, fh, indent=1)

    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)
    _summary(results, kinds)
    print(f"[written] {args.out}", flush=True)
    return 0


def _record(results, name, key, ok, samples=None, reasons=None):
    kind, depth = key
    slot = results.setdefault(name, {}).setdefault(kind, {})
    slot[str(depth)] = {"n": len(ok), "acc": round(sum(ok) / len(ok), 4)}
    if reasons:
        slot[str(depth)]["reasons"] = reasons
    if samples:
        slot[str(depth)]["samples"] = samples
    print(f"[{name}] {kind} d={depth} acc={sum(ok) / len(ok):.3f}", flush=True)


def _summary(results, kinds):
    print("\n=== accuracy by condition, kind and depth ===")
    for name in results:
        if name.startswith("induction") or name == "config":
            continue
        for kind in kinds:
            row = results[name].get(kind, {})
            if not row:
                continue
            cells = " ".join(f"{d}:{row[d]['acc']:.3f}" for d in sorted(row, key=int))
            print(f"{name:26s} {kind:18s} {cells}")


if __name__ == "__main__":
    raise SystemExit(main())
