"""System C: the normalizer reads, the interpreter runs.

The network is handed the item's text and nothing else. It writes a token
stream, `src/norm/ntok.py:deserialize` turns that into a structure, and
`src/norm/interp.py:run` executes it. The network never sees the question's
answer and never computes one.

Both decodings are run over the same items: greedy, and sampled at temperature
1.0 with a fixed seed. Greedy has produced false zeros on this project, so the
sampled column travels with it.

Structure level exact match is recorded beside the answer, so a cell where the
answer is right and the structure is wrong is visible rather than pooled away.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import time

import numpy as np
import torch

from src.norm import ndata, nmodel, neval
from src.norm.interp import run
from src.norm.lang import NormError, program_load
from src.norm.ntok import TokenizeError, deserialize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="results/norm/train/ckpt_l.pt")
    ap.add_argument("--items", default="results/norm/compare/items.jsonl.gz")
    ap.add_argument("--out", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    iv, ov = ndata._vocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    tag = os.path.basename(a.ckpt).replace("ckpt_", "").replace(".pt", "")
    out = a.out or f"results/norm/compare/c_{tag}.jsonl.gz"
    device = "cuda"
    model = nmodel.build(ck["size"], len(iv), len(ov)).to(device)
    model.load_state_dict(ck["state"])
    model.eval()

    items = [json.loads(l) for l in gzip.open(a.items, "rt")]
    if a.limit:
        items = items[:a.limit]

    enc, drops = [], []
    for it in items:
        try:
            ids, slots, n_unk = iv.encode(it["text"])
        except TokenizeError as exc:
            drops.append({"id": it["id"], "why": f"tokenize: {exc}"[:120]})
            enc.append(None)
            continue
        if n_unk or len(ids) > ndata.MAX_IN:
            drops.append({"id": it["id"],
                          "why": f"n_unk={n_unk} len={len(ids)}"})
            enc.append(None)
            continue
        enc.append({"ids": np.asarray(ids, dtype=np.int64), "slots": slots})

    live = [i for i, e in enumerate(enc) if e is not None]
    modes = {}
    t0 = time.time()
    for mode in ("greedy", "sampled"):
        sub = [{"ids": enc[i]["ids"]} for i in live]
        em = neval.emit(model, sub, ov, device, mode,
                        temperature=a.temperature, batch=a.batch,
                        max_len=ndata.MAX_OUT, seed=a.seed)
        modes[mode] = {live[k]: em[k] for k in range(len(live))}
        print(mode, "emitted", len(em), f"{time.time()-t0:.0f}s", flush=True)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    n_ok = 0
    with gzip.open(out, "wt") as fh:
        for i, it in enumerate(items):
            rec = {"id": it["id"], "split": it["split"], "shape": it["shape"],
                   "fid": it["fid"], "gold": it["gold"],
                   "options": it["options"]}
            gold_prog = program_load(it["prog"])
            for mode in ("greedy", "sampled"):
                if enc[i] is None:
                    rec[mode] = {"answer": "", "state": "unreadable_input",
                                 "exact": 0}
                    continue
                toks = ov.decode(modes[mode][i])
                try:
                    prog = deserialize(toks, enc[i]["slots"])
                except Exception as exc:
                    rec[mode] = {"answer": "", "state": "malformed",
                                 "exact": 0,
                                 "reason": f"{type(exc).__name__}"[:60]}
                    continue
                ex = int(prog == gold_prog)
                r = run(prog)
                if not r.ok:
                    rec[mode] = {"answer": "", "state": "refused",
                                 "exact": ex, "reason": r.reason[:120]}
                else:
                    rec[mode] = {"answer": r.text, "state": "ran", "exact": ex}
                    n_ok += 1
            fh.write(json.dumps(rec) + "\n")
    meta = {"ckpt": os.path.abspath(a.ckpt), "size": ck["size"],
            "params": ck["params"], "steps": ck["steps"],
            "n_items": len(items), "n_unreadable_input": len(drops),
            "drops": drops[:20], "temperature": a.temperature,
            "seed": a.seed, "seconds": round(time.time() - t0, 1), "out": out}
    with open(out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps({k: v for k, v in meta.items() if k != "drops"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
