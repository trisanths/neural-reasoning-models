"""The autoregressive baseline given the latent conditions' reasoning compute.

R latent steps cost R forward passes. If the token channel is handed the same
number of extra forward passes and reaches the same accuracy, then what the
latent conditions bought is test time compute and the vocabulary bottleneck
claim is dead. Nothing else in this experiment can decide that, so the control
is run cell by cell against measured pass counts rather than against a nominal
sample count.

The accounting. Every condition reads the prompt once and writes one answer
once; that is the floor and it is not charged to anyone. Reasoning compute is
what a condition spends on top of that floor:

  latent at R          R forward passes, one per latent step
  token channel at N   (N - 1) decode passes, the extra samples
  trace at N = 1       its decode is longer than direct's, and the difference
                       is reasoning spent in the token channel

Re-reading the prompt for each extra sample is real compute the token channel
pays and the latent conditions do not, and it is deliberately not charged here.
That makes the baseline stronger than a strict FLOP match would, which is the
right direction for a control that exists to kill a claim.

Three selection rules, because best of N without a selector is not a method:

  greedy      the N = 1 reference, temperature zero
  vote        majority over the N sampled answers, self consistency
  executor    plan arms only: drop the samples that fail to parse or fail to
              run, then take the majority of the values the executor returned
  any         an oracle picks the right sample if one exists. Not achievable,
              reported as the ceiling the selectors are working against
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter

import torch

from src.latent.infer import token_generate
from src.opgraph.data import (direct_prompt, eval_items, plan_prompt,
                              trace_prompt)
from src.opgraph.opdef import OpError
from src.opgraph.plan import PlanError, answer_text, parse_plan, run_plan, \
    trace_answer
from src.opgraph.run import _norm, load_model
from src.train.tokenizer import load_tokenizer

ARMS = ("direct", "trace", "opgraph")


def prompts_for(arm: str, items, oracle_page: bool = False):
    if arm == "direct":
        return [direct_prompt(it.world, it.text,
                              set(it.pages) if oracle_page else None)
                for it in items]
    if arm == "trace":
        return [trace_prompt(it.world, it.text,
                             set(it.pages) if oracle_page else None)
                for it in items]
    return [plan_prompt(it.world.ops, it.text) for it in items]


def max_new_for(arm: str, depth: int) -> int:
    if arm == "direct":
        return 24
    if arm == "trace":
        return min(640, 64 + 16 * max(1, depth))
    return min(512, 48 + 12 * max(1, depth))


def read_answer(arm: str, text: str, item):
    """The answer a sample claims, and whether the executor could produce it.

    Returns (answer_string_or_None, reason). None means the sample produced no
    answer at all, which is what a selector has to be able to discard.
    """
    if arm == "direct":
        return text.strip(), "ok"
    if arm == "trace":
        a = trace_answer(text)
        return (a or None), ("ok" if a else "no_ans")
    try:
        plan = parse_plan(text)
    except PlanError:
        return None, "plan_parse"
    try:
        value = run_plan(plan, item.world.ops)
    except (PlanError, OpError):
        return None, "execute"
    return answer_text(value), "ok"


def vote(answers: list) -> str | None:
    """Majority over the answers that exist, first past the post on a tie."""
    live = [a for a in answers if a is not None]
    if not live:
        return None
    counts = Counter(live)
    best = max(counts.values())
    for a in live:            # first occurrence order breaks the tie
        if counts[a] == best:
            return a
    return None


def greedy_once(model, tok, arm, items, *, device, batch_size, depth,
                oracle_page=False):
    """The N = 1 reference for a (kind, depth). Run once and reused by every
    budget, so the depth 32 trace arm does not decode 348 tokens eight times."""
    prompts = prompts_for(arm, items, oracle_page)
    mn = max_new_for(arm, depth)
    outs, gcost = token_generate(model, tok, prompts, max_new=mn,
                                 temperature=0.0, device=device,
                                 batch_size=batch_size)
    ans = [read_answer(arm, o, it)[0] for o, it in zip(outs, items)]
    ok = [a is not None and _norm(a) == _norm(it.gold)
          for a, it in zip(ans, items)]
    return {"outs": outs, "ok": ok, "cost": gcost}


def run_cell(model, tok, arm, items, n_samples, *, device, batch_size, depth,
             temperature=0.8, seed0=1000, oracle_page=False, ref=None):
    """One (kind, depth, N) cell of the token channel, with its counters."""
    t0 = time.time()
    prompts = prompts_for(arm, items, oracle_page)
    mn = max_new_for(arm, depth)
    if ref is None:
        ref = greedy_once(model, tok, arm, items, device=device,
                          batch_size=batch_size, depth=depth,
                          oracle_page=oracle_page)
    greedy_out, greedy_ok, gcost = ref["outs"], ref["ok"], ref["cost"]

    per_sample: list[list] = []
    reasons = Counter()
    scost = None
    for s in range(n_samples):
        outs, c = token_generate(model, tok, prompts, max_new=mn,
                                 temperature=temperature, seed=seed0 + s,
                                 device=device, batch_size=batch_size)
        row = []
        for o, it in zip(outs, items):
            a, why = read_answer(arm, o, it)
            reasons[why] += 1
            row.append(a)
        per_sample.append(row)
        scost = c if scost is None else (scost.add(c) or scost)

    voted = [vote([per_sample[s][i] for s in range(n_samples)])
             for i in range(len(items))]
    vote_ok = [a is not None and _norm(a) == _norm(it.gold)
               for a, it in zip(voted, items)]
    any_ok = [any(per_sample[s][i] is not None
                  and _norm(per_sample[s][i]) == _norm(items[i].gold)
                  for s in range(n_samples))
              for i in range(len(items))]
    mean_ok = sum(
        sum(1 for i in range(len(items))
            if per_sample[s][i] is not None
            and _norm(per_sample[s][i]) == _norm(items[i].gold))
        for s in range(n_samples)) / max(1, n_samples * len(items))

    g = gcost.per_example()
    decode1 = g["decode_passes_per_example"]
    out = {
        "arm": arm, "n": len(items), "samples": n_samples,
        "temperature": temperature,
        "greedy": sum(greedy_ok) / len(items),
        "vote": sum(vote_ok) / len(items),
        "any": sum(any_ok) / len(items),
        "sampled_mean": mean_ok,
        "decode_passes_greedy_per_example": decode1,
        "extra_reason_passes_per_example": (n_samples - 1) * decode1,
        "total_passes_per_example": (g["prompt_passes_per_example"]
                                     + n_samples * decode1),
        "prompt_positions_per_example": g["prompt_positions_per_example"],
        "greedy_cost": g,
        "sampled_cost": scost.per_example() if scost is not None else None,
        "reasons": dict(reasons),
        "wall_seconds": round(time.time() - t0, 2),
        "example_output": greedy_out[0][:200] if greedy_out else "",
    }
    return out


def samples_for(budget: float, decode1: float, cap: int = 48) -> int:
    """N whose extra decode passes come closest to the budget."""
    if decode1 <= 0:
        return 1
    return max(1, min(cap, 1 + int(round(budget / decode1))))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--arm", required=True, choices=list(ARMS))
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--budgets", default="0,1,2,4,8,16,32,64",
                    help="reasoning forward passes per example to hand the "
                         "token channel, one cell each. 0 is the greedy "
                         "reference and always runs first.")
    ap.add_argument("--depths", default="1,2,3,4,5,6,8,12,16,32")
    ap.add_argument("--breadths", default="1,2,3,4,5,6")
    ap.add_argument("--novel-depths", default="2,3,4,5,6")
    ap.add_argument("--kinds", default="sequential")
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--style", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--cap", type=int, default=48)
    ap.add_argument("--oracle-page", action="store_true")
    args = ap.parse_args(argv)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = load_tokenizer(args.tokenizer)
    model, _state = load_model(args.ckpt, device)
    budgets = [float(x) for x in args.budgets.split(",")]
    depths = [int(x) for x in args.depths.split(",")]
    breadths = [int(x) for x in args.breadths.split(",")]
    novels = [int(x) for x in args.novel_depths.split(",")]
    kinds = [k for k in args.kinds.split(",") if k]

    results = {"ckpt": args.ckpt, "arm": args.arm, "style": args.style,
               "n": args.n, "cells": []}
    for kind in kinds:
        ds = {"breadth": breadths, "novel": novels}.get(kind, depths)
        for d in ds:
            items = eval_items(kind, d, args.n, style=args.style)
            ref = greedy_once(model, tok, args.arm, items, device=device,
                              batch_size=args.batch_size, depth=d,
                              oracle_page=args.oracle_page)
            decode1 = ref["cost"].per_example()["decode_passes_per_example"]
            done: dict[int, dict] = {}
            for b in budgets:
                nsamp = samples_for(b, decode1, args.cap)
                if nsamp in done:
                    # This budget buys no extra sample over one already run.
                    # Record it against the same measured cell rather than
                    # decoding it a second time.
                    c = dict(done[nsamp])
                    c.update({"kind": kind, "depth": d, "budget": b})
                    results["cells"].append(c)
                    _dump(args.out, results)
                    continue
                c = run_cell(model, tok, args.arm, items, nsamp, device=device,
                             batch_size=args.batch_size, depth=d,
                             temperature=args.temperature,
                             oracle_page=args.oracle_page, ref=ref)
                done[nsamp] = c
                c = dict(c)
                c.update({"kind": kind, "depth": d, "budget": b})
                results["cells"].append(c)
                print(json.dumps({k: v for k, v in c.items()
                                  if k not in ("example_output", "greedy_cost",
                                               "sampled_cost")}), flush=True)
                _dump(args.out, results)
    _dump(args.out, results)
    print(f"[done] -> {args.out}", flush=True)
    return 0


def _dump(path, results):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(results, fh, indent=1)
    os.replace(tmp, path)


if __name__ == "__main__":
    raise SystemExit(main())
