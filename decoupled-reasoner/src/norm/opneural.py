"""The network reads an episode and writes a structure; the interpreter runs it.

Two vocabularies are supported and the difference between them is the whole of
what the network was given.

    base   the shipped checkpoint and the target language it was trained with,
           which has no way to write down an operator at all. This is the no
           gradient condition: the definition page is in the network's context
           window and nothing about the network has changed.
    ext    a checkpoint from `src/norm/opft.py`, whose output vocabulary carries
           the operator tokens of `src/norm/optok.py`.

Greedy and sampled decoding are both run over the same items, because greedy
has produced false zeros on this project before. What the network emits is
turned back into a structure and executed, so a wrong answer here is a wrong
structure and not a wrong sentence.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time

import numpy as np
import torch

from src.norm import ndata, neval, nmodel, ntok, optok
from src.norm.interp import run
from src.norm.lang import program_load
from src.norm.ntok import TokenizeError
from src.norm.opft import MAX_TGT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="results/norm/train/ckpt_l.pt")
    ap.add_argument("--vocab", choices=("base", "ext"), default="base")
    ap.add_argument("--items", default="results/norm/oneshot/items.jsonl.gz")
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--modes", default="greedy,sampled")
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=0)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    iv, base_ov = ndata._vocab()
    ov = optok.OpVocab() if a.vocab == "ext" else base_ov
    de = optok.deserialize if a.vocab == "ext" else ntok.deserialize
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    device = "cuda"
    kw = {"max_tgt": MAX_TGT} if a.vocab == "ext" else {}
    model = nmodel.build(ck["size"], len(iv), len(ov), **kw).to(device)
    model.load_state_dict(ck["state"])
    model.eval()

    items = [json.loads(l) for l in gzip.open(a.items, "rt")]
    if a.only:
        want = set(a.only.split(","))
        items = [it for it in items if it["cond"] in want]
    max_len = a.max_len or (MAX_TGT - 8 if a.vocab == "ext"
                            else ndata.MAX_OUT)

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
    modes = [m for m in a.modes.split(",") if m]
    got = {}
    t0 = time.time()
    for mode in modes:
        sub = [{"ids": enc[i]["ids"]} for i in live]
        em = neval.emit(model, sub, ov, device, mode,
                        temperature=a.temperature, batch=a.batch,
                        max_len=max_len, seed=a.seed)
        got[mode] = {live[k]: em[k] for k in range(len(live))}
        print(mode, "emitted", len(em), f"{time.time() - t0:.0f}s", flush=True)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with gzip.open(a.out, "wt") as fh:
        for i, it in enumerate(items):
            rec = {"id": it["id"], "cond": it["cond"], "family": it["family"],
                   "split": it["split"], "fid": it["fid"], "gold": it["gold"],
                   "options": it["options"], "n_pages": it["n_pages"],
                   "n": it["n"], "item_key": it["item_key"]}
            gold_prog = program_load(it["prog"])
            for mode in modes:
                if enc[i] is None:
                    rec[mode] = {"answer": "", "state": "unreadable_input",
                                 "exact": 0}
                    continue
                toks = ov.decode(got[mode][i])
                try:
                    prog = de(toks, enc[i]["slots"])
                except Exception as exc:
                    rec[mode] = {"answer": "", "state": "malformed",
                                 "exact": 0,
                                 "reason": f"{type(exc).__name__}: {exc}"[:90]}
                    continue
                ex = int(prog == gold_prog)
                r = run(prog)
                if not r.ok:
                    rec[mode] = {"answer": "", "state": "refused",
                                 "exact": ex, "reason": r.reason[:120]}
                else:
                    rec[mode] = {"answer": r.text, "state": "ran", "exact": ex}
            fh.write(json.dumps(rec) + "\n")
    meta = {"ckpt": os.path.abspath(a.ckpt), "vocab": a.vocab,
            "size": ck["size"], "params": ck["params"],
            "finetune": ck.get("finetune"), "n_items": len(items),
            "n_unreadable_input": len(drops), "drops": drops[:10],
            "modes": modes, "max_len": max_len, "temperature": a.temperature,
            "seed": a.seed, "items": os.path.abspath(a.items),
            "seconds": round(time.time() - t0, 1), "out": os.path.abspath(a.out)}
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps({k: v for k, v in meta.items() if k != "drops"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
