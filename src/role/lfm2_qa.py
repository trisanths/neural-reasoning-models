"""The lookup answers, rescored against the item's own symbol list.

The first pass called the answer whichever word of the page appeared first in
the generation, and a page is mostly English, so a reply opening `The desk
that ...` was scored on the word `the`. This pass takes the candidate set to
be the item's slot table, which is the invented words and nothing else, so the
answer is the first invented word the model names. It also states the floor
that set implies: one over the number of distinct candidates, averaged over
the items of the cell.

The generations are re-read from disk. Nothing is decoded again.
"""
from __future__ import annotations

import glob
import gzip
import json
import math
import os
import re
from collections import defaultdict

from src.norm.ndata import load_meta

RUNS = "results/role/lfm2/runs"


def wilson(k, n, z=1.96):
    if not n:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round(max(0.0, (c - h) / d), 4), round(min(1.0, (c + h) / d), 4))


def main():
    slots = {}
    out = {}
    for path in sorted(glob.glob(f"{RUNS}/page_qa_gen*.jsonl.gz")):
        tag = os.path.basename(path)[:-len(".jsonl.gz")]
        meta = json.load(open(f"{RUNS}/{tag}.meta.json"))
        sp = meta["split"]
        if meta["n"] < 1000:
            continue
        if sp not in slots:
            slots[sp] = [m["slots"] for m in load_meta(f"data/norm/{sp}")]
        items = {json.loads(l)["iid"]: json.loads(l) for l in gzip.open(
            f"results/role/lfm2/items/{sp}.jsonl.gz", "rt")}
        agg = defaultdict(lambda: defaultdict(float))
        for rec in (json.loads(l) for l in gzip.open(path, "rt")):
            it = items[rec["iid"]]
            cand = {s.lower() for s in slots[sp][int(rec["iid"].split("/")[1])]}
            gold = it["gold_answer"].lower()
            toks = [w.lower() for w in re.findall(r"[A-Za-z0-9_]+", rec["raw"])]
            first = next((w for w in toks if w in cand or w == gold), None)
            for cn in (rec["kp"], f'{rec["kp"]}|{rec["shape"]}'):
                c = agg[cn]
                c["n"] += 1
                c["first"] += int(first == gold)
                c["any"] += int(gold in toks)
                c["named"] += int(first is not None)
                c["floor"] += 1.0 / max(len(cand), 1)
        out[tag] = {"path": os.path.abspath(path), "split": sp,
                    "decode": meta["decode"], "cells": {}}
        print(tag)
        for cn, c in sorted(agg.items()):
            n = int(c["n"])
            lo, hi = wilson(int(c["first"]), n)
            lo2, hi2 = wilson(int(c["any"]), n)
            d = {"n": n, "first_symbol_exact": round(c["first"] / n, 4),
                 "lo": lo, "hi": hi,
                 "gold_named_anywhere": round(c["any"] / n, 4),
                 "lo_any": lo2, "hi_any": hi2,
                 "named_a_candidate": round(c["named"] / n, 4),
                 "floor": round(c["floor"] / n, 4)}
            out[tag]["cells"][cn] = d
            if "|" not in cn:
                print(f"   {cn:12s} n={n:5d} first {d['first_symbol_exact']:.4f}"
                      f" [{lo:.4f},{hi:.4f}]  anywhere "
                      f"{d['gold_named_anywhere']:.4f} [{lo2:.4f},{hi2:.4f}]"
                      f"  floor {d['floor']:.4f}")
        for sh in sorted({c.split("|")[1] for c in agg if "|" in c}):
            a = out[tag]["cells"].get("key_first|" + sh)
            b = out[tag]["cells"].get("value_first|" + sh)
            if a and b:
                print(f"      {sh:18s} kf {a['first_symbol_exact']:.4f} "
                      f"[{a['lo']:.4f},{a['hi']:.4f}] | vf "
                      f"{b['first_symbol_exact']:.4f} "
                      f"[{b['lo']:.4f},{b['hi']:.4f}]  floor "
                      f"{a['floor']:.4f}")
    dest = "results/role/lfm2/page_qa_rescore.json"
    json.dump(out, open(dest, "w"), indent=1)
    print("wrote", os.path.abspath(dest))


if __name__ == "__main__":
    main()
