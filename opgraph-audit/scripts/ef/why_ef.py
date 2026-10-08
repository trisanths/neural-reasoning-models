"""Why a decoded plan does not parse, instruction by instruction.

`plan_parses` says a plan failed. It does not say where. This prints the
decoded token names and the exception `decode_plan` raised, for a handful of
items at one depth, which is the difference between "the model cannot write a
deep plan" and "the model writes one the reader rejects for one reason".
"""

from __future__ import annotations

import argparse

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.ladder_run import GoalHook, TokenGenerator, plan_outputs
from src.opgraph.run import Generator, induce_worlds, load_model
from src.opgraph.vocab import (REP_OF_ARM, decode_plan, encode_plan, lex,
                               rep_plan_prompt, token_name)
from src.train.tokenizer import load_tokenizer


class FreeGoalHook(GoalHook):
    def banned(self):
        return None


def names(tok, text):
    return [token_name(t) or t for t in lex(text)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--kind", default="sequential")
    ap.add_argument("--depths", default="3,4")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--max-new", type=int, default=400)
    ap.add_argument("--free", type=int, default=1)
    args = ap.parse_args()

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, state = load_model(args.ckpt, device)
    rep = REP_OF_ARM[state["arm"]]
    ind_gen = Generator(model, tok, device, batch_size=8)
    gen = TokenGenerator(model, tok, device, batch_size=8, temperature=0.0,
                         seed=0)

    for depth in [int(d) for d in args.depths.split(",")]:
        breadth = depth if args.kind == "breadth" else 3
        ws = eval_worlds(args.kind, args.n, breadth=breadth, style=0)
        items = [make_item(args.kind, w, depth, i) for i, w in enumerate(ws)]
        induced = induce_worlds(ind_gen, {it.world.seed: it.world
                                          for it in items})
        hooks = [(FreeGoalHook if args.free else GoalHook)(
            tok, induced[it.world.seed].ops, it) for it in items]
        prompts = [rep_plan_prompt(rep, induced[it.world.seed].ops, it.text)
                   for it in items]
        outs = gen.generate(prompts, max_new=args.max_new, hooks=hooks)
        for it, (_, text) in zip(items, outs):
            ops = induced[it.world.seed].ops
            gold = encode_plan(rep, it.plan, ops, it)
            gold_t = gold if isinstance(gold, str) else " ".join(gold)
            print("=" * 70)
            print(f"depth={depth} q={it.text}  gold_answer={it.gold}")
            print("gold :", " ".join(names(tok, gold_t)))
            print("model:", " ".join(names(tok, text)))
            try:
                plan = decode_plan(rep, text, ops)
                print("parsed ok, steps:", len(plan.steps))
            except Exception as exc:
                print(f"parse failed: {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
