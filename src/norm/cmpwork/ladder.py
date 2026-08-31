"""What each rung of the example ladder buys, on one pass per checkpoint.

Two item sets per checkpoint, both already built and both graded by the same
forced choice used everywhere else in this lane:

    x_items   the shared domain grid, in an original and a transposed version
              of the same page. `follows_page` is the answer the page in front
              of the reader states, `follows_alt` is what the other version
              states. This is the transposed operand test.
    items     the twelve shape comparison set, which is the regression check.
              A checkpoint that acquires the grid by forgetting `compose` has
              not acquired anything.

Never pooled: the grid numbers are split by frame group and by version, and the
regression numbers are split by frame group and shape.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
from collections import defaultdict

import numpy as np
import torch

from src.norm import ndata, neval, nmodel
from src.norm.cmpwork.grade import forced
from src.norm.interp import run
from src.norm.lang import program_load
from src.norm.ntok import TokenizeError, deserialize


def load(path):
    return [json.loads(l) for l in gzip.open(path, "rt")]


def encode(items, iv):
    enc = []
    for it in items:
        try:
            ids, slots, n_unk = iv.encode(it["text"])
        except TokenizeError:
            enc.append(None)
            continue
        enc.append(None if (n_unk or len(ids) > ndata.MAX_IN)
                   else {"ids": np.asarray(ids, dtype=np.int64), "slots": slots})
    return enc


def answers(model, items, enc, ov, device, mode, batch):
    live = [i for i, e in enumerate(enc) if e is not None]
    em = neval.emit(model, [{"ids": enc[i]["ids"]} for i in live], ov, device,
                    mode, batch=batch, max_len=ndata.MAX_OUT, seed=0)
    out = [None] * len(items)
    for k, i in enumerate(live):
        rec = {"answer": "", "state": "malformed", "exact": 0}
        try:
            prog = deserialize(ov.decode(em[k]), enc[i]["slots"])
        except Exception:
            out[i] = rec
            continue
        rec["exact"] = int(prog == program_load(items[i]["prog"]))
        r = run(prog)
        if r.ok:
            rec.update(answer=r.text, state="ran")
        else:
            rec["state"] = "refused"
        out[i] = rec
    for i, e in enumerate(enc):
        if e is None:
            out[i] = {"answer": "", "state": "unreadable_input", "exact": 0}
    return out


def grid_cells(items, recs):
    cells = defaultdict(lambda: defaultdict(int))
    for it, r in zip(items, recs):
        for key in ((it["version"], it["split"]), (it["version"], "all")):
            c = cells[key]
            g = forced(r["answer"], it["options"], it["gold"])
            b = forced(r["answer"], it["options"], it["alt"])
            c["n"] += 1
            c["page"] += g["strict_correct"]
            c["alt"] += b["strict_correct"]
            c["exact"] += r["exact"]
            c["declined"] += int(r["state"] != "ran")
            c["floor"] += g["floor"]
    return {f"{a}|{b}": {"n": c["n"],
                         "follows_page": round(c["page"] / c["n"], 4),
                         "follows_alt": round(c["alt"] / c["n"], 4),
                         "neither": round((c["n"] - c["page"] - c["alt"]) / c["n"], 4),
                         "structure_exact": round(c["exact"] / c["n"], 4),
                         "declined": round(c["declined"] / c["n"], 4),
                         "floor": round(c["floor"] / c["n"], 4),
                         "page_count": f"{c['page']} / {c['n']}"}
            for (a, b), c in cells.items()}


def main_cells(items, recs):
    cells = defaultdict(lambda: defaultdict(int))
    for it, r in zip(items, recs):
        c = cells[(it["split"], it["shape"])]
        g = forced(r["answer"], it["options"], it["gold"])
        c["n"] += 1
        c["hit"] += g["strict_correct"]
        c["exact"] += r["exact"]
        c["floor"] += g["floor"]
    return {f"{a}|{b}": {"n": c["n"], "strict": round(c["hit"] / c["n"], 4),
                         "structure_exact": round(c["exact"] / c["n"], 4),
                         "floor": round(c["floor"] / c["n"], 4)}
            for (a, b), c in cells.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", required=True, help="comma separated")
    ap.add_argument("--x", default="results/norm/compare/x_items.jsonl.gz")
    ap.add_argument("--main", default="results/norm/compare/items.jsonl.gz")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--out", default="results/norm/compare/ladder.json")
    a = ap.parse_args()

    iv, ov = ndata._vocab()
    xi, mi = load(a.x), load(a.main)
    xe, me = encode(xi, iv), encode(mi, iv)
    rep = {"x_items": os.path.abspath(a.x), "main_items": os.path.abspath(a.main),
           "runs": {}}
    for path in a.ckpts.split(","):
        ck = torch.load(path, map_location="cpu", weights_only=False)
        model = nmodel.build(ck["size"], len(iv), len(ov)).cuda()
        model.load_state_dict(ck["state"])
        model.eval()
        tag = os.path.basename(path).replace(".pt", "")
        entry = {"ckpt": os.path.abspath(path), "size": ck["size"],
                 "params": ck["params"]["total"],
                 "finetune": ck.get("finetune")}
        for mode in ("greedy", "sampled"):
            entry[f"grid_{mode}"] = grid_cells(
                xi, answers(model, xi, xe, ov, "cuda", mode, a.batch))
            entry[f"main_{mode}"] = main_cells(
                mi, answers(model, mi, me, ov, "cuda", mode, a.batch))
        rep["runs"][tag] = entry
        g = entry["grid_greedy"]
        m = entry["main_greedy"]
        worst = min(v["strict"] for v in m.values())
        print(f"{tag:22s} transposed page {g['transposed|all']['page_count']:>10s} "
              f"exact {g['transposed|all']['structure_exact']:.4f}  "
              f"original page {g['original|all']['page_count']:>10s}  "
              f"main worst cell {worst:.4f}", flush=True)
        del model
        torch.cuda.empty_cache()
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print("wrote", os.path.abspath(a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
