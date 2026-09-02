"""The hop curve, per family and per decode, never pooled.

`src.corpus.rescore relation` scores a family as a whole. The failure that
survived every data fix is not visible there: it is the drop from one
derivation step to two. This reads the same rollout file that rescore reads
and cuts it by the question's hop count, scoring each cell with the same
forced-choice scorer `src/frames/score.py:summarize` that rescore calls, so
the numbers come from the project's scorer rather than from a new one.

Greedy and sampled cells are kept apart because pooling them has produced a
false zero on this project before.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict

from src.e3.interval import summarise as interval
from src.frames import score as sc

# The rollout records call the derivation-step count plan_len. It is 1 to 4
# on the chaining families and 1 on the single-lookup ones, and it is the
# axis RETRAIN.md reports as depth. The other spellings are accepted so the
# scorer keeps working if the field is ever renamed.
HOP_KEYS = ("plan_len", "hops", "n_hops", "depth", "derivation_steps")


def hop_of(rec: dict):
    for k in HOP_KEYS:
        if k in rec and rec[k] is not None:
            try:
                return int(rec[k])
            except (TypeError, ValueError):
                continue
    return None


def read(path):
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rolls", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--families", default="")
    ap.add_argument("--min-cell", type=int, default=1,
                    help="drop cells smaller than this")
    a = ap.parse_args()

    want = set(f for f in a.families.split(",") if f)
    cells = defaultdict(list)
    seen_keys = set()
    for r in read(a.rolls):
        fam = r.get("episode_family") or r.get("family") or "?"
        if want and fam not in want:
            continue
        seen_keys.update(r.keys())
        h = hop_of(r)
        cells[(r.get("decode", "?"), fam, h)].append(r)


    out = {"rolls": a.rolls, "hop_field_candidates": sorted(
        k for k in seen_keys if k in HOP_KEYS), "cells": {}}
    for key in sorted(cells, key=lambda k: (k[0], k[1], -1 if k[2] is None
                                            else k[2])):
        rows = cells[key]
        if len(rows) < a.min_cell:
            continue
        # Open numeric families carry no candidate set; forced choice is not
        # defined on them, so they are reported by exact match with floor 0.
        has_cand = any(r.get("candidates") for r in rows)
        for r in rows:
            r.setdefault("candidates", [])
            r["served"] = bool(r.get("chunks")) and any(
                re.search(
                    rf"(?<![A-Za-z]){re.escape(str(r['gold']))}(?![A-Za-z])",
                    c, re.I) for c in r["chunks"])
        name = "|".join(str(x) for x in key)
        if has_cand:
            vocab = sc.nonce_vocab(rows)
            s = sc.summarize(rows, vocab)
            k_correct = round(s["acc_forced"] * s["n"])
            cell = {"decode": key[0], "family": key[1], "hops": key[2],
                    "scored": "forced_choice",
                    "acc_forced": s["acc_forced"],
                    "chance": s["chance_cand"],
                    "none_rate": s.get("none_rate"),
                    "served": s.get("served"),
                    "mean_rounds": sum(r.get("n_rounds", 0)
                                       for r in rows) / len(rows),
                    "interval": interval(k_correct, s["n"], s["chance_cand"])}
        else:
            from src.evals.naturalized import exact_match
            k_correct = sum(exact_match(r.get("answer", ""), r["gold"])
                            for r in rows)
            cell = {"decode": key[0], "family": key[1], "hops": key[2],
                    "scored": "exact_match", "chance": 0.0,
                    "acc_exact": round(k_correct / len(rows), 4),
                    "mean_rounds": sum(r.get("n_rounds", 0)
                                       for r in rows) / len(rows),
                    "interval": interval(k_correct, len(rows), 0.0)}
        out["cells"][name] = cell

    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({"n_cells": len(out["cells"]),
                      "hop_field": out["hop_field_candidates"]}))
    for name, c in out["cells"].items():
        acc = c.get("acc_forced", c.get("acc_exact"))
        print("%-42s n=%4d hops=%-4s acc=%.3f chance=%.3f ci=%s"
              % (name, c["interval"]["n"], c["hops"], acc, c["chance"],
                 c["interval"]["ci95"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
