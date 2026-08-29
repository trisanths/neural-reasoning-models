"""Fine tune one latent condition from the shared base checkpoint.

  latent_answer   condition D. R latent steps, then the answer. Nothing
                  external runs. The answer comes out of the latent state.
  latent_plan     condition E. R latent steps, then an opcode plan, which
                  src.opgraph.plan's executor runs. The same induction half the
                  opgraph arm trains on is in the stream, with no latent
                  positions, in the same proportion.

Matched against the token channel arms on: base checkpoint, worlds, seeds,
questions, page subset draws, optimizer, batch size in sequences, optimizer
steps, held out ranges.

Not matched, and reported rather than buried:

  parameters   the latent head adds 2 * slots * d_model, and with proj=linear
               another d_model squared. Printed at startup and stored in the
               checkpoint.
  training compute  a step costs R + 1 forward passes rather than one. The arms
               are matched on optimizer steps and batch size, not on training
               FLOPs, and this asymmetry favours the latent conditions. Every
               log line carries the passes and the token positions spent.

Run without a curriculum first. Whether latent recurrence trains at all with
the loss placed only on the answer is a finding on its own, and reporting "it
did not train" as "it does not work" would be the worst outcome available here.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time

import torch

from src.latent.chain import ChainCost, run_chain
from src.latent.core import LatentHead, measure_scale, with_depth_recurrence
from src.latent.data import (ARMS, answer_target, build_episodes,
                             build_induction, chunks_of, collate, encode,
                             latent_answer_prompt, latent_plan_prompt,
                             plan_target)
from src.opgraph.plan import trace_text
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer


def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--arm", required=True, choices=list(ARMS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--head-lr", type=float, default=None,
                    help="learning rate for the latent head, default --lr")
    ap.add_argument("--warmup", type=int, default=200)
    ap.add_argument("--worlds", type=int, default=40000)
    ap.add_argument("--log-every", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    # the latent channel
    ap.add_argument("--r", type=int, default=4, help="latent steps per example")
    ap.add_argument("--r-sampling", default="",
                    help="lo,hi to draw R per optimizer step, the same idea as "
                         "model.recurrent.train_loop_sampling")
    ap.add_argument("--proj", default="none", choices=["none", "linear"])
    ap.add_argument("--film-slots", type=int, default=0,
                    help="0 means the largest R this run can ask for")
    ap.add_argument("--backprop-last-k", type=int, default=None)
    # curriculum
    ap.add_argument("--curriculum", default="none",
                    choices=["none", "stage", "ramp"])
    ap.add_argument("--latents-per-step", type=int, default=2)
    ap.add_argument("--stage-steps", type=int, default=1000)
    ap.add_argument("--stage-mix", type=float, default=0.3)
    # halting
    ap.add_argument("--halting", default="none", choices=["none", "ponder"])
    ap.add_argument("--ponder-beta", type=float, default=0.01)
    # optional depth recurrence, off by default
    ap.add_argument("--depth-recurrence", default="",
                    help="prelude,core,coda,loops to run the middle layers as a "
                         "weight tied core; changes the base function")
    ap.add_argument("--induction-frac", type=float, default=0.5,
                    help="latent_plan only: fraction of batches drawn from the "
                         "induction half, matching the opgraph arm's stream")
    return ap.parse_args(argv)


def max_r(args) -> int:
    if args.r_sampling:
        return max(args.r, int(args.r_sampling.split(",")[1]))
    if args.curriculum == "stage":
        return max(args.r, args.latents_per_step * 8)
    return args.r


class Prepared:
    """Episodes with their prompts tokenized once, and the drop table."""

    def __init__(self, tok, arm, episodes, max_len, r_cap):
        self.tok = tok
        self.arm = arm
        self.kept = []
        self.dropped: dict[str, int] = {}
        for ep in episodes:
            prompt = (latent_answer_prompt(ep.item.world, ep.item.text, ep.keys)
                      if arm == "latent_answer"
                      else latent_plan_prompt(ep.item.world.ops, ep.item.text))
            worst = self._worst_target(ep)
            need = (len(tok.encode(prompt)) + r_cap + 1
                    + len(tok.encode(" " + worst)) + 1)
            if need > max_len:
                self.dropped[ep.kind] = self.dropped.get(ep.kind, 0) + 1
                continue
            self.kept.append((ep, prompt))

    def _worst_target(self, ep):
        if self.arm == "latent_plan":
            return plan_target(ep)
        return trace_text(ep.item.plan, ep.item.world.ops)


def stage_for(step: int, args, rng: random.Random, k_max: int) -> int:
    if args.curriculum == "none":
        return k_max
    k = min(k_max, step // max(1, args.stage_steps))
    if args.stage_mix and rng.random() < args.stage_mix and k > 0:
        k = rng.randrange(0, k + 1)
    return k


def main(argv=None) -> int:
    args = parse_args(argv)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    torch.manual_seed(args.seed)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    state = torch.load(args.base, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    rec_report = None
    if args.depth_recurrence:
        p, c, k, lo = (int(x) for x in args.depth_recurrence.split(","))
        model, rec_report = with_depth_recurrence(model, p, c, k, lo)
    model.to(device)
    model.train()

    r_cap = max_r(args)
    slots = args.film_slots or max(1, r_cap)

    seeds = range(args.worlds)
    episodes = build_episodes(seeds)
    prep = Prepared(tok, args.arm, episodes, args.max_len, r_cap)
    if not prep.kept:
        raise SystemExit("every episode was dropped for length")
    k_max = max(len(chunks_of(trace_text(e.item.plan, e.item.world.ops))[0])
                for e, _ in prep.kept) if args.arm == "latent_answer" else 0
    induction = build_induction(seeds) if args.arm == "latent_plan" else []

    # The injection scale is measured on real prompts, not on a degenerate
    # batch: it has to match the RMS of the states these sequences actually
    # produce, and a run of one repeated token does not produce them.
    cal_ids = [tok.encode(p)[:256] for _, p in prep.kept[:4]]
    cw = min(len(x) for x in cal_ids)
    cal = torch.tensor([x[:cw] for x in cal_ids], dtype=torch.long,
                       device=device)
    scale = measure_scale(model, cal)
    head = LatentHead(model.cfg.d_model, slots, proj=args.proj, scale=scale)
    head.to(device).train()

    gate = None
    if args.halting == "ponder":
        from src.latentret.gate import RetrievalGate
        gate = RetrievalGate(model.cfg.d_model, norm_eps=model.cfg.norm_eps)
        gate.to(device).train()

    head_params = head.num_params() + (sum(p.numel() for p in gate.parameters())
                                       if gate is not None else 0)
    setup = {
        "arm": args.arm, "device": device,
        "episodes": len(episodes), "kept": len(prep.kept),
        "dropped_over_max_len": prep.dropped,
        "induction_examples": len(induction),
        "latent_scale": round(scale, 4), "film_slots": slots,
        "r": args.r, "r_cap": r_cap, "curriculum": args.curriculum,
        "k_max_chunks": k_max,
        "base_params": model.num_params(non_embedding=False),
        "added_params": head_params,
        "added_params_frac": head_params / model.num_params(non_embedding=False),
        "effective_depth": model.cfg.effective_depth(),
        "depth_recurrence": rec_report,
    }
    print(json.dumps(setup), flush=True)

    params = [{"params": list(model.parameters()), "lr": args.lr},
              {"params": list(head.parameters()),
               "lr": args.head_lr or args.lr}]
    if gate is not None:
        params.append({"params": list(gate.parameters()),
                       "lr": args.head_lr or args.lr})
    opt = torch.optim.AdamW(params, lr=args.lr, betas=(0.9, 0.95),
                            weight_decay=0.1)
    base_lrs = [g["lr"] for g in opt.param_groups]

    rng = random.Random(args.seed + 11)
    order = list(range(len(prep.kept)))
    rng.shuffle(order)
    cursor = 0
    ind_order = list(range(len(induction)))
    rng.shuffle(ind_order)
    ind_cursor = 0

    log: list[dict] = []
    total = ChainCost()
    seen_tokens = 0
    supervised = 0
    t0 = time.time()
    r_sample = None
    if args.r_sampling:
        lo, hi = (int(x) for x in args.r_sampling.split(","))
        r_sample = (lo, hi)

    for step in range(1, args.steps + 1):
        use_induction = (args.arm == "latent_plan" and induction
                         and rng.random() < args.induction_frac)
        if use_induction:
            batch, ind_cursor = _take(induction, ind_order, ind_cursor,
                                      args.batch_size, rng)
            enc = [encode(tok, p, t, 0, args.max_len, kind="induce",
                          add_answer_token=False) for p, t in batch]
            enc = [e for e in enc if e is not None]
            if not enc:
                continue
            n_latent = 0
        else:
            stage = stage_for(step, args, rng, k_max)
            if args.curriculum == "none":
                n_latent = args.r
            elif args.curriculum == "stage":
                n_latent = args.latents_per_step * stage
            else:
                n_latent = min(args.r, args.latents_per_step * stage)
            if r_sample is not None:
                n_latent = rng.randint(*r_sample)
            batch, cursor = _take(prep.kept, order, cursor, args.batch_size, rng)
            enc = []
            for ep, prompt in batch:
                target = (plan_target(ep) if args.arm == "latent_plan"
                          else answer_target(ep, stage if args.curriculum ==
                                             "stage" else k_max))
                e = encode(tok, prompt, target, n_latent, args.max_len,
                           kind=ep.kind)
                if e is not None:
                    enc.append(e)
            if not enc:
                continue

        packed = collate(enc)
        packed = {k: (v.to(device) if torch.is_tensor(v) else v)
                  for k, v in packed.items()}
        seen_tokens += int(packed["ids"].numel())
        supervised += int((packed["tgt"] != -100).sum())

        frac = (step / args.warmup if step < args.warmup else
                0.5 * (1 + math.cos(math.pi * (step - args.warmup) /
                                    max(1, args.steps - args.warmup))))
        for g, base in zip(opt.param_groups, base_lrs):
            g["lr"] = base * frac

        with torch.autocast(device_type=device, dtype=torch.bfloat16):
            out = run_chain(model, head, packed, gate=gate,
                            ponder_beta=args.ponder_beta,
                            backprop_last_k=args.backprop_last_k,
                            loss_at="all" if gate is not None else "last")
        opt.zero_grad(set_to_none=True)
        out.loss.backward()
        torch.nn.utils.clip_grad_norm_(
            [p for g in opt.param_groups for p in g["params"]], 1.0)
        opt.step()
        total.add(out.cost)

        if step % args.log_every == 0 or step == 1:
            rec = {"step": step, "loss": float(out.loss.item()),
                   "n_latent": n_latent, "induction": bool(use_induction),
                   "lr": base_lrs[0] * frac, "tokens": seen_tokens,
                   "supervised": supervised,
                   "fwd_passes": total.passes,
                   "fwd_positions": total.positions,
                   "reason_passes": total.reason_passes,
                   "peak_gib": (round(torch.cuda.max_memory_allocated() / 2**30, 2)
                                if device == "cuda" else 0.0),
                   "secs": round(time.time() - t0, 1)}
            if out.ponder is not None:
                rec["ponder_kl"] = float(out.ponder.item())
                rec["halt_mean_step"] = float(
                    (out.halt_probs
                     * torch.arange(out.halt_probs.shape[1],
                                    device=out.halt_probs.device)
                     ).sum(1).mean().item())
            log.append(rec)
            print(json.dumps(rec), flush=True)

    payload = {"model": model.state_dict(), "head": head.state_dict(),
               "head_config": head.config(), "config": state["config"],
               "arm": args.arm, "args": vars(args), "setup": setup,
               "cost": total.as_dict(), "step": args.steps,
               "peak_gib": (round(torch.cuda.max_memory_allocated() / 2**30, 2)
                            if device == "cuda" else 0.0)}
    if gate is not None:
        payload["gate"] = gate.state_dict()
    torch.save(payload, args.out)
    with open(args.out + ".log.json", "w") as fh:
        json.dump({"arm": args.arm, "args": vars(args), "setup": setup,
                   "cost": total.as_dict(), "log": log}, fh, indent=1)
    print(f"[done] {args.arm} -> {args.out} passes={total.passes} "
          f"positions={total.positions} secs={round(time.time() - t0, 1)}",
          flush=True)
    return 0


def _take(pool, order, cursor, n, rng):
    """n items from a shuffled cursor over the pool, reshuffling at the end."""
    out = []
    while len(out) < n:
        if cursor >= len(order):
            rng.shuffle(order)
            cursor = 0
        out.append(pool[order[cursor]])
        cursor += 1
    return out, cursor


if __name__ == "__main__":
    raise SystemExit(main())
