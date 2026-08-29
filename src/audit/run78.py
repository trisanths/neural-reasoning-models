"""Checks 7 and 8 on the sequential depth curve, plus a parser-only baseline.

Check 7 holds the seeds, the operators, the questions, the gold plans, the gold
answers and the page count fixed, re-renders every page in three wordings no arm
trained on, and re-runs every condition.

Check 8 keeps the trained wording and the glyph and swaps the two operand roles
inside each binary operator's rule, recomputing the page's own worked examples so
the page states the swapped rule twice. Every condition is then scored twice,
once against the answer the page implies and once against the answer the
operator's training identity implies.

The parser baseline in `src/audit/pageparser.py` is run on the same items, from
the same context string `direct_all` gets.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
from collections import Counter

import torch

from src.audit import pageparser
from src.audit.surfaces import restyle_world, transpose_world
from src.opgraph.data import eval_worlds, make_item
from src.opgraph.invent import copyable
from src.opgraph.opdef import OpError, parse_operators, serialize
from src.opgraph.plan import (PlanError, answer_text, parse_plan, run_plan,
                              serialize_plan)
from src.opgraph.run import (Generator, induce_worlds, load_model, score_direct,
                             score_trace)
from src.train.tokenizer import load_tokenizer

KIND = "sequential"
DEPTHS = [1, 2, 3, 4, 8]
SURFACE_TAGS = {"s0": 0, "s2": 2, "s3": 3, "s4": 4}
PROBES = [(7, 4), (12, 5), (3, 9), (11, 2), (2, 11), (0, 6), (5, 1), (1, 5)]


def _norm(s) -> str:
    return str(s).strip().strip(".").strip().lower()


def build(n: int):
    """Every item set, with the transposed set carrying two golds."""
    base = eval_worlds(KIND, n, breadth=3, style=0)
    sets: dict = {}
    golds: dict = {}
    for tag, style in SURFACE_TAGS.items():
        worlds = [restyle_world(w, style) for w in base]
        if style == 0:
            for a, b in zip(base, worlds):
                assert [p.text for p in a.pages] == [p.text for p in b.pages]
        for d in DEPTHS:
            items = [make_item(KIND, w, d, i) for i, w in enumerate(worlds)]
            sets[(tag, d)] = items
            golds[(tag, d)] = ([it.gold for it in items], [it.gold for it in items])
    # transposed: same questions as s0, page-implied gold, training-implied gold
    tworlds = [transpose_world(w) for w in base]
    drop = Counter()
    for d in DEPTHS:
        ctrl = sets[("s0", d)]
        items, gp, gt = [], [], []
        for it, tw in zip(ctrl, tworlds):
            page_gold = answer_text(run_plan(it.plan, tw.ops))
            if page_gold == it.gold:
                drop["indistinguishable"] += 1
                continue
            if copyable(page_gold, it.text):
                drop["copyable"] += 1
                continue
            moved = dataclasses.replace(it, world=tw, gold=page_gold)
            items.append(moved)
            gp.append(page_gold)
            gt.append(it.gold)
        sets[("perm", d)] = items
        golds[("perm", d)] = (gp, gt)
    return sets, golds, dict(drop), base, tworlds


def _cell(ok_p, ok_t):
    n = len(ok_p)
    return {"n": n,
            "acc_page": round(sum(ok_p) / n, 4) if n else 0.0,
            "acc_train": round(sum(ok_t) / n, 4) if n else 0.0}


def record(res, name, tag, depth, outs, gp, gt, sample=None):
    ok_p = [_norm(o) == _norm(g) for o, g in zip(outs, gp)]
    ok_t = [_norm(o) == _norm(g) for o, g in zip(outs, gt)]
    slot = res.setdefault(name, {}).setdefault(tag, {})
    slot[str(depth)] = _cell(ok_p, ok_t)
    if sample:
        slot[str(depth)]["samples"] = sample
    print(f"[{name}] {tag} d={depth} page={slot[str(depth)]['acc_page']:.3f} "
          f"train={slot[str(depth)]['acc_train']:.3f} n={len(outs)}", flush=True)


def planned_values(gen, items, induced, use_gold_plan, use_gold_ops,
                   max_new: int = 144):
    """The value the plan path returns for each item, or the empty string."""
    from src.opgraph.data import plan_prompt
    plans: dict[int, str] = {}
    if not use_gold_plan:
        prompts = []
        for it in items:
            ops = it.world.ops if use_gold_ops else induced[it.world.seed].ops
            prompts.append(plan_prompt(ops, it.text))
        for it, o in zip(items, gen.generate(prompts, max_new=max_new)):
            plans[id(it)] = o
    out, reasons, texts = [], [], []
    for it in items:
        ops = it.world.ops if use_gold_ops else induced[it.world.seed].ops
        ptext = serialize_plan(it.plan) if use_gold_plan else plans[id(it)]
        texts.append(ptext)
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
    return out, texts, reasons


def classify_induction(induced, worlds_page, worlds_train):
    """Per binary operator: does the induced body follow the page or training?"""
    c = Counter()
    for wp, wt in zip(worlds_page, worlds_train):
        ind = induced[wp.seed]
        for p in wp.pages:
            if not p.key.startswith("binop:"):
                continue
            sym = p.ops[0].symbol
            page_op = p.ops[0]
            train_op = next(o for q in wt.pages for o in q.ops if o.symbol == sym)
            vp = [_safe(page_op, a) for a in PROBES]
            vt = [_safe(train_op, a) for a in PROBES]
            if vp == vt:
                c["indistinguishable"] += 1
                continue
            c["distinguishable"] += 1
            got = ind.ops.get(sym)
            if got is None:
                c["absent"] += 1
                continue
            vg = [_safe(got, a) for a in PROBES]
            if vg == vp:
                c["follows_page"] += 1
            elif vg == vt:
                c["follows_training"] += 1
            else:
                c["neither"] += 1
            if got.assoc == page_op.assoc:
                c["assoc_kept"] += 1
    return dict(c)


def _safe(op, args):
    try:
        return op(*args)
    except OpError:
        return "__err__"


def induction_stats(induced, worlds):
    c = Counter()
    for w in worlds:
        ind = induced[w.seed]
        c["pages"] += ind.pages
        c["pages_parsed"] += ind.parsed
        c["gold_ops"] += ind.gold_count
        c["induced_ops"] += len(ind.ops)
        c["self_verified"] += ind.self_verified
        c["exact_text"] += ind.exact
        c["behavioural"] += ind.behavioural
    return dict(c)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--direct-ckpt", default="runs/direct.pt")
    ap.add_argument("--trace-ckpt", default="runs/trace.pt")
    ap.add_argument("--opgraph-ckpt", default="runs/opgraph.pt")
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--out", default="results/audit_c78.json")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--skip-trace", action="store_true")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sets, golds, drop, base, tworlds = build(args.n)
    tags = list(SURFACE_TAGS) + ["perm"]
    res: dict = {"config": vars(args), "dropped_from_perm": drop,
                 "depths": DEPTHS, "n": args.n}

    # the questions must be identical across every surface form
    for tag in SURFACE_TAGS:
        for d in DEPTHS:
            a, b = sets[("s0", d)], sets[(tag, d)]
            assert [x.text for x in a] == [x.text for x in b], (tag, d)
            assert [x.gold for x in a] == [x.gold for x in b], (tag, d)
            assert [serialize_plan(x.plan) for x in a] == \
                   [serialize_plan(x.plan) for x in b], (tag, d)
    print("[ok] questions, golds and gold plans identical across wordings",
          flush=True)

    # ---------------------------------------------------------- parser only
    for tag in tags:
        for d in DEPTHS:
            items = sets[(tag, d)]
            gp, gt = golds[(tag, d)]
            for name, styles in (("parser_all_wordings", (0, 2, 3, 4)),
                                 ("parser_trained_wording", (0,))):
                outs = []
                for it in items:
                    try:
                        outs.append(pageparser.answer(it.world.context(), it.text,
                                                      styles))
                    except Exception:
                        outs.append("")
                record(res, name, tag, d, outs, gp, gt)
    _save(res, args.out)

    # ------------------------------------------------------------- direct
    model, _ = load_model(args.direct_ckpt, device)
    gen = Generator(model, tok, device, batch_size=args.batch_size)
    for tag in tags:
        for d in DEPTHS:
            items = sets[(tag, d)]
            gp, gt = golds[(tag, d)]
            for name, oracle in (("direct_all", False),
                                 ("direct_oracle_page", True)):
                _, outs = score_direct(gen, items, oracle)
                record(res, name, tag, d, outs, gp, gt, sample=outs[:3])
    del model, gen
    torch.cuda.empty_cache()
    _save(res, args.out)

    # -------------------------------------------------------------- trace
    if not args.skip_trace:
        from src.opgraph.plan import trace_answer
        model, _ = load_model(args.trace_ckpt, device)
        gen = Generator(model, tok, device, batch_size=args.batch_size)
        for tag in tags:
            for d in DEPTHS:
                items = sets[(tag, d)]
                gp, gt = golds[(tag, d)]
                for name, oracle in (("trace_all", False),
                                     ("trace_oracle_page", True)):
                    _, outs = score_trace(gen, items, oracle)
                    vals = [trace_answer(o) for o in outs]
                    record(res, name, tag, d, vals, gp, gt, sample=outs[:2])
        del model, gen
        torch.cuda.empty_cache()
        _save(res, args.out)

    # ------------------------------------------------------------ opgraph
    model, _ = load_model(args.opgraph_ckpt, device)
    gen = Generator(model, tok, device, batch_size=args.batch_size)
    for tag in tags:
        worlds = {it.world.seed: it.world
                  for d in DEPTHS for it in sets[(tag, d)]}
        induced = induce_worlds(gen, worlds, progress=1)
        res.setdefault("induction", {})[tag] = induction_stats(
            induced, list(worlds.values()))
        print(f"[induction {tag}]", json.dumps(res["induction"][tag]), flush=True)
        if tag == "perm":
            pw = [w for w in worlds.values()]
            tw_by_seed = {w.seed: w for w in base}
            res["induction_identity"] = classify_induction(
                induced, pw, [tw_by_seed[w.seed] for w in pw])
            print("[identity]", json.dumps(res["induction_identity"]), flush=True)
            res["induced_samples"] = [
                serialize(induced[w.seed].ops[p.ops[0].symbol])
                for w in pw[:6] for p in w.pages
                if p.key.startswith("binop:")
                and p.ops[0].symbol in induced[w.seed].ops][:8]
        for d in DEPTHS:
            items = sets[(tag, d)]
            gp, gt = golds[(tag, d)]
            for name, gplan, gops in (("plan_execute", False, False),
                                      ("oracle_plan", True, False),
                                      ("oracle_ops", False, True),
                                      ("oracle_both", True, True)):
                if tag not in ("s0", "perm") and gops:
                    continue  # gold operators do not depend on the wording
                vals, texts, reasons = planned_values(gen, items, induced,
                                                      gplan, gops)
                record(res, name, tag, d, vals, gp, gt, sample=texts[:2])
                res[name][tag][str(d)]["reasons"] = dict(Counter(reasons))
        _save(res, args.out)
    del model, gen
    torch.cuda.empty_cache()
    _save(res, args.out)
    print("[written]", args.out, flush=True)
    return 0


def _save(res, path):
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    raise SystemExit(main())
