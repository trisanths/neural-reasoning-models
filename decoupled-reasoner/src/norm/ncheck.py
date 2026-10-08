"""The gate on the scoring seam.

Exact match compares two things that arrive by different routes. The target the
network is trained to emit is `serialize(program, slots)`, stored as token ids.
The gold it is scored against is `program_load(program_json(program))`, stored
as JSON in the split's metadata sidecar. If those two routes disagree anywhere,
every exact match number is bounded below one by a bug rather than by the
network, and eight shapes sitting at 1.000 would be the only reason anyone
noticed.

Three identities are checked on every item of every evaluation split:

    deserialize(gold ids) == program_load(gold json)
    serialize(program_load(gold json), slots) == gold tokens
    run(gold) succeeds

The first is the one that matters. The second catches a serialiser that is
right in one direction only, and the third is the assumption
`src/norm/neval.py` makes when it divides `answer_ok` by `n_gold_executes`.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter

from src.norm.interp import run
from src.norm.lang import program_load
from src.norm.ndata import load_meta, load_split
from src.norm.ntok import OutVocab, deserialize, serialize

SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode", "mixed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--out", default="results/norm/ncheck.json")
    ap.add_argument("--splits", default=",".join(SPLITS))
    ap.add_argument("--n", type=int, default=0)
    a = ap.parse_args()

    ov = OutVocab()
    report = {"splits": {}, "bad": 0}
    for sp in a.splits.split(","):
        path = os.path.join(a.data, sp)
        ins, outs, ioff, ooff = load_split(path)
        meta = load_meta(path)
        n = len(meta) if not a.n else min(a.n, len(meta))
        c = Counter()
        first = []
        for i in range(n):
            m = meta[i]
            gold_ids = outs[ooff[i]:ooff[i + 1]].tolist()[1:-1]
            toks = ov.decode(gold_ids)
            prog = program_load(m["prog"])
            c["n"] += 1
            try:
                back = deserialize(toks, m["slots"])
            except Exception as exc:
                c["deserialize_raised"] += 1
                if len(first) < 3:
                    first.append({"i": i, "why": f"{type(exc).__name__}: {exc}"[:200]})
                continue
            if back != prog:
                c["deserialize_mismatch"] += 1
                if len(first) < 3:
                    first.append({"i": i, "why": "deserialize != program_load",
                                  "fid": m["fid"], "shape": m["shape"]})
            try:
                again = serialize(prog, m["slots"])
            except Exception as exc:
                c["serialize_raised"] += 1
                if len(first) < 3:
                    first.append({"i": i, "why": f"{type(exc).__name__}: {exc}"[:200]})
                continue
            if again != toks:
                c["serialize_mismatch"] += 1
                if len(first) < 3:
                    first.append({"i": i, "why": "serialize != stored tokens",
                                  "fid": m["fid"], "shape": m["shape"]})
            if not run(prog).ok:
                c["gold_refused"] += 1
        bad = sum(v for k, v in c.items() if k != "n")
        report["bad"] += bad
        report["splits"][sp] = {"counts": dict(c), "bad": bad,
                                "examples": first}
        print(sp, json.dumps(dict(c)), "bad", bad, flush=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(report, fh, indent=1)
    print("wrote", os.path.abspath(a.out), "total bad", report["bad"])
    raise SystemExit(1 if report["bad"] else 0)


if __name__ == "__main__":
    main()
