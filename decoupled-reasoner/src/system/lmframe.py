"""Does the checkpoint still read a held-out frame after it learns to write
structure.

The corpus retrain bought surface generalisation: `src/corpus/RETRAIN.md`
records held-out frames read at 0.990 to 1.000 forced choice. Teaching that
same checkpoint to emit `src/norm/lang.py` structure is a second fine tune, and
a second fine tune can take the first one away. This measures the same
checkpoint before and after on one item set.

The item set is `results/norm/compare/items.jsonl.gz`, built by
`src/norm/cmpwork/items.py` from `src/norm/ndata.py:split_frames`, so a
held-out frame here is the same held-out frame the ladder is scored on. Its
option set is `src/norm/neval.py:candidates` and the chance floor is one over
its size, per item, averaged and never assumed.

The prompt is the world header and the question, with pages served through
retrieval, which is `src/norm/cmpwork/runa.py`'s condition and the one the
harness gate covers. Grading is `src/norm/cmpwork/grade.py:forced`: exactly one
option named and it is the gold one. Nothing asks whether an answer contains
something.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from collections import Counter, defaultdict

from src.norm.cmpwork.grade import forced
from src.norm.cmpwork.runa import DOMAIN, load_items, sampled_step


def aggregate(rows) -> dict:
    """Per split and per shape, never pooled across either."""
    cells = defaultdict(Counter)
    floors = defaultdict(list)
    for r in rows:
        g = forced(r["raw"], r["options"], r["gold"])
        for key in ((r["split"], "ALL_SHAPES"), (r["split"], r["shape"])):
            c = cells[key]
            c["n"] += 1
            c["strict"] += g["strict_correct"]
            c["lenient"] += g["lenient_correct"]
            c["hedged"] += g["hedged"]
            c["none"] += g["named_none"]
            c["rounds"] += r["rounds"]
            floors[key].append(g["floor"])
    out = {}
    for key, c in sorted(cells.items()):
        n = c["n"]
        fl = sum(floors[key]) / n
        acc = c["strict"] / n
        out[f"{key[0]}|{key[1]}"] = {
            "n": n, "floor": round(fl, 4),
            "strict": round(acc, 4),
            "lenient": round(c["lenient"] / n, 4),
            "corrected": round((acc - fl) / (1 - fl), 4) if fl < 1 else None,
            "hedge": round(c["hedged"] / n, 4),
            "none": round(c["none"] / n, 4),
            "mean_rounds": round(c["rounds"] / n, 3)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--items", default="results/norm/compare/items.jsonl.gz")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--mode", default="greedy", choices=("greedy", "sampled"))
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top-k", type=int, default=50)
    ap.add_argument("--cap", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-new-tokens", type=int, default=192)
    ap.add_argument("--max-rounds", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()

    from src.evals.interactive import (generate_with_retrieval,
                                       make_checkpoint_step_fn)
    from src.train.data import render_world_preamble
    from src.train.tokenizer import load_tokenizer

    items = load_items(a.items, a.cap)
    if a.limit:
        items = items[:a.limit]
    tok = load_tokenizer(a.tokenizer)
    raw_step, _model, state = make_checkpoint_step_fn(a.ckpt, a.device)
    step = raw_step if a.mode == "greedy" else sampled_step(
        raw_step, a.temperature, a.top_k, a.seed)
    sid = tok.special_ids
    head = [sid["<|world|>"],
            *tok.encode(render_world_preamble({"domain": DOMAIN}))]

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    rolls = os.path.join(os.path.dirname(a.out),
                         f"rolls_{a.tag}_{a.mode}.jsonl.gz")
    t0 = time.time()
    rows = []
    with gzip.open(rolls, "wt") as fh:
        for k, it in enumerate(items, 1):
            chunks = [{"text": p, "reliability": 1.0} for p in it["pages"]]
            prompt = head + [sid["<|q|>"], *tok.encode(it["question"])]
            r = generate_with_retrieval(step, tok, chunks, prompt,
                                        max_rounds=a.max_rounds,
                                        max_new_tokens=a.max_new_tokens,
                                        seed=a.seed)
            row = {"id": it["id"], "split": it["split"], "shape": it["shape"],
                   "fid": it["fid"], "gold": it["gold"],
                   "options": it["options"], "raw": r["answer_text"],
                   "rounds": r["n_rounds"], "stop": r["stop_reason"]}
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
            if k % 250 == 0:
                el = time.time() - t0
                print(f"{k}/{len(items)} {el:.0f}s {el/k:.2f}s/item", flush=True)
    rep = {"ckpt": os.path.abspath(a.ckpt), "tag": a.tag, "mode": a.mode,
           "n": len(rows), "domain": DOMAIN, "seed": a.seed,
           "max_new_tokens": a.max_new_tokens, "max_rounds": a.max_rounds,
           "step": int(state.get("step", -1)),
           "rollouts": os.path.abspath(rolls),
           "seconds": round(time.time() - t0, 1),
           "cells": aggregate(rows)}
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    for k, v in rep["cells"].items():
        if k.endswith("ALL_SHAPES"):
            print(k, json.dumps(v), flush=True)
    print("wrote", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
