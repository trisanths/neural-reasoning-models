"""Does a bidirectional slot head actually read its own slot inputs.

The refinement schedule resets every uncommitted slot to MASK after each pass,
so by the second pass three different starting arrays have collapsed to the
same state and a multi pass run cannot tell whether the head conditions on the
array it was handed. One pass can.

Four starts, one forward pass, greedy, same items and same prompt:

  all_mask     what the planner really starts from
  gold         the answer handed to it
  one_wrong    the answer with a single opcode replaced
  truncated    the answer with the tail of the program masked

If the head reads its inputs, `gold` reproduces itself far better than
`all_mask` does, and `one_wrong` restores the replaced opcode. If the four
agree, the head is conditioning on the prompt alone and the slot array is
decoration, which would make the refinement arm vacuous however good its
accuracy looks.
"""

from __future__ import annotations

import argparse
import json
import os
import random

import torch

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.planheads import (BUILTIN_ORDER, EMPTY_LOCAL, F_ANS, F_OPCODE,
                                   K_MAX, MASK_LOCAL, N_NODES, O_BUILTIN0,
                                   O_EMPTY, O_OP0, SlotError, SlotPlanHead,
                                   all_masked, encode_plan, field_logit_mask,
                                   gid, local_of, plan_prompt_text, readout,
                                   schema_for, slot_forward, slot_logits)
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer


@torch.no_grad()
def one_pass(model, head, tok, items, ops, device, schema, head_name, starts):
    prompts = [plan_prompt_text(o, it.text, head_name) for it, o in zip(items, ops)]
    ids = [tok.encode(p) for p in prompts]
    pw = max(len(x) for x in ids)
    pad = torch.zeros(len(items), pw, dtype=torch.long, device=device)
    ok = torch.zeros(len(items), pw, dtype=torch.bool, device=device)
    for i, x in enumerate(ids):
        pad[i, pw - len(x):] = torch.tensor(x, device=device)
        ok[i, pw - len(x):] = True
    fmask = field_logit_mask(schema.fields, device)
    cur = torch.tensor(starts, dtype=torch.long, device=device)
    with torch.autocast(device_type="cuda" if pad.is_cuda else "cpu",
                        dtype=torch.bfloat16, enabled=pad.is_cuda):
        hidden = slot_forward(model, head, pad, ok, cur, schema, False)
    logits = slot_logits(head, readout(hidden, False).float(), fmask)
    return logits.argmax(-1).tolist()


def active_opcode_nodes(gold, schema):
    f = schema.fields
    return [i for i in range(N_NODES)
            if local_of(gold, schema.opcode_slot(i), f) != O_EMPTY]


def make_one_wrong(gold, schema, n_ops, rng):
    out = list(gold)
    nodes = active_opcode_nodes(gold, schema)
    if not nodes:
        return out, None
    i = rng.choice(nodes)
    j = schema.opcode_slot(i)
    ch = [O_OP0 + k for k in range(min(n_ops, K_MAX))]
    ch += [O_BUILTIN0 + b for b in range(len(BUILTIN_ORDER))]
    alt = [c for c in ch if gid(F_OPCODE, c) != gold[j]]
    if not alt:
        return out, None
    out[j] = gid(F_OPCODE, rng.choice(alt))
    return out, j


def make_truncated(gold, schema):
    f = schema.fields
    out = list(gold)
    nodes = active_opcode_nodes(gold, schema)
    if len(nodes) < 2:
        return out
    for i in nodes[len(nodes) // 2:]:
        for off in range(schema.node_width):
            k = schema.at(i, off)
            out[k] = gid(f[k], MASK_LOCAL[f[k]])
    out[schema.answer_slot] = gid(F_ANS, MASK_LOCAL[F_ANS])
    return out


def agree(a, b):
    return sum(1 for x, y in zip(a, b) if x == y) / len(a)


def content_agree(pred, gold, schema):
    f = schema.fields
    n = k = 0
    for j, fk in enumerate(f):
        if local_of(gold, j, f) == EMPTY_LOCAL[fk]:
            continue
        n += 1
        k += int(pred[j] == gold[j])
    return k / n if n else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--depths", default="1,2,3,6")
    ap.add_argument("--batch-size", type=int, default=8)
    args = ap.parse_args()

    rng = random.Random(23)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    state = torch.load(args.ckpt, map_location="cpu", weights_only=False)
    head_name = state["head"]
    if head_name not in ("p3", "p4"):
        raise SystemExit(f"{head_name} is not a bidirectional head")
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    model.to(device).eval()
    head = SlotPlanHead(model.cfg.d_model)
    head.load_state_dict(state["plan_head"])
    head.to(device).eval()
    schema = schema_for(head_name)

    res = {"ckpt": args.ckpt, "head": head_name, "by_depth": {}}
    worlds = eval_worlds("sequential", args.n, breadth=3, style=0)
    for depth in [int(d) for d in args.depths.split(",")]:
        items = [make_item("sequential", w, depth, i) for i, w in enumerate(worlds)]
        keep, golds = [], []
        for it in items:
            try:
                golds.append(encode_plan(it.plan, it.world.ops, schema))
                keep.append(it)
            except SlotError:
                pass
        if not keep:
            continue
        ops = [it.world.ops for it in keep]
        wrongs, wslots = [], []
        for g, o in zip(golds, ops):
            w, j = make_one_wrong(g, schema, len(o), rng)
            wrongs.append(w)
            wslots.append(j)
        starts = {"all_mask": [all_masked(schema) for _ in keep],
                  "gold": [list(g) for g in golds],
                  "one_wrong": wrongs,
                  "truncated": [make_truncated(g, schema) for g in golds]}
        preds = {}
        for name, st in starts.items():
            out = []
            for lo in range(0, len(keep), args.batch_size):
                hi = min(lo + args.batch_size, len(keep))
                out += one_pass(model, head, tok, keep[lo:hi], ops[lo:hi], device,
                                schema, head_name, st[lo:hi])
            preds[name] = out
        cell = {"n": len(keep)}
        for name, pr in preds.items():
            cell[name] = {
                "slot_agree_with_gold": round(
                    sum(agree(p, g) for p, g in zip(pr, golds)) / len(pr), 4),
                "content_agree_with_gold": round(
                    sum(content_agree(p, g, schema) for p, g in zip(pr, golds))
                    / len(pr), 4),
                "exact_gold_array": round(
                    sum(1 for p, g in zip(pr, golds) if p == g) / len(pr), 4),
                "slot_agree_with_own_start": round(
                    sum(agree(p, s) for p, s in zip(pr, starts[name])) / len(pr), 4),
                "identical_to_all_mask_output": round(
                    sum(1 for p, q in zip(pr, preds["all_mask"]) if p == q)
                    / len(pr), 4),
            }
        restored = tot = 0
        for p, g, j in zip(preds["one_wrong"], golds, wslots):
            if j is None:
                continue
            tot += 1
            restored += int(p[j] == g[j])
        cell["one_wrong_opcode_restored"] = (round(restored / tot, 4) if tot else None)
        cell["one_wrong_opcode_n"] = tot
        res["by_depth"][str(depth)] = cell
        print(f"[d{depth}] n={cell['n']} " + json.dumps(
            {k: cell[k]["content_agree_with_gold"] for k in starts}) +
            f" identical_to_mask=" + json.dumps(
                {k: cell[k]["identical_to_all_mask_output"] for k in starts}) +
            f" restored={cell['one_wrong_opcode_restored']}", flush=True)

    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"[written] {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
