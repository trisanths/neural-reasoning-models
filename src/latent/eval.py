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
from src.opgraph.plan import (PlanError, answer_text, parse_plan, run_plan,
                              trace_answer)
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
    for it, text in zip(items, outs):
        ops = it.world.ops if ops_by_world is None else \
            ops_by_world[it.world.seed].ops
        try:
            plan = parse_plan(text)
        except PlanError:
            correct.append(False)
            reasons.append("plan_parse")
            continue
        try:
            value = run_plan(plan, ops)
        except (PlanError, OpError):
            correct.append(False)
            reasons.append("execute")
            continue
        ok = _norm(answer_text(value)) == _norm(it.gold)
        correct.append(ok)
        reasons.append("ok" if ok else "wrong_value")
    return correct, outs, cost, reasons


def cell(model, head, tok, arm, items, r_steps, *, samples=1,
         temperature=0.8, top_k=0, device="cuda", batch_size=16,
         ops_by_world=None, oracle_page=False):
    """One (kind, depth, R) cell: greedy, sampled, counters, denominator."""
    t0 = time.time()
    if arm == "latent_answer":
        greedy, outs, cost = score_answer(
            model, head, tok, items, r_steps, device=device,
            batch_size=batch_size, oracle_page=oracle_page)
        reasons = None
    else:
        greedy, outs, cost, reasons = score_plan(
            model, head, tok, items, r_steps, ops_by_world=ops_by_world,
            device=device, batch_size=batch_size)
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
            ok, _, c2, _ = score_plan(model, head, tok, items, r_steps,
                                      ops_by_world=ops_by_world,
                                      temperature=temperature, top_k=top_k,
                                      seed=1000 + s, device=device,
                                      batch_size=batch_size)
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
    kinds = [k for k in args.kinds.split(",") if k]

    results = {"ckpt": args.ckpt, "arm": arm, "style": args.style,
               "setup": state.get("setup"), "cells": [], "shape": {}}
    for r in rs:
        for kind in kinds:
            ds = breadths if kind == "breadth" else depths
            rates = []
            for d in ds:
                items = eval_items(kind, d, args.n, style=args.style)
                c = cell(model, head, tok, arm, items, r,
                         samples=args.samples, temperature=args.temperature,
                         device=device, batch_size=args.batch_size,
                         oracle_page=args.oracle_page)
                c.update({"kind": kind, "depth": d})
                rates.append(c["greedy"])
                results["cells"].append(c)
                print(json.dumps({k: v for k, v in c.items()
                                  if k != "example_output"}), flush=True)
            results["shape"][f"{kind}@R{r}"] = {
                "depths": ds, "greedy": rates, **fit_decay(ds, rates)}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"[done] -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
