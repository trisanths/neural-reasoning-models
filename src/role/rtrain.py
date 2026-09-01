"""One arm of the role experiment, trained.

With no options this is `src/system/strain.py` at the 45M rung: the same model
class, the same `src/norm/ntrain.py:batches` length bucketing, the same
`make_batch`, the same schedule, the same seed and the same training file, so
arm A is a reproduction and not a near miss. Two switches are added and each
arm turns on exactly one of them.

    --pairs 1        the training file holds minimal pairs at rows 2k and
                     2k+1, and batching keeps the two together. Length
                     bucketing sorts by the longer of the two, and a batch
                     takes whole pairs, so no pair is ever split across two
                     optimiser steps.

    --aux W          a linear head over the encoder output predicts, at every
                     input position that is a copy slot, whether that invented
                     word is used as a key and whether it is used as a value.
                     Two independent bits, so a compose chain's middle level
                     can be both. The head is not part of the model: it is not
                     in `state`, the parameter count does not move, and the
                     checkpoint loads through `src/system/sreport.py`
                     unchanged. It shapes the encoder during training and then
                     goes away.

The main loss is unchanged in both: cross entropy over target tokens, summed
and divided by the number of target tokens in the whole batch. The auxiliary
loss is a mean over the slot positions of the batch, so W is the ratio between
two per-token means and does not drift with batch composition.
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
from src.norm.ntok import MAX_SLOTS
from src.norm.ntrain import batches, make_batch
from src.system import sizes


def pair_batches(ioff, budget: int, max_rows: int = 512):
    """Length bucketed batches over pairs, never splitting one.

    `src/norm/ntrain.py:batches` with the row replaced by the pair: the width
    of a pair is the longer of its two sources, pairs are sorted by that, and
    a batch closes when the padded source tokens it would hold exceed the
    budget. Rows come out as 2k, 2k+1, so the two members of a pair are always
    in the same optimiser step.
    """
    lens = (ioff[1:] - ioff[:-1])
    n_pairs = (len(ioff) - 1) // 2
    w = np.maximum(lens[0:2 * n_pairs:2], lens[1:2 * n_pairs:2])
    order = np.argsort(w, kind="stable")
    out, cur, width = [], [], 0
    for p in order:
        lp = int(w[p])
        nw = max(width, lp)
        if cur and (nw * (2 * len(cur) + 2) > budget
                    or 2 * len(cur) + 2 > max_rows):
            out.append(np.asarray([i for k in cur for i in (2 * k, 2 * k + 1)]))
            cur, width = [], 0
            nw = lp
        cur.append(int(p))
        width = nw
    if cur:
        out.append(np.asarray([i for k in cur for i in (2 * k, 2 * k + 1)]))
    return out


class AuxHead(nn.Module):
    """Key and value, as two independent bits, at every copy slot position."""

    def __init__(self, d_model: int):
        super().__init__()
        self.lin = nn.Linear(d_model, 2)
        nn.init.normal_(self.lin.weight, std=0.02)
        nn.init.zeros_(self.lin.bias)

    def forward(self, mem):
        return self.lin(mem)


def aux_targets(src, roles_b, slot0):
    """(is_key, is_value, which positions count) for one batch."""
    is_slot = src >= slot0
    sidx = (src - slot0).clamp(min=0, max=MAX_SLOTS - 1)
    lab = torch.gather(roles_b, 1, sidx)
    tgt = torch.stack([(lab & 1).float(), ((lab >> 1) & 1).float()], -1)
    return tgt, is_slot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="l45", choices=list(sizes.LADDER))
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--train-split", default="")
    ap.add_argument("--roles", default="")
    ap.add_argument("--out", default="results/role/train")
    ap.add_argument("--steps", type=int, default=30000)
    ap.add_argument("--budget", type=int, default=32768)
    ap.add_argument("--lr", type=float, default=0.0)
    ap.add_argument("--warmup", type=int, default=500)
    ap.add_argument("--eval-every", type=int, default=3000)
    ap.add_argument("--eval-n", type=int, default=700)
    ap.add_argument("--pairs", type=int, default=0)
    ap.add_argument("--aux", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()

    torch.manual_seed(a.seed)
    random.seed(a.seed)
    np.random.seed(a.seed)
    device = a.device
    iv, ov = ndata._vocab()
    os.makedirs(a.out, exist_ok=True)
    log = open(os.path.join(a.out, f"log_{a.tag}.jsonl"), "a")

    tsplit = a.train_split or os.path.join(a.data, "train")
    ins, outs, ioff, ooff = ndata.load_split(tsplit)
    n_train = len(ioff) - 1
    ins = ins.astype(np.int64)
    outs = outs.astype(np.int64)

    roles = None
    if a.aux:
        rp = a.roles or (tsplit + ".roles.npy")
        roles = np.load(rp)
        if len(roles) != n_train:
            raise SystemExit(f"{rp} has {len(roles)} rows, split has {n_train}")

    model = sizes.build(a.size, len(iv), len(ov)).to(device)
    pc = nmodel.count_params(model)
    lr = a.lr or sizes.LR[a.size]
    params = list(model.parameters())
    head = None
    if a.aux:
        head = AuxHead(sizes.LADDER[a.size]["d_model"]).to(device)
        params += list(head.parameters())

    head_rec = {"event": "start", "size": a.size, "cfg": sizes.LADDER[a.size],
                "params": pc, "lr": lr, "steps": a.steps, "n_train": n_train,
                "budget": a.budget, "in_vocab": len(iv), "out_vocab": len(ov),
                "seed": a.seed, "tag": a.tag, "torch": torch.__version__,
                "train_split": os.path.abspath(tsplit), "pairs": a.pairs,
                "aux": a.aux,
                "roles": os.path.abspath(a.roles or (tsplit + ".roles.npy"))
                if a.aux else None}
    print(json.dumps(head_rec), flush=True)
    log.write(json.dumps(head_rec) + "\n")
    log.flush()

    bs = pair_batches(ioff, a.budget) if a.pairs else batches(ioff, ooff,
                                                              a.budget)
    opt = torch.optim.AdamW(params, lr=lr, betas=(0.9, 0.98),
                            weight_decay=0.01, eps=1e-9)
    lossf = nn.CrossEntropyLoss(ignore_index=ov.pad, reduction="sum")
    bce = nn.BCEWithLogitsLoss(reduction="none")

    def lr_at(step):
        if step < a.warmup:
            return lr * step / max(1, a.warmup)
        t = (step - a.warmup) / max(1, a.steps - a.warmup)
        return lr * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * min(1.0, t))))

    ev = {} if a.smoke else {
        k: neval.load_eval(os.path.join(a.data, k), a.eval_n)
        for k in ("train_frames_eval", "qframe", "lexicon", "mode")}

    step = 0
    t0 = time.time()
    order = list(range(len(bs)))
    run = {"loss": 0.0, "aux": 0.0, "acc": 0.0, "n": 0}
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
            src, spad, tgt = make_batch(idx, ins, outs, ioff, ooff, iv.pad,
                                        ov.pad, device)
            ntok = int((tgt[:, 1:] != ov.pad).sum())
            with torch.autocast("cuda", dtype=torch.bfloat16,
                                enabled=(device == "cuda")):
                mem, mask = model.encode(src, spad)
                logits = model.decode(tgt[:, :-1], mem, mask)
                loss = lossf(logits.reshape(-1, logits.size(-1)).float(),
                             tgt[:, 1:].reshape(-1)) / max(1, ntok)
                aux = torch.zeros((), device=device)
                acc = 0.0
                if a.aux:
                    rb = torch.from_numpy(
                        roles[idx].astype(np.int64)).to(device)
                    at, is_slot = aux_targets(src, rb, iv.slot0)
                    al = head(mem).float()
                    m = (is_slot & ~spad)[..., None].float()
                    d = m.sum().clamp(min=1.0)
                    aux = (bce(al, at) * m).sum() / (2 * d)
                    acc = float((((al > 0).float() == at).float()
                                 * m).sum() / (2 * d))
                total = loss + a.aux * aux
            total.backward()
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            run["loss"] += float(loss.detach())
            run["aux"] += float(aux.detach())
            run["acc"] += acc
            run["n"] += 1
            if step % (10 if a.smoke else 200) == 0:
                n = max(1, run["n"])
                rec = {"event": "step", "step": step,
                       "loss": round(run["loss"] / n, 4),
                       "aux_loss": round(run["aux"] / n, 4),
                       "aux_acc": round(run["acc"] / n, 4),
                       "lr": round(lr_at(step), 7),
                       "gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)
                       if device == "cuda" else 0.0,
                       "sec": round(time.time() - t0, 1)}
                run = {"loss": 0.0, "aux": 0.0, "acc": 0.0, "n": 0}
                print(json.dumps(rec), flush=True)
                log.write(json.dumps(rec) + "\n")
                log.flush()
            if ev and (step % a.eval_every == 0 or step == a.steps):
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

    ck = os.path.join(a.out, f"ckpt_{a.tag}.pt")
    blob = {"size": a.size, "state": model.state_dict(), "params": pc,
            "steps": a.steps, "n_train": n_train, "seed": a.seed,
            "ladder": True, "arm": {"pairs": a.pairs, "aux": a.aux,
                                    "train_split": os.path.abspath(tsplit)}}
    if head is not None:
        blob["aux_head"] = head.state_dict()
    torch.save(blob, ck)
    done = {"event": "done", "ckpt": os.path.abspath(ck),
            "sec": round(time.time() - t0, 1), "params": pc,
            "n_batches": len(bs),
            "peak_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)
            if device == "cuda" else 0.0}
    print(json.dumps(done), flush=True)
    log.write(json.dumps(done) + "\n")
    log.close()


if __name__ == "__main__":
    main()
