"""What the training stream actually contains, checked rather than asserted.

Two holdouts carry the whole extrapolation claim: no training plan goes past
depth three, and no training plan uses two distinct operator symbols. If either
leaked, depth four and novel composition would not be extrapolation and every
number past depth three would mean something else. So they are counted over the
real stream rather than argued from the code that builds it.

The third check is that the latent conditions see the same episodes the token
channel arms saw. src.latent.data.training_episodes draws from the same
generator in the same order as src.opgraph.data.training_examples, and this
compares the prompts and golds it produces against the direct arm's, seed by
seed.
"""

from __future__ import annotations

import argparse
import json

from src.latent.data import (build_episodes, latent_answer_prompt,
                             latent_plan_prompt, plan_target, training_episodes)
from src.opgraph.data import direct_prompt, plan_prompt, training_examples
from src.opgraph.plan import serialize_plan


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=40000)
    ap.add_argument("--match-worlds", type=int, default=2000)
    ap.add_argument("--out", default="results/latent/verify.json")
    args = ap.parse_args(argv)

    eps = build_episodes(range(args.worlds))
    by_kind: dict[str, dict] = {}
    depth_hist: dict[int, int] = {}
    symbol_hist: dict[int, int] = {}
    worst = []
    for ep in eps:
        it = ep.item
        d = len(it.plan.steps)
        depth_hist[d] = depth_hist.get(d, 0) + 1
        syms = {s.symbol for s in it.plan.steps}
        symbol_hist[len(syms)] = symbol_hist.get(len(syms), 0) + 1
        k = by_kind.setdefault(it.kind, {"n": 0, "max_depth": 0,
                                         "max_symbols": 0})
        k["n"] += 1
        k["max_depth"] = max(k["max_depth"], d)
        k["max_symbols"] = max(k["max_symbols"], len(syms))
        if d > 3 or len(syms) > 1:
            if len(worst) < 5:
                worst.append({"kind": it.kind, "depth": d,
                              "symbols": sorted(syms),
                              "plan": serialize_plan(it.plan)})

    # the direct arm's own stream, prompt for prompt and gold for gold
    mismatch = 0
    checked = 0
    for s in range(args.match_worlds):
        arm = training_examples(s, "direct")
        mine = training_episodes(s)
        if len(arm) != len(mine):
            mismatch += 1
            continue
        for (p, g), ep in zip(arm, mine):
            checked += 1
            want = direct_prompt(ep.item.world, ep.item.text, ep.keys)
            if want != p or g != ep.item.gold:
                mismatch += 1
    # and the plan prompt condition E is actually trained on
    plan_mismatch = 0
    for s in range(min(200, args.match_worlds)):
        arm = [x for x in training_examples(s, "opgraph")
               if x[0].startswith("<|world|> opgraph <|doc|> ops ")]
        mine = training_episodes(s)
        for (p, g), ep in zip(arm, mine):
            want = plan_prompt(ep.item.world.ops, ep.item.text)
            if want != p or g != plan_target(ep):
                plan_mismatch += 1

    out = {
        "worlds": args.worlds,
        "episodes": len(eps),
        "plan_depth_histogram": {str(k): v for k, v in sorted(depth_hist.items())},
        "distinct_symbols_histogram": {str(k): v for k, v in
                                       sorted(symbol_hist.items())},
        "max_plan_depth": max(depth_hist),
        "max_distinct_symbols": max(symbol_hist),
        "by_kind": by_kind,
        "violations": worst,
        "direct_stream_pairs_checked": checked,
        "direct_stream_mismatches": mismatch,
        "plan_stream_mismatches": plan_mismatch,
        "holdout_depth_ok": max(depth_hist) <= 3,
        "holdout_single_symbol_ok": max(symbol_hist) <= 1,
    }
    print(json.dumps({k: v for k, v in out.items() if k != "by_kind"},
                     indent=1))
    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"[done] -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
