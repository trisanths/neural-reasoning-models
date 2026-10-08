"""Score one autoregressive plan head over the extrapolation grid.

This is the shared `scripts/planheads_eval.py` with three changes, and it
imports the schema, the planners and the grader from `src.opgraph.planheads`
rather than reimplementing them, so nothing about how a plan is built or judged
differs from the shared path.

  1. The depth grid runs past eight. Sequential depth goes 1 2 3 4 5 6 8 12 16
     32. Thirty two is the ceiling of the strict plan parser, whose MAX_STEPS is
     32, so a depth 40 gold plan raises "plan too long" and cannot be scored at
     all. That ceiling is a property of the executor, not of a head.
  2. The generation cap is an argument rather than the shared default of 160. A
     gold depth 32 plan costs up to 260 tokens in P1's spelling and 292 in P2's,
     so a cap of 160 would truncate the only correct answer and the depth curve
     would be reporting the cap. The cap is identical for both heads.
  3. Every cell also reports how long the head's own plan was: tokens generated,
     how many items hit the cap without an end of text, and how many steps the
     emitted plan actually contained against the depth the question needed. A
     decoder trained on plans of at most three steps that writes three steps at
     depth sixteen fails for a different reason than one that writes sixteen
     wrong steps, and only the emitted step count separates the two.

Conditions, denominators, plan level diagnostics and the compute accounting are
the shared ones. oracle_both and oracle_both_roundtrip are scored first and must
be 1.000 or nothing else may be read.
"""

from __future__ import annotations

import argparse
import json
import os
import time

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.plan import parse_plan
from src.opgraph.planheads import (ForwardCounter, GoldPlanner, SlotPlanHead,
                                   grade, make_planner, mixture_for)
from src.opgraph.run import Generator, induce_worlds
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 8, 12, 16, 32],
    "sequential_paren": [2, 3, 4, 5, 6, 8, 12, 16, 32],
    "breadth": [1, 2, 3, 4, 5, 6],
    "novel": [2, 3, 4, 5, 6, 8, 12],
    "same_page_pair": [2],
    "units": [1],
}

CONDITIONS = (("plan_execute", False, False),
              ("oracle_ops", False, True),
              ("oracle_plan", True, False),
              ("oracle_both", True, True))


def load_plan_model(path: str, device: str):
    state = torch.load(path, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    head_name = state.get("head", "p1")
    model.to(device).eval()
    model.plan_head = None
    if state.get("plan_head") is not None:
        h = SlotPlanHead(model.cfg.d_model)
        h.load_state_dict(state["plan_head"])
        model.plan_head = h.to(device).eval()
    return model, state, head_name


def build_sets(kinds, n, style):
    sets, cache = {}, {}
    for kind in kinds:
        for depth in GRID[kind]:
            breadth = depth if kind == "breadth" else 3
            key = (kind, breadth)
            if key not in cache:
                cache[key] = eval_worlds(kind, n, breadth=breadth, style=style)
            sets[(kind, depth)] = [make_item(kind, w, depth, i)
                                   for i, w in enumerate(cache[key])]
    return sets


def extras(items, outs, max_new: int) -> dict:
    """How long the plan the head wrote was, and how much of it was right.

    The step count separates two failures a bare accuracy number folds together.
    A decoder trained on plans of at most three steps that writes three steps at
    depth sixteen has stopped early; one that writes sixteen wrong steps has
    planned wrongly. The prefix rate separates them further: if the three steps
    it wrote are exactly the first three steps of the gold plan, everything the
    head produced was correct and only the stopping rule failed.
    """
    gen, steps, at_cap, eq = [], [], 0, 0
    prefix = first_ok = 0
    matched = []
    hist: dict[str, int] = {}
    for it, out in zip(items, outs):
        gen.append(out.slot_decisions)
        if out.slot_decisions >= max_new:
            at_cap += 1
        try:
            got = parse_plan(out.text)
        except Exception:
            continue
        k = len(got.steps)
        steps.append(k)
        hist[str(k)] = hist.get(str(k), 0) + 1
        if k == len(it.plan.steps):
            eq += 1
        gold = it.plan.steps
        run = 0
        while run < min(k, len(gold)) and got.steps[run] == gold[run]:
            run += 1
        matched.append(run)
        if run == k and k <= len(gold):
            prefix += 1
        if run >= 1:
            first_ok += 1
    n = max(1, len(items))
    return {
        "gold_steps": len(items[0].plan.steps) if items else 0,
        "gen_tokens_mean": round(sum(gen) / n, 2),
        "gen_tokens_max": max(gen) if gen else 0,
        "at_generation_cap": at_cap,
        "emitted_steps_mean": round(sum(steps) / len(steps), 3) if steps else None,
        "emitted_steps_hist": hist,
        "emitted_steps_eq_gold_rate": round(eq / n, 4),
        "prefix_of_gold_rate": round(prefix / n, 4),
        "first_step_correct_rate": round(first_ok / n, 4),
        "matched_prefix_len_mean": round(sum(matched) / len(matched), 3) if matched else None,
    }


def verify_counter(model, tok, planner, item, ops, device) -> dict:
    saved = planner.batch_size
    planner.batch_size = 1
    with ForwardCounter(model) as fc:
        out = planner.build(model, tok, [item], [ops], device)[0]
    planner.batch_size = saved
    return {"reported": out.fwd_passes, "observed": fc.count,
            "ok": out.fwd_passes == fc.count}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--kinds", default=",".join(GRID))
    ap.add_argument("--styles", default="0,1")
    ap.add_argument("--max-new", type=int, default=320)
    ap.add_argument("--temperatures", default="0.0,0.8")
    ap.add_argument("--verify-counter", action="store_true")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, state, head = load_plan_model(args.ckpt, device)
    if head not in ("p1", "p2"):
        raise SystemExit(f"this script covers the autoregressive heads only, got {head}")
    kinds = args.kinds.split(",")
    styles = [int(s) for s in args.styles.split(",")]
    temps = [float(x) for x in args.temperatures.split(",")]

    results: dict = {"config": vars(args), "head": head,
                     "corruption_mixture": mixture_for(head),
                     "train_args": state.get("args"),
                     "holdout": state.get("holdout"),
                     "dropped": state.get("dropped"),
                     "grid": GRID, "max_new": args.max_new}
    sets = {st: build_sets(kinds, args.n, st) for st in styles}

    gen = Generator(model, tok, device, batch_size=args.batch_size)
    for st in styles:
        worlds = {it.world.seed: it.world
                  for items in sets[st].values() for it in items}
        t0 = time.time()
        induced = induce_worlds(gen, worlds, progress=0)
        ind = {"worlds": len(worlds), "pages": 0, "pages_parsed": 0,
               "gold_ops": 0, "induced_ops": 0, "self_verified": 0,
               "exact_text": 0, "behavioural": 0,
               "secs": round(time.time() - t0, 1)}
        for v in induced.values():
            ind["pages"] += v.pages
            ind["pages_parsed"] += v.parsed
            ind["gold_ops"] += v.gold_count
            ind["induced_ops"] += len(v.ops)
            ind["self_verified"] += v.self_verified
            ind["exact_text"] += v.exact
            ind["behavioural"] += v.behavioural
        results[_tag("induction", st)] = ind
        print(f"[induction style={st}] {json.dumps(ind)}", flush=True)
        with open(args.out, "w") as fh:
            json.dump(results, fh, indent=1)

        for name, rt in (("oracle_both", None), ("oracle_both_roundtrip", head)):
            planner = GoldPlanner(roundtrip=rt)
            for key, items in sorted(sets[st].items()):
                ops = [it.world.ops for it in items]
                outs = planner.build(model, tok, items, ops, device)
                _record(results, _tag(name, st), key, grade(items, outs, ops),
                        extra=extras(items, outs, args.max_new))
        with open(args.out, "w") as fh:
            json.dump(results, fh, indent=1)

        for temp in temps:
            planner = make_planner(head, batch_size=args.batch_size,
                                   temperature=temp, max_new=args.max_new, seed=7)
            suffix = f"@T{temp:g}"
            if args.verify_counter:
                key0 = sorted(sets[st])[0]
                item0 = sets[st][key0][0]
                chk = verify_counter(model, tok, planner, item0,
                                     item0.world.ops, device)
                results.setdefault("counter_check", {})[_tag(head + suffix, st)] = chk
                print(f"[counter {head}{suffix}] {json.dumps(chk)}", flush=True)
            for name, gold_plan, gold_ops in CONDITIONS:
                if gold_plan and gold_ops:
                    continue
                for key, items in sorted(sets[st].items()):
                    ops = [it.world.ops if gold_ops
                           else induced[it.world.seed].ops for it in items]
                    t0 = time.time()
                    if gold_plan:
                        outs = GoldPlanner().build(model, tok, items, ops, device)
                    else:
                        outs = planner.build(model, tok, items, ops, device)
                    _record(results, _tag(name + suffix, st), key,
                            grade(items, outs, ops),
                            extra=extras(items, outs, args.max_new),
                            secs=round(time.time() - t0, 1),
                            sample=outs[0].text or outs[0].error)
                    with open(args.out, "w") as fh:
                        json.dump(results, fh, indent=1)
    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)
    _summary(results)
    print(f"[written] {args.out}", flush=True)
    return 0


def _tag(name: str, style: int) -> str:
    return name if style == 0 else name + "@para"


def _record(results, name, key, cell, extra=None, secs=None, sample=None):
    kind, depth = key
    row = cell.as_dict()
    if extra:
        row.update(extra)
    if secs is not None:
        row["secs"] = secs
    if sample is not None:
        row["sample"] = sample[:220]
    results.setdefault(name, {}).setdefault(kind, {})[str(depth)] = row
    print(f"[{name}] {kind} d={depth} n={row['n']} acc={row['acc']:.3f} "
          f"parse={row['parse_rate']:.3f} typed={row['well_typed_rate']:.3f} "
          f"exact={row['exact_gold_plan_rate']:.3f} "
          f"steps={row.get('emitted_steps_mean')} cap={row.get('at_generation_cap')} "
          f"fwd={row['fwd_passes_mean']:.1f}", flush=True)


def _summary(results):
    print("\n=== accuracy by condition, kind and depth ===")
    for name, block in results.items():
        if not isinstance(block, dict) or name in ("config", "counter_check", "grid"):
            continue
        for kind, row in block.items():
            if not isinstance(row, dict) or not row:
                continue
            first = next(iter(row.values()))
            if not isinstance(first, dict) or "acc" not in first:
                continue
            cells = " ".join(f"{d}:{row[d]['acc']:.3f}"
                             for d in sorted(row, key=int))
            print(f"{name:34s} {kind:18s} {cells}")


if __name__ == "__main__":
    raise SystemExit(main())
