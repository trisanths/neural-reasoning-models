"""How many tokens the gold plan needs, per representation, over the whole grid.

The decoding budget is shared by every rung, so it has to clear the longest
gold plan any rung has to write, with room to spare. A budget that clips one
representation and not another would look like that representation failing.
On this project a length filter has silently removed a whole task family once
already, so the number is measured rather than assumed.
"""

from __future__ import annotations

import argparse
import json

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.vocab import REPS, encode_plan, rep_plan_prompt
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
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--budget", type=int, default=192)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    tok = load_tokenizer(args.tokenizer)
    out: dict = {"budget": args.budget}
    worst: dict = {}
    for style in (0, 1):
        for kind, depths in GRID.items():
            for depth in depths:
                breadth = depth if kind == "breadth" else 3
                worlds = eval_worlds(kind, args.n, breadth=breadth, style=style)
                items = [make_item(kind, w, depth, i)
                         for i, w in enumerate(worlds)]
                for rep in REPS:
                    for it in items:
                        obj = encode_plan(rep, it.plan, it.world.ops, it)
                        text = obj if isinstance(obj, str) else " ".join(obj)
                        n = len(tok.encode(" " + text)) + 1
                        p = len(tok.encode(rep_plan_prompt(rep, it.world.ops,
                                                           it.text)))
                        cur = worst.get(rep, (0, 0, ""))
                        if n > cur[0]:
                            worst[rep] = (n, p, f"{kind}/{depth}/style{style}")
    for rep, (n, p, where) in worst.items():
        out[rep] = {"longest_target_tokens": n, "prompt_tokens_there": p,
                    "where": where, "fits_budget": n <= args.budget}
        print(f"{rep:10s} longest target {n:4d} tokens, prompt {p:4d}, "
              f"at {where}, fits {args.budget}: {n <= args.budget}")
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
