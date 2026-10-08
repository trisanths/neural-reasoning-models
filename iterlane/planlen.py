"""How many steps does the head write, against how many the question needs.

Accuracy going to zero at depth four says the plan is wrong. It does not say
how. If the emitted plan is three steps long whatever the question asks, the
failure is a length prior learned from a holdout that stops at three, and every
other diagnostic is downstream of that. This counts the steps in the plan each
head actually emits and puts it beside the gold length.
"""
from __future__ import annotations
import argparse, importlib, json
import torch
from src.opgraph.data import eval_worlds, make_item
from src.opgraph.plan import parse_plan, PlanError
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--depths", default="1,2,3,4,5,6,8,12")
    ap.add_argument("--kind", default="sequential")
    ap.add_argument("--iters", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--wide", action="store_true")
    a = ap.parse_args()

    ph = importlib.import_module(
        "iterlane.planheads_wide" if a.wide else "src.opgraph.planheads")
    tok = load_tokenizer(a.tokenizer)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    st = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**st["config"]["model"]))
    model.load_state_dict(st["model"]); model.to(dev).eval()
    model.plan_head = None
    if st.get("plan_head") is not None:
        h = ph.SlotPlanHead(model.cfg.d_model); h.load_state_dict(st["plan_head"])
        model.plan_head = h.to(dev).eval()
    head = st["head"]

    out = {"ckpt": a.ckpt, "head": head, "kind": a.kind,
           "temperature": a.temperature, "iters": a.iters, "cells": {}}
    for d in [int(x) for x in a.depths.split(",")]:
        b = d if a.kind == "breadth" else 3
        ws = eval_worlds(a.kind, a.n, breadth=b, style=0)
        items = [make_item(a.kind, w, d, i) for i, w in enumerate(ws)]
        ops = [it.world.ops for it in items]
        pl = ph.make_planner(head, iters=a.iters, batch_size=a.batch_size,
                             temperature=a.temperature, seed=7)
        outs = pl.build(model, tok, items, ops, dev)
        hist, gold_hist, unparsed = {}, {}, 0
        lens = []
        for it, o in zip(items, outs):
            gold_hist[len(it.plan.steps)] = gold_hist.get(len(it.plan.steps), 0) + 1
            if o.error:
                unparsed += 1
                continue
            try:
                p = parse_plan(o.text)
            except PlanError:
                unparsed += 1
                continue
            k = len(p.steps)
            hist[k] = hist.get(k, 0) + 1
            lens.append(k)
        out["cells"][str(d)] = {
            "n": len(items),
            "gold_steps": sorted(gold_hist.items()),
            "emitted_steps_histogram": dict(sorted(hist.items())),
            "mean_emitted_steps": round(sum(lens) / len(lens), 3) if lens else None,
            "max_emitted_steps": max(lens) if lens else None,
            "unparsed": unparsed,
            "frac_emitting_gold_length": round(
                hist.get(d, 0) / len(items), 4) if items else 0.0,
        }
        print(d, json.dumps(out["cells"][str(d)]), flush=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print("[written]", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
