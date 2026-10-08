"""A second, more generous reading of the same generations.

The first pass takes the last word left of the arrow and the first word right
of it, which throws away a line like `ledger muthxanth -> filing muthnevi`
where the model put the noun next to the arrow. That would drop items rather
than score them, and dropping items is how a formulation ends up measuring its
own parser. This pass looks on each side for a symbol the page actually names
and reads the direction off those, so an answer counts whenever both symbols
of a stated pair are present on opposite sides of one arrow.

Nothing is re-decoded. The raw generations on disk are re-read, so the two
passes are two readings of one run and the difference between them is the
parser's alone.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import math
import os
import re
from collections import defaultdict

POS = ("key_first", "value_first")


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round(max(0.0, (c - h) / d), 4), round(min(1.0, (c + h) / d), 4))


def words(s):
    return re.findall(r"[A-Za-z0-9_]+", s)


def arrows(raw, syms):
    """(left symbol, right symbol) for every arrow line naming two symbols."""
    out = []
    for ln in raw.split("\n"):
        if "->" not in ln:
            continue
        left, _, right = ln.partition("->")
        ls = [w.lower() for w in words(left) if w.lower() in syms]
        rs = [w.lower() for w in words(right) if w.lower() in syms]
        if ls and rs:
            out.append((ls[-1], rs[0]))
    return out


def rescore_table(rec, item):
    ents = [(k.lower(), v.lower()) for k, v in item["table"]["entries"]]
    dflt = (item["table"].get("default") or "").lower()
    syms = {s for e in ents for s in e} | ({dflt} if dflt else set())
    un = {frozenset(e): e for e in ents if e[0] != e[1]}
    got = [(a, b) for a, b in arrows(rec["raw"], syms)
           if a != dflt and b != dflt]
    matched = dirok = 0
    for a, b in got:
        key = frozenset((a, b))
        if key in un:
            matched += 1
            dirok += int(un[key] == (a, b))
    strict = int({(a, b) for a, b in got} == set(ents) and len(got) == len(ents))
    return {"matched": matched, "dirok": dirok, "strict": strict,
            "n_arrows": len(got)}


def rescore_line(rec, item):
    k, v = item["pair"]["k"].lower(), item["pair"]["v"].lower()
    got = arrows(rec["raw"], {k, v})
    for a, b in got:
        if {a, b} == {k, v}:
            return {"well_formed": 1, "correct": int(a == k)}
    return {"well_formed": 0, "correct": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="results/role/lfm2/runs")
    ap.add_argument("--items", default="results/role/lfm2/items")
    ap.add_argument("--out", default="results/role/lfm2/rescore.json")
    a = ap.parse_args()
    pool = {}
    rep = {}
    for path in sorted(glob.glob(os.path.join(
            a.runs, "*emit_gen*.jsonl.gz"))):
        tag = os.path.basename(path)[:-len(".jsonl.gz")]
        meta = json.load(open(os.path.join(a.runs, tag + ".meta.json")))
        sp = meta["split"]
        if sp not in pool:
            pool[sp] = {json.loads(l)["iid"]: json.loads(l) for l in
                        gzip.open(os.path.join(a.items, f"{sp}.jsonl.gz"), "rt")}
        tab = meta["form"] == "table_emit_gen"
        agg = defaultdict(lambda: defaultdict(int))
        for rec in (json.loads(l) for l in gzip.open(path, "rt")):
            item = pool[sp][rec["iid"]]
            s = rescore_table(rec, item) if tab else rescore_line(rec, item)
            for cellname in (rec["kp"], f'{rec["kp"]}|{rec["mode"]}'):
                c = agg[cellname]
                c["n"] += 1
                for k2, v2 in s.items():
                    c[k2] += v2
        rep[tag] = {"path": os.path.abspath(path), "form": meta["form"],
                    "split": sp, "decode": meta["decode"], "cells": {}}
        print(tag)
        for cellname, c in sorted(agg.items()):
            if tab:
                acc = c["dirok"] / c["matched"] if c["matched"] else None
                lo, hi = wilson(c["dirok"], c["matched"])
                d = {"n_items": c["n"], "matched_pairs": c["matched"],
                     "direction_correct": c["dirok"],
                     "direction_acc": round(acc, 4) if acc is not None else None,
                     "lo": lo, "hi": hi, "floor": 0.5,
                     "strict_sets": c["strict"],
                     "arrows_per_item": round(c["n_arrows"] / c["n"], 2)}
            else:
                wf = c["well_formed"]
                acc = c["correct"] / wf if wf else None
                lo, hi = wilson(c["correct"], wf)
                d = {"n_items": c["n"], "well_formed": wf,
                     "well_formed_rate": round(wf / c["n"], 4),
                     "direction_correct": c["correct"],
                     "direction_acc": round(acc, 4) if acc is not None else None,
                     "lo": lo, "hi": hi, "floor": 0.5}
            rep[tag]["cells"][cellname] = d
            if "|" not in cellname:
                print(f"   {cellname:12s} {json.dumps(d)}")
        for cellname, c in sorted(agg.items()):
            if "|" in cellname:
                d = rep[tag]["cells"][cellname]
                print(f"      {cellname:34s} dir {d['direction_acc']} "
                      f"[{d['lo']},{d['hi']}] "
                      f"n={d.get('matched_pairs', d.get('well_formed'))}")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(rep, open(a.out, "w"), indent=1)
    print("wrote", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
