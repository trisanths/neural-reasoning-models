"""Is the deep plan malformed, or only misnamed?

Rungs B to E name the value a step produces with an explicit register, and the
reader requires destinations to appear in order: step k must write r_k. Past
its trained depth the goal-stack model keeps applying but stops advancing the
destination index, so the reader rejects the plan before anything is executed.

That rejection is about naming. This measures what is underneath it. The
emitted token stream is rewritten so that destinations are renumbered in the
order they are written and every operand reference is redirected to the most
recent writer of that register, which is the ordinary register-machine reading
rather than the single-assignment one. The rewritten plan then goes through the
same `decode_plan` and the same executor as everything else.

Three numbers come out per cell: how often the plan parses as written, how
often it parses after renumbering, and how often it then produces the right
answer. If the second is high and the third is not, the model is writing a
wrong plan and the naming rule is only where it is caught first.
"""

from __future__ import annotations

import argparse
import json
import re

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.ladder_run import GoalHook, TokenGenerator
from src.opgraph.opdef import OpError
from src.opgraph.plan import PlanError, answer_text, run_plan
from src.opgraph.run import Generator, induce_worlds, load_model
from src.opgraph.vocab import (REG, REP_OF_ARM, RepError, decode_plan, lex,
                               rep_plan_prompt, token_name)
from src.train.tokenizer import load_tokenizer


class FreeGoalHook(GoalHook):
    def banned(self):
        return None


def renumber(text: str) -> str:
    """Destinations in emission order, operands to the most recent writer."""
    toks = lex(text)
    names = [token_name(t) or t for t in toks]
    out: list[str] = []
    cur: dict[int, int] = {}
    step = 0
    i = 0
    while i < len(names):
        # One instruction, up to and including its <end>.
        j = i
        while j < len(names) and names[j] != "end":
            j += 1
        chunk = list(range(i, min(j + 1, len(names))))
        head = names[i] if i < len(names) else ""
        if head == "goal":
            out.extend(toks[k] for k in chunk)
            i = j + 1
            continue
        if head not in ("apply", "ret"):
            out.extend(toks[k] for k in chunk)
            i = j + 1
            continue
        idx_to = next((k for k in chunk if names[k] == "to"), None)
        for k in chunk:
            m = re.fullmatch(r"r(\d+)", names[k])
            if not m:
                out.append(toks[k])
                continue
            phys = int(m.group(1))
            if idx_to is not None and k == idx_to + 1:
                out.append(REG[step] if step < len(REG) else toks[k])
                cur[phys] = step
            else:
                out.append(REG[cur[phys]] if phys in cur else toks[k])
        if head == "apply":
            step += 1
        i = j + 1
    return " ".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--kind", default="sequential")
    ap.add_argument("--depths", default="1,2,3,4,5,6,8,10,12,14,16")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--styles", default="0,1")
    ap.add_argument("--batch-size", type=int, default=48)
    ap.add_argument("--temperature", type=float, default=0.0)
    args = ap.parse_args()

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, state = load_model(args.ckpt, device)
    rep = REP_OF_ARM[state["arm"]]
    ind_gen = Generator(model, tok, device, batch_size=args.batch_size)
    gen = TokenGenerator(model, tok, device, batch_size=args.batch_size,
                         temperature=args.temperature, seed=0)
    rows = []
    for style in [int(s) for s in args.styles.split(",")]:
        for depth in [int(d) for d in args.depths.split(",")]:
            breadth = depth if args.kind == "breadth" else 3
            ws = eval_worlds(args.kind, args.n, breadth=breadth, style=style)
            items = [make_item(args.kind, w, depth, i)
                     for i, w in enumerate(ws)]
            induced = induce_worlds(ind_gen, {it.world.seed: it.world
                                              for it in items})
            for label, hook_cls in (("constrained", GoalHook),
                                    ("free", FreeGoalHook)):
                ops_of = {it.world.seed: induced[it.world.seed].ops
                          for it in items}
                prompts = [rep_plan_prompt(rep, ops_of[it.world.seed], it.text)
                           for it in items]
                hooks = [hook_cls(tok, ops_of[it.world.seed], it)
                         for it in items]
                budget = max(320, 30 * depth + 120)
                outs = gen.generate(prompts, max_new=budget, hooks=hooks)
                strict = tol = tol_ok = strict_ok = applies_right = 0
                for it, (_, text) in zip(items, outs):
                    ops = ops_of[it.world.seed]
                    n_apply = sum(1 for t in lex(text)
                                  if token_name(t) == "apply")
                    applies_right += int(n_apply == len(it.plan.steps))
                    for which, body in (("strict", text),
                                        ("tol", renumber(text))):
                        try:
                            plan = decode_plan(rep, body, ops)
                        except (RepError, PlanError, OpError, KeyError,
                                IndexError, ValueError):
                            continue
                        ok = False
                        try:
                            ok = (str(answer_text(run_plan(plan, ops))).strip()
                                  == str(it.gold).strip())
                        except (PlanError, OpError):
                            ok = False
                        if which == "strict":
                            strict += 1
                            strict_ok += int(ok)
                        else:
                            tol += 1
                            tol_ok += int(ok)
                n = len(items)
                row = {"style": style, "depth": depth, "decode": label, "n": n,
                       "max_new": budget,
                       "right_number_of_applies": round(applies_right / n, 4),
                       "parse_strict": round(strict / n, 4),
                       "acc_strict": round(strict_ok / n, 4),
                       "parse_renumbered": round(tol / n, 4),
                       "acc_renumbered": round(tol_ok / n, 4)}
                rows.append(row)
                print(json.dumps(row), flush=True)
                with open(args.out, "w") as fh:
                    json.dump({"config": vars(args), "rows": rows}, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
