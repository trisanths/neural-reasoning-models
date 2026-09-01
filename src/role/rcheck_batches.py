"""Do the paired batches hold together, and do they cost what the baseline costs.

Two questions. Whether every pair really lands in one optimiser step, which is
the whole mechanism of arm B, and whether the pair-aware bucketing changes the
size of a step. If arm B took fewer rows or fewer target tokens per step than
arm A, the arms would differ in budget as well as in draw and neither number
would mean anything.
"""
import json
import sys

import numpy as np

from src.norm import ndata
from src.norm.ntrain import batches
from src.role.rtrain import pair_batches

BUDGET = 32768
out = {}
for name, path, paired in (("baseline", "data/norm/train", False),
                           ("paired", "data/role/paired_train", True)):
    ins, outs, ioff, ooff = ndata.load_split(path)
    bs = pair_batches(ioff, BUDGET) if paired else batches(ioff, ooff, BUDGET)
    sl = (ioff[1:] - ioff[:-1]).astype(np.int64)
    tl = (ooff[1:] - ooff[:-1]).astype(np.int64)
    rows = np.array([len(b) for b in bs])
    tgt = np.array([int(tl[b].sum()) for b in bs])
    src = np.array([int(sl[b].sum()) for b in bs])
    pad = np.array([int(len(b) * sl[b].max()) for b in bs])
    bad = 0
    if paired:
        for b in bs:
            a = np.asarray(b)
            if len(a) % 2 or not np.all(a[0::2] % 2 == 0) \
                    or not np.all(a[1::2] == a[0::2] + 1):
                bad += 1
    out[name] = {"n_items": len(sl), "n_batches": len(bs),
                 "rows_per_batch_mean": round(float(rows.mean()), 2),
                 "rows_per_batch_max": int(rows.max()),
                 "target_tokens_per_batch_mean": round(float(tgt.mean()), 1),
                 "real_source_tokens_per_batch_mean": round(float(src.mean()), 1),
                 "padded_source_tokens_per_batch_mean": round(float(pad.mean()), 1),
                 "padded_over_budget": int((pad > BUDGET).sum()),
                 "batches_with_a_split_pair": bad}
print(json.dumps(out, indent=1))
with open("results/role/batches.json", "w") as fh:
    json.dump({"budget": BUDGET, "cells": out}, fh, indent=1)
