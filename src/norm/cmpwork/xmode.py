"""What the normalizer writes when the page states the transposed rule.

Counted over every transposed item, per checkpoint, at the structure level
rather than the answer level. The categories are disjoint and exhaustive:

    exact              the emitted structure is the gold one
    malformed          the token stream is not a structure
    key_order_canonical
                       the nine values are the page's nine values in the
                       page's order, and the nine key pairs are the row major
                       order of an untransposed grid rather than the order the
                       page states. Keys right, values right, pairing wrong,
                       which is the same failure src/norm/TRAIN.md section 9
                       reads out of `compose`
    other              anything else

An untransposed companion is counted the same way, so the categories can be
read as a difference between the two versions of one page.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
from collections import Counter

import numpy as np
import torch

from src.norm import ndata, neval, nmodel
from src.norm.lang import program_load
from src.norm.ntok import TokenizeError, deserialize


def canonical_order(keys):
    """Row major over the symbols in their order of first appearance."""
    syms = []
    for a, b in keys:
        for s in (a, b):
            if s not in syms:
                syms.append(s)
    return [(a, b) for a in syms for b in syms]


def classify(got, gold):
    if got is None:
        return "malformed"
    if got == gold:
        return "exact"
    if len(got.defs) != 1 or len(gold.defs) != 1:
        return "other"
    gd, dd = gold.defs[0], got.defs[0]
    gk = [k for k, _ in gd.entries]
    dk = [k for k, _ in dd.entries]
    gv = [v for _, v in gd.entries]
    dv = [v for _, v in dd.entries]
    if gv == dv and sorted(map(tuple, gk)) == sorted(map(tuple, dk)) \
            and dk != gk and dk == canonical_order(gk):
        return "key_order_canonical"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", required=True)
    ap.add_argument("--items", default="results/norm/compare/x_items.jsonl.gz")
    ap.add_argument("--out", default="results/norm/compare/xmode.json")
    a = ap.parse_args()
    iv, ov = ndata._vocab()
    items = [json.loads(l) for l in gzip.open(a.items, "rt")]
    enc = []
    for it in items:
        try:
            ids, slots, n_unk = iv.encode(it["text"])
        except TokenizeError:
            enc.append(None)
            continue
        enc.append(None if (n_unk or len(ids) > ndata.MAX_IN) else
                   {"ids": np.asarray(ids, dtype=np.int64), "slots": slots})
    rep = {"items": os.path.abspath(a.items), "runs": {}}
    for path in a.ckpts.split(","):
        ck = torch.load(path, map_location="cpu", weights_only=False)
        model = nmodel.build(ck["size"], len(iv), len(ov)).cuda()
        model.load_state_dict(ck["state"])
        model.eval()
        live = [i for i, e in enumerate(enc) if e is not None]
        em = neval.emit(model, [{"ids": enc[i]["ids"]} for i in live], ov,
                        "cuda", "greedy", batch=48, max_len=ndata.MAX_OUT,
                        seed=0)
        c = Counter()
        for k, i in enumerate(live):
            gold = program_load(items[i]["prog"])
            try:
                got = deserialize(ov.decode(em[k]), enc[i]["slots"])
            except Exception:
                got = None
            c[(items[i]["version"], classify(got, gold))] += 1
        tag = os.path.basename(path).replace(".pt", "")
        rep["runs"][tag] = {
            "ckpt": os.path.abspath(path), "size": ck["size"],
            "finetune": ck.get("finetune"),
            "counts": {f"{v}|{k}": n for (v, k), n in sorted(c.items())}}
        print(tag, json.dumps(rep["runs"][tag]["counts"]), flush=True)
        del model
        torch.cuda.empty_cache()
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print("wrote", os.path.abspath(a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
