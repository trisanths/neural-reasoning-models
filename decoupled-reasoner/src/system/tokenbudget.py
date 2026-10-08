"""What each rung's training budget actually was, in tokens and in epochs.

`ntrain.batches` caps padded source tokens per batch at `budget`, and the loss
falls on target tokens, so there are three different counts and they matter
differently. The ratio between two rungs is the same under all of them, which
is the part the reading turns on.
"""
import json
import os

import numpy as np

from src.norm import ndata
from src.norm.ntrain import batches

ROOT = os.path.expanduser("~/decoupled-reasoner")
STEPS = 30000
BUDGET = 32768
PARAMS = {"l45": 45483008, "xl93": 93579520,
          "xxl167": 167182336, "xxxl355": 355127936}

ins, outs, ioff, ooff = ndata.load_split(os.path.join(ROOT, "data/norm/train"))
bs = batches(ioff, ooff, BUDGET)
n_ex = len(ioff) - 1
src_len = (ioff[1:] - ioff[:-1]).astype(np.int64)
tgt_len = (ooff[1:] - ooff[:-1]).astype(np.int64)

rows = np.array([len(b) for b in bs], dtype=np.int64)
real_src = np.array([int(src_len[b].sum()) for b in bs], dtype=np.int64)
real_tgt = np.array([int(tgt_len[b].sum()) for b in bs], dtype=np.int64)
pad_src = np.array([int(len(b) * src_len[b].max()) for b in bs], dtype=np.int64)

per_step = {"rows": float(rows.mean()),
            "real_source_tokens": float(real_src.mean()),
            "real_target_tokens": float(real_tgt.mean()),
            "padded_source_tokens": float(pad_src.mean())}
seen = {k: v * STEPS for k, v in per_step.items()}
epochs = seen["rows"] / n_ex

print(f"training examples in the file : {n_ex:,}")
print(f"batches at budget {BUDGET}      : {len(bs):,}")
print(f"mean rows per batch           : {per_step['rows']:.1f}")
print(f"one pass over the file         : {len(bs):,} steps")
print()
print(f"over {STEPS:,} steps")
for k in ("rows", "real_source_tokens", "real_target_tokens",
          "padded_source_tokens"):
    print(f"  {k:24s} {seen[k]:,.0f}")
print(f"  epochs over the file     {epochs:.2f}")
print()
print("tokens per parameter, by which count of tokens")
hdr = "rung".ljust(10) + "params".rjust(13) + "target".rjust(10) \
    + "real source".rjust(14) + "padded source".rjust(16)
print(hdr)
out = {}
for name, p in PARAMS.items():
    t = seen["real_target_tokens"] / p
    s = seen["real_source_tokens"] / p
    q = seen["padded_source_tokens"] / p
    print(name.ljust(10) + f"{p:13,}" + f"{t:10.2f}" + f"{s:14.2f}"
          + f"{q:16.2f}")
    out[name] = {"params": p, "target_per_param": round(t, 3),
                 "real_source_per_param": round(s, 3),
                 "padded_source_per_param": round(q, 3)}
print()
print("steps needed for each rung to match l45 on target tokens per parameter")
base = seen["real_target_tokens"] / PARAMS["l45"]
for name, p in PARAMS.items():
    need = base * p / per_step["real_target_tokens"]
    out[name]["steps_to_match_l45"] = int(round(need))
    print(f"  {name:10s} {need:10,.0f} steps  "
          f"({need / STEPS:.2f}x the 30,000 run)")

dest = os.path.join(ROOT, "results/system/token_budget.json")
with open(dest, "w") as fh:
    json.dump({"steps": STEPS, "budget": BUDGET,
               "examples_in_file": int(n_ex), "batches_per_epoch": len(bs),
               "per_step": {k: round(v, 2) for k, v in per_step.items()},
               "seen_over_run": {k: int(v) for k, v in seen.items()},
               "epochs_over_file": round(epochs, 3),
               "note": ("ntrain.batches caps padded source tokens; the loss "
                        "falls on target tokens. The ratio between two rungs "
                        "is the same under every count."),
               "rungs": out}, fh, indent=1)
print("wrote", dest)
