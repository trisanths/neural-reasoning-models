"""Plan length census at sequential depths 4 to 8, for both plan-writing arms.

The audit's reading of the flat tail is that the scheduler carries a hard length
prior at three steps, inherited from a training set that never shows a longer
plan. `runs/opgraph_step.pt` is the repair for exactly that: the same model asked
for one step at a time, so plan length is never a quantity the decoder has to
emit. If the prior lives in the decoding scheme, the stepwise arm writes plans of
the length the question needs. If it lives in the learned content, it does not.

Counts the steps in every emitted plan, 150 items per cell, and records how many
plans have the length the question requires (depth d needs d steps).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.expanduser("~/opg"))

import torch  # noqa: E402,F401

from src.opgraph.data import eval_worlds, make_item, plan_prompt  # noqa: E402
from src.opgraph.plan import PlanError, parse_plan  # noqa: E402
from src.opgraph.run import (Generator, induce_worlds, load_model,  # noqa: E402
                             stepwise_plans)
from src.train.tokenizer import load_tokenizer  # noqa: E402

DEPTHS = [4, 5, 6, 7, 8]


def nsteps(text: str):
    """Steps in a plan, by the strict parser, falling back to chunk counting."""
    try:
        return len(parse_plan(text).steps), True
    except PlanError:
        chunks = [c for c in text.split(";") if c.strip()]
        return max(len(chunks) - 1, 0), False


def census(gen, worlds, items_by_depth, ind, stepwise):
    out = {}
    for d, items in items_by_depth.items():
        if stepwise:
            plans = stepwise_plans(gen, items, ind, False)
        else:
            prompts = [plan_prompt(ind[it.world.seed].ops, it.text) for it in items]
            plans = gen.generate(prompts, max_new=144)
        lens, parsed = [], 0
        for p in plans:
            n, ok = nsteps(p)
            lens.append(n)
            parsed += int(ok)
        out[str(d)] = {"n": len(items),
                       "hist": dict(sorted(Counter(lens).items())),
                       "max_steps": max(lens),
                       "needed": d,
                       "long_enough": sum(1 for n in lens if n >= d),
                       "exact_length": sum(1 for n in lens if n == d),
                       "parsed": parsed,
                       "samples": plans[:3]}
        print(f"  d={d} hist={out[str(d)]['hist']} long_enough="
              f"{out[str(d)]['long_enough']}/{len(items)}", flush=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--out", default="results/audit_steplen.json")
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    args = ap.parse_args()

    tok = load_tokenizer(args.tokenizer)
    ws = eval_worlds("sequential", args.n, breadth=3, style=0)
    worlds = {w.seed: w for w in ws}
    items_by_depth = {d: [make_item("sequential", w, d, i)
                          for i, w in enumerate(ws)] for d in DEPTHS}

    result = {}
    for tag, ckpt, stepwise in [("step_plan_execute", "runs/opgraph_step.pt", True),
                                ("plan_execute", "runs/opgraph2.pt", False)]:
        print(f"[{tag}] loading {ckpt}", flush=True)
        model, _ = load_model(ckpt)
        gen = Generator(model, tok, batch_size=args.batch_size)
        ind = induce_worlds(gen, worlds)
        result[tag] = census(gen, worlds, items_by_depth, ind, stepwise)
        del model, gen
        torch.cuda.empty_cache()

    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
