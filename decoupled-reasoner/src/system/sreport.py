"""Scoring one rung of the ladder, on the norm lane's own grader.

`src/norm/nreport.py` reconstructs its model through `nmodel.build`, which only
knows the four sizes that lane defined, so the model is built here instead.
Everything that produces a number is imported: `neval.emit` decodes,
`neval.score` counts exact, malformed, refused and wrong per shape and carries
the parser and modal baselines, and `nreport.by_axis` breaks the frame axes
out. No grading code is rewritten.

All five frame groups are scored and none is pooled into a headline. Greedy
and sampled decoding both run, because greedy has produced false zeros here.
"""

from __future__ import annotations

import argparse
import json
import os

import torch

from src.norm import ndata, neval, nmodel, nreport
from src.system import sizes

SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode", "mixed")


def load(ckpt: str, device: str):
    """A rung of the ladder, or a checkpoint the norm lane's own sizes wrote.

    The 45M rung of this ladder is `src/norm/`'s `l` and is not retrained, so
    its checkpoint carries a size name from that lane's table. Both tables are
    tried and the model class is the same either way.
    """
    ck = torch.load(ckpt, map_location="cpu", weights_only=False)
    build = sizes.build if ck["size"] in sizes.LADDER else nmodel.build
    model = build(ck["size"], *(_v())).to(device)
    model.load_state_dict(ck["state"])
    return model, ck


def _v():
    iv, ov = ndata._vocab()
    return len(iv), len(ov)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--out", default="results/system/eval")
    ap.add_argument("--n", type=int, default=7000)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--splits", default=",".join(SPLITS))
    ap.add_argument("--tag", default="")
    a = ap.parse_args()

    device = "cuda"
    iv, ov = ndata._vocab()
    model, ck = load(a.ckpt, device)
    tag = a.tag or os.path.basename(a.ckpt).replace("ckpt_", "") \
        .replace(".pt", "")
    outdir = os.path.join(a.out, tag)
    os.makedirs(outdir, exist_ok=True)

    report = {"ckpt": os.path.abspath(a.ckpt), "size": ck["size"],
              "cfg": sizes.LADDER.get(ck["size"],
                                      nmodel.SIZES.get(ck["size"])),
              "params": ck["params"],
              "steps": ck["steps"], "n_train_examples": ck["n_train"],
              "seed": ck.get("seed"), "temperature": a.temperature,
              "eval_n": a.n, "splits": {}}
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
            summ["by_axis"] = nreport.by_axis(recs)
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
