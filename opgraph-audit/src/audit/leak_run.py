"""Audit checks 5 and 6: plan leakage and executor independence.

GPU stage. Everything this writes is raw enough that every later analysis is a
pure CPU pass over the dump.

What it does:
  1. builds the sequential eval sets exactly as scripts/opgraph_eval.py does
  2. induces operators from pages with the shipped opgraph checkpoint
  3. runs oracle_plan through the REAL executor with a recording proxy in front
     of the operator table, so every call the executor makes is logged with the
     identity of the operator object it invoked
  4. dumps induced and gold operator text per world, and every model plan, so
     the counterfactuals can run on CPU
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter

import torch

import src.opgraph.run as R
from src.opgraph.data import eval_worlds, make_item
from src.opgraph.opdef import serialize
from src.opgraph.plan import run_plan as REAL_RUN_PLAN
from src.opgraph.plan import serialize_plan
from src.opgraph.run import (Generator, induce_worlds, load_model,
                             score_planned)
from src.train.tokenizer import load_tokenizer

GRID = {"sequential": [1, 2, 3, 4, 5, 6, 7, 8], "breadth": [1, 2, 3, 4, 5, 6],
        "novel": [2, 3, 4, 5, 6], "sequential_paren": [2, 3, 4, 5, 6],
        "same_page_pair": [2], "units": [1]}

CALLS: list = []          # every operator invocation the executor made
CURRENT: dict = {}        # set by the driver before each score_planned call


class _Proxy:
    """Stands in front of one Operator and records what the executor did."""

    __slots__ = ("op", "symbol")

    def __init__(self, op):
        self.op = op
        self.symbol = op.symbol

    def __call__(self, *args):
        v = self.op(*args)
        CALLS.append({
            "cond": CURRENT.get("cond"),
            "depth": CURRENT.get("depth"),
            "symbol": self.symbol,
            "op_id": id(self.op),
            "args": [x if not isinstance(x, bool) else bool(x) for x in args],
            "value": v if not isinstance(v, bool) else bool(v),
        })
        return v


class _RecTable(dict):
    """The operator table as the executor sees it, with a proxy on every get."""

    def get(self, k, default=None):
        o = dict.get(self, k, None)
        if o is None:
            CALLS.append({"cond": CURRENT.get("cond"),
                          "depth": CURRENT.get("depth"),
                          "symbol": k, "op_id": None, "missing": True})
            return default
        return _Proxy(o)


def _run_plan_recording(plan, ops):
    """The real executor, fed a table that logs every lookup and every call."""
    CALLS.append({"marker": True,
                  "cond": CURRENT.get("cond"),
                  "depth": CURRENT.get("depth"),
                  "n_steps": len(plan.steps),
                  "answer": plan.answer,
                  "table_ids": {k: id(v) for k, v in ops.items()}})
    return REAL_RUN_PLAN(plan, _RecTable(ops))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="runs/opgraph.pt")
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--out", default="results/audit_leak_raw.json")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--style", type=int, default=0)
    ap.add_argument("--kind", default="sequential")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    kind = args.kind
    depths = GRID[kind]
    worlds_by_seed = {}
    sets = {}
    cache = {}
    for d in depths:
        b = d if kind == "breadth" else 3
        if b not in cache:
            cache[b] = eval_worlds(kind, args.n, breadth=b, style=args.style)
        ws = cache[b]
        for w in ws:
            worlds_by_seed[w.seed] = w
        sets[d] = [make_item(kind, w, d, i) for i, w in enumerate(ws)]

    model, _ = load_model(args.ckpt, device)
    gen = Generator(model, tok, device, batch_size=args.batch_size)
    induced = induce_worlds(gen, worlds_by_seed, progress=1)

    dump = {"config": vars(args), "worlds": {}, "items": {}, "calls": [],
            "induction": {}}

    stats = Counter()
    for seed, ind in induced.items():
        w = worlds_by_seed[seed]
        gold = w.ops
        stats["pages"] += ind.pages
        stats["pages_parsed"] += ind.parsed
        stats["gold_ops"] += ind.gold_count
        stats["induced_ops"] += len(ind.ops)
        stats["exact_text"] += ind.exact
        stats["behavioural"] += ind.behavioural
        dump["worlds"][str(seed)] = {
            "gold": {k: serialize(v) for k, v in gold.items()},
            "gold_ids": {k: id(v) for k, v in gold.items()},
            "induced": {k: serialize(v) for k, v in ind.ops.items()},
            "induced_ids": {k: id(v) for k, v in ind.ops.items()},
            "order": list(w.order),
            "page_keys": [p.key for p in w.pages],
            "page_lens": [len(p.text) for p in w.pages],
            "shuffled_keys": [p.key for p in w.shuffled_pages()],
        }
    dump["induction"] = dict(stats)
    print("[induction]", json.dumps(dict(stats)), flush=True)

    # ---- the instrumented conditions ------------------------------------
    R.run_plan = _run_plan_recording

    # every prompt the model is shown, tagged by the condition that showed it
    PROMPTS: list = []
    _real_generate = gen.generate

    def _rec_generate(prompts, max_new=96):
        PROMPTS.append({"cond": CURRENT.get("cond"), "depth": CURRENT.get("depth"),
                        "n": len(prompts), "max_new": max_new,
                        "sample": prompts[:2]})
        return _real_generate(prompts, max_new=max_new)

    gen.generate = _rec_generate
    dump["prompts"] = PROMPTS

    conds = (("plan_execute", False, False),
             ("oracle_plan", True, False),
             ("oracle_ops", False, True),
             ("oracle_both", True, True))

    for d in depths:
        items = sets[d]
        rec = {"gold_plans": [serialize_plan(it.plan) for it in items],
               "gold": [it.gold for it in items],
               "texts": [it.text for it in items],
               "seeds": [it.world.seed for it in items],
               "symbols": [it.symbols for it in items],
               "assoc": [it.world.ops[it.symbols[0]].assoc for it in items],
               "arity": [it.world.ops[it.symbols[0]].arity for it in items],
               "conds": {}}
        for name, gp, go in conds:
            CURRENT["cond"], CURRENT["depth"] = name, d
            before = len(CALLS)
            ok, texts, reasons = score_planned(gen, items, induced,
                                               use_gold_plan=gp,
                                               use_gold_ops=go)
            after = len(CALLS)
            rec["conds"][name] = {
                "acc": round(sum(ok) / len(ok), 4),
                "ok": [bool(x) for x in ok],
                "plans": texts,
                "reasons": reasons,
                "n_calls": after - before,
            }
            print(f"[{name}] d={d} acc={sum(ok)/len(ok):.3f} "
                  f"calls={after - before}", flush=True)
        dump["items"][str(d)] = rec
        with open(args.out, "w") as fh:
            json.dump(dump, fh)

    dump["calls"] = CALLS
    with open(args.out, "w") as fh:
        json.dump(dump, fh)
    print("[written]", args.out, len(CALLS), "calls", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
