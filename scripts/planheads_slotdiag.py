"""Where does a slot head's array go wrong, field by field.

Answer accuracy says a head failed. It does not say whether the opcode was
wrong, whether an argument was wrong, or whether P4's two encodings of the same
dependency disagreed with each other. This reads the committed array directly
and compares it to the gold array slot by slot, so the failure lands on a field.

Three starting points, because a refinement head is supposed to be able to do
more than write a program from nothing:

  from_mask         every slot MASK, which is what the planner actually does
  repair_wrong_op   the gold array with one active node's opcode replaced
  repair_truncate   the gold array with the tail of the program masked

Read the three together with care. The refinement schedule resets every
uncommitted slot to MASK after each pass, so a run of more than one pass has
collapsed all three starts onto the same state by its second pass and the three
columns come out nearly equal whatever the head does. Use
planheads_condprobe.py, which is one pass, to ask whether the head reads its
slot inputs at all.

The last two are the repair objective's own training conditions asked at
evaluation time. A head that cannot restore a program it was handed with one
symbol wrong has not learned repair, whatever its answer accuracy says.

P4 carries every dependency twice: once as the temporary named in an argument
slot and once as an explicit edge. The two can disagree, and a program whose
edges disagree with its arguments still parses and still executes, in the wrong
order, giving a wrong answer with no error. That disagreement rate is reported
here because nothing in the answer accuracy separates it from a wrong opcode.
"""

from __future__ import annotations

import argparse
import json
import os

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.planheads import (A_MAX, D_NODE0, D_NONE, F_ACTIVE, F_ANS,
                                   F_ARG, F_DEP, F_OPCODE, F_REG, G_EMPTY,
                                   G_TEMP0, N_NODES, O_BUILTIN0, O_EMPTY,
                                   O_OP0, R_REG0, A_YES, SlotError,
                                   SlotPlanHead, all_masked, encode_plan,
                                   field_logit_mask, gid, local_of,
                                   plan_prompt_text, readout, schema_for,
                                   slot_forward, slot_logits, MASK_LOCAL,
                                   EMPTY_LOCAL, K_MAX, BUILTIN_ORDER)
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer

FIELD_NAME = {F_ACTIVE: "active", F_OPCODE: "opcode", F_REG: "register",
              F_ARG: "argument", F_DEP: "dependency", F_ANS: "answer"}


def load(path: str, device: str):
    state = torch.load(path, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    model.to(device).eval()
    head_name = state["head"]
    if state.get("plan_head") is None:
        raise SystemExit(f"{path} is head {head_name}, which has no slot array")
    if head_name not in ("p3", "p4"):
        raise SystemExit(
            f"{path} is head {head_name}, which commits its slots left to right "
            f"under a causal mask. Running it through the bidirectional "
            f"refinement loop reads every slot from the wrong position and "
            f"reports zeros that say nothing about the head.")
    h = SlotPlanHead(model.cfg.d_model)
    h.load_state_dict(state["plan_head"])
    return model, h.to(device).eval(), head_name, state


@torch.no_grad()
def refine(model, head, tok, items, ops_by_item, device, schema, head_name,
           starts, iters, temperature, seed=7):
    """The planner's own refinement loop, from an arbitrary starting array."""
    s = schema.n_slots
    prompts = [plan_prompt_text(o, it.text, head_name)
               for it, o in zip(items, ops_by_item)]
    ids = [tok.encode(p) for p in prompts]
    pw = max(len(x) for x in ids)
    pad = torch.zeros(len(items), pw, dtype=torch.long, device=device)
    ok = torch.zeros(len(items), pw, dtype=torch.bool, device=device)
    for i, x in enumerate(ids):
        pad[i, pw - len(x):] = torch.tensor(x, device=device)
        ok[i, pw - len(x):] = True
    fmask = field_logit_mask(schema.fields, device)
    gen = torch.Generator(device=device)
    gen.manual_seed(seed)
    cur = torch.tensor(starts, dtype=torch.long, device=device)
    for t in range(iters):
        with torch.autocast(device_type="cuda" if pad.is_cuda else "cpu",
                            dtype=torch.bfloat16, enabled=pad.is_cuda):
            hidden = slot_forward(model, head, pad, ok, cur, schema, False)
        logits = slot_logits(head, readout(hidden, False).float(), fmask)
        if temperature <= 0:
            pick = logits.argmax(-1)
        else:
            b, ss, v = logits.shape
            p = torch.softmax(logits.reshape(-1, v) / temperature, dim=-1)
            pick = torch.multinomial(p, 1, generator=gen).view(b, ss)
        if t == iters - 1:
            cur = pick
            break
        conf = torch.softmax(logits, -1).gather(2, pick[..., None]).squeeze(-1)
        keep = max(1, int(round(s * (t + 1) / iters)))
        order = torch.argsort(conf, dim=1, descending=True)
        nxt = torch.tensor(all_masked(schema), device=device)[None].repeat(len(items), 1)
        idx = order[:, :keep]
        nxt.scatter_(1, idx, pick.gather(1, idx))
        cur = nxt
    return cur.tolist()


def arg_dep_disagreement(slots, schema) -> bool | None:
    """P4 only: do the argument temporaries and the edge slots name the same deps."""
    if not schema.graph:
        return None
    fields = schema.fields
    producer = {}
    active = []
    for i in range(N_NODES):
        if local_of(slots, schema.active_slot(i), fields) != A_YES:
            continue
        active.append(i)
        rv = local_of(slots, schema.reg_slot(i), fields)
        if rv >= R_REG0:
            producer.setdefault(rv - R_REG0 + 1, i)
    for i in active:
        from_args = set()
        for k in range(A_MAX):
            v = local_of(slots, schema.arg_slot(i, k), fields)
            if G_TEMP0 <= v < G_TEMP0 + N_NODES:
                j = producer.get(v - G_TEMP0 + 1)
                if j is not None:
                    from_args.add(j)
        declared = set()
        for k in range(2):
            dv = local_of(slots, schema.dep_slot(i, k), fields)
            if dv != D_NONE and dv >= D_NODE0:
                declared.add(dv - D_NODE0)
        if from_args != declared:
            return True
    return False


def wrong_op_start(gold, schema, n_ops, rng):
    fields = schema.fields
    out = list(gold)
    nodes = [i for i in range(N_NODES)
             if local_of(gold, schema.opcode_slot(i), fields) not in (O_EMPTY,)]
    if not nodes:
        return out
    i = nodes[rng.randrange(len(nodes))]
    j = schema.opcode_slot(i)
    choices = [O_OP0 + k for k in range(min(n_ops, K_MAX))]
    choices += [O_BUILTIN0 + b for b in range(len(BUILTIN_ORDER))]
    alt = [c for c in choices if gid(F_OPCODE, c) != gold[j]]
    if alt:
        out[j] = gid(F_OPCODE, alt[rng.randrange(len(alt))])
    return out


def truncate_start(gold, schema):
    fields = schema.fields
    out = list(gold)
    nodes = [i for i in range(N_NODES)
             if local_of(gold, schema.opcode_slot(i), fields) != O_EMPTY]
    if len(nodes) < 2:
        return out
    for i in nodes[len(nodes) // 2:]:
        for off in range(schema.node_width):
            k = schema.at(i, off)
            out[k] = gid(fields[k], MASK_LOCAL[fields[k]])
    out[schema.answer_slot] = gid(F_ANS, MASK_LOCAL[F_ANS])
    return out


def score(golds, preds, schema):
    """Exact array match, and per field accuracy over the slots that carry content."""
    fields = schema.fields
    exact = 0
    per = {}
    for g, p in zip(golds, preds):
        if g == p:
            exact += 1
        for j, f in enumerate(fields):
            # A slot carries content when gold put something other than this
            # field's EMPTY there. Most slots of a shallow plan are EMPTY, and
            # counting them would report a head that emits an empty program as
            # highly accurate.
            content = local_of(g, j, fields) != EMPTY_LOCAL[f]
            bucket = per.setdefault(FIELD_NAME[f], {"n": 0, "ok": 0,
                                                    "content_n": 0, "content_ok": 0})
            bucket["n"] += 1
            bucket["ok"] += int(g[j] == p[j])
            if content:
                bucket["content_n"] += 1
                bucket["content_ok"] += int(g[j] == p[j])
    out = {"n": len(golds), "exact_array_rate": round(exact / max(1, len(golds)), 4)}
    for name, b in per.items():
        out[name] = {
            "slot_acc": round(b["ok"] / b["n"], 4) if b["n"] else None,
            "content_slot_acc": (round(b["content_ok"] / b["content_n"], 4)
                                 if b["content_n"] else None),
            "content_slots": b["content_n"],
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--depths", default="1,2,3,4,6,8")
    ap.add_argument("--iters", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--batch-size", type=int, default=8)
    args = ap.parse_args()

    import random as _r
    rng = _r.Random(11)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, head, head_name, state = load(args.ckpt, device)
    schema = schema_for(head_name)
    res = {"ckpt": args.ckpt, "head": head_name, "iters": args.iters,
           "temperature": args.temperature, "n_slots": schema.n_slots,
           "train_args": state.get("args"), "holdout": state.get("holdout"),
           "by_depth": {}}

    worlds = eval_worlds("sequential", args.n, breadth=3, style=0)
    for depth in [int(d) for d in args.depths.split(",")]:
        items = [make_item("sequential", w, depth, i) for i, w in enumerate(worlds)]
        ops = [it.world.ops for it in items]
        golds, keep = [], []
        for it, o in zip(items, ops):
            try:
                golds.append(encode_plan(it.plan, o, schema))
                keep.append(it)
            except SlotError:
                pass
        if not keep:
            continue
        ops = [it.world.ops for it in keep]
        starts = {
            "from_mask": [all_masked(schema) for _ in keep],
            "repair_wrong_op": [wrong_op_start(g, schema, len(o.keys()), rng)
                                for g, o in zip(golds, ops)],
            "repair_truncate": [truncate_start(g, schema) for g in golds],
        }
        cell = {}
        for name, st in starts.items():
            preds = []
            for lo in range(0, len(keep), args.batch_size):
                hi = min(lo + args.batch_size, len(keep))
                preds += refine(model, head, tok, keep[lo:hi], ops[lo:hi], device,
                                schema, head_name, st[lo:hi], args.iters,
                                args.temperature)
            cell[name] = score(golds, preds, schema)
            if schema.graph:
                dis = [arg_dep_disagreement(p, schema) for p in preds]
                cell[name]["arg_dep_disagreement_rate"] = round(
                    sum(1 for d in dis if d) / len(dis), 4)
        res["by_depth"][str(depth)] = cell
        print(f"[d{depth}] " + json.dumps(
            {k: {"exact": v["exact_array_rate"],
                 "opcode": v.get("opcode", {}).get("content_slot_acc"),
                 "argument": v.get("argument", {}).get("content_slot_acc"),
                 "dep_disagree": v.get("arg_dep_disagreement_rate")}
             for k, v in cell.items()}), flush=True)

    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"[written] {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
