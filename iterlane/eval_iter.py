"""Score P3 and P4 over the full depth grid, with the refinement trajectory kept.

This is the shipped scripts/planheads_eval.py with three additions and no change
to the shared head code:

  1. the sequential grid runs to depth 32 rather than depth 8, and every cell
     records whether this head's codec can represent the gold plan at all, so a
     structural zero is never reported as a measured decay
  2. the refinement loop is subclassed rather than edited, so what each pass
     committed is recorded and a later pass rewriting an earlier slot can be
     counted instead of assumed
  3. a widened copy of the schema (32 plan nodes) can be selected with --wide,
     because the shipped schema holds 12 nodes and cannot express a depth 16 or
     depth 32 plan

oracle_both must be 1.000 under every head or the harness is broken.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import time

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.run import Generator, induce_worlds
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 8, 12, 16, 32],
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


def get_ph(wide: bool):
    return importlib.import_module(
        "iterlane.planheads_wide" if wide else "src.opgraph.planheads")


def make_recorder(ph):
    """SlotPlanner with the per-pass trajectory kept.

    The arithmetic below is the shipped loop, copied rather than edited so the
    shared module is untouched. What is added is `trace`: the committed array
    after every pass, which is what lets "a later pass changed a slot an earlier
    pass had filled" be a count rather than an assumption.
    """

    class RecordingSlotPlanner(ph.SlotPlanner):

        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.traces: dict[int, list[list[int]]] = {}

        def _batch(self, model, tok, items, ops_by_item, device, chunk, outs):
            head = model.plan_head
            schema = self.schema
            s = schema.n_slots
            prompts = [ph.plan_prompt_text(ops_by_item[i], items[i].text, self.head)
                       for i in chunk]
            ids = [tok.encode(p) for p in prompts]
            pw = max(len(x) for x in ids)
            if pw + s > model.cfg.max_seq_len:
                raise ph.SlotError("prompt plus slots exceeds the model context")
            pad = torch.zeros(len(chunk), pw, dtype=torch.long, device=device)
            ok = torch.zeros(len(chunk), pw, dtype=torch.bool, device=device)
            for i, x in enumerate(ids):
                pad[i, pw - len(x):] = torch.tensor(x, device=device)
                ok[i, pw - len(x):] = True
            fmask = ph.field_logit_mask(schema.fields, device)
            gen = torch.Generator(device=device)
            gen.manual_seed(self.seed + chunk[0])
            cur = torch.tensor(ph.all_masked(schema), device=device)[None].repeat(
                len(chunk), 1)
            causal = self.head == "p2s"
            if causal:
                raise ph.SlotError("the recorder is for the bidirectional heads")
            n_fwd = self.iters
            trace: list[list[list[int]]] = []
            with torch.no_grad():
                for t in range(self.iters):
                    logits = self._logits(model, head, pad, ok, cur, fmask)
                    probs = torch.softmax(logits, dim=-1)
                    pick = self._pick_all(logits, gen)
                    conf = probs.gather(2, pick[..., None]).squeeze(-1)
                    if t == self.iters - 1:
                        cur = pick
                        trace.append(cur.tolist())
                        break
                    keep = max(1, int(round(s * (t + 1) / self.iters)))
                    order = torch.argsort(conf, dim=1, descending=True)
                    nxt = torch.tensor(ph.all_masked(schema), device=device)[None].repeat(
                        len(chunk), 1)
                    idx = order[:, :keep]
                    nxt.scatter_(1, idx, pick.gather(1, idx))
                    cur = nxt
                    trace.append(cur.tolist())
                decisions = self.iters * s
                positions = pw + s * self.iters
            arrays = cur.tolist()
            for i, g in enumerate(chunk):
                out = ph.PlanOut(fwd_passes=n_fwd, slot_decisions=decisions,
                                 position_evals=positions, slots=arrays[i])
                try:
                    out.text = ph.decode_plan_text(arrays[i], ops_by_item[g], schema)
                except ph.SlotError as exc:
                    out.error = f"slot_decode:{str(exc)[:40]}"
                outs[g] = out
                self.traces[g] = [tr[i] for tr in trace]

    return RecordingSlotPlanner


def revision_stats(ph, traces: dict, schema) -> dict:
    """How often a later pass rewrote a slot an earlier pass had already filled.

    A slot counts as committed early when some pass before the last one gave it
    a non MASK symbol. For those slots three things are separated: the value
    changed to a different non MASK symbol, the slot fell back to MASK, and the
    symbol standing at the end differs from the one first committed. If all
    three are zero the refinement never revises and the mechanism is not doing
    what it was built to do.
    """
    mask_ids = ph.all_masked(schema)
    tot = dict(items=0, items_any_revision=0, early=0, changed=0,
               to_mask=0, final_differs=0, distinct=0, slots_total=0,
               answer_early=0, answer_changed=0)
    for _idx, tr in traces.items():
        if len(tr) < 2:
            continue
        tot["items"] += 1
        n_slots = len(tr[0])
        tot["slots_total"] += n_slots
        any_rev = False
        for j in range(n_slots):
            seq = [a[j] for a in tr]
            first = next((t for t in range(len(seq) - 1) if seq[t] != mask_ids[j]), None)
            if first is None:
                continue
            tot["early"] += 1
            v0 = seq[first]
            later = seq[first + 1:]
            changed = any(v != mask_ids[j] and v != v0 for v in later)
            to_mask = any(v == mask_ids[j] for v in later)
            tot["changed"] += int(changed)
            tot["to_mask"] += int(to_mask)
            tot["final_differs"] += int(seq[-1] != v0)
            tot["distinct"] += len({v for v in seq[first:] if v != mask_ids[j]})
            if changed or to_mask:
                any_rev = True
            if j == schema.answer_slot:
                tot["answer_early"] += 1
                tot["answer_changed"] += int(seq[-1] != v0)
        tot["items_any_revision"] += int(any_rev)
    e = tot["early"] or 1
    i = tot["items"] or 1
    a = tot["answer_early"] or 1
    return {
        "items": tot["items"],
        "slots_per_item": round(tot["slots_total"] / i, 1),
        "slots_committed_before_last_pass": tot["early"],
        "slots_committed_early_per_item": round(tot["early"] / i, 1),
        "value_changed_rate": round(tot["changed"] / e, 4),
        "returned_to_mask_rate": round(tot["to_mask"] / e, 4),
        "final_differs_from_first_rate": round(tot["final_differs"] / e, 4),
        "mean_distinct_values_per_slot": round(tot["distinct"] / e, 4),
        "items_with_any_revision_rate": round(tot["items_any_revision"] / i, 4),
        "answer_slot_final_differs_rate": round(tot["answer_changed"] / a, 4),
    }


def load_plan_model(ph, path: str, device: str):
    state = torch.load(path, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    head_name = state.get("head", "p1")
    model.to(device).eval()
    model.plan_head = None
    if state.get("plan_head") is not None:
        h = ph.SlotPlanHead(model.cfg.d_model)
        h.load_state_dict(state["plan_head"])
        model.plan_head = h.to(device).eval()
    return model, state, head_name


def build_sets(kinds, depths_by_kind, n, style):
    sets, cache = {}, {}
    for kind in kinds:
        for depth in depths_by_kind[kind]:
            breadth = depth if kind == "breadth" else 3
            key = (kind, breadth)
            if key not in cache:
                cache[key] = eval_worlds(kind, n, breadth=breadth, style=style)
            sets[(kind, depth)] = [make_item(kind, w, depth, i)
                                   for i, w in enumerate(cache[key])]
    return sets


def representable(ph, items, head) -> dict:
    """Can this head's array hold the gold plan of this cell at all.

    A cell whose gold plan does not fit is a cell where accuracy is zero by
    construction. Recording it separately is what stops a representation cap
    being read as a measured collapse.
    """
    schema = ph.schema_for(head)
    ok = 0
    err = ""
    for it in items:
        try:
            ph.encode_plan(it.plan, it.world.ops, schema)
            ok += 1
        except Exception as exc:
            if not err:
                err = f"{type(exc).__name__}: {exc}"
    return {"n": len(items), "codec_ok": ok,
            "codec_rate": round(ok / len(items), 4) if items else 0.0,
            "first_error": err}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--gen-batch-size", type=int, default=96)
    ap.add_argument("--kinds", default=",".join(GRID))
    ap.add_argument("--depths", default="", help="override depths, comma list")
    ap.add_argument("--styles", default="0")
    ap.add_argument("--iters", default="8")
    ap.add_argument("--temperatures", default="0.0,0.8")
    ap.add_argument("--conditions", default="plan_execute,oracle_ops,oracle_plan")
    ap.add_argument("--wide", action="store_true")
    ap.add_argument("--record-revisions", action="store_true")
    ap.add_argument("--verify-counter", action="store_true")
    ap.add_argument("--skip-gold", action="store_true")
    args = ap.parse_args()

    ph = get_ph(args.wide)
    Recorder = make_recorder(ph)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, state, head = load_plan_model(ph, args.ckpt, device)
    kinds = args.kinds.split(",")
    depths_by_kind = dict(GRID)
    if args.depths:
        override = [int(x) for x in args.depths.split(",")]
        for k in kinds:
            depths_by_kind[k] = [d for d in override if d in GRID[k]] or override
    styles = [int(s) for s in args.styles.split(",")]
    iters = [int(x) for x in args.iters.split(",")]
    temps = [float(x) for x in args.temperatures.split(",")]
    want = set(args.conditions.split(","))

    results: dict = {"config": vars(args), "head": head, "wide": args.wide,
                     "schema_nodes": ph.N_NODES,
                     "n_slots": ph.schema_for(head).n_slots,
                     "corruption_mixture": ph.mixture_for(head),
                     "train_args": state.get("args"),
                     "train_step": state.get("step"),
                     "holdout": state.get("holdout")}
    sets = {st: build_sets(kinds, depths_by_kind, args.n, st) for st in styles}

    for key, items in sets[styles[0]].items():
        _put(results, "codec", key, representable(ph, items, head))

    gen = Generator(model, tok, device, batch_size=args.gen_batch_size)
    for st in styles:
        worlds = {it.world.seed: it.world
                  for items in sets[st].values() for it in items}
        t0 = time.time()
        induced = induce_worlds(gen, worlds, progress=0)
        ind = {"pages": 0, "pages_parsed": 0, "gold_ops": 0, "induced_ops": 0,
               "self_verified": 0, "exact_text": 0, "behavioural": 0,
               "secs": round(time.time() - t0, 1)}
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

        if not args.skip_gold:
            for name, rt in (("oracle_both", None), ("oracle_both_roundtrip", head)):
                planner = ph.GoldPlanner(roundtrip=rt)
                for key, items in sets[st].items():
                    ops = [it.world.ops for it in items]
                    outs = planner.build(model, tok, items, ops, device)
                    _record(results, _tag(name, st), key, ph.grade(items, outs, ops))

        for temp in temps:
            for it_count in (iters if head in ("p3", "p4") else [0]):
                cls = Recorder if (args.record_revisions and head in ("p3", "p4")) \
                    else None
                def new_planner():
                    if cls is not None:
                        return cls(head, iters=it_count, batch_size=args.batch_size,
                                   temperature=temp, seed=7)
                    return ph.make_planner(head, batch_size=args.batch_size,
                                           temperature=temp, iters=it_count, seed=7)
                planner = new_planner()
                suffix = f"@T{temp:g}"
                if head in ("p3", "p4"):
                    suffix += f"@it{it_count}"
                if args.verify_counter:
                    key0 = sorted(sets[st])[0]
                    item0 = sets[st][key0][0]
                    saved = planner.batch_size
                    planner.batch_size = 1
                    with ph.ForwardCounter(model) as fc:
                        o = planner.build(model, tok, [item0], [item0.world.ops],
                                          device)[0]
                    planner.batch_size = saved
                    chk = {"reported": o.fwd_passes, "observed": fc.count,
                           "ok": o.fwd_passes == fc.count}
                    results.setdefault("counter_check", {})[
                        _tag(head + suffix, st)] = chk
                    print(f"[counter {head}{suffix}] {json.dumps(chk)}", flush=True)
                    planner = new_planner()
                for name, gold_plan, gold_ops in CONDITIONS:
                    if name not in want:
                        continue
                    for key, items in sets[st].items():
                        ops = [it.world.ops if gold_ops
                               else induced[it.world.seed].ops for it in items]
                        t0 = time.time()
                        if gold_plan:
                            outs = ph.GoldPlanner().build(model, tok, items, ops, device)
                            rev = None
                        else:
                            planner = new_planner()
                            outs = planner.build(model, tok, items, ops, device)
                            rev = (revision_stats(ph, planner.traces, planner.schema)
                                   if cls is not None else None)
                        cell = ph.grade(items, outs, ops)
                        _record(results, _tag(name + suffix, st), key, cell,
                                secs=round(time.time() - t0, 1),
                                sample=outs[0].text or outs[0].error, revision=rev)
                    with open(args.out, "w") as fh:
                        json.dump(results, fh, indent=1)
    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"[written] {args.out}", flush=True)
    return 0


def _tag(name: str, style: int) -> str:
    return name if style == 0 else name + "@para"


def _put(results, name, key, row):
    kind, depth = key
    results.setdefault(name, {}).setdefault(kind, {})[str(depth)] = row


def _record(results, name, key, cell, secs=None, sample=None, revision=None):
    kind, depth = key
    row = cell.as_dict()
    if secs is not None:
        row["secs"] = secs
    if sample is not None:
        row["sample"] = sample[:200]
    if revision is not None:
        row["revision"] = revision
    _put(results, name, key, row)
    extra = ""
    if revision:
        extra = (f" rev_val={revision['value_changed_rate']:.3f}"
                 f" rev_fin={revision['final_differs_from_first_rate']:.3f}")
    print(f"[{name}] {kind} d={depth} n={row['n']} acc={row['acc']:.3f} "
          f"parse={row['parse_rate']:.3f} typed={row['well_typed_rate']:.3f} "
          f"exact={row['exact_gold_plan_rate']:.3f} fwd={row['fwd_passes_mean']:.1f}"
          f"{extra}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
