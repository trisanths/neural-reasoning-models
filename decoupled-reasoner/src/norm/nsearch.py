"""The trivial program given exactly what the normalizer is given.

`src/norm/parse.py` is handed the frame id, so comparing it to the normalizer
compares a reader that is told the grammar of the sentence in front of it
against one that is not. The fair trivial program is the same parser run over
every frame whose templates it is allowed to have, which is the 490 training
frames, keeping the reading that succeeds. On a training frame that search
finds the right pattern set and is exact. On a withheld frame the pattern set
does not exist and the search refuses, which is the whole difference the
network is being asked to make up.

Both the first successful reading and the unique reading are counted, since a
search that accepts two different structures has not read anything.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter, defaultdict

from src.norm import ndata, neval
from src.norm.interp import run
from src.norm.parse import parse

SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode", "mixed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--out", default="results/norm/nsearch/summary.json")
    ap.add_argument("--n", type=int, default=280)
    ap.add_argument("--splits", default=",".join(SPLITS))
    a = ap.parse_args()

    groups = ndata.split_frames()
    train_fids = groups["train"]
    report = {"n_train_frames": len(train_fids), "n_per_split": a.n,
              "splits": {}}
    for sp in a.splits.split(","):
        items = neval.load_eval(os.path.join(a.data, sp), a.n)
        rows = defaultdict(Counter)
        t0 = time.time()
        for it in items:
            c = rows[it["shape"]]
            c["n"] += 1
            got = []
            for fid in train_fids:
                pp = parse(it["text"], fid)
                if pp.ok:
                    got.append(pp.program)
                    if len(got) > 1:
                        break
            if not got:
                c["refused"] += 1
                continue
            c["read"] += 1
            c["ambiguous"] += int(len(got) > 1)
            c["exact_first"] += int(got[0] == it["prog"])
            if len(got) == 1:
                c["exact_unique"] += int(got[0] == it["prog"])
            gr = run(it["prog"])
            pr = run(got[0])
            if gr.ok:
                c["gold_exec"] += 1
                c["answer_ok"] += int(pr.ok and pr.text == gr.text)
        out = {}
        for sh, c in sorted(rows.items()):
            n = c["n"]
            out[sh] = {"n": n,
                       "refused": round(c["refused"] / n, 4),
                       "read": round(c["read"] / n, 4),
                       "ambiguous": round(c["ambiguous"] / n, 4),
                       "exact_first": round(c["exact_first"] / n, 4),
                       "exact_unique": round(c["exact_unique"] / n, 4),
                       "answer_ok": (round(c["answer_ok"] / c["gold_exec"], 4)
                                     if c["gold_exec"] else None)}
        tot = sum(rows.values(), Counter())
        report["splits"][sp] = {
            "by_shape": out,
            "pooled_do_not_headline": {
                "n": tot["n"],
                "exact_first": round(tot["exact_first"] / tot["n"], 4),
                "refused": round(tot["refused"] / tot["n"], 4)},
            "seconds": round(time.time() - t0, 1)}
        print(sp, json.dumps(report["splits"][sp]["pooled_do_not_headline"]),
              flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(report, fh, indent=1)
    print("wrote", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
