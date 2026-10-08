"""Does the fine tuned network reproduce its own training examples?

A network that cannot emit the targets it was trained on is a broken harness,
not a slow learner, so this is the check that has to pass before any of the
ladder numbers mean anything. It decodes the pool the run trained on and
compares token stream to token stream.
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np
import torch

from src.norm import ndata, neval, nmodel, optok
from src.norm.opft import MAX_TGT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    iv, _ = ndata._vocab()
    ov = optok.OpVocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    model = nmodel.build(ck["size"], len(iv), len(ov),
                         max_tgt=MAX_TGT).to("cuda")
    model.load_state_dict(ck["state"])
    model.eval()

    z = np.load(a.pool)
    ins, outs = z["ins"].astype(np.int64), z["outs"].astype(np.int64)
    ioff, ooff = z["ioff"], z["ooff"]
    n = min(a.n, len(ioff) - 1)
    items = [{"ids": ins[ioff[i]:ioff[i + 1]]} for i in range(n)]
    em = neval.emit(model, items, ov, "cuda", "greedy", batch=32,
                    max_len=MAX_TGT - 8, seed=0)
    exact = 0
    for i in range(n):
        want = list(outs[ooff[i] + 1:ooff[i + 1] - 1])
        exact += int(list(em[i]) == want)
    out = {"ckpt": os.path.abspath(a.ckpt), "pool": os.path.abspath(a.pool),
           "n": n, "token_exact_on_training_examples": round(exact / n, 4),
           "finetune": ck.get("finetune")}
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(out, fh, indent=1)
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
