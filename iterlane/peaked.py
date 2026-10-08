"""Why sampled decoding reproduces greedy exactly, measured rather than asserted.

Greedy has produced false zeros on this project, so the brief asks for sampled
decoding beside greedy. On these heads the two agree cell for cell, which is
either a bug in how temperature reaches the sampler or a policy so peaked that
sampling at 0.8 returns the argmax anyway. This separates the two: it reports
the mean and the minimum of the largest softmax probability over the slots of a
final pass, and the Hamming distance between the greedy array and a sampled one
on the same items.
"""
from __future__ import annotations
import argparse, importlib, json
import torch
from src.opgraph.data import eval_worlds, make_item
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--depths", default="1,2,3,4,6,8,12")
    ap.add_argument("--iters", type=int, default=8)
    ap.add_argument("--wide", action="store_true")
    a = ap.parse_args()

    ph = importlib.import_module(
        "iterlane.planheads_wide" if a.wide else "src.opgraph.planheads")
    tok = load_tokenizer(a.tokenizer)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    st = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**st["config"]["model"]))
    model.load_state_dict(st["model"]); model.to(dev).eval()
    h = ph.SlotPlanHead(model.cfg.d_model); h.load_state_dict(st["plan_head"])
    model.plan_head = h.to(dev).eval()
    head = st["head"]
    schema = ph.schema_for(head)

    out = {"ckpt": a.ckpt, "head": head, "iters": a.iters, "cells": {}}
    for d in [int(x) for x in a.depths.split(",")]:
        ws = eval_worlds("sequential", a.n, breadth=3, style=0)
        items = [make_item("sequential", w, d, i) for i, w in enumerate(ws)]
        ops = [it.world.ops for it in items]
        arrays, probs = {}, None
        for temp in (0.0, 0.8):
            pl = ph.make_planner(head, iters=a.iters, batch_size=a.n,
                                 temperature=temp, seed=7)
            outs = pl.build(model, tok, items, ops, dev)
            arrays[temp] = [o.slots for o in outs]
        # the confidence of the final pass, measured directly
        pl = ph.make_planner(head, iters=a.iters, batch_size=a.n,
                             temperature=0.0, seed=7)
        prompts = [ph.plan_prompt_text(ops[i], items[i].text, head)
                   for i in range(len(items))]
        ids = [tok.encode(p) for p in prompts]
        pw = max(len(x) for x in ids)
        pad = torch.zeros(len(ids), pw, dtype=torch.long, device=dev)
        okm = torch.zeros(len(ids), pw, dtype=torch.bool, device=dev)
        for i, x in enumerate(ids):
            pad[i, pw - len(x):] = torch.tensor(x, device=dev); okm[i, pw - len(x):] = True
        fmask = ph.field_logit_mask(schema.fields, dev)
        cur = torch.tensor(arrays[0.0], device=dev)
        with torch.no_grad():
            lg = pl._logits(model, model.plan_head, pad, okm, cur, fmask)
            probs = torch.softmax(lg, dim=-1).max(-1).values
        ham = [sum(1 for x, y in zip(arrays[0.0][i], arrays[0.8][i]) if x != y)
               for i in range(len(items))]
        out["cells"][str(d)] = {
            "n": len(items), "slots": schema.n_slots,
            "mean_max_prob": round(float(probs.mean()), 6),
            "min_max_prob": round(float(probs.min()), 6),
            "frac_slots_above_0.999": round(float((probs > 0.999).float().mean()), 4),
            "mean_hamming_greedy_vs_sampled": round(sum(ham) / len(ham), 3),
            "items_identical": sum(1 for x in ham if x == 0),
        }
        print(d, json.dumps(out["cells"][str(d)]), flush=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print("[written]", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
