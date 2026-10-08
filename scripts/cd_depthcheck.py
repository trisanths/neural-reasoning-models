"""How deep the opcode and typed forms can be written at all, and how many
tokens the gold plan costs there.

Two separate limits decide how far the depth sweep can go, and they are not the
same limit. The register file caps how many steps a plan can name: the opcode
form spells a register as a letter and has 32 of them, the typed form spells it
as a reserved token and has 16. The decoding budget caps how many tokens the
model may write. Both are measured here rather than assumed, on CPU, before any
GPU time is spent.
"""

from __future__ import annotations

import argparse
import json

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.vocab import RepError, encode_plan, rep_plan_prompt
from src.train.tokenizer import load_tokenizer

REPS_HERE = ["opcode", "typed"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--depths", default="1,2,3,4,5,6,7,8,10,12,16,20,24,32")
    ap.add_argument("--kinds", default="sequential,novel,sequential_paren")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    tok = load_tokenizer(args.tokenizer)
    depths = [int(d) for d in args.depths.split(",")]
    out: dict = {}
    for kind in args.kinds.split(","):
        for style in (0, 1):
            for depth in depths:
                if kind in ("novel", "sequential_paren") and depth < 2:
                    continue
                worlds = eval_worlds(kind, args.n, breadth=3, style=style)
                items = [make_item(kind, w, depth, i)
                         for i, w in enumerate(worlds)]
                steps = [len(it.plan.steps) for it in items]
                for rep in REPS_HERE:
                    ok = 0
                    err = {}
                    longest = 0
                    prompt_there = 0
                    for it in items:
                        try:
                            obj = encode_plan(rep, it.plan, it.world.ops, it)
                        except RepError as exc:
                            err[str(exc)[:60]] = err.get(str(exc)[:60], 0) + 1
                            continue
                        except Exception as exc:  # noqa: BLE001
                            k = type(exc).__name__ + ": " + str(exc)[:50]
                            err[k] = err.get(k, 0) + 1
                            continue
                        ok += 1
                        text = obj if isinstance(obj, str) else " ".join(obj)
                        n = len(tok.encode(" " + text)) + 1
                        if n > longest:
                            longest = n
                            prompt_there = len(tok.encode(
                                rep_plan_prompt(rep, it.world.ops, it.text)))
                    key = f"{kind}/d{depth}/style{style}/{rep}"
                    out[key] = {"encodable": ok, "n": len(items),
                                "plan_steps_min": min(steps),
                                "plan_steps_max": max(steps),
                                "longest_target_tokens": longest,
                                "prompt_tokens_there": prompt_there,
                                "errors": err}
                    print(f"{key:44s} enc={ok}/{len(items)} "
                          f"steps={min(steps)}-{max(steps)} "
                          f"tok={longest:4d} prompt={prompt_there:4d} "
                          f"{list(err)[:1]}", flush=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print("[written] " + args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
