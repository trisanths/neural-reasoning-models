"""The original opgraph arm on the deep sequential tail, as a floor.

The recorded grid stops at sequential depth eight, so a rung measured at depth
16 and 32 has no floor to be scored against and its gap recovered would have to
be taken on an assumption. This runs the arm that set the floor, `runs/opgraph.pt`,
on exactly the same items the ladder rungs see at those depths, in that arm's
own plan notation, so the fraction of the gap is measured at every depth rather
than assumed past eight.

Depth 8 is repeated here so this run can be checked against the record: it has
to reproduce 0.013 for plan_execute and 1.000 for oracle_plan, or the pairing
is wrong and the deep numbers mean nothing.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.plan import serialize_plan
from src.opgraph.run import Generator, induce_worlds, load_model, score_planned
from src.train.tokenizer import load_tokenizer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="runs/opgraph.pt")
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--depths", default="8,16,32")
    ap.add_argument("--styles", default="0,1")
    ap.add_argument("--max-new", type=int, default=512)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ds = [int(d) for d in args.depths.split(",")]
    styles = [int(s) for s in args.styles.split(",")]

    sets = {}
    for st in styles:
        ws = eval_worlds("sequential", args.n, breadth=3, style=st)
        for d in ds:
            sets[(st, d)] = [make_item("sequential", w, d, i)
                             for i, w in enumerate(ws)]

    results: dict = {"config": vars(args), "budget": {}}
    for (st, d), items in sets.items():
        worst = max(len(tok.encode(" " + serialize_plan(it.plan))) + 1
                    for it in items)
        results["budget"][f"style{st}/sequential/{d}"] = {
            "longest_gold_plan_tokens": worst, "max_new": args.max_new,
            "fits": worst <= args.max_new}
    print(f"[budget] {json.dumps(results['budget'])}", flush=True)

    model, _ = load_model(args.ckpt, device)
    gen = Generator(model, tok, device, batch_size=args.batch_size)
    conds = (("plan_execute", False, False),
             ("oracle_plan", True, False),
             ("oracle_ops", False, True),
             ("oracle_both", True, True))

    for st in styles:
        worlds = {it.world.seed: it.world
                  for (s, _), items in sets.items() if s == st
                  for it in items}
        induced = induce_worlds(gen, worlds, progress=1)
        for d in ds:
            items = sets[(st, d)]
            for name, gp, go in conds:
                if st != 0 and name in ("oracle_ops", "oracle_both"):
                    continue
                ok, texts, reasons = score_planned(gen, items, induced,
                                                   use_gold_plan=gp,
                                                   use_gold_ops=go,
                                                   max_new=args.max_new)
                rc = Counter(reasons)
                n = len(ok)
                tag = name if st == 0 else name + "@para"
                results.setdefault(tag, {}).setdefault("sequential", {})[str(d)] = {
                    "n": n, "acc": round(sum(ok) / n, 4),
                    "plan_parses": round(1 - rc["plan_parse"] / n, 4),
                    "well_typed": 0.0, "exact_gold_plan": 0.0,
                    "parsed_but_wrong": round(
                        (rc["wrong_value"] + rc["execute"]) / n, 4),
                    "reasons": dict(rc), "samples": texts[:3]}
                print(f"[{tag}] sequential d={d} acc={sum(ok)/n:.3f} "
                      f"parse={1 - rc['plan_parse']/n:.3f}", flush=True)
            with open(args.out, "w") as fh:
                json.dump(results, fh, indent=1)

    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"[written] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
