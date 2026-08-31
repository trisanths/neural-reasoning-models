"""The corner of the item set the RL checkpoint was actually trained in.

That checkpoint's rollouts are `skill_substitution_rule`,
`skill_exception_rule` and `skill_threshold_rule`, asked as wh questions. The
three structure shapes those families are are `lookup`, `lookup_general` and
`classify`, and the frame axis that carries the question form is `qform`. This
set holds those three shapes in `wh` frames only, so A is answering the kind of
question it was rewarded for, and B and C answer the same items.

Frame groups are kept apart as everywhere else. `wh` with the scope first is
the corpus's own held out band, so it lands entirely in `qframe` and `mixed`,
and `train` and `lexicon` and `mode` carry `wh` with the scope last.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os

from src.norm import ndata
from src.norm.cmpwork.items import build

SHAPES = ("lookup", "lookup_general", "classify")
SPLITS = ("train", "qframe", "lexicon", "mode", "mixed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=515151)
    ap.add_argument("--out", default="results/norm/compare/h_items.jsonl.gz")
    a = ap.parse_args()
    sp = ndata.split_frames()
    rows = []
    for split in SPLITS:
        fids = [f for f in sp[split] if f.split(".")[3] == "wh"]
        if not fids:
            print(f"{split:10s} no wh frames")
            continue
        for shape in SHAPES:
            got = build(split, fids, shape, a.n, a.seed)
            for r in got:
                r["id"] = "h/" + r["id"]
            rows.extend(got)
            print(f"{split:10s} {shape:16s} {len(got):4d} from {len(fids)} wh frames",
                  flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with gzip.open(a.out, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump({"n_rows": len(rows), "shapes": list(SHAPES),
                   "qform": "wh", "n_per_cell": a.n, "seed": a.seed}, fh,
                  indent=2)
    print(json.dumps({"n_rows": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
