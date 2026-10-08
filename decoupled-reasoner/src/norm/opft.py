"""How many examples of one operation the network needs to acquire it.

The run starts from the shipped normalizer checkpoint, extends its output
embedding by the eleven operator tokens and the extra temporaries of
`src/norm/optok.py`, and continues training on a mixture: half of every batch is
drawn from the original training file so what the network could already read it
has to keep reading, and half is drawn with replacement from the k examples of
the new operation available at that point on the ladder. k = 0 is the control,
the same optimiser and the same number of steps with no new operation in the
batch, which separates acquiring an operation from being trained again.

Extending the vocabulary is a gift to the network and it is worth naming as
one. The eleven new rows are appended after every token the checkpoint already
has, so every old target stream still means what it meant, and the network is
handed for free a notation it would otherwise have had to be retrained to have.
The learning rate is the size's own final cosine value from `ntrain.py`, because
this is a continuation and not a fresh run.
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

from src.norm import ndata, nmodel, optok

LR = {"xs": 1.5e-4, "s": 1.0e-4, "m": 6e-5, "l": 4e-5}

# Long enough for the deepest plan this lane asks for, which is sixteen rounds
# of a three reading operation.
MAX_TGT = 800


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
    src_t = torch.from_numpy(src).to(device)
    return src_t, (src_t == pad_in), torch.from_numpy(tgt).to(device)


def widen(ckpt_path: str, device: str):
    """The checkpoint's model with the operator tokens appended to its output.

    Old rows are copied across unchanged and new rows keep the fresh
    initialisation, so the model starts the run knowing exactly what it knew.
    """
    iv, _ = ndata._vocab()
    ov = optok.OpVocab()
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = nmodel.build(ck["size"], len(iv), len(ov),
                         max_tgt=MAX_TGT).to(device)
    state = dict(ck["state"])
    new = model.state_dict()
    for k in ("tgt_emb.weight", "head.weight"):
        if k in state:
            old = state[k]
            grown = new[k].clone()
            grown[:old.shape[0]] = old
            state[k] = grown
    for k in ("tgt_pos.weight",):
        if k in state and state[k].shape[0] != new[k].shape[0]:
            grown = new[k].clone()
            n = min(state[k].shape[0], grown.shape[0])
            grown[:n] = state[k][:n]
            state[k] = grown
    model.load_state_dict(state)
    return model, ck, ov, iv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="results/norm/train/ckpt_l.pt")
    ap.add_argument("--pool", required=True)
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--rows", type=int, default=16)
    ap.add_argument("--lr", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    torch.manual_seed(a.seed)
    random.seed(a.seed)
    np.random.seed(a.seed)
    device = "cuda"
    model, ck, ov, iv = widen(a.ckpt, device)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)

    oins, oouts, oioff, oooff = ndata.load_split("data/norm/train")
    oins = oins.astype(np.int64)
    oouts = oouts.astype(np.int64)
    n_ord = len(oioff) - 1
    gins, gouts, gioff, gooff = load_npz(a.pool)
    n_pool = len(gioff) - 1
    if a.k > n_pool:
        raise SystemExit(f"asked for {a.k} examples, pool holds {n_pool}")
    lr = a.lr or LR[ck["size"]]

    opt = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.98),
                            weight_decay=0.01, eps=1e-9)
    lossf = nn.CrossEntropyLoss(ignore_index=ov.pad)
    rng = random.Random(a.seed)
    half = a.rows // 2
    model.train()
    t0 = time.time()
    log = []
    for step in range(1, a.steps + 1):
        oidx = [rng.randrange(n_ord)
                for _ in range(a.rows - (half if a.k else 0))]
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
        if step % 300 == 0:
            log.append({"step": step, "loss": round(float(loss), 5)})
            print(json.dumps(log[-1]), flush=True)
    torch.save({"state": model.state_dict(), "size": ck["size"],
                "params": ck["params"], "steps": ck["steps"],
                "n_train": ck["n_train"], "seed": a.seed, "vocab": "ext",
                "finetune": {"k": a.k, "steps": a.steps, "lr": lr,
                             "rows": a.rows, "pool": os.path.abspath(a.pool),
                             "from": os.path.abspath(a.ckpt)}}, a.out)
    print(json.dumps({"out": a.out, "k": a.k, "size": ck["size"], "lr": lr,
                      "steps": a.steps, "pool_n": n_pool,
                      "seconds": round(time.time() - t0, 1),
                      "log": log[-2:]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
