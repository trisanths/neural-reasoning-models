"""The prediction-letter distribution behind the MMLU rows `E3.md` still has.

The n=1000 row of that lane, and the n=500 eot-prefix arm beside it, were
written under `/mnt/nvme/e3eval/` on a terminated worker and were never
mirrored, so they cannot be recomputed. The rows that survive are recomputed
here rather than copied, item by item off the per-item `pred` and `gold` fields,
so the table in the document has a script behind it and an output file to read.
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter

S3 = "s3://decoupled-reasoner-009398924577"

SOURCES = (
    ("n200_no_prefix", "results/extern/bench/ours_corpus-v1-8k_mmlu.json",
     "in the checkout"),
    ("n200_eot_prefix", "results/extern/bench/ours_mmlu_eotprefix_n200.json",
     "in the checkout"),
    ("n500_no_prefix", "",
     S3 + "/runs/real-v1-8k/results/mmlu_closed_corpus-v1-8k_n500.json"),
)


def row(path):
    d = json.load(open(path))
    recs = d["records"]
    n = len(recs)
    pred = Counter(r["pred"] for r in recs)
    gold = Counter(r["gold"] for r in recs)
    acc = sum(1 for r in recs if r["pred"] == r["gold"]) / n
    return {"n": n, "acc_recounted": round(acc, 4), "acc_in_file": d["acc"],
            "reproduces": round(acc, 4) == round(d["acc"], 4),
            "predictions": [pred.get(i, 0) for i in range(4)],
            "modal_share": round(max(pred.values()) / n, 4),
            "gold_A_share": round(gold.get(0, 0) / n, 4),
            "always_A_would_score": round(gold.get(0, 0) / n, 4),
            "eot_prefix": d.get("eot_prefix"),
            "floor": d.get("floor"), "seed": d.get("seed"),
            "shots": d.get("shots"), "model": d.get("model")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n500", default="",
                    help="local copy of the n=500 record pulled from S3")
    ap.add_argument("--out", default="results/e3/letters.json")
    a = ap.parse_args()
    out = {"unverifiable": {
        "/mnt/nvme/e3eval/mmlu_ref_n1000.json":
            "instance store on a terminated worker, never mirrored to S3",
        "/mnt/nvme/e3eval/mmlu_ref-eot_n500.json":
            "instance store on a terminated worker, never mirrored to S3"},
        "rows": {}}
    for name, path, where in SOURCES:
        p = path or a.n500
        if not p or not os.path.exists(p):
            out["rows"][name] = {"missing": True, "where": where}
            continue
        r = row(p)
        r["artifact"] = where if not path else os.path.abspath(p)
        out["rows"][name] = r
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out, indent=1))
    bad = [k for k, v in out["rows"].items()
           if not v.get("missing") and not v["reproduces"]]
    if bad:
        raise SystemExit("recount disagrees with the file: " + ", ".join(bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
