"""What the network's emission is, structurally, beside whether it is right.

An earlier lane found the checkpoint emitting about one distinct symbol on a
task that needs two, which is a sharper statement than an accuracy. The same
count is available here: a composition of two acquired operations needs a plan
that calls two different operators, and this module counts how many the network
actually calls, next to how many the gold plan calls.

It decodes greedily, deserializes, and writes counts. It scores nothing.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os

import numpy as np
import torch

from src.norm import ndata, neval, nmodel, ntok, optok
from src.norm.lang import program_load
from src.norm.ntok import TokenizeError
from src.norm.opft import MAX_TGT


def shape_of(p) -> dict:
    calls = [s for s in p.steps if s.op == "call"]
    names = {a for s in calls for a in s.args if isinstance(a, str)}
    return {"defs": len(p.defs),
            "ops": sum(1 for d in p.defs if d.kind == "op"),
            "tables": sum(1 for d in p.defs if d.kind == "table"),
            "steps": len(p.steps),
            "calls": len(calls),
            "distinct_called": len(names),
            "distinct_operators": p.distinct_operators()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="results/norm/train/ckpt_l.pt")
    ap.add_argument("--vocab", choices=("base", "ext"), default="base")
    ap.add_argument("--items", default="results/norm/oneshot/items.jsonl.gz")
    ap.add_argument("--only", default="compose")
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=32)
    a = ap.parse_args()

    iv, base_ov = ndata._vocab()
    ov = optok.OpVocab() if a.vocab == "ext" else base_ov
    de = optok.deserialize if a.vocab == "ext" else ntok.deserialize
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    kw = {"max_tgt": MAX_TGT} if a.vocab == "ext" else {}
    model = nmodel.build(ck["size"], len(iv), len(ov), **kw).to("cuda")
    model.load_state_dict(ck["state"])
    model.eval()

    items = [json.loads(l) for l in gzip.open(a.items, "rt")]
    want = set(a.only.split(",")) if a.only else None
    if want:
        items = [it for it in items if it["cond"] in want]
    enc = []
    for it in items:
        try:
            ids, slots, unk = iv.encode(it["text"])
        except TokenizeError:
            enc.append(None)
            continue
        enc.append(None if unk or len(ids) > ndata.MAX_IN
                   else {"ids": np.asarray(ids, dtype=np.int64),
                         "slots": slots})
    live = [i for i, e in enumerate(enc) if e is not None]
    em = neval.emit(model, [{"ids": enc[i]["ids"]} for i in live], ov, "cuda",
                    "greedy", batch=a.batch,
                    max_len=(MAX_TGT - 8 if a.vocab == "ext"
                             else ndata.MAX_OUT), seed=0)
    got = {live[k]: em[k] for k in range(len(live))}

    rows, agg = [], {"n": 0, "malformed": 0}
    keys = ("defs", "ops", "tables", "steps", "calls", "distinct_called",
            "distinct_operators")
    sums = {f"emitted_{k}": 0 for k in keys}
    sums.update({f"gold_{k}": 0 for k in keys})
    for i, it in enumerate(items):
        gold = shape_of(program_load(it["prog"]))
        rec = {"id": it["id"], "cond": it["cond"], "gold": gold}
        agg["n"] += 1
        for k in keys:
            sums[f"gold_{k}"] += gold[k]
        if enc[i] is None:
            rec["state"] = "unreadable_input"
        else:
            try:
                p = de(ov.decode(got[i]), enc[i]["slots"])
                rec["state"] = "read"
                rec["emitted"] = shape_of(p)
                for k in keys:
                    sums[f"emitted_{k}"] += rec["emitted"][k]
            except Exception as exc:
                rec["state"] = "malformed"
                rec["reason"] = f"{type(exc).__name__}: {exc}"[:90]
                agg["malformed"] += 1
        rows.append(rec)
    n_read = agg["n"] - agg["malformed"]
    out = {"ckpt": os.path.abspath(a.ckpt), "vocab": a.vocab,
           "items": os.path.abspath(a.items), "cond": a.only,
           "n": agg["n"], "n_malformed": agg["malformed"],
           "means_over_gold": {k: round(sums[f"gold_{k}"] / agg["n"], 3)
                               for k in keys},
           "means_over_emitted_that_read": {
               k: round(sums[f"emitted_{k}"] / n_read, 3) if n_read else None
               for k in keys},
           "rows": rows[:40]}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
