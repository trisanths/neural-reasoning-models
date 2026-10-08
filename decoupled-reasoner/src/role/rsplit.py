"""Every arm's numbers, split by key position and never pooled across it.

Pooling across key position is the error this experiment exists to expose: the
45M rung reads 0.5256 pooled on the held-out sentence mode and 0.7302 against
0.3177 underneath, and the 93M rung reads 0.5231 pooled and the two halves the
other way round. So nothing here averages the two halves. The pooled row is
carried only so that a reader can see it is uninformative.

Read off the record files `src/system/sreport.py` wrote, which hold one line
per item with its frame id, its shape and its outcome, so a cell here is a
recount of the same items and not a second decode. Greedy and sampled are both
reported. The floor and the parser ceiling come from `src/role/rfloor.py`.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import time
from collections import Counter

SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode")
CATS = ("exact", "wrong", "refused", "malformed")
SEVEN = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
         "precedence")
POS = ("key_first", "value_first")


def read(path):
    with gzip.open(path, "rt") as fh:
        for line in fh:
            yield json.loads(line)


def cells(path):
    c = Counter()
    for r in read(path):
        kp = r["fid"].split(".")[2]
        sh = r["shape"]
        groups = [kp, f"{kp}|seven"] if sh in SEVEN else [kp]
        for g in groups:
            c[(g, "n")] += 1
            for k in CATS:
                c[(g, k)] += int(r[k])
        c[(kp, sh, "n")] += 1
        c[(kp, sh, "exact")] += int(r["exact"])
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", required=True)
    ap.add_argument("--eval", default="results/system/eval")
    ap.add_argument("--out", default="results/role")
    a = ap.parse_args()

    floors = json.load(open(os.path.join(a.out, "floors.json")))["cells"]
    for tag in a.tags.split(","):
        d = os.path.join(a.eval, tag)
        rep = {"tag": tag, "eval_dir": os.path.abspath(d),
               "read_at": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
               "splits": {}}
        print("=" * 78)
        print(tag)
        for sp in SPLITS:
            rep["splits"][sp] = {}
            got = {}
            for dm in ("greedy", "sampled"):
                p = os.path.join(d, f"records_{sp}_{dm}.jsonl.gz")
                if not os.path.exists(p):
                    continue
                got[dm] = cells(p)
                rep["splits"][sp][dm] = {
                    "records": os.path.abspath(p),
                    "records_mtime": time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.gmtime(os.path.getmtime(p))),
                    "cells": {f"{x}|{y}" if isinstance(y, str) else str((x, y)):
                              v for (x, *rest), v in
                              [((k[0], *k[1:]), v) for k, v in got[dm].items()]
                              for y in [".".join(map(str, rest))]}}
            if not got:
                continue
            print(f"  {sp}")
            for kp in POS:
                fl = floors[sp][kp]
                row = [f"    {kp:12s} n={got['greedy'][(kp, 'n')]:5d}"]
                for dm in ("greedy", "sampled"):
                    if dm in got:
                        c = got[dm]
                        row.append(f"{dm} {c[(kp, 'exact')] / c[(kp, 'n')]:.4f}")
                row.append(f"floor {fl['modal_shape_floor']:.4f}")
                row.append(f"parser {fl['parser_exact']:.4f}")
                print("   ".join(row))
            g = got["greedy"]
            kf = g[("key_first", "exact")] / g[("key_first", "n")]
            vf = g[("value_first", "exact")] / g[("value_first", "n")]
            rep["splits"][sp]["gap_key_first_minus_value_first"] = round(
                kf - vf, 4)
            rep["splits"][sp]["commits_to"] = (
                "neither" if abs(kf - vf) < 0.05
                else ("key_first" if kf > vf else "value_first"))
            pooled_n = g[("key_first", "n")] + g[("value_first", "n")]
            pooled = (g[("key_first", "exact")]
                      + g[("value_first", "exact")]) / pooled_n
            rep["splits"][sp]["pooled_do_not_headline"] = round(pooled, 4)
            print(f"    gap {kf - vf:+.4f}   pooled (uninformative) "
                  f"{pooled:.4f}")
        p = os.path.join(d, "records_mode_greedy.jsonl.gz")
        if os.path.exists(p):
            c = cells(p)
            print("  held-out sentence mode, what the failures are made of")
            fail = {}
            for cell in ("value_first", "value_first|seven", "key_first",
                         "key_first|seven"):
                n = c[(cell, "n")]
                fail[cell] = {"n": n, **{k: c[(cell, k)] for k in CATS},
                              **{k + "_rate": round(c[(cell, k)] / n, 4)
                                 for k in CATS}}
                print(f"    {cell:20s} n={n:5d}  " + "  ".join(
                    f"{k} {c[(cell, k)]:4d} ({c[(cell, k)] / n:.4f})"
                    for k in CATS))
            rep["failure_decomposition_mode_greedy"] = fail
            rep["mode_greedy_by_shape"] = {
                f"{kp}|{sh}": {"n": c[(kp, sh, "n")],
                               "exact": round(c[(kp, sh, "exact")]
                                              / c[(kp, sh, "n")], 4)}
                for kp in POS for sh in sorted({k[1] for k in c
                                                if len(k) == 3})
                if c[(kp, sh, "n")]}
        os.makedirs(a.out, exist_ok=True)
        dest = os.path.join(a.out, f"split_{tag}.json")
        with open(dest, "w") as fh:
            json.dump(rep, fh, indent=1)
        print("  wrote", os.path.abspath(dest))


if __name__ == "__main__":
    main()
