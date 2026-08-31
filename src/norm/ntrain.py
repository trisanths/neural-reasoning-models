"""Training the normalizer, and the size sweep.

One job: invert the rendering. The structure came first and the text was
derived from it, so every target is exact and the loss is an ordinary
cross entropy over a translation, not a reward over a search. That is the
property the thesis rests on, and it is why this trains at all.

Nothing about the world is learned. The network never sees a gold answer, never
executes anything, and is never told what a page means.
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
from src.norm.ntok import InputVocab, OutVocab


def batches(ioff, ooff, budget: int, max_rows: int = 512):
    """Length bucketed batches: sort by source length, cap padded tokens."""
    n = len(ioff) - 1
    lens = (ioff[1:] - ioff[:-1])
    order = np.argsort(lens, kind="stable")
    out, cur, w = [], [], 0
    for i in order:
        li = int(lens[i])
        nw = max(w, li)
        if cur and (nw * (len(cur) + 1) > budget or len(cur) >= max_rows):
            out.append(np.asarray(cur))
            cur, w = [], 0
            nw = li
        cur.append(int(i))
        w = nw
    if cur:
        out.append(np.asarray(cur))
    return out


def make_batch(idx, ins, outs, ioff, ooff, pad_in, pad_out, device):
    sl = [int(ioff[i + 1] - ioff[i]) for i in idx]
    tl = [int(ooff[i + 1] - ooff[i]) for i in idx]
    sw, tw = max(sl), max(tl)
    src = np.full((len(idx), sw), pad_in, dtype=np.int64)
    tgt = np.full((len(idx), tw), pad_out, dtype=np.int64)
    for r, i in enumerate(idx):
        src[r, :sl[r]] = ins[ioff[i]:ioff[i + 1]]
        tgt[r, :tl[r]] = outs[ooff[i]:ooff[i + 1]]
    spad = torch.from_numpy(src == pad_in).to(device, non_blocking=True)
    src = torch.from_numpy(src).to(device, non_blocking=True)
    tgt = torch.from_numpy(tgt).to(device, non_blocking=True)
    return src, spad, tgt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="s", choices=list(nmodel.SIZES))
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--out", default="results/norm/train")
    ap.add_argument("--steps", type=int, default=12000)
    ap.add_argument("--budget", type=int, default=32768)
    ap.add_argument("--lr", type=float, default=0.0)
    ap.add_argument("--warmup", type=int, default=500)
    ap.add_argument("--eval-every", type=int, default=2000)
    ap.add_argument("--eval-n", type=int, default=700)
    ap.add_argument("--train-examples", type=int, default=0)
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
    logp = os.path.join(a.out, f"log_{tag}.jsonl")
    log = open(logp, "a")

    ins, outs, ioff, ooff = ndata.load_split(os.path.join(a.data, "train"))
    if a.train_examples:
        n = min(a.train_examples, len(ioff) - 1)
        ioff, ooff = ioff[:n + 1], ooff[:n + 1]
        ins, outs = ins[:ioff[-1]], outs[:ooff[-1]]
    n_train = len(ioff) - 1
    ins = ins.astype(np.int64)
    outs = outs.astype(np.int64)

    model = nmodel.build(a.size, len(iv), len(ov)).to(device)
    pc = nmodel.count_params(model)
    lr = a.lr or {"xs": 1.5e-3, "s": 1e-3, "m": 6e-4, "l": 4e-4}[a.size]
    head = {"event": "start", "size": a.size, "params": pc, "lr": lr,
            "steps": a.steps, "n_train": n_train, "budget": a.budget,
            "in_vocab": len(iv), "out_vocab": len(ov), "seed": a.seed,
            "tag": tag}
    print(json.dumps(head), flush=True)
    log.write(json.dumps(head) + "\n")
    log.flush()

    bs = batches(ioff, ooff, a.budget)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.98),
                            weight_decay=0.01, eps=1e-9)
    lossf = nn.CrossEntropyLoss(ignore_index=ov.pad)

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
            src, spad, tgt = make_batch(bs[bi], ins, outs, ioff, ooff,
                                        iv.pad, ov.pad, device)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(src, spad, tgt[:, :-1])
                loss = lossf(logits.reshape(-1, logits.size(-1)).float(),
                             tgt[:, 1:].reshape(-1))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            run_loss += float(loss.detach())
            run_n += 1
            if step % 200 == 0:
                rec = {"event": "step", "step": step,
                       "loss": round(run_loss / run_n, 4),
                       "lr": round(lr_at(step), 6),
                       "sec": round(time.time() - t0, 1)}
                run_loss, run_n = 0.0, 0
                print(json.dumps(rec), flush=True)
                log.write(json.dumps(rec) + "\n")
                log.flush()
            if step % a.eval_every == 0 or step == a.steps:
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
    torch.save({"size": a.size, "state": model.state_dict(), "params": pc,
                "steps": a.steps, "n_train": n_train, "seed": a.seed}, ck)
    done = {"event": "done", "ckpt": ck, "sec": round(time.time() - t0, 1),
            "params": pc}
    print(json.dumps(done), flush=True)
    log.write(json.dumps(done) + "\n")
    log.close()


if __name__ == "__main__":
    main()
