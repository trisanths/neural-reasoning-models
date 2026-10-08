"""The report on one trained normalizer.

Every split is scored per shape and never pooled into a headline. Greedy and
sampled decoding are both reported, because greedy has produced false zeros on
this project before. The three baselines of `src/norm/neval.py` travel with
every row, and the frame axes are broken out separately so a frame effect
cannot hide inside an average.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict

import torch

from src.norm import ndata, neval, nmodel

SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode", "mixed")
AXES = ("lexicon", "mode", "key_pos", "qform", "scope_pos")


def by_axis(records) -> dict:
    """Exact match per frame axis value, from the fid, per shape kept apart."""
    out = {}
    for k, ax in enumerate(AXES):
        c = defaultdict(Counter)
        for r in records:
            v = r["fid"].split(".")[k]
            c[v]["n"] += 1
            c[v]["exact"] += int(r["exact"])
        out[ax] = {v: {"n": d["n"], "exact": round(d["exact"] / d["n"], 4)}
                   for v, d in sorted(c.items())}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--out", default="results/norm/eval")
    ap.add_argument("--n", type=int, default=7000)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--splits", default=",".join(SPLITS))
    a = ap.parse_args()

    device = "cuda"
    iv, ov = ndata._vocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    model = nmodel.build(ck["size"], len(iv), len(ov)).to(device)
    model.load_state_dict(ck["state"])
    tag = os.path.basename(a.ckpt).replace("ckpt_", "").replace(".pt", "")
    outdir = os.path.join(a.out, tag)
    os.makedirs(outdir, exist_ok=True)

    report = {"ckpt": os.path.abspath(a.ckpt), "size": ck["size"],
              "params": ck["params"], "steps": ck["steps"],
              "n_train_examples": ck["n_train"], "seed": ck.get("seed"),
              "temperature": a.temperature, "splits": {}}
    for sp in a.splits.split(","):
        items = neval.load_eval(os.path.join(a.data, sp), a.n)
        report["splits"][sp] = {"n": len(items), "modes": {}}
        for mode in ("greedy", "sampled"):
            em = neval.emit(model, items, ov, device, mode,
                            temperature=a.temperature, batch=a.batch)
            summ, recs = neval.score(items, em, ov, f"{tag}/{sp}/{mode}",
                                     want_parser=(mode == "greedy"))
            rp = os.path.join(outdir, f"records_{sp}_{mode}.jsonl.gz")
            neval.write_records(rp, recs)
            summ["records"] = os.path.abspath(rp)
            summ["by_axis"] = by_axis(recs)
            report["splits"][sp]["modes"][mode] = summ
            print(json.dumps({"split": sp, "mode": mode,
                              "pooled": summ["pooled_do_not_headline"]}),
                  flush=True)
    path = os.path.join(outdir, "summary.json")
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1)
    print("wrote", os.path.abspath(path))


if __name__ == "__main__":
    main()
