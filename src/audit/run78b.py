"""Second pass: dump every induced operator, and run the out-of-support control.

Two things the first pass did not produce.

The induced operator table is written out per world and per wording, so the
question "was the symbol the question needs present at all, and if it was, was
its body right" can be answered on CPU without another decode.

The out-of-support control renumbers every binary operator's constants to values
the generator can never draw during training, keeps the trained wording and the
trained operand roles, and re-runs the plan path. It is the positive control for
the transposition: a model that reads numerals off the page passes it.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter

import torch

from src.audit.surfaces import (renumber_world, restyle_world, transpose_world)
from src.opgraph.data import eval_worlds, make_item, plan_prompt
from src.opgraph.opdef import OpError, serialize
from src.opgraph.plan import (PlanError, answer_text, parse_plan, run_plan,
                              serialize_plan)
from src.opgraph.run import Generator, induce_worlds, load_model, score_direct
from src.train.tokenizer import load_tokenizer

DEPTHS = [1, 2, 3, 4, 8]


def _norm(s) -> str:
    return str(s).strip().strip(".").strip().lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--direct-ckpt", default="runs/direct.pt")
    ap.add_argument("--opgraph-ckpt", default="runs/opgraph.pt")
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--out", default="results/audit_c78b.json")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=32)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    base = eval_worlds("sequential", args.n, breadth=3, style=0)
    families = {
        "s0": [restyle_world(w, 0) for w in base],
        "s2": [restyle_world(w, 2) for w in base],
        "s3": [restyle_world(w, 3) for w in base],
        "s4": [restyle_world(w, 4) for w in base],
        "perm": [transpose_world(w) for w in base],
        "renum": [renumber_world(w) for w in base],
    }
    res: dict = {"config": vars(args), "depths": DEPTHS}

    model, _ = load_model(args.opgraph_ckpt, device)
    gen = Generator(model, tok, device, batch_size=args.batch_size)
    dump: dict = {}
    for tag, worlds in families.items():
        induced = induce_worlds(gen, {w.seed: w for w in worlds}, progress=1)
        dump[tag] = {}
        for w in worlds:
            ind = induced[w.seed]
            gold = {}
            for p in w.pages:
                if p.key.startswith("binop:"):
                    gold[p.ops[0].symbol] = serialize(p.ops[0])
            dump[tag][str(w.seed)] = {
                "gold_binops": gold,
                "induced": {s: serialize(o) for s, o in ind.ops.items()
                            if s in gold},
                "parsed_pages": ind.parsed,
            }
        print(f"[dumped] {tag}", flush=True)
        if tag != "renum":
            continue
        for d in DEPTHS:
            items = [make_item("sequential", w, d, i) for i, w in enumerate(worlds)]
            for name, gplan, gops in (("plan_execute", False, False),
                                      ("oracle_plan", True, False),
                                      ("oracle_ops", False, True),
                                      ("oracle_both", True, True)):
                vals, reasons = _planned(gen, items, induced, gplan, gops)
                ok = [_norm(v) == _norm(it.gold) for v, it in zip(vals, items)]
                res.setdefault(name, {})[str(d)] = {
                    "n": len(ok), "acc": round(sum(ok) / len(ok), 4),
                    "reasons": dict(Counter(reasons))}
                print(f"[renum {name}] d={d} acc={sum(ok) / len(ok):.3f}",
                      flush=True)
    del model, gen
    torch.cuda.empty_cache()

    model, _ = load_model(args.direct_ckpt, device)
    gen = Generator(model, tok, device, batch_size=args.batch_size)
    for d in DEPTHS:
        items = [make_item("sequential", w, d, i)
                 for i, w in enumerate(families["renum"])]
        for name, oracle in (("direct_all", False), ("direct_oracle_page", True)):
            ok, _outs = score_direct(gen, items, oracle)
            res.setdefault(name, {})[str(d)] = {
                "n": len(ok), "acc": round(sum(ok) / len(ok), 4)}
            print(f"[renum {name}] d={d} acc={sum(ok) / len(ok):.3f}", flush=True)
    del model, gen
    torch.cuda.empty_cache()

    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    with open(args.out.replace(".json", "_ops.json"), "w") as fh:
        json.dump(dump, fh)
    print("[written]", args.out, flush=True)
    return 0


def _planned(gen, items, induced, use_gold_plan, use_gold_ops, max_new=144):
    plans: dict[int, str] = {}
    if not use_gold_plan:
        prompts = []
        for it in items:
            ops = it.world.ops if use_gold_ops else induced[it.world.seed].ops
            prompts.append(plan_prompt(ops, it.text))
        for it, o in zip(items, gen.generate(prompts, max_new=max_new)):
            plans[id(it)] = o
    out, reasons = [], []
    for it in items:
        ops = it.world.ops if use_gold_ops else induced[it.world.seed].ops
        ptext = serialize_plan(it.plan) if use_gold_plan else plans[id(it)]
        try:
            plan = parse_plan(ptext)
        except PlanError:
            out.append("")
            reasons.append("plan_parse")
            continue
        try:
            out.append(answer_text(run_plan(plan, ops)))
            reasons.append("ok")
        except (PlanError, OpError):
            out.append("")
            reasons.append("execute")
    return out, reasons


if __name__ == "__main__":
    raise SystemExit(main())
