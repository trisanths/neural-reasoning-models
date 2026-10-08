"""Scoring the two latent conditions on the existing evaluation sets.

Everything graded here is graded by src.opgraph's own functions. Condition D is
read back with trace_answer and compared exactly as the trace arm is compared.
Condition E is parsed with parse_plan and run with run_plan against an operator
table, so a plan that does not parse and a plan that runs to the wrong value
are separated rather than pooled.

Every cell carries its denominator, its greedy rate, its sampled rate, the
forward passes and token positions spent on reasoning, and the wall clock. A
depth curve without the compute axis beside it can recommend a configuration
that does not deploy, and a rate without a denominator is not a number.

Relational breadth is scored for every condition and at every R. The registered
prediction is that breadth does not move, because breadth fails at induction
and no plan representation has shifted it. A moved breadth falsifies the
localisation and is worth more than a confirmed prediction, so it is reported
in the same table and not in a footnote.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time

import torch

from src.latent.core import LatentHead, with_depth_recurrence
from src.latent.data import latent_answer_prompt, latent_plan_prompt
from src.latent.infer import latent_generate
from src.opgraph.data import eval_items
from src.opgraph.opdef import OpError
from src.opgraph.plan import (BUILTIN_STEPS, PlanError, answer_text, parse_plan,
                              run_plan, serialize_plan, trace_answer)
from src.opgraph.run import _norm
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer


def load_latent(path: str, device: str = "cuda"):
    state = torch.load(path, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    rec = state.get("args", {}).get("depth_recurrence", "")
    if rec:
        p, c, k, lo = (int(x) for x in rec.split(","))
        model, _ = with_depth_recurrence(model, p, c, k, lo)
    model.load_state_dict(state["model"])
    hc = dict(state["head_config"])
    hc.pop("params", None)
    head = LatentHead(hc["d_model"], hc["slots"], proj=hc["proj"],
                      scale=hc["scale"])
    head.load_state_dict(state["head"])
    model.to(device).eval()
    head.to(device).eval()
    return model, head, state


# ------------------------------------------------------------------ cells

def score_answer(model, head, tok, items, r_steps, *, temperature=0.0,
                 top_k=0, seed=0, device="cuda", batch_size=16, max_new=64,
                 oracle_page=False):
    """Condition D. The answer comes out of the latent state."""
    prompts = [latent_answer_prompt(it.world, it.text,
                                    set(it.pages) if oracle_page else None)
               for it in items]
    outs, cost = latent_generate(model, head, tok, prompts, r_steps,
                                 max_new=max_new, temperature=temperature,
                                 top_k=top_k, seed=seed, device=device,
                                 batch_size=batch_size)
    correct = [_norm(trace_answer(o)) == _norm(it.gold)
               for o, it in zip(outs, items)]
    return correct, outs, cost


def plan_max_new(depth: int) -> int:
    """Decode budget for a plan of the asked depth, with room to spare.

    A gold plan at depth 32 is 259 tokens. A fixed 144 would truncate every
    plan past depth about sixteen and the truncation would be scored as a parse
    failure, which is the same shape of mistake as the max_prompt_tokens of 384
    that once removed a whole task family from this project's numbers.
    """
    return min(512, 48 + 12 * max(1, int(depth)))


def well_typed(plan, ops) -> bool:
    """Does every step name a real operator and give it the right arity.

    Separated from execution because an operator can refuse its arguments at
    run time for reasons that have nothing to do with the plan being wrong
    about the shape of the program.
    """
    for s in plan.steps:
        if s.symbol in BUILTIN_STEPS:
            if len(s.args) != BUILTIN_STEPS[s.symbol][0]:
                return False
            continue
        op = ops.get(s.symbol)
        if op is None or op.arity != len(s.args):
            return False
    return True


def score_plan(model, head, tok, items, r_steps, *, ops_by_world=None,
               temperature=0.0, top_k=0, seed=0, device="cuda",
               batch_size=16, max_new=144):
    """Condition E. The latent state emits a plan and the executor runs it."""
    prompts = []
    for it in items:
        ops = it.world.ops if ops_by_world is None else \
            ops_by_world[it.world.seed].ops
        prompts.append(latent_plan_prompt(ops, it.text))
    outs, cost = latent_generate(model, head, tok, prompts, r_steps,
                                 max_new=max_new, temperature=temperature,
                                 top_k=top_k, seed=seed, device=device,
                                 batch_size=batch_size)
    correct, reasons = [], []
    diag = {"parsed": 0, "well_typed": 0, "exact_gold": 0, "n": len(items),
            "steps_written": 0, "steps_gold": 0, "steps_written_n": 0}
    for it, text in zip(items, outs):
        ops = it.world.ops if ops_by_world is None else \
            ops_by_world[it.world.seed].ops
        diag["steps_gold"] += len(it.plan.steps)
        try:
            plan = parse_plan(text)
        except PlanError:
            correct.append(False)
            reasons.append("plan_parse")
            continue
        diag["parsed"] += 1
        diag["steps_written"] += len(plan.steps)
        diag["steps_written_n"] += 1
        if well_typed(plan, ops):
            diag["well_typed"] += 1
        if serialize_plan(plan) == serialize_plan(it.plan):
            diag["exact_gold"] += 1
        try:
            value = run_plan(plan, ops)
        except (PlanError, OpError):
            correct.append(False)
            reasons.append("execute")
            continue
        ok = _norm(answer_text(value)) == _norm(it.gold)
        correct.append(ok)
        reasons.append("ok" if ok else "wrong_value")
    return correct, outs, cost, reasons, diag


def cell(model, head, tok, arm, items, r_steps, *, samples=1,
         temperature=0.8, top_k=0, device="cuda", batch_size=16,
         ops_by_world=None, oracle_page=False, depth=1):
    """One (kind, depth, R) cell: greedy, sampled, counters, denominator."""
    t0 = time.time()
    max_new = plan_max_new(depth)
    if arm == "latent_answer":
        greedy, outs, cost = score_answer(
            model, head, tok, items, r_steps, device=device,
            batch_size=batch_size, oracle_page=oracle_page)
        reasons = diag = None
    else:
        greedy, outs, cost, reasons, diag = score_plan(
            model, head, tok, items, r_steps, ops_by_world=ops_by_world,
            device=device, batch_size=batch_size, max_new=max_new)
    sampled_rates = []
    any_correct = [False] * len(items)
    for s in range(samples):
        if arm == "latent_answer":
            ok, _, c2 = score_answer(model, head, tok, items, r_steps,
                                     temperature=temperature, top_k=top_k,
                                     seed=1000 + s, device=device,
                                     batch_size=batch_size,
                                     oracle_page=oracle_page)
        else:
            ok, _, c2, _, _ = score_plan(model, head, tok, items, r_steps,
                                         ops_by_world=ops_by_world,
                                         temperature=temperature, top_k=top_k,
                                         seed=1000 + s, device=device,
                                         batch_size=batch_size,
                                         max_new=max_new)
        sampled_rates.append(sum(ok) / len(ok))
        any_correct = [a or b for a, b in zip(any_correct, ok)]
    out = {
        "n": len(items),
        "greedy": sum(greedy) / len(greedy),
        "greedy_correct": sum(greedy),
        "sampled_mean": (sum(sampled_rates) / len(sampled_rates)
                         if sampled_rates else None),
        "sampled_rates": sampled_rates,
        "sampled_any": (sum(any_correct) / len(items)) if samples else None,
        "samples": samples, "temperature": temperature,
        "r_steps": r_steps,
        "cost": cost.per_example(),
        "wall_seconds": round(time.time() - t0, 2),
        "example_output": outs[0][:200] if outs else "",
    }
    if reasons is not None:
        tally: dict[str, int] = {}
        for x in reasons:
            tally[x] = tally.get(x, 0) + 1
        out["reasons"] = tally
        n = max(1, diag["n"])
        out["plan"] = {
            "n": diag["n"],
            "parse_rate": diag["parsed"] / n,
            "well_typed_rate": diag["well_typed"] / n,
            "exact_gold_rate": diag["exact_gold"] / n,
            "mean_steps_written": (diag["steps_written"]
                                   / max(1, diag["steps_written_n"])),
            "mean_steps_gold": diag["steps_gold"] / n,
            "max_new": max_new,
            "counts": diag,
        }
    return out


# ------------------------------------------------------------------ shape

def fit_decay(depths, rates, floor: float = 1e-3):
    """Log linear fit of the depth curve, and the crossing depth.

    The distinction this exists to protect is between a cliff that moved and a
    curve that went flat. A slope near zero with a high intercept is flat; a
    steep slope with a later crossing is a moved cliff. Reporting one as the
    other would be the most damaging error available here, so both numbers are
    always emitted together.
    """
    pts = [(d, r) for d, r in zip(depths, rates) if r > floor]
    out = {"points": len(pts)}
    if len(pts) >= 2:
        xs = [float(d) for d, _ in pts]
        ys = [math.log(r) for _, r in pts]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        var = sum((x - mx) ** 2 for x in xs)
        slope = (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / var
                 if var > 0 else 0.0)
        out["log_slope_per_depth"] = slope
        out["decay_per_depth"] = math.exp(slope)
        out["intercept"] = math.exp(my - slope * mx)
        out["half_life_depths"] = (math.log(0.5) / slope if slope < 0
                                   else float("inf"))
    for thr in (0.5, 0.25, 0.1):
        cross = None
        for d, r in zip(depths, rates):
            if r < thr:
                cross = d
                break
        out[f"first_depth_below_{thr}"] = cross
    return out


# -------------------------------------------------------------------- cli

def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--arm", default="", help="default: read it from the ckpt")
    ap.add_argument("--r", default="4", help="comma separated latent step counts")
    ap.add_argument("--depths", default="1,2,3,4,5,8")
    ap.add_argument("--breadths", default="1,2,3,4,5")
    ap.add_argument("--novel-depths", default="2,3,4,5,6")
    ap.add_argument("--induce", action="store_true",
                    help="latent_plan only: induce the operator table with this "
                         "same model instead of handing it the gold one, which "
                         "is the plan_execute analogue rather than the "
                         "oracle_ops analogue")
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--style", type=int, default=0,
                    help="1 evaluates on the paraphrased page wordings")
    ap.add_argument("--kinds", default="sequential,breadth,novel")
    ap.add_argument("--oracle-page", action="store_true")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = load_tokenizer(args.tokenizer)
    model, head, state = load_latent(args.ckpt, device)
    arm = args.arm or state.get("arm")
    rs = [int(x) for x in args.r.split(",")]
    depths = [int(x) for x in args.depths.split(",")]
    breadths = [int(x) for x in args.breadths.split(",")]
    novels = [int(x) for x in args.novel_depths.split(",")]
    kinds = [k for k in args.kinds.split(",") if k]

    # Worlds are shared across the depths of a kind, so one induction pass per
    # (kind, breadth) covers the whole curve, exactly as scripts/opgraph_eval.py
    # does it for the token channel arms.
    induced = {}
    results_induction: list = []
    if args.induce:
        from src.opgraph.run import Generator, induce_worlds
        from src.opgraph.data import eval_worlds
        gen = Generator(model, tok, device=device, batch_size=args.batch_size)
        for kind in kinds:
            bs = breadths if kind == "breadth" else [3]
            for b in bs:
                ws = eval_worlds(kind, args.n, breadth=b, style=args.style)
                tab = induce_worlds(gen, {w.seed: w for w in ws})
                induced[(kind, b)] = tab
                pages = sum(i.pages for i in tab.values())
                rep = {"induce": kind, "breadth": b, "worlds": len(tab),
                       "pages": pages,
                       "parsed": sum(i.parsed for i in tab.values()) / max(1, pages),
                       "exact": sum(i.exact for i in tab.values())
                       / max(1, sum(i.gold_count for i in tab.values())),
                       "behavioural": sum(i.behavioural for i in tab.values())
                       / max(1, sum(i.gold_count for i in tab.values()))}
                results_induction.append(rep)
                print(json.dumps(rep), flush=True)

    results = {"ckpt": args.ckpt, "arm": arm, "style": args.style,
               "n": args.n, "induce": bool(args.induce),
               "setup": state.get("setup"),
               "head_config": state.get("head_config"),
               "train_args": state.get("args"),
               "induction": results_induction,
               "cells": [], "shape": {}}
    for r in rs:
        for kind in kinds:
            ds = {"breadth": breadths, "novel": novels}.get(kind, depths)
            rates = []
            for d in ds:
                items = eval_items(kind, d, args.n, style=args.style)
                obw = induced.get((kind, d if kind == "breadth" else 3)) \
                    if args.induce else None
                c = cell(model, head, tok, arm, items, r,
                         samples=args.samples, temperature=args.temperature,
                         device=device, batch_size=args.batch_size,
                         oracle_page=args.oracle_page, depth=d,
                         ops_by_world=obw)
                c.update({"kind": kind, "depth": d})
                rates.append(c["greedy"])
                results["cells"].append(c)
                print(json.dumps({k: v for k, v in c.items()
                                  if k != "example_output"}), flush=True)
                _dump(args.out, results)
            results["shape"][f"{kind}@R{r}"] = {
                "depths": ds, "greedy": rates, **fit_decay(ds, rates)}
    _dump(args.out, results)
    print(f"[done] -> {args.out}", flush=True)
    return 0


def _dump(path, results):
    """Persist after every cell. A sweep that dies at hour three should still
    have every cell it finished on disk rather than in a dead process."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(results, fh, indent=1)
    os.replace(tmp, path)


if __name__ == "__main__":
    raise SystemExit(main())
