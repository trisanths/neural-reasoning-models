"""Per-item records for the sequential depth curve, plus associativity twins.

Two things the shipped evaluation does not keep are needed here.

The first is per item correctness. `scripts/opgraph_eval.py` stores a cell
accuracy and three sample strings, which is enough for a table and not enough to
ask whether the items a condition got right are the ones where a shorter
computation would have hit the same number. Every condition here writes one row
per item.

The second is a twin. For each question a twin world is built whose page for the
operator in that question is byte identical except that the sentence stating
which way a run associates is flipped. Nothing else moves: same rule, same
modulus, same worked examples, same question, same operands. At depth one the
twin's answer is identical, which makes depth one the control. At depth two and
above the twin's answer is almost always different, so a plan written without
reading the associativity can be right on at most one of the pair.

The twin's gold comes from src.audit.refprose, not from the generator, so the
twin arm is graded by the independent reader throughout.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import replace

import torch

sys.path.insert(0, os.path.expanduser("~/opg"))

from src.audit.refprose import RefWorld, answer_question  # noqa: E402
from src.opgraph.data import eval_worlds, make_item, plan_prompt  # noqa: E402
from src.opgraph.invent import Page, World  # noqa: E402
from src.opgraph.opdef import OpError  # noqa: E402
from src.opgraph.plan import PlanError, answer_text, parse_plan, run_plan  # noqa: E402
from src.opgraph.run import Generator, induce_worlds, load_model  # noqa: E402
from src.train.tokenizer import load_tokenizer  # noqa: E402

FLIPS = [("associates left to right", "associates right to left"),
         ("associates right to left", "associates left to right"),
         ("with no brackets is read left to right",
          "with no brackets is read right to left"),
         ("with no brackets is read right to left",
          "with no brackets is read left to right")]


def flip_assoc(text: str) -> str:
    for a, b in FLIPS:
        if a in text:
            return text.replace(a, b)
    raise ValueError("page states no associativity")


def twin_world(w: World, glyph: str, seed: int) -> World:
    """The same world with one operator's associativity sentence flipped."""
    pages = []
    for p in w.pages:
        if p.key == f"binop:{glyph}":
            ops = [replace(o, assoc=("right" if o.assoc == "left" else "left"))
                   for o in p.ops]
            q = Page(p.key, flip_assoc(p.text), ops)
            q.glyph = glyph                       # type: ignore[attr-defined]
            q.right_assoc = not p.right_assoc     # type: ignore[attr-defined]
            pages.append(q)
        else:
            pages.append(p)
    return World(seed, pages, list(w.order))


def fold_answer(question: str, ops, assoc: str) -> str:
    """What a flat chain comes to when folded one way. Classification only."""
    m = re.match(r"^Evaluate\s+(.*?)\.$", question.strip())
    parts = m.group(1).split()
    vals = [int(v) for v in parts[0::2]]
    op = ops[parts[1]]
    if assoc == "left":
        acc = vals[0]
        for v in vals[1:]:
            acc = op(acc, v)
    else:
        acc = vals[-1]
        for v in reversed(vals[:-1]):
            acc = op(v, acc)
    return str(acc)


def _norm(s) -> str:
    return str(s).strip().strip(".").strip().lower()


def run_arm(gen, items, golds, ops_for, tag, rows, max_new=144):
    prompts = [plan_prompt(o, it.text) for o, it in zip(ops_for, items)]
    outs = gen.generate(prompts, max_new=max_new)
    for gold, ops, ptext, row in zip(golds, ops_for, outs, rows):
        rec = {"plan": ptext}
        try:
            plan = parse_plan(ptext)
        except PlanError:
            rec.update(ok=False, why="plan_parse", value=None, steps=None)
            row[tag] = rec
            continue
        try:
            v = run_plan(plan, ops)
        except (PlanError, OpError):
            rec.update(ok=False, why="execute", value=None,
                       steps=len(plan.steps))
            row[tag] = rec
            continue
        got = answer_text(v)
        ok = _norm(got) == _norm(gold)
        rec.update(ok=ok, value=got, why="ok" if ok else "wrong_value",
                   steps=len(plan.steps))
        row[tag] = rec


TWIN_SEED0 = 700_000_000


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="runs/opgraph.pt")
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--depths", default="1,2,3,4,8")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--out", default="results/audit_seq_items.json")
    args = ap.parse_args()

    depths = [int(d) for d in args.depths.split(",")]
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_model(args.ckpt, device)
    gen = Generator(model, tok, device, batch_size=args.batch_size)

    ordered = eval_worlds("sequential", args.n, breadth=3)
    sets = {d: [make_item("sequential", w, d, i) for i, w in enumerate(ordered)]
            for d in depths}
    readers = {w.seed: RefWorld.read([p.text for p in w.shuffled_pages()])
               for w in ordered}

    keys = sorted({(it.world.seed, it.symbols[0])
                   for d in depths for it in sets[d]})
    twins, twin_readers, twin_seed = {}, {}, {}
    for k, (seed, g) in enumerate(keys):
        w = next(w for w in ordered if w.seed == seed)
        tw = twin_world(w, g, TWIN_SEED0 + k)
        twins[(seed, g)] = tw
        twin_seed[(seed, g)] = tw.seed
        twin_readers[(seed, g)] = RefWorld.read(
            [p.text for p in tw.shuffled_pages()])
    print(f"[setup] {len(ordered)} worlds, {len(twins)} twin worlds", flush=True)

    induced = induce_worlds(gen, {w.seed: w for w in ordered}, progress=1)
    tw_induced = induce_worlds(gen, {tw.seed: tw for tw in twins.values()},
                               progress=1)
    print("[induction done]", flush=True)

    out_rows = []
    for d in depths:
        items = sets[d]
        rows = []
        for it in items:
            g = it.symbols[0]
            b = readers[it.world.seed].binops[g]
            key = (it.world.seed, g)
            ind = induced[it.world.seed].ops.get(g)
            ti = tw_induced[twin_seed[key]].ops.get(g)
            rows.append({
                "depth": d, "seed": it.world.seed, "glyph": g, "q": it.text,
                "gold": it.gold, "assoc": b.assoc, "modulus": b.modulus,
                "form": b.form,
                "left_answer": fold_answer(it.text, it.world.ops, "left"),
                "right_answer": fold_answer(it.text, it.world.ops, "right"),
                "induced_assoc": ind.assoc if ind else None,
                "induced_present": ind is not None,
                "twin_induced_assoc": ti.assoc if ti else None,
                "twin_induced_present": ti is not None})

        golds = [it.gold for it in items]
        run_arm(gen, items, golds, [induced[it.world.seed].ops for it in items],
                "plan_execute", rows)
        run_arm(gen, items, golds, [it.world.ops for it in items],
                "oracle_ops", rows)

        twin_items, twin_golds = [], []
        for it, row in zip(items, rows):
            key = (it.world.seed, it.symbols[0])
            tw = twins[key]
            twin_items.append(replace(it, world=tw))
            tg = answer_question(it.text, twin_readers[key])
            twin_golds.append(tg)
            row["twin_gold"] = tg
            row["twin_differs"] = tg != it.gold
        run_arm(gen, twin_items, twin_golds,
                [tw_induced[ti.world.seed].ops for ti in twin_items],
                "twin_plan_execute", rows)
        run_arm(gen, twin_items, twin_golds,
                [ti.world.ops for ti in twin_items], "twin_oracle_ops", rows)

        out_rows.extend(rows)
        a = sum(r["plan_execute"]["ok"] for r in rows) / len(rows)
        b2 = sum(r["oracle_ops"]["ok"] for r in rows) / len(rows)
        t = sum(r["twin_plan_execute"]["ok"] for r in rows) / len(rows)
        print(f"[d{d}] plan_execute={a:.3f} oracle_ops={b2:.3f} "
              f"twin_plan_execute={t:.3f}", flush=True)
        with open(args.out, "w") as fh:
            json.dump(out_rows, fh)

    with open(args.out, "w") as fh:
        json.dump(out_rows, fh)
    print(f"[written] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
