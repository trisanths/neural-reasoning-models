"""Does the auxiliary head itself carry role across an unseen sentence mode.

The structure score says whether the arm reads the page right. This says
whether the thing the arm was asked to represent transferred at all. The head
is a linear probe over the encoder output that was trained to say, at every
copy slot, whether that invented word is used as a key and whether it is used
as a value. Running it on a held-out sentence mode asks the same question the
structure score asks, one layer earlier and without the decoder in the way.

Reported per key position, like everything else here, and restricted as well to
the slots whose truth is one role and not both, because a compose chain's
middle level is both and a probe can be right about it without reading
anything.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter

import numpy as np
import torch

from src.norm import ndata, neval
from src.role.rtrain import AuxHead
from src.system import sizes

SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode")


@torch.no_grad()
def run_split(model, head, items, roles, device, batch=64):
    iv, _ = ndata._vocab()
    c = Counter()
    order = sorted(range(len(items)), key=lambda i: len(items[i]["ids"]))
    for b0 in range(0, len(order), batch):
        idx = order[b0:b0 + batch]
        w = max(len(items[i]["ids"]) for i in idx)
        src = torch.full((len(idx), w), iv.pad, dtype=torch.long)
        pad = torch.ones((len(idx), w), dtype=torch.bool)
        for r, i in enumerate(idx):
            a = items[i]["ids"]
            src[r, :len(a)] = torch.from_numpy(a)
            pad[r, :len(a)] = False
        src, pad = src.to(device), pad.to(device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            mem, _ = model.encode(src, pad)
            logit = head(mem).float()
        pred = (logit > 0).cpu().numpy()
        s = src.cpu().numpy()
        for r, i in enumerate(idx):
            kp = items[i]["fid"].split(".")[2]
            row = roles[i]
            a = s[r]
            for pos in range(len(items[i]["ids"])):
                if a[pos] < iv.slot0:
                    continue
                truth = int(row[a[pos] - iv.slot0])
                pk, pv = bool(pred[r, pos, 0]), bool(pred[r, pos, 1])
                tk, tv = bool(truth & 1), bool(truth & 2)
                cells = [kp, f"{kp}|one_role"] if (tk != tv) else [kp]
                for cell in cells:
                    c[(cell, "n")] += 1
                    c[(cell, "key_bit")] += int(pk == tk)
                    c[(cell, "value_bit")] += int(pv == tv)
                    c[(cell, "both_bits")] += int(pk == tk and pv == tv)
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", default="results/role")
    ap.add_argument("--n", type=int, default=7000)
    a = ap.parse_args()

    device = "cuda"
    iv, ov = ndata._vocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    if "aux_head" not in ck:
        raise SystemExit(f"{a.ckpt} has no auxiliary head")
    model = sizes.build(ck["size"], len(iv), len(ov)).to(device)
    model.load_state_dict(ck["state"])
    model.eval()
    head = AuxHead(sizes.LADDER[ck["size"]]["d_model"]).to(device)
    head.load_state_dict(ck["aux_head"])
    head.eval()

    rep = {"ckpt": os.path.abspath(a.ckpt), "tag": a.tag, "splits": {}}
    for sp in SPLITS:
        items = neval.load_eval(os.path.join(a.data, sp), a.n)
        roles = np.load(os.path.join(a.data, sp) + ".roles.npy")[:len(items)]
        c = run_split(model, head, items, roles, device)
        rep["splits"][sp] = {}
        print(f"== {sp}")
        for cell in ("key_first", "value_first", "key_first|one_role",
                     "value_first|one_role"):
            n = c[(cell, "n")]
            if not n:
                continue
            row = {"n_slot_positions": n,
                   "key_bit": round(c[(cell, "key_bit")] / n, 4),
                   "value_bit": round(c[(cell, "value_bit")] / n, 4),
                   "both_bits": round(c[(cell, "both_bits")] / n, 4)}
            rep["splits"][sp][cell] = row
            print(f"   {cell:22s} n={n:7d}  key {row['key_bit']:.4f}  "
                  f"value {row['value_bit']:.4f}  both {row['both_bits']:.4f}")
    os.makedirs(a.out, exist_ok=True)
    dest = os.path.join(a.out, f"aux_{a.tag}.json")
    with open(dest, "w") as fh:
        json.dump(rep, fh, indent=1)
    print("wrote", os.path.abspath(dest))


if __name__ == "__main__":
    main()
