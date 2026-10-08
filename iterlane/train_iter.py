"""Fine tune one plan head from the shared base checkpoint.

Five heads, one trainer, one schedule. Every head sees the same worlds drawn
from the same seeds, the same four questions per world, the same induction
supervision under the same text objective, the same number of optimizer steps
and the same number of sequences per step. The only thing that changes is how a
plan is written down and how it is produced.

  p1   plan text in the page's own operator symbols, causal, pretrained lm_head
  p2   plan text in dedicated opcode tokens, causal, pretrained lm_head
  p2s  the slot array of p3, committed left to right under a causal mask
  p3   the slot array, corrupted and repaired, bidirectional
  p4   the graph slot array with dependency edges, corrupted and repaired

The step schedule alternates: even steps are an induction batch, odd steps are a
plan batch. Both pools are shuffled with the same seed for every head, so step k
of one head and step k of another hold the same worlds and the same questions.

Holdout, asserted here rather than assumed: no training plan is deeper than
three steps and no training plan uses two distinct induced operator symbols.
The assertion runs over the whole pool before the first optimizer step and the
counts are printed, because a holdout that is only described is a holdout that
has already been broken once on this project.

Sequences that do not fit inside max_len are counted rather than dropped in
silence. The slot heads raise on a prompt that does not fit; a text head that
quietly dropped one would take a smaller step on the same nominal batch size,
and the arms would stop being matched on sequences per step without saying so.
The counts go to stdout and into the run log next to the checkpoint.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time

import torch

from src.opgraph.data import IGNORE, encode_example, induce_prompt
from src.opgraph.invent import (breadth_item, make_world, seq_flat, seq_paren,
                                units_item)
from src.opgraph.opdef import serialize_all
from src.opgraph.plan import BUILTIN_STEPS, serialize_plan
from src.opgraph.planheads import (HEADS, SlotPlanHead, all_masked, corrupt,
                                   encode_plan, field_logit_mask, mixture_for,
                                   plan_prompt_text, readout, schema_for,
                                   slot_forward, slot_logits, to_opcode_text)
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer


def episode(seed: int):
    """One world and its four questions. Identical to data.training_examples."""
    rng = random.Random(seed * 104729 + 7)
    breadth = rng.choice([1, 2, 3])
    w = make_world(seed, breadth=breadth)
    items = [seq_flat(w, rng, rng.choice([1, 2, 3])),
             seq_paren(w, rng, rng.choice([2, 3])),
             breadth_item(w, rng, breadth),
             units_item(w, rng)]
    return w, items


def build_pools(n_worlds: int, seed: int = 17):
    """The induction pool and the plan pool, in the order every head sees them."""
    ind: list[tuple[str, str]] = []
    plans: list = []
    for s in range(n_worlds):
        w, items = episode(s)
        for p in w.shuffled_pages():
            ind.append((induce_prompt(p.text), serialize_all(p.ops)))
        for it in items:
            plans.append(it)
    random.Random(seed).shuffle(ind)
    random.Random(seed + 1).shuffle(plans)
    return ind, plans


def check_holdout(plans) -> dict:
    """Depth at most three, at most one induced symbol. Fails loudly."""
    depths: dict[int, int] = {}
    worst = 0
    for it in plans:
        d = len(it.plan.steps)
        depths[d] = depths.get(d, 0) + 1
        syms = {s.symbol for s in it.plan.steps if s.symbol not in BUILTIN_STEPS}
        worst = max(worst, len(syms))
        if d > 3:
            raise SystemExit(f"holdout broken: a training plan has depth {d}")
        if len(syms) > 1:
            raise SystemExit(f"holdout broken: a training plan uses {sorted(syms)}")
    return {"depth_histogram": {str(k): depths[k] for k in sorted(depths)},
            "max_distinct_operator_symbols": worst, "plans": len(plans)}


def text_batch(tok, pairs, max_len: int, device):
    """Padded ids and labels, plus how many pairs did not fit inside max_len.

    A dropped pair is not a neutral event here. The slot heads raise when a
    prompt does not fit, so a text head that quietly dropped one instead would
    take a smaller optimizer step on the same nominal batch size, and the arms
    would stop being matched on sequences per step without saying so. The count
    is returned, accumulated, printed and written into the run log.
    """
    enc = [encode_example(tok, p, t, max_len) for p, t in pairs]
    dropped = sum(1 for e in enc if e is None)
    enc = [e for e in enc if e is not None]
    if not enc:
        return None, dropped
    width = max(len(a) for a, _ in enc)
    ids = torch.zeros(len(enc), width, dtype=torch.long)
    lab = torch.full((len(enc), width), IGNORE, dtype=torch.long)
    for i, (a, b) in enumerate(enc):
        ids[i, :len(a)] = torch.tensor(a)
        lab[i, :len(b)] = torch.tensor(b)
    return (ids.to(device), lab.to(device)), dropped


def slot_batch(tok, items, head: str, max_len: int, device, rng: random.Random):
    """Prompt ids, prompt mask, input slot symbols and gold slot symbols."""
    schema = schema_for(head)
    mixture = mixture_for(head)
    prompts, golds, kinds = [], [], []
    for it in items:
        ops = it.world.ops
        try:
            golds.append(encode_plan(it.plan, ops, schema))
        except Exception as exc:  # a plan this head cannot represent
            raise SystemExit(f"encode_plan failed on a training item: {exc}")
        prompts.append(tok.encode(plan_prompt_text(ops, it.text, head)))
    pw = max(len(p) for p in prompts)
    if pw + schema.n_slots > max_len:
        raise SystemExit(f"prompt {pw} plus {schema.n_slots} slots over max_len")
    n = len(items)
    pad = torch.zeros(n, pw, dtype=torch.long)
    ok = torch.zeros(n, pw, dtype=torch.bool)
    for i, p in enumerate(prompts):
        pad[i, pw - len(p):] = torch.tensor(p)
        ok[i, pw - len(p):] = True
    gold = torch.tensor(golds, dtype=torch.long)
    if head == "p2s":
        inp = gold.clone()          # teacher forcing under the causal mask
        kinds = ["teacher_forced"] * n
    else:
        rows = []
        for i, it in enumerate(items):
            c, kind = corrupt(golds[i], schema, len(it.world.ops), rng, mixture)
            rows.append(c)
            kinds.append(kind)
        inp = torch.tensor(rows, dtype=torch.long)
    return (pad.to(device), ok.to(device), inp.to(device), gold.to(device), kinds)


def save_blob(path, model, state, args, holdout, kind_counts, dropped, head, step, log):
    blob = {"model": model.state_dict(), "config": state["config"],
            "head": args.head, "step": step, "args": vars(args),
            "holdout": holdout, "corruption_mixture": mixture_for(args.head),
            "corruption_counts": kind_counts, "dropped": dropped}
    if head is not None:
        blob["plan_head"] = head.state_dict()
    torch.save(blob, path)
    with open(path + ".log.json", "w") as fh:
        json.dump({"head": args.head, "step": step, "args": vars(args),
                   "holdout": holdout, "corruption_mixture": mixture_for(args.head),
                   "corruption_counts": kind_counts, "dropped": dropped,
                   "log": log}, fh, indent=1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--head", required=True, choices=list(HEADS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--head-lr", type=float, default=2e-4)
    ap.add_argument("--warmup", type=int, default=200)
    ap.add_argument("--worlds", type=int, default=40000)
    ap.add_argument("--log-every", type=int, default=100)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--ckpt-every", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    state = torch.load(args.base, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    model.to(device).train()

    head = None
    schema = None
    if args.head in ("p2s", "p3", "p4"):
        schema = schema_for(args.head)
        head = SlotPlanHead(model.cfg.d_model).to(device).train()

    ind_pool, plan_pool = build_pools(args.worlds, seed=args.seed)
    holdout = check_holdout(plan_pool)
    print("[holdout]", json.dumps(holdout), flush=True)
    print(f"[pools] induction={len(ind_pool)} plans={len(plan_pool)} "
          f"head={args.head}", flush=True)
    if head is not None:
        print(f"[head] params={sum(p.numel() for p in head.parameters())} "
              f"slots={schema.n_slots} mixture={json.dumps(mixture_for(args.head))}",
          flush=True)

    groups = [{"params": list(model.parameters()), "lr": args.lr, "base": args.lr}]
    if head is not None:
        groups.append({"params": list(head.parameters()), "lr": args.head_lr,
                       "base": args.head_lr})
    opt = torch.optim.AdamW(groups, betas=(0.9, 0.95), weight_decay=0.1)

    fmask = (field_logit_mask(schema.fields, device) if schema is not None else None)
    corr_rng = random.Random(args.seed * 31 + 5)
    log: list[dict] = []
    kind_counts: dict[str, int] = {}
    dropped = {"induce": 0, "plan": 0, "sequences": 0}
    ic = pc = 0
    t0 = time.time()
    for step in range(1, args.steps + 1):
        frac = (step / args.warmup if step < args.warmup else
                0.5 * (1 + math.cos(math.pi * (step - args.warmup) /
                                    max(1, args.steps - args.warmup))))
        for g in opt.param_groups:
            g["lr"] = g["base"] * frac
        if step % 2 == 1:
            batch = [ind_pool[(ic + i) % len(ind_pool)] for i in range(args.batch_size)]
            ic += args.batch_size
            tb, drop = text_batch(tok, batch, args.max_len, device)
            dropped["induce"] += drop
            dropped["sequences"] += args.batch_size
            if tb is None:
                continue
            ids, lab = tb
            with torch.autocast(device_type=device, dtype=torch.bfloat16):
                _, loss = model(ids[:, :-1], lab[:, 1:])
            tag = "induce"
        else:
            batch = [plan_pool[(pc + i) % len(plan_pool)] for i in range(args.batch_size)]
            pc += args.batch_size
            if args.head in ("p1", "p2"):
                pairs = []
                for it in batch:
                    ops = it.world.ops
                    target = serialize_plan(it.plan)
                    if args.head == "p2":
                        target = to_opcode_text(target, ops)
                    pairs.append((plan_prompt_text(ops, it.text, args.head), target))
                tb, drop = text_batch(tok, pairs, args.max_len, device)
                dropped["plan"] += drop
                dropped["sequences"] += args.batch_size
                if tb is None:
                    continue
                ids, lab = tb
                with torch.autocast(device_type=device, dtype=torch.bfloat16):
                    _, loss = model(ids[:, :-1], lab[:, 1:])
            else:
                dropped["sequences"] += args.batch_size
                pad, ok, inp, gold, kinds = slot_batch(
                    tok, batch, args.head, args.max_len, device, corr_rng)
                for k in kinds:
                    kind_counts[k] = kind_counts.get(k, 0) + 1
                causal = args.head == "p2s"
                with torch.autocast(device_type=device, dtype=torch.bfloat16):
                    hidden = slot_forward(model, head, pad, ok, inp, schema, causal)
                logits = slot_logits(head, readout(hidden, causal).float(), fmask)
                loss = torch.nn.functional.cross_entropy(
                    logits.reshape(-1, logits.shape[-1]), gold.reshape(-1))
            tag = "plan"
        opt.zero_grad(set_to_none=True)
        loss.backward()
        params = list(model.parameters()) + (list(head.parameters()) if head else [])
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        if args.ckpt_every and step % args.ckpt_every == 0 and step != args.steps:
            p = args.out[:-3] + f"_s{step}.pt" if args.out.endswith(".pt") else args.out + f"_s{step}"
            save_blob(p, model, state, args, holdout, kind_counts, dropped, head, step, log)
            print(f"[ckpt] step={step} -> {p}", flush=True)
        if step % args.log_every == 0 or step == 1:
            rec = {"step": step, "kind": tag, "loss": round(float(loss.item()), 5),
                   "lr": round(opt.param_groups[0]["lr"], 8),
                   "secs": round(time.time() - t0, 1)}
            log.append(rec)
            print(json.dumps(rec), flush=True)

    print(f"[dropped] {json.dumps(dropped)}", flush=True)
    if dropped["induce"] or dropped["plan"]:
        print("[dropped] WARNING: sequences did not fit max_len, so this arm "
              "took fewer sequences per step than an arm with no drops",
              flush=True)
    blob = {"model": model.state_dict(), "config": state["config"],
            "head": args.head, "step": args.steps, "args": vars(args),
            "holdout": holdout, "corruption_mixture": mixture_for(args.head),
            "corruption_counts": kind_counts, "dropped": dropped}
    if head is not None:
        blob["plan_head"] = head.state_dict()
    torch.save(blob, args.out)
    with open(args.out + ".log.json", "w") as fh:
        json.dump({"head": args.head, "args": vars(args), "holdout": holdout,
                   "corruption_mixture": mixture_for(args.head),
                   "corruption_counts": kind_counts, "dropped": dropped,
                   "log": log}, fh, indent=1)
    print(f"[done] head={args.head} -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
