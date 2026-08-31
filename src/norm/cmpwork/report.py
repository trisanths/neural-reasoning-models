"""Every cell of the three-way comparison, from the record files.

Nothing is pooled across shape or across frame split. Every cell carries its
denominator, the chance floor computed from that cell's own option counts, the
strict forced-choice score, the lenient companion, the hedge rate and the rate
at which the system names nothing. Greedy and sampled travel together for both
networks.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import statistics as st
from collections import defaultdict

from src.norm.cmpwork.grade import forced

ROOT = "results/norm/compare"


def read(path):
    if not os.path.exists(path):
        return {}
    return {json.loads(l)["id"]: json.loads(l) for l in gzip.open(path, "rt")}


def systems(stem: str) -> dict:
    """id -> {system: answer text} for every system that ran on this item set."""
    pre = "" if stem == "main" else f"{stem}_"
    out = defaultdict(dict)
    for sysname, path, get in (
        ("A_greedy", f"{ROOT}/{pre}a_greedy.jsonl.gz", lambda r: r["raw"]),
        ("A_sampled", f"{ROOT}/{pre}a_sampled.jsonl.gz", lambda r: r["raw"]),
        ("B_oracle", f"{ROOT}/{pre}b.jsonl.gz", lambda r: r["b_oracle"]["answer"]),
        ("B_train", f"{ROOT}/{pre}b.jsonl.gz", lambda r: r["b_train"]["answer"]),
        ("C_l_greedy", f"{ROOT}/{pre}c_l.jsonl.gz", lambda r: r["greedy"]["answer"]),
        ("C_l_sampled", f"{ROOT}/{pre}c_l.jsonl.gz", lambda r: r["sampled"]["answer"]),
        ("C_xs_greedy", f"{ROOT}/{pre}c_xs.jsonl.gz", lambda r: r["greedy"]["answer"]),
        ("C_xs_sampled", f"{ROOT}/{pre}c_xs.jsonl.gz", lambda r: r["sampled"]["answer"]),
    ):
        for i, r in read(path).items():
            out[i][sysname] = get(r)
    return out


def extras(stem: str) -> dict:
    """Per system side facts: structure exactness, refusals, retrieval rounds."""
    pre = "" if stem == "main" else f"{stem}_"
    out = defaultdict(dict)
    for i, r in read(f"{ROOT}/{pre}c_l.jsonl.gz").items():
        out[i]["C_l_greedy"] = {"exact": r["greedy"]["exact"],
                                "state": r["greedy"]["state"]}
        out[i]["C_l_sampled"] = {"exact": r["sampled"]["exact"],
                                 "state": r["sampled"]["state"]}
    for i, r in read(f"{ROOT}/{pre}c_xs.jsonl.gz").items():
        out[i]["C_xs_greedy"] = {"exact": r["greedy"]["exact"],
                                 "state": r["greedy"]["state"]}
        out[i]["C_xs_sampled"] = {"exact": r["sampled"]["exact"],
                                  "state": r["sampled"]["state"]}
    for i, r in read(f"{ROOT}/{pre}b.jsonl.gz").items():
        out[i]["B_oracle"] = {"state": "ran" if r["b_oracle"]["read"] else "refused"}
        out[i]["B_train"] = {"state": "ran" if r["b_train"]["read"] else "refused",
                             "self": r["b_train"].get("self", 0),
                             "match_fid": r["b_train"].get("match_fid", "")}
    for i, r in read(f"{ROOT}/{pre}a_greedy.jsonl.gz").items():
        out[i]["A_greedy"] = {"rounds": r["rounds"], "stop": r["stop"]}
    for i, r in read(f"{ROOT}/{pre}a_sampled.jsonl.gz").items():
        out[i]["A_sampled"] = {"rounds": r["rounds"], "stop": r["stop"]}
    return out


def cell(rows):
    """rows is a list of (answer, options, gold, extra)."""
    n = len(rows)
    if not n:
        return None
    strict = lenient = hedge = none = 0
    floors, exact, refused = [], [], 0
    for ans, opts, gold, ex in rows:
        g = forced(ans, opts, gold)
        strict += g["strict_correct"]
        lenient += g["lenient_correct"]
        hedge += g["hedged"]
        none += g["named_none"]
        floors.append(g["floor"])
        if ex and "exact" in ex:
            exact.append(ex["exact"])
        if ex and ex.get("state") in ("refused", "malformed", "unreadable_input"):
            refused += 1
    out = {"n": n, "strict": round(strict / n, 4),
           "lenient": round(lenient / n, 4),
           "hedge": round(hedge / n, 4), "none": round(none / n, 4),
           "floor": round(sum(floors) / n, 4),
           "declined": round(refused / n, 4)}
    if exact:
        out["structure_exact"] = round(sum(exact) / len(exact), 4)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default="main")
    ap.add_argument("--items", default=f"{ROOT}/items.jsonl.gz")
    ap.add_argument("--keys", default="split,shape")
    ap.add_argument("--out", default=f"{ROOT}/report_main.json")
    a = ap.parse_args()

    items = {}
    for l in gzip.open(a.items, "rt"):
        r = json.loads(l)
        items[r["id"]] = r
    ans = systems(a.stem)
    ext = extras(a.stem)
    keys = a.keys.split(",")

    dist = {}
    dp = f"{ROOT}/frame_distance.json"
    if os.path.exists(dp):
        dist = json.load(open(dp))["frames"]

    names = sorted({s for v in ans.values() for s in v})
    buckets = defaultdict(lambda: defaultdict(list))
    for i, it in items.items():
        k = tuple(str(it.get(x, "")) for x in keys)
        for s in names:
            if s not in ans.get(i, {}):
                continue
            buckets[k][s].append((ans[i][s], it["options"], it["gold"],
                                  ext.get(i, {}).get(s)))

    rep = {"stem": a.stem, "items": os.path.abspath(a.items),
           "keys": keys, "systems": names, "cells": {}}
    for k, per in sorted(buckets.items()):
        row = {}
        for s in names:
            c = cell(per[s])
            if c:
                row[s] = c
        ids = [i for i, it in items.items()
               if tuple(str(it.get(x, "")) for x in keys) == k]
        if dist:
            sd = [dist[items[i]["fid"]]["shape_distance"] for i in ids
                  if items[i]["fid"] in dist]
            ld = [dist[items[i]["fid"]]["lex_distance_at_nearest"] for i in ids
                  if items[i]["fid"] in dist]
            if sd:
                row["_distance"] = {"shape_median": round(st.median(sd), 4),
                                    "shape_min": round(min(sd), 4),
                                    "shape_max": round(max(sd), 4),
                                    "lex_median": round(st.median(ld), 4)}
        rep["cells"]["|".join(k)] = row
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print("wrote", os.path.abspath(a.out), len(rep["cells"]), "cells",
          "systems", names)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
