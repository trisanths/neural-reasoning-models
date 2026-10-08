"""How far in depth the opcode and typed representations can be written at all.

vocab.MAX_REGS is 16, so a plan that needs one register per step has a ceiling
that is a fact about the representation and not about the model. This measures
where encode_plan starts to fail and how many tokens the longest gold plan
needs, so a decoding budget can be set above it rather than guessed.
"""
from __future__ import annotations

import argparse
import json
import sys

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.vocab import MAX_REGS, encode_plan, rep_plan_prompt
from src.train.tokenizer import load_tokenizer

SEQ = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 32]
NOV = [2, 3, 4, 5, 6, 8, 10, 12, 16, 24, 32]
BRD = [1, 2, 3, 4, 5, 6]
PAR = [2, 3, 4, 5, 6]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--reps", default="opcode,typed,english,symbolic")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    tok = load_tokenizer(args.tokenizer)
    reps = args.reps.split(",")
    grid = {"sequential": SEQ, "novel": NOV, "breadth": BRD,
            "sequential_paren": PAR}
    out: dict = {"MAX_REGS": MAX_REGS, "cells": {}}
    for kind, depths in grid.items():
        for depth in depths:
            breadth = depth if kind == "breadth" else 3
            try:
                worlds = eval_worlds(kind, args.n, breadth=breadth, style=0)
                items = [make_item(kind, w, depth, i)
                         for i, w in enumerate(worlds)]
            except Exception as exc:
                out["cells"][f"{kind}/{depth}"] = {
                    "item_build_error": f"{type(exc).__name__}: {exc}"}
                print(f"{kind:18s} d={depth:<3d} ITEM BUILD FAILS "
                      f"{type(exc).__name__}: {exc}", flush=True)
                continue
            steps = sum(len(it.plan.steps) for it in items) / len(items)
            row: dict = {"mean_gold_steps": round(steps, 2)}
            for rep in reps:
                ok = 0
                longest = 0
                prompt_max = 0
                err = ""
                for it in items:
                    try:
                        obj = encode_plan(rep, it.plan, it.world.ops, it)
                    except Exception as exc:
                        if not err:
                            err = f"{type(exc).__name__}: {exc}"[:90]
                        continue
                    ok += 1
                    text = obj if isinstance(obj, str) else " ".join(obj)
                    longest = max(longest, len(tok.encode(" " + text)) + 1)
                    prompt_max = max(prompt_max, len(tok.encode(
                        rep_plan_prompt(rep, it.world.ops, it.text))))
                row[rep] = {"encodes": ok, "of": len(items),
                            "longest_target_tokens": longest,
                            "prompt_tokens": prompt_max, "error": err}
            out["cells"][f"{kind}/{depth}"] = row
            msg = f"{kind:18s} d={depth:<3d} steps={steps:5.2f}  "
            for rep in reps:
                r = row[rep]
                msg += (f"{rep}={r['encodes']}/{r['of']}"
                        f":tgt{r['longest_target_tokens']}"
                        f":pr{r['prompt_tokens']}  ")
            print(msg, flush=True)
            for rep in reps:
                if row[rep]["error"]:
                    print(f"      {rep} err: {row[rep]['error']}", flush=True)
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
