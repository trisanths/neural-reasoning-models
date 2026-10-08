"""Training one rung of the parameter ladder.

The loop, the batching, the data and the quick eval are the norm lane's own.
`src/norm/ntrain.py:batches` and `make_batch` are imported rather than copied,
the training split is `data/norm/train` unchanged, and the frame split is
`src/norm/ndata.py:split_frames` unchanged, so a held-out frame here is held
out exactly as it was for the 45M run.

Two things this adds. Gradient accumulation, because a rung at d_model 1024
with 12 encoder and 12 decoder layers cannot hold the 45M rung's whole batch
at once on a 46GB card, and the batch is what has to stay fixed across the
ladder rather than the micro batch. And peak memory in the log, so a rung that
silently ran a smaller batch is visible.
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
from torch import nn

from src.norm import ndata, neval, nmodel
from src.norm.ntrain import batches, make_batch
from src.system import sizes


def split_micro(idx, n_micro):
    """One batch as n_micro contiguous slices, keeping every row."""
    if n_micro <= 1:
        return [idx]
    k = int(math.ceil(len(idx) / n_micro))
    return [idx[i:i + k] for i in range(0, len(idx), k)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="xl93", choices=list(sizes.LADDER))
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--out", default="results/system/train")
    ap.add_argument("--steps", type=int, default=15000)
    ap.add_argument("--budget", type=int, default=32768)
    ap.add_argument("--micro", type=int, default=1)
    ap.add_argument("--lr", type=float, default=0.0)
    ap.add_argument("--warmup", type=int, default=500)
    ap.add_argument("--eval-every", type=int, default=1500)
    ap.add_argument("--log-every", type=int, default=200)
    ap.add_argument("--final-eval", type=int, default=1)
    ap.add_argument("--eval-n", type=int, default=700)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()

    torch.manual_seed(a.seed)
    random.seed(a.seed)
    np.random.seed(a.seed)
    device = "cuda"
    iv, ov = ndata._vocab()
    tag = a.tag or a.size
    os.makedirs(a.out, exist_ok=True)
    log = open(os.path.join(a.out, f"log_{tag}.jsonl"), "a")

    ins, outs, ioff, ooff = ndata.load_split(os.path.join(a.data, "train"))
    n_train = len(ioff) - 1
    ins = ins.astype(np.int64)
    outs = outs.astype(np.int64)

    model = sizes.build(a.size, len(iv), len(ov)).to(device)
    pc = nmodel.count_params(model)
    lr = a.lr or sizes.LR[a.size]
    head = {"event": "start", "size": a.size, "cfg": sizes.LADDER[a.size],
            "params": pc, "lr": lr, "steps": a.steps, "n_train": n_train,
            "budget": a.budget, "micro": a.micro, "in_vocab": len(iv),
            "out_vocab": len(ov), "seed": a.seed, "tag": tag,
            "torch": torch.__version__}
    print(json.dumps(head), flush=True)
    log.write(json.dumps(head) + "\n")
    log.flush()

    bs = batches(ioff, ooff, a.budget)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.98),
                            weight_decay=0.01, eps=1e-9)
    lossf = nn.CrossEntropyLoss(ignore_index=ov.pad, reduction="sum")

    def lr_at(step):
        if step < a.warmup:
            return lr * step / max(1, a.warmup)
        t = (step - a.warmup) / max(1, a.steps - a.warmup)
        return lr * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * min(1.0, t))))

    ev = {k: neval.load_eval(os.path.join(a.data, k), a.eval_n)
          for k in ("train_frames_eval", "qframe", "lexicon", "mode")}

    step = 0
    t0 = time.time()
    order = list(range(len(bs)))
    run_loss, run_n = 0.0, 0
    while step < a.steps:
        random.shuffle(order)
        for bi in order:
            if step >= a.steps:
                break
            step += 1
            for g in opt.param_groups:
                g["lr"] = lr_at(step)
            opt.zero_grad(set_to_none=True)
            idx = bs[bi]
            built = [make_batch(m, ins, outs, ioff, ooff, iv.pad, ov.pad,
                                device)
                     for m in split_micro(idx, a.micro)]
            ntok = sum(int((t[:, 1:] != ov.pad).sum()) for _, _, t in built)
            tot = 0.0
            for src, spad, tgt in built:
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    logits = model(src, spad, tgt[:, :-1])
                    loss = lossf(logits.reshape(-1, logits.size(-1)).float(),
                                 tgt[:, 1:].reshape(-1)) / max(1, ntok)
                loss.backward()
                tot += float(loss.detach())
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            run_loss += tot
            run_n += 1
            if step % a.log_every == 0:
                rec = {"event": "step", "step": step,
                       "loss": round(run_loss / run_n, 4),
                       "lr": round(lr_at(step), 7),
                       "gb": round(torch.cuda.max_memory_allocated() / 2**30,
                                   2),
                       "sec": round(time.time() - t0, 1)}
                run_loss, run_n = 0.0, 0
                print(json.dumps(rec), flush=True)
                log.write(json.dumps(rec) + "\n")
                log.flush()
            if step % a.eval_every == 0 or (a.final_eval
                                            and step == a.steps):
                quick = {"event": "eval", "step": step}
                for k, items in ev.items():
                    em = neval.emit(model, items, ov, device, "greedy",
                                    batch=48)
                    ex = sum(int(neval.classify_emission(
                        ov.decode(e), it["slots"], it["prog"])["exact"])
                        for e, it in zip(em, items))
                    quick[k] = round(ex / len(items), 4)
                model.train()
                print(json.dumps(quick), flush=True)
                log.write(json.dumps(quick) + "\n")
                log.flush()
                ck = os.path.join(a.out, f"ckpt_{tag}.pt")
                torch.save({"size": a.size, "state": model.state_dict(),
                            "params": pc, "steps": step, "n_train": n_train,
                            "seed": a.seed, "ladder": True}, ck + ".tmp")
                os.replace(ck + ".tmp", ck)

    ck = os.path.join(a.out, f"ckpt_{tag}.pt")
    torch.save({"size": a.size, "state": model.state_dict(), "params": pc,
                "steps": a.steps, "n_train": n_train, "seed": a.seed,
                "ladder": True}, ck)
    done = {"event": "done", "ckpt": os.path.abspath(ck),
            "sec": round(time.time() - t0, 1), "params": pc,
            "peak_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)}
    print(json.dumps(done), flush=True)
    log.write(json.dumps(done) + "\n")
    log.close()


if __name__ == "__main__":
    main()
