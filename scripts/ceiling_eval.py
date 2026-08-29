"""Score one training-ceiling arm, and persist every plan it wrote.

The headline measurement is not accuracy. It is the plan the model emitted:
how many steps it has against how many the question needs, how many distinct
operator symbols it names against how many the question needs, and whether
the operands, the ordering and the register wiring stay correct as the
question gets deeper.

Every item produces one JSONL record holding the emitted plan text and its
structural comparison against gold, so any number in the writeup can be
recomputed from the artifact rather than trusted.

Four conditions, as registered:

  plan_execute  model induces the operators, model writes the plan, executor runs it
  oracle_plan   model induces, gold plan, executor runs it
  oracle_ops    gold operators, model writes the plan, executor runs it
  oracle_both   gold operators, gold plan; must come out at 1.000

Gold operators do not depend on the page wording, so the two ops-oracle
conditions run on style 0 only. The two gold-plan conditions ask nothing of
the decoder beyond induction, so they run greedy only; the model-plan
conditions run at every requested temperature.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter

import torch

from src.ceiling.gen import TGenerator
from src.ceiling.planmetrics import measure
from src.opgraph.data import eval_worlds, make_item, plan_prompt
from src.opgraph.opdef import OpError
from src.opgraph.plan import (PlanError, answer_text, parse_plan, run_plan,
                              serialize_plan)
from src.opgraph.run import induce_worlds, load_model
from src.train.tokenizer import load_tokenizer

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 32],
    "sequential_paren": [2, 3, 4, 5, 6, 8],
    "breadth": [1, 2, 3, 4, 5, 6],
    "novel": [2, 3, 4, 5, 6, 8],
    "same_page_pair": [2],
    "units": [1],
}

CONDS = {  # name -> (gold_plan, gold_ops)
    "plan_execute": (False, False),
    "oracle_plan": (True, False),
    "oracle_ops": (False, True),
    "oracle_both": (True, True),
}


def build_sets(kinds, grid, n, style):
    sets = {}
    cache = {}
    for kind in kinds:
        for depth in grid[kind]:
            breadth = depth if kind == "breadth" else 3
            key = (kind, breadth)
            if key not in cache:
                cache[key] = eval_worlds(kind, n, breadth=breadth, style=style)
            sets[(kind, depth)] = [make_item(kind, w, depth, i)
                                   for i, w in enumerate(cache[key])]
    return sets


def _norm(s) -> str:
    return str(s).strip().strip(".").strip().lower()


def budget_for(req_steps: int, extra: int = 0) -> int:
    """Token budget for a plan of the required length, with headroom.

    Deliberately generous. A plan truncated by the cap would read as a short
    plan, and short plans are the thing being counted.
    """
    return 64 + 22 * req_steps + extra


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True, help="summary json")
    ap.add_argument("--records", default=None, help="jsonl of every item")
    ap.add_argument("--arm", default="", help="label for the records")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--kinds", default=",".join(GRID))
    ap.add_argument("--styles", default="0,1")
    ap.add_argument("--temperatures", default="0.0,0.8")
    ap.add_argument("--conditions", default=",".join(CONDS))
    ap.add_argument("--depths", default="", help="override, e.g. sequential=1,2,3")
    ap.add_argument("--induce-max-new", type=int, default=288)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    grid = {k: list(v) for k, v in GRID.items()}
    for chunk in [c for c in args.depths.split(";") if c.strip()]:
        k, v = chunk.split("=")
        grid[k.strip()] = [int(x) for x in v.split(",")]

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    recpath = args.records or (args.out.rsplit(".", 1)[0] + ".records.jsonl")
    os.makedirs(os.path.dirname(recpath) or ".", exist_ok=True)
    rec_fh = open(recpath, "w")

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    kinds = [k for k in args.kinds.split(",") if k]
    styles = [int(s) for s in args.styles.split(",")]
    temps = [float(t) for t in args.temperatures.split(",")]
    conds = [c for c in args.conditions.split(",") if c]

    model, _ = load_model(args.ckpt, device)
    greedy = TGenerator(model, tok, device, batch_size=args.batch_size,
                        temperature=0.0, seed=args.seed)
    gens = {0.0: greedy}
    for t in temps:
        if t not in gens:
            gens[t] = TGenerator(model, tok, device, batch_size=args.batch_size,
                                 temperature=t, seed=args.seed)

    results: dict = {"config": vars(args), "cells": {}}
    t0 = time.time()

    for style in styles:
        sets = build_sets(kinds, grid, args.n, style)
        need_induced = any(not CONDS[c][1] for c in conds)
        induced = {}
        if need_induced:
            worlds = {it.world.seed: it.world
                      for items in sets.values() for it in items}
            print(f"[induce] style={style} worlds={len(worlds)}", flush=True)
            induced = induce_worlds(greedy, worlds, max_new=args.induce_max_new,
                                    progress=1)
            stats = Counter()
            for ind in induced.values():
                stats["pages"] += ind.pages
                stats["pages_parsed"] += ind.parsed
                stats["gold_ops"] += ind.gold_count
                stats["induced_ops"] += len(ind.ops)
                stats["self_verified"] += ind.self_verified
                stats["exact_text"] += ind.exact
                stats["behavioural"] += ind.behavioural
            results[f"induction_style{style}"] = dict(stats)
            print(f"[induction style={style}] {json.dumps(dict(stats))}",
                  flush=True)

        for cond in conds:
            gold_plan, gold_ops = CONDS[cond]
            if style != 0 and gold_ops:
                continue  # gold operators do not depend on the page wording
            use_temps = [0.0] if gold_plan else temps
            for temp in use_temps:
                gen = gens[temp]
                for kind in kinds:
                    for depth in grid[kind]:
                        items = sets[(kind, depth)]
                        cell = _run_cell(gen, items, induced, gold_plan,
                                         gold_ops, args, cond, style, temp,
                                         kind, depth, rec_fh)
                        key = f"{cond}|s{style}|t{temp}|{kind}|{depth}"
                        results["cells"][key] = cell
                        print(f"[{key}] acc={cell['acc']:.3f} n={cell['n']} "
                              f"steps mean={cell['emit_steps_mean']} "
                              f"max={cell['emit_steps_max']} req={depth_req(cell)} "
                              f"sym mean={cell['emit_symbols_mean']} "
                              f"parse={cell['parse_rate']:.3f} "
                              f"secs={round(time.time() - t0)}", flush=True)
                        with open(args.out, "w") as fh:
                            json.dump(results, fh, indent=1)
    rec_fh.close()
    results["records"] = recpath
    results["seconds"] = round(time.time() - t0, 1)
    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)

    bad = [k for k, c in results["cells"].items()
           if k.startswith("oracle_both") and c["acc"] < 1.0]
    if bad:
        print("[HARNESS BROKEN] oracle_both below 1.000 in cells: "
              + ", ".join(bad), flush=True)
    print(f"[written] {args.out} and {recpath}", flush=True)
    return 1 if bad else 0


def depth_req(cell):
    return cell.get("req_steps_mean")


def _run_cell(gen, items, induced, gold_plan, gold_ops, args, cond, style,
              temp, kind, depth, rec_fh) -> dict:
    ops_for = []
    for it in items:
        if gold_ops:
            ops_for.append(it.world.ops)
        else:
            ind = induced.get(it.world.seed)
            ops_for.append(ind.ops if ind else {})
    req = max(len(it.plan.steps) for it in items)
    outs: list[dict]
    if gold_plan:
        outs = [{"text": serialize_plan(it.plan), "ntok": 0, "hit_cap": False}
                for it in items]
    else:
        prompts = [plan_prompt(ops_for[i], items[i].text)
                   for i in range(len(items))]
        outs = gen.generate_full(prompts, max_new=budget_for(req))

    n = len(items)
    agg = {
        "cond": cond, "style": style, "temperature": temp, "kind": kind,
        "depth": depth, "n": n, "gold_plan": gold_plan, "gold_ops": gold_ops,
    }
    correct = 0
    counters = Counter()
    steps: list[int] = []
    syms: list[int] = []
    reqs: list[int] = []
    reqsyms: list[int] = []
    lenhist = Counter()
    reasons = Counter()
    golds = Counter()
    for i, it in enumerate(items):
        m = measure(outs[i]["text"], it.plan, ops_for[i])
        m["hit_cap"] = outs[i]["hit_cap"]
        m["ntok"] = outs[i]["ntok"]
        golds[_norm(it.gold)] += 1
        reqs.append(m["req_steps"])
        reqsyms.append(m["req_symbols"])
        ok = False
        reason = "plan_parse"
        value = None
        if m["parse_ok"]:
            steps.append(m["steps"])
            syms.append(m["n_symbols"])
            lenhist[str(m["steps"])] += 1
            for f in ("well_typed", "exact_gold", "shape_match",
                      "operands_match", "symbol_seq_match", "symbol_collapse"):
                counters[f] += int(bool(m[f]))
            counters["dead_steps"] += m["dead_steps"]
            counters["builtins"] += m["builtins"]
            try:
                value = run_plan(parse_plan(outs[i]["text"]), ops_for[i])
                ok = _norm(answer_text(value)) == _norm(it.gold)
                reason = "ok" if ok else "wrong_value"
            except (PlanError, OpError) as exc:
                reason = "execute"
                m["exec_error"] = str(exc)[:120]
        counters["hit_cap"] += int(bool(m["hit_cap"]))
        counters["empty"] += int(bool(m["empty"]))
        counters["parse_ok"] += int(bool(m["parse_ok"]))
        counters["contains_gold"] += int(
            _norm(it.gold) in _norm(outs[i]["text"]).split())
        reasons[reason] += 1
        correct += int(ok)
        rec = {"arm": args.arm, "cond": cond, "style": style,
               "temperature": temp, "kind": kind, "depth": depth,
               "world": it.world.seed, "i": i, "gold_answer": it.gold,
               "gold_plan": serialize_plan(it.plan),
               "value": answer_text(value) if value is not None else None,
               "correct": ok, "reason": reason}
        rec.update(m)
        rec_fh.write(json.dumps(rec) + "\n")

    parsed = max(1, counters["parse_ok"])
    agg.update({
        "acc": round(correct / n, 4),
        "correct": correct,
        "majority_gold_rate": round(golds.most_common(1)[0][1] / n, 4),
        "distinct_golds": len(golds),
        "parse_rate": round(counters["parse_ok"] / n, 4),
        "empty_rate": round(counters["empty"] / n, 4),
        "hit_cap_rate": round(counters["hit_cap"] / n, 4),
        "well_typed_rate": round(counters["well_typed"] / n, 4),
        "exact_gold_rate": round(counters["exact_gold"] / n, 4),
        "shape_match_rate": round(counters["shape_match"] / n, 4),
        "operands_match_rate": round(counters["operands_match"] / n, 4),
        "symbol_seq_match_rate": round(counters["symbol_seq_match"] / n, 4),
        "symbol_collapse_rate": round(counters["symbol_collapse"] / n, 4),
        "contains_gold_rate": round(counters["contains_gold"] / n, 4),
        "dead_steps_total": counters["dead_steps"],
        "builtin_steps_total": counters["builtins"],
        "req_steps_mean": round(sum(reqs) / n, 3),
        "req_steps_max": max(reqs),
        "req_symbols_mean": round(sum(reqsyms) / n, 3),
        "req_symbols_max": max(reqsyms),
        "emit_steps_mean": round(sum(steps) / len(steps), 3) if steps else None,
        "emit_steps_max": max(steps) if steps else None,
        "emit_symbols_mean": round(sum(syms) / len(syms), 3) if syms else None,
        "emit_symbols_max": max(syms) if syms else None,
        "emit_len_hist": dict(lenhist),
        "reasons": dict(reasons),
        "parsed_denominator": parsed,
    })
    return agg


if __name__ == "__main__":
    raise SystemExit(main())
