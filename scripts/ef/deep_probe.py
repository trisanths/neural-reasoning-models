"""How deep can the goalstack and slot representations be encoded at all.

Runs on CPU. For each sequential depth it writes the gold plan in the
representation, reads it back, executes it, and measures the token length of
the target. A depth where the round trip fails is a depth where oracle_both
cannot be 1.000, which is a fact about the fixed register file and the fixed
slot count rather than about the model.
"""

from __future__ import annotations

import argparse
import json

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.plan import answer_text, run_plan
from src.opgraph.vocab import (F_SLOTS, MAX_REGS, RepError, canonical,
                               decode_plan, encode_plan, rep_plan_prompt)
from src.train.tokenizer import load_tokenizer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--reps", default="goalstack,slots,typed,english")
    ap.add_argument("--depths", default="1,2,3,4,5,6,7,8,10,12,14,16,17,18,20,24,32")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    tok = load_tokenizer(args.tokenizer)
    depths = [int(d) for d in args.depths.split(",")]
    reps = args.reps.split(",")
    out = {"max_regs": MAX_REGS, "f_slots": F_SLOTS, "cells": []}
    for style in (0, 1):
        for depth in depths:
            worlds = eval_worlds("sequential", args.n, breadth=3, style=style)
            items = [make_item("sequential", w, depth, i)
                     for i, w in enumerate(worlds)]
            for rep in reps:
                ok = 0
                longest = 0
                prompt_max = 0
                err = ""
                for it in items:
                    try:
                        obj = encode_plan(rep, it.plan, it.world.ops, it)
                    except (RepError, Exception) as exc:
                        err = err or f"encode:{type(exc).__name__}:{exc}"[:90]
                        continue
                    text = obj if isinstance(obj, str) else " ".join(obj)
                    longest = max(longest, len(tok.encode(" " + text)) + 1)
                    prompt_max = max(prompt_max, len(tok.encode(
                        rep_plan_prompt(rep, it.world.ops, it.text))))
                    try:
                        back = decode_plan(rep, obj, it.world.ops)
                        same = canonical(back) == canonical(it.plan)
                        val = answer_text(run_plan(back, it.world.ops))
                        ok += int(same and str(val).strip() == str(it.gold).strip())
                    except Exception as exc:
                        err = err or f"decode:{type(exc).__name__}:{exc}"[:90]
                row = {"style": style, "depth": depth, "rep": rep, "n": len(items),
                       "roundtrip_ok": ok, "longest_target_tokens": longest,
                       "prompt_tokens": prompt_max, "error": err}
                out["cells"].append(row)
                print(json.dumps(row), flush=True)
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
