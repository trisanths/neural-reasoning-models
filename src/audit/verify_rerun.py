"""Independent re-run of the decisive checks 7/8 measurements.

Rebuilds the perm and style-2 item sets with the shipped generator, re-runs the
shipped induction path on the shipped opgraph checkpoint, classifies each
induced binary operator with a probe set of my own, and scores oracle_plan
(gold plan + induced operators) against both golds.
"""
import dataclasses, json, sys
from collections import Counter
import torch

from src.audit.surfaces import restyle_world, transpose_world
from src.opgraph.data import eval_worlds, make_item
from src.opgraph.invent import copyable
from src.opgraph.opdef import OpError, serialize
from src.opgraph.plan import PlanError, answer_text, run_plan
from src.opgraph.run import Generator, induce_worlds, load_model
from src.train.tokenizer import load_tokenizer

DEPTHS = [1, 2, 3, 4, 8]
# deliberately different from run78's PROBES
MYPROBES = [(3, 8), (8, 3), (1, 12), (12, 1), (5, 5), (0, 7), (7, 0), (2, 9), (9, 2), (6, 11)]
N = 150

def _norm(s):
    return str(s).strip().strip(".").strip().lower()

def _safe(op, args):
    try:
        return op(*args)
    except OpError:
        return "__err__"

def main():
    tok = load_tokenizer("/home/ec2-user/data/tokenizer_v2.json")
    dev = "cuda"
    base = eval_worlds("sequential", N, breadth=3, style=0)
    tworlds = [transpose_world(w) for w in base]
    s2worlds = [restyle_world(w, 2) for w in base]

    # sanity: the transposed page differs from the trained page only in the rule
    # clause and the two example values
    diffs = []
    for a, b in zip(base[:5], tworlds[:5]):
        for p, q in zip(a.pages, b.pages):
            if p.text == q.text:
                continue
            la, lb = p.text.split("\n"), q.text.split("\n")
            diffs.append(sum(1 for x, y in zip(la, lb) if x != y))
    print("[sanity] differing lines per transposed binop page:", Counter(diffs), flush=True)

    model, _ = load_model("runs/opgraph.pt", dev)
    gen = Generator(model, tok, dev, batch_size=32)

    out = {}
    for tag, worlds in (("perm", tworlds), ("s2", s2worlds)):
        induced = induce_worlds(gen, {w.seed: w for w in worlds}, progress=1)
        if tag == "perm":
            c = Counter()
            for wp, wt in zip(worlds, base):
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
                        c["indistinguishable"] += 1
                        continue
                    c["distinguishable"] += 1
                    got = ind.ops.get(sym)
                    if got is None:
                        c["absent"] += 1
                        continue
                    vg = [_safe(got, a) for a in MYPROBES]
                    if vg == vp: c["follows_page"] += 1
                    elif vg == vt: c["follows_training"] += 1
                    else: c["neither"] += 1
                    if got.assoc == page_op.assoc: c["assoc_kept"] += 1
            print("[rerun identity]", json.dumps(dict(c)), flush=True)
            out["identity"] = dict(c)

        cells = {}
        for d in DEPTHS:
            ctrl = [make_item("sequential", w, d, i) for i, w in enumerate(base)]
            if tag == "perm":
                items, gp, gt = [], [], []
                for it, tw in zip(ctrl, tworlds):
                    pg = answer_text(run_plan(it.plan, tw.ops))
                    if pg == it.gold or copyable(pg, it.text):
                        continue
                    items.append(dataclasses.replace(it, world=tw, gold=pg))
                    gp.append(pg); gt.append(it.gold)
            else:
                items = [make_item("sequential", w, d, i) for i, w in enumerate(worlds)]
                gp = [it.gold for it in items]; gt = list(gp)
            vals, reasons = [], Counter()
            for it in items:
                ops = induced[it.world.seed].ops
                try:
                    vals.append(answer_text(run_plan(it.plan, ops)))
                    reasons["ok"] += 1
                except (PlanError, OpError):
                    vals.append(""); reasons["execute"] += 1
            okp = sum(_norm(v) == _norm(g) for v, g in zip(vals, gp))
            okt = sum(_norm(v) == _norm(g) for v, g in zip(vals, gt))
            cells[d] = {"n": len(items), "page": okp, "train": okt,
                        "acc_page": round(okp / len(items), 4),
                        "acc_train": round(okt / len(items), 4),
                        "reasons": dict(reasons)}
            print(f"[oracle_plan {tag}] d={d} n={len(items)} page={okp} train={okt}", flush=True)
        out[tag] = cells
        tot_n = sum(v["n"] for v in cells.values())
        print(f"[oracle_plan {tag}] TOTAL n={tot_n} page={sum(v['page'] for v in cells.values())} "
              f"train={sum(v['train'] for v in cells.values())}", flush=True)

    with open("results/verify_c78_rerun.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("[written] results/verify_c78_rerun.json", flush=True)

if __name__ == "__main__":
    sys.exit(main() or 0)
