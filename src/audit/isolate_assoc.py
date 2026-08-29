"""Isolate the associativity field on ONE checkpoint.

The audit compared two checkpoints (opgraph.pt without the field, opgraph2.pt
with it) and concluded the depth two and three cells are a coin flip. Two
things changed between those checkpoints: the induction target and the plan
prompt. This holds the weights fixed at opgraph2.pt and changes only the
operator table handed to the planner:

  present   the induced table as the model wrote it
  stripped  the same table with assoc set to None
  flipped   the same table with assoc reversed, graded against the real gold

If "stripped" lands near 0.5 with plans that no longer track the page, the
0.480 and 0.500 in the audited table are the missing field and nothing else.
"""
from __future__ import annotations
import json, os, sys
from dataclasses import replace

import torch
sys.path.insert(0, os.path.expanduser("~/opg"))
from src.opgraph.data import eval_worlds, make_item, plan_prompt
from src.opgraph.opdef import OpError
from src.opgraph.plan import PlanError, answer_text, parse_plan, run_plan
from src.opgraph.run import Generator, induce_worlds, load_model
from src.train.tokenizer import load_tokenizer
from src.audit.seqrerun import fold_answer

CKPT = os.environ.get("CKPT", "runs/opgraph2.pt")
OUT = os.environ.get("OUT", "results/audit_isolate_assoc.json")
DEPTHS = [int(d) for d in os.environ.get("DEPTHS", "1,2,3,4").split(",")]
N = 150


def _norm(s):
    return str(s).strip().strip(".").strip().lower()


def run_arm(gen, items, golds, tables):
    prompts = [plan_prompt(t, it.text) for t, it in zip(tables, items)]
    outs = gen.generate(prompts, max_new=144)
    recs = []
    for gold, tbl, ptext, it in zip(golds, tables, outs, items):
        rec = {"plan": ptext, "prompt": prompts[len(recs)]}
        try:
            plan = parse_plan(ptext)
            v = run_plan(plan, it.world.ops)      # always the true semantics
        except (PlanError, OpError):
            rec.update(ok=False, value=None, steps=None)
            recs.append(rec)
            continue
        got = answer_text(v)
        rec.update(ok=_norm(got) == _norm(gold), value=got, steps=len(plan.steps))
        recs.append(rec)
    return recs


def main():
    tok = load_tokenizer("/home/ec2-user/data/tokenizer_v2.json")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_model(CKPT, device)
    gen = Generator(model, tok, device, batch_size=32)

    worlds = eval_worlds("sequential", N, breadth=3)
    induced = induce_worlds(gen, {w.seed: w for w in worlds}, progress=1)
    print("[induction done]", flush=True)

    out = {}
    rows = []
    for d in DEPTHS:
        items = [make_item("sequential", w, d, i) for i, w in enumerate(worlds)]
        golds = [it.gold for it in items]

        present, stripped, flipped = [], [], []
        for it in items:
            t = induced[it.world.seed].ops
            present.append(t)
            stripped.append({k: replace(o, assoc=None) for k, o in t.items()})
            flipped.append({k: replace(o, assoc=("right" if o.assoc == "left"
                                                 else "left" if o.assoc else None))
                            for k, o in t.items()})

        A = run_arm(gen, items, golds, present)
        B = run_arm(gen, items, golds, stripped)
        C = run_arm(gen, items, golds, flipped)

        accA = sum(r["ok"] for r in A) / len(A)
        accB = sum(r["ok"] for r in B) / len(B)
        accC = sum(r["ok"] for r in C) / len(C)
        identAB = sum(1 for a, b in zip(A, B) if a["plan"] == b["plan"])
        identAC = sum(1 for a, c in zip(A, C) if a["plan"] == c["plan"])
        # what did the stripped arm compute
        foldB = {"left": 0, "right": 0, "both": 0, "neither": 0}
        for r, it in zip(B, items):
            lf = fold_answer(it.text, it.world.ops, "left")
            rf = fold_answer(it.text, it.world.ops, "right")
            v = r["value"]
            if v is None:
                foldB["neither"] += 1
            elif lf == rf and _norm(v) == _norm(lf):
                foldB["both"] += 1
            elif _norm(v) == _norm(lf):
                foldB["left"] += 1
            elif _norm(v) == _norm(rf):
                foldB["right"] += 1
            else:
                foldB["neither"] += 1
        # stripped accuracy split by what the page actually says
        pa = {}
        for r, it in zip(B, items):
            page = [p for p in it.world.pages
                    if p.key == f"binop:{it.symbols[0]}"][0]
            k = "right" if page.right_assoc else "left"
            n, c = pa.get(k, (0, 0))
            pa[k] = (n + 1, c + int(r["ok"]))
        out[str(d)] = {
            "n": len(items), "present": round(accA, 4), "stripped": round(accB, 4),
            "flipped_graded_on_true_gold": round(accC, 4),
            "identical_plan_present_vs_stripped": identAB,
            "identical_plan_present_vs_flipped": identAC,
            "stripped_fold": foldB,
            "stripped_acc_by_page_assoc": {k: [v[0], v[1], round(v[1] / v[0], 4)]
                                           for k, v in pa.items()},
            "stripped_pair_sum_proxy": round(accB + (1 - accB), 4),
            "steps_present": sorted({r["steps"] for r in A}, key=lambda x: (x is None, x)),
            "steps_stripped": sorted({r["steps"] for r in B}, key=lambda x: (x is None, x)),
        }
        print(f"[d{d}] present={accA:.3f} stripped={accB:.3f} "
              f"flipped={accC:.3f} identAB={identAB} identAC={identAC} "
              f"fold={foldB}", flush=True)
        for i, (a, b, c) in enumerate(zip(A, B, C)):
            rows.append({"depth": d, "i": i, "gold": golds[i],
                         "present_plan": a["plan"], "present_ok": a["ok"],
                         "stripped_plan": b["plan"], "stripped_ok": b["ok"],
                         "flipped_plan": c["plan"], "flipped_ok": c["ok"],
                         "prompt_present": a["prompt"], "prompt_stripped": b["prompt"]})
        with open(OUT, "w") as fh:
            json.dump({"ckpt": CKPT, "cells": out}, fh, indent=1)
    with open(OUT.replace(".json", "_items.json"), "w") as fh:
        json.dump(rows, fh)
    print("[written]", OUT, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
