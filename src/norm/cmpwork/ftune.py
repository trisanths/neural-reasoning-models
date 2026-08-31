"""How many examples the normalizer needs to acquire one new page shape.

The network already reads thirteen shapes. The shared domain grid is a
fourteenth, and it is the one the transposed operand test needs. This lane
starts from the trained checkpoint, shows it k grids, and asks what k buys.

Half of every batch is drawn from the original training file, so the measurement
is acquisition rather than a trade: what the network could already read it has
to keep reading, and the regression is measured on the same item set the rest of
this comparison uses. The other half is drawn, with replacement, from the k
grids available at that point on the ladder. k = 0 is the control and is the
shipped checkpoint under the same optimiser and the same number of steps.

The learning rate is the size's own final cosine value from `ntrain.py` rather
than its peak, because this is a continuation and not a fresh run.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import time

import numpy as np
import torch
import torch.nn as nn

from src.norm import ndata, nmodel

LR = {"xs": 1.5e-4, "s": 1.0e-4, "m": 6e-5, "l": 4e-5}


def load_npz(path):
    z = np.load(path)
    return (z["ins"].astype(np.int64), z["outs"].astype(np.int64),
            z["ioff"], z["ooff"])


def batch_of(idx, ins, outs, ioff, ooff, pad_in, pad_out, device):
    si = [ins[ioff[i]:ioff[i + 1]] for i in idx]
    so = [outs[ooff[i]:ooff[i + 1]] for i in idx]
    wi, wo = max(len(a) for a in si), max(len(a) for a in so)
    src = np.full((len(idx), wi), pad_in, dtype=np.int64)
    tgt = np.full((len(idx), wo), pad_out, dtype=np.int64)
    for r, (a, b) in enumerate(zip(si, so)):
        src[r, :len(a)] = a
        tgt[r, :len(b)] = b
    src = torch.from_numpy(src).to(device)
    tgt = torch.from_numpy(tgt).to(device)
    return src, (src == pad_in), tgt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="results/norm/train/ckpt_xs.pt")
    ap.add_argument("--grids", default="data/norm/grid_train.npz")
    ap.add_argument("--k", type=int, default=64)
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--rows", type=int, default=24)
    ap.add_argument("--lr", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    torch.manual_seed(a.seed)
    random.seed(a.seed)
    np.random.seed(a.seed)
    device = "cuda"
    iv, ov = ndata._vocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    size = ck["size"]
    model = nmodel.build(size, len(iv), len(ov)).to(device)
    model.load_state_dict(ck["state"])
    out = a.out or f"results/norm/compare/ft_{size}_k{a.k}.pt"
    os.makedirs(os.path.dirname(out), exist_ok=True)

    oins, oouts, oioff, oooff = ndata.load_split("data/norm/train")
    oins = oins.astype(np.int64)
    oouts = oouts.astype(np.int64)
    n_ord = len(oioff) - 1
    gins, gouts, gioff, gooff = load_npz(a.grids)
    lr = a.lr or LR[size]

    opt = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.98),
                            weight_decay=0.01, eps=1e-9)
    lossf = nn.CrossEntropyLoss(ignore_index=ov.pad)
    rng = random.Random(a.seed)
    half = a.rows // 2
    model.train()
    t0 = time.time()
    log = []
    for step in range(1, a.steps + 1):
        oidx = [rng.randrange(n_ord) for _ in range(a.rows - (half if a.k else 0))]
        src, pad, tgt = batch_of(oidx, oins, oouts, oioff, oooff,
                                 iv.pad, ov.pad, device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits = model(src, pad, tgt[:, :-1])
            loss = lossf(logits.reshape(-1, logits.size(-1)),
                         tgt[:, 1:].reshape(-1))
        if a.k:
            gidx = [rng.randrange(a.k) for _ in range(half)]
            gsrc, gpad, gtgt = batch_of(gidx, gins, gouts, gioff, gooff,
                                        iv.pad, ov.pad, device)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                glogits = model(gsrc, gpad, gtgt[:, :-1])
                gloss = lossf(glogits.reshape(-1, glogits.size(-1)),
                              gtgt[:, 1:].reshape(-1))
            loss = 0.5 * loss + 0.5 * gloss
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % 250 == 0:
            log.append({"step": step, "loss": round(float(loss), 5)})
            print(json.dumps(log[-1]), flush=True)
    torch.save({"state": model.state_dict(), "size": size,
                "params": ck["params"], "steps": ck["steps"],
                "n_train": ck["n_train"], "seed": a.seed,
                "finetune": {"k": a.k, "steps": a.steps, "lr": lr,
                             "rows": a.rows, "from": os.path.abspath(a.ckpt),
                             "grids": os.path.abspath(a.grids)}}, out)
    print(json.dumps({"out": out, "k": a.k, "size": size, "lr": lr,
                      "steps": a.steps, "seconds": round(time.time() - t0, 1),
                      "log": log[-3:]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
