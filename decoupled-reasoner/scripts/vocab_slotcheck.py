"""Does the model's own operator table agree with gold about slot order?

Rungs B to F name an operator by its slot, which is its index in `sorted(ops)`.
The prompt's signature line and the plan agree on what `op0` names because both
are written from the same table. In `oracle_plan` the gold plan is written from
the gold table and read back against the table the model induced, so if
induction loses or invents a symbol the sorted order shifts and `op0` binds to a
different operator. Rung A is immune, because it names the operator by the
symbol the page uses.

This measures that coupling directly, over the same evaluation worlds the ladder
scores on, and needs induction only, no plan decoding.

  symbols_match     the induced table has exactly the gold symbol set
  slots_match       every symbol a gold plan uses sits at the same index in both
  plan_slots_match  the same, restricted to the symbols this item's plan uses
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.run import Generator, induce_worlds, load_model
from src.train.tokenizer import load_tokenizer

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 7, 8],
    "breadth": [1, 2, 3, 4, 5, 6],
    "novel": [2, 3, 4, 5, 6],
    "sequential_paren": [2, 3, 4, 5, 6],
    "same_page_pair": [2],
    "units": [1],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--kinds", default="sequential,breadth,novel,units")
    ap.add_argument("--styles", default="0,1")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_model(args.ckpt, device)
    gen = Generator(model, tok, device, batch_size=args.batch_size)

    out: dict = {"config": vars(args)}
    for style in [int(s) for s in args.styles.split(",")]:
        items = []
        cache = {}
        for kind in args.kinds.split(","):
            for depth in GRID[kind]:
                breadth = depth if kind == "breadth" else 3
                key = (kind, breadth)
                if key not in cache:
                    cache[key] = eval_worlds(kind, args.n, breadth=breadth,
                                             style=style)
                for i, w in enumerate(cache[key]):
                    items.append((kind, depth, make_item(kind, w, depth, i)))
        worlds = {it.world.seed: it.world for _, _, it in items}
        induced = induce_worlds(gen, worlds, progress=1)

        per: dict = {}
        for kind, depth, it in items:
            gold = sorted(it.world.ops)
            got = sorted(induced[it.world.seed].ops)
            used = sorted({s.symbol for s in it.plan.steps})
            c = per.setdefault(f"{kind}/{depth}", Counter())
            c["n"] += 1
            c["symbols_match"] += int(gold == got)
            c["slots_match"] += int(all(
                s in got and gold.index(s) == got.index(s) for s in gold))
            c["plan_slots_match"] += int(all(
                s in got and gold.index(s) == got.index(s) for s in used))
        out[f"style{style}"] = {k: dict(v) for k, v in per.items()}
        tot = Counter()
        for v in per.values():
            tot.update(v)
        out[f"style{style}_total"] = dict(tot)
        print(f"[style {style}] {json.dumps(dict(tot))}", flush=True)

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"[written] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
