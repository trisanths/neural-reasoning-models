"""Check 8 on the OTHER checkpoint: does runs/opgraph2.pt read the transposed page?

The audit ran the transposition on runs/opgraph.pt only. opgraph2.pt is the
checkpoint the current shipped report is built from, and it emits the
associativity clause the audited one drops. If it follows the page here, the
audit's verdict is checkpoint-local.
"""
import dataclasses, json, os, sys
from collections import Counter
from src.audit.surfaces import transpose_world
from src.opgraph.data import eval_worlds, make_item
from src.opgraph.invent import copyable
from src.opgraph.opdef import OpError, serialize
from src.opgraph.plan import PlanError, answer_text, run_plan
from src.opgraph.run import Generator, induce_worlds, load_model
from src.train.tokenizer import load_tokenizer

DEPTHS = [1, 2, 3, 4, 8]
MYPROBES = [(3, 8), (8, 3), (1, 12), (12, 1), (5, 5), (0, 7), (7, 0), (2, 9), (9, 2), (6, 11)]
CKPT = os.environ.get("CKPT", "runs/opgraph2.pt")

def _norm(s): return str(s).strip().strip(".").strip().lower()
def _safe(op, a):
    try: return op(*a)
    except OpError: return "__err__"

tok = load_tokenizer("/home/ec2-user/data/tokenizer_v2.json")
base = eval_worlds("sequential", 150, breadth=3, style=0)
tworlds = [transpose_world(w) for w in base]
model, _ = load_model(CKPT, "cuda")
gen = Generator(model, tok, "cuda", batch_size=16)
induced = induce_worlds(gen, {w.seed: w for w in tworlds}, progress=1)

c = Counter()
samples = []
for wp, wt in zip(tworlds, base):
    ind = induced[wp.seed]
    for p in wp.pages:
        if not p.key.startswith("binop:"):
            continue
        sym = p.ops[0].symbol
        page_op = p.ops[0]
        train_op = next(o for q in wt.pages for o in q.ops if o.symbol == sym)
        vp = [_safe(page_op, a) for a in MYPROBES]
        vt = [_safe(train_op, a) for a in MYPROBES]
        if vp == vt:
            c["indistinguishable"] += 1; continue
        c["distinguishable"] += 1
        got = ind.ops.get(sym)
        if got is None:
            c["absent"] += 1; continue
        vg = [_safe(got, a) for a in MYPROBES]
        if vg == vp: c["follows_page"] += 1
        elif vg == vt: c["follows_training"] += 1
        else: c["neither"] += 1
        if got.assoc == page_op.assoc: c["assoc_kept"] += 1
        if len(samples) < 4:
            samples.append({"page": serialize(page_op), "got": serialize(got)})
print(f"[{CKPT}] identity:", json.dumps(dict(c)), flush=True)
for s in samples:
    print("  page:", s["page"], flush=True)
    print("  got :", s["got"], flush=True)

cells = {}
for d in DEPTHS:
    ctrl = [make_item("sequential", w, d, i) for i, w in enumerate(base)]
    items, gp, gt = [], [], []
    for it, tw in zip(ctrl, tworlds):
        pg = answer_text(run_plan(it.plan, tw.ops))
        if pg == it.gold or copyable(pg, it.text):
            continue
        items.append(dataclasses.replace(it, world=tw, gold=pg))
        gp.append(pg); gt.append(it.gold)
    vals = []
    for it in items:
        try:
            vals.append(answer_text(run_plan(it.plan, induced[it.world.seed].ops)))
        except (PlanError, OpError):
            vals.append("")
    okp = sum(_norm(v) == _norm(g) for v, g in zip(vals, gp))
    okt = sum(_norm(v) == _norm(g) for v, g in zip(vals, gt))
    cells[d] = {"n": len(items), "page": okp, "train": okt}
    print(f"[oracle_plan perm {CKPT}] d={d} n={len(items)} page={okp} train={okt}", flush=True)
print("TOTAL n=%d page=%d train=%d" % (sum(v["n"] for v in cells.values()),
      sum(v["page"] for v in cells.values()), sum(v["train"] for v in cells.values())), flush=True)
json.dump({"ckpt": CKPT, "identity": dict(c), "cells": {str(k): v for k, v in cells.items()},
           "samples": samples}, open("results/verify_c8_opgraph2.json", "w"), indent=1)
print("[written] results/verify_c8_opgraph2.json", flush=True)
