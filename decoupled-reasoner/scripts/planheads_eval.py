"""Score one plan head on every condition, kind and depth, with its compute.

Conditions, in the order they localise what is left of the failure:

  plan_execute   the head induces the operators and writes the plan
  oracle_ops     gold operators, the head still writes the plan
  oracle_plan    gold plan, the head still induces the operators
  oracle_both    gold plan and gold operators, the executor alone
  oracle_both_rt gold plan pushed through this head's own plan representation
                 and back, then executed

oracle_both must be 1.000 under every head or the harness is broken. The round
trip variant must be 1.000 as well, and it is the stronger check: it fails if
the slot codec cannot express a plan the executor would have answered, which is
a way an arm could be quietly capped.

Every cell reports its denominator, its accuracy, the plan level diagnostics
kept separate from accuracy (parse rate, well typed rate, exact gold plan rate,
and the rate at which a plan that parses still gives a wrong answer), and the
compute the head spent building the plan: forward passes, discrete slot
decisions, and positions evaluated.

Greedy and sampled decoding are both run. Greedy has produced false zeros on
this project, so a greedy zero is not reported alone.
"""

from __future__ import annotations

import argparse
import json
import os
import time

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.planheads import (ForwardCounter, GoldPlanner, SlotPlanHead,
                                   grade, make_planner, mixture_for)
from src.opgraph.run import Generator, induce_worlds
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 7, 8],
    "breadth": [1, 2, 3, 4, 5, 6],
    "novel": [2, 3, 4, 5, 6],
    "sequential_paren": [2, 3, 4, 5, 6],
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


def verify_counter(model, tok, planner, item, ops, device) -> dict:
    """Run one plan at batch one and compare the reported count to the model.

    The hook sits on the token embedding, which every path through the backbone
    touches exactly once per stack invocation, including the key/value cached
    decoder that inlines the blocks rather than calling them.
    """
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
    ap.add_argument("--styles", default="0")
    ap.add_argument("--iters", default="8", help="refinement passes for p3 and p4")
    ap.add_argument("--temperatures", default="0.0,0.8")
    ap.add_argument("--verify-counter", action="store_true")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, state, head = load_plan_model(args.ckpt, device)
    kinds = args.kinds.split(",")
    styles = [int(s) for s in args.styles.split(",")]
    iters = [int(x) for x in args.iters.split(",")]
    temps = [float(x) for x in args.temperatures.split(",")]

    results: dict = {"config": vars(args), "head": head,
                     "corruption_mixture": mixture_for(head),
                     "train_args": state.get("args"),
                     "holdout": state.get("holdout")}
    sets = {st: build_sets(kinds, args.n, st) for st in styles}

    gen = Generator(model, tok, device, batch_size=args.batch_size)
    for st in styles:
        worlds = {it.world.seed: it.world
                  for items in sets[st].values() for it in items}
        induced = induce_worlds(gen, worlds, progress=1)
        ind = {"pages": 0, "pages_parsed": 0, "gold_ops": 0, "induced_ops": 0,
               "self_verified": 0, "exact_text": 0, "behavioural": 0}
        for v in induced.values():
            ind["pages"] += v.pages
            ind["pages_parsed"] += v.parsed
            ind["gold_ops"] += v.gold_count
            ind["induced_ops"] += len(v.ops)
            ind["self_verified"] += v.self_verified
            ind["exact_text"] += v.exact
            ind["behavioural"] += v.behavioural
        results[_tag("induction", st)] = ind
        print(f"[induction style={st}]", json.dumps(ind), flush=True)

        # oracle_both, and the same gold plan pushed through this head's own
        # representation. Both must be 1.000 before any other number is read.
        for name, rt in (("oracle_both", None), ("oracle_both_roundtrip", head)):
            planner = GoldPlanner(roundtrip=rt)
            for key, items in sets[st].items():
                ops = [it.world.ops for it in items]
                outs = planner.build(model, tok, items, ops, device)
                st_ = grade(items, outs, ops)
                _record(results, _tag(name, st), key, st_)

        for temp in temps:
            for it_count in (iters if head in ("p3", "p4") else [0]):
                planner = make_planner(head, batch_size=args.batch_size,
                                       temperature=temp, iters=it_count, seed=7)
                suffix = f"@T{temp:g}"
                if head in ("p3", "p4"):
                    suffix += f"@it{it_count}"
                if args.verify_counter:
                    key0 = sorted(sets[st])[0]
                    item0 = sets[st][key0][0]
                    chk = verify_counter(model, tok, planner, item0,
                                         item0.world.ops, device)
                    results.setdefault("counter_check", {})[
                        _tag(head + suffix, st)] = chk
                    print(f"[counter {head}{suffix}] {json.dumps(chk)}", flush=True)
                    if not chk["ok"]:
                        print("[counter] MISMATCH", flush=True)
                for name, gold_plan, gold_ops in CONDITIONS:
                    if gold_plan and gold_ops:
                        continue  # already scored above, and costs no forwards
                    for key, items in sets[st].items():
                        ops = [it.world.ops if gold_ops
                               else induced[it.world.seed].ops for it in items]
                        t0 = time.time()
                        if gold_plan:
                            outs = GoldPlanner().build(model, tok, items, ops, device)
                        else:
                            outs = planner.build(model, tok, items, ops, device)
                        cell = grade(items, outs, ops)
                        _record(results, _tag(name + suffix, st), key, cell,
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


def _record(results, name, key, cell, secs=None, sample=None):
    kind, depth = key
    row = cell.as_dict()
    if secs is not None:
        row["secs"] = secs
    if sample is not None:
        row["sample"] = sample[:200]
    results.setdefault(name, {}).setdefault(kind, {})[str(depth)] = row
    print(f"[{name}] {kind} d={depth} n={row['n']} acc={row['acc']:.3f} "
          f"parse={row['parse_rate']:.3f} exact={row['exact_gold_plan_rate']:.3f} "
          f"fwd={row['fwd_passes_mean']:.1f}", flush=True)


def _summary(results):
    print("\n=== accuracy by condition, kind and depth ===")
    for name, block in results.items():
        if not isinstance(block, dict) or name in ("config", "counter_check"):
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
