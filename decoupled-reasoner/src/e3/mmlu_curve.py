"""MMLU against tokens seen, through the existing calibrated harness.

This runs `src.extern.bench_ours` unchanged, once per checkpoint, and then
collates the record files it wrote. Nothing here rescores: the accuracy is
recomputed from the per-item records only to attach an interval and a floor
test, and it is asserted equal to what the harness reported.

The floor is the mean of 1/n_choices over the sampled items, which the harness
already records, and it is 0.25 on MMLU.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from src.e3.interval import summarise

TOKENS_PER_STEP = 262144


def run_one(ckpt: str, tag: str, n: int, seed: int, out: Path, device: str,
            root: str) -> dict:
    if not out.exists():
        cmd = [sys.executable, "-m", "src.extern.bench_ours",
               "--ckpt", ckpt, "--tag", tag, "--task", "mmlu",
               "--n", str(n), "--seed", str(seed), "--out", str(out),
               "--device", device, "--root", root]
        print("run:", " ".join(cmd), flush=True)
        r = subprocess.run(cmd)
        if r.returncode != 0:
            raise SystemExit(f"bench_ours failed for {tag}")
    return json.load(open(out))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", action="append", required=True,
                    help="tag=path, repeatable")
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--collate", required=True)
    a = ap.parse_args()

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for spec in a.ckpt:
        tag, _, path = spec.partition("=")
        rec_path = outdir / f"mmlu_{tag}_n{a.n}_s{a.seed}.json"
        res = run_one(path, tag, a.n, a.seed, rec_path, a.device, a.root)
        recs = res["records"]
        k = sum(r["pred"] == r["gold"] for r in recs)
        assert abs(k / len(recs) - res["acc"]) < 1e-9, "recount disagrees"
        row = summarise(k, len(recs), res["floor"])
        row["tag"] = tag
        row["ckpt"] = res["ckpt"]
        row["params"] = res["params_total"]
        row["seed"] = res["seed"]
        row["shots"] = res["shots"]
        row["prompts_over_context"] = res["prompts_over_context"]
        row["record_file"] = str(rec_path)
        row["record_mtime"] = os.path.getmtime(rec_path)
        # Distribution over the four letters, which is how the bos fault was
        # first visible on the Liquid side: a model that piles onto one option
        # is not answering.
        counts = [0, 0, 0, 0]
        for r in recs:
            if r["pred"] < 4:
                counts[r["pred"]] += 1
        row["pred_letter_counts"] = counts
        step = None
        if "step" in tag:
            try:
                step = int(tag.split("step")[-1])
            except ValueError:
                step = None
        row["step"] = step
        row["tokens_seen"] = step * TOKENS_PER_STEP if step else None
        if row["tokens_seen"]:
            row["tokens_per_param"] = round(
                row["tokens_seen"] / res["params_total"], 3)
        rows.append(row)

    rows.sort(key=lambda r: (r["tokens_seen"] is None, r["tokens_seen"] or 0))
    out = {"task": "mmlu", "fmt": "completion", "shots": 5, "n": a.n,
           "seed": a.seed, "floor": 0.25,
           "reference": {"ours_corpus_v1_8k_n200": 0.2750,
                         "lfm2_350m_n200": 0.4300,
                         "lfm2_350m_published": 0.4343},
           "rows": rows}
    json.dump(out, open(a.collate, "w"), indent=1)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
