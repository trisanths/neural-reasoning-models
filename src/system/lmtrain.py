"""Teaching the 350M corpus checkpoint to emit the typed structure.

Not trained from scratch. `s3://decoupled-reasoner-009398924577/runs/
corpus-v1-8k/` already reads held-out frames at 0.990 to 1.000 forced choice
against a 0.200 floor, so the question this run asks is narrower than the
ladder's: can a checkpoint that already generalises over surface be taught to
write the structure down, and does it still generalise afterwards.

The optimizer settings are `src/corpus/RETRAIN.md`'s, which is the budget every
number on that checkpoint was measured under: batch 32 reached by micro batch
and accumulation, AdamW at 2e-5 with betas 0.9/0.95, no weight decay, grad clip
1.0, 200 warmup steps and cosine decay to a tenth, bfloat16 autocast. Loss
falls on the structure and the end marker only; the page and the question carry
none.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time

import numpy as np
import torch
import torch.nn.functional as F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--pack", default="data/system/lm")
    ap.add_argument("--out", required=True)
    ap.add_argument("--log", default="results/system/lm/train.jsonl")
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--micro", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--warmup", type=int, default=200)
    ap.add_argument("--min-lr-ratio", type=float, default=0.1)
    ap.add_argument("--weight-decay", type=float, default=0.0)
    ap.add_argument("--grad-clip", type=float, default=1.0)
    ap.add_argument("--log-every", type=int, default=25)
    ap.add_argument("--ckpt-every", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=1234)
    a = ap.parse_args()

    from src.evals.mc import load_checkpoint_model

    torch.manual_seed(a.seed)
    device = "cuda"
    model, state = load_checkpoint_model(a.ckpt, device)
    model.train()

    z = np.load(os.path.join(a.pack, "train.npz"))
    toks, mask, off = z["toks"], z["mask"], z["off"]
    n = len(off) - 1
    accum = a.batch // a.micro
    if accum * a.micro != a.batch:
        raise SystemExit("batch must be a multiple of micro")

    order = list(range(n))
    rng = random.Random(a.seed)
    rng.shuffle(order)
    cursor = 0

    def next_micro():
        nonlocal cursor
        if cursor + a.micro > len(order):
            rng.shuffle(order)
            cursor = 0
        rows = order[cursor:cursor + a.micro]
        cursor += a.micro
        w = max(int(off[i + 1] - off[i]) for i in rows)
        t = torch.zeros(len(rows), w, dtype=torch.long)
        m = torch.zeros(len(rows), w, dtype=torch.float)
        for i, r in enumerate(rows):
            s, e = int(off[r]), int(off[r + 1])
            t[i, :e - s] = torch.from_numpy(toks[s:e].astype(np.int64))
            m[i, :e - s] = torch.from_numpy(mask[s:e].astype(np.float32))
        return t.to(device), m.to(device)

    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, betas=(0.9, 0.95),
                            weight_decay=a.weight_decay, eps=1e-8)
    os.makedirs(os.path.dirname(a.log) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    log = open(a.log, "a")
    head = {"event": "start", "base": os.path.abspath(a.ckpt), "n": n,
            "steps": a.steps, "batch": a.batch, "micro": a.micro, "lr": a.lr,
            "params": sum(p.numel() for p in model.parameters()),
            "cfg": state["config"]["model"], "seed": a.seed}
    print(json.dumps(head), flush=True)
    log.write(json.dumps(head) + "\n")
    log.flush()

    t0 = time.time()
    for step in range(1, a.steps + 1):
        warm = min(1.0, step / max(1, a.warmup))
        frac = step / max(1, a.steps)
        lr = a.lr * warm * (a.min_lr_ratio + (1 - a.min_lr_ratio)
                            * 0.5 * (1 + math.cos(math.pi * frac)))
        for g in opt.param_groups:
            g["lr"] = lr
        opt.zero_grad(set_to_none=True)
        tot = 0.0
        for _ in range(accum):
            t, m = next_micro()
            x, y = t[:, :-1], t[:, 1:]
            mm = m[:, 1:]
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits, _ = model(x)
            ce = F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]),
                                 y.reshape(-1), reduction="none")
            loss = (ce * mm.reshape(-1)).sum() / mm.sum().clamp(min=1.0)
            (loss / accum).backward()
            tot += float(loss) / accum
            del logits, ce, loss
        gn = torch.nn.utils.clip_grad_norm_(model.parameters(), a.grad_clip)
        opt.step()
        if step % a.log_every == 0 or step == 1:
            rec = {"event": "step", "step": step, "loss": round(tot, 5),
                   "lr": lr, "grad_norm": round(float(gn), 4),
                   "sec": round(time.time() - t0, 1),
                   "gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)}
            print(json.dumps(rec), flush=True)
            log.write(json.dumps(rec) + "\n")
            log.flush()
        if a.ckpt_every and step % a.ckpt_every == 0 and step < a.steps:
            save(model, state, a, step, a.out)
    save(model, state, a, a.steps, a.out)
    done = {"event": "done", "out": os.path.abspath(a.out),
            "sec": round(time.time() - t0, 1)}
    print(json.dumps(done), flush=True)
    log.write(json.dumps(done) + "\n")
    log.close()


def save(model, state, a, step, path):
    save_obj = {"model": model.state_dict(), "config": state["config"],
                "step": step,
                "norm_sft": {"pack": a.pack, "steps": a.steps,
                             "batch": a.batch, "micro": a.micro, "lr": a.lr,
                             "warmup": a.warmup, "seed": a.seed,
                             "base": a.ckpt}}
    torch.save(save_obj, path + ".tmp")
    os.replace(path + ".tmp", path)


if __name__ == "__main__":
    main()
