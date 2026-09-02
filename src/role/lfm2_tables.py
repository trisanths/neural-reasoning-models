"""One compact dump of every cell the writeup quotes, from the record files.

Nothing here decodes or re-runs. It reads the per item records each run wrote
and recounts them, so a number in the document can be traced to a file on
disk. Key position is never pooled.
"""
from __future__ import annotations

import glob
import gzip
import json
import math
import os
from collections import defaultdict

RUNS = "results/role/lfm2/runs"
ITEMS = "results/role/lfm2/items"
POS = ("key_first", "value_first")


def wilson(k, n, z=1.96):
    if not n:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round(max(0.0, (c - h) / d), 4), round(min(1.0, (c + h) / d), 4))


def frac(k, n):
    lo, hi = wilson(k, n)
    return {"n": n, "k": k, "acc": round(k / n, 4) if n else None,
            "lo": lo, "hi": hi}


def words(s):
    import re
    return re.findall(r"[A-Za-z0-9_]+", s)


def arrows(raw, syms):
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


def main():
    pool = {}
    out = {"items": json.load(open(f"{ITEMS}/items_summary.json")),
           "control": json.load(open("results/role/lfm2/control.json")),
           "runs": {}}
    out["control"].pop("chat_template_sha256", None)
    for path in sorted(glob.glob(f"{RUNS}/*.jsonl.gz")):
        tag = os.path.basename(path)[:-len(".jsonl.gz")]
        mp = f"{RUNS}/{tag}.meta.json"
        if not os.path.exists(mp):
            continue
        meta = json.load(open(mp))
        sp, form = meta["split"], meta["form"]
        recs = [json.loads(l) for l in gzip.open(path, "rt")]
        r = {"form": form, "split": sp, "direction": meta.get("direction"),
             "phrasing": meta.get("phrasing"), "shots": meta.get("shots", 0),
             "decode": meta["decode"], "n": len(recs),
             "records": os.path.abspath(path), "cells": {}}
        if form in ("table_emit_gen",):
            if sp not in pool:
                pool[sp] = {json.loads(l)["iid"]: json.loads(l) for l in
                            gzip.open(f"{ITEMS}/{sp}.jsonl.gz", "rt")}
            agg = defaultdict(lambda: defaultdict(int))
            for rec in recs:
                it = pool[sp][rec["iid"]]
                ents = [(k.lower(), v.lower())
                        for k, v in it["table"]["entries"]]
                dflt = (it["table"].get("default") or "").lower()
                syms = {s for e in ents for s in e} | ({dflt} if dflt else set())
                un = {frozenset(e): e for e in ents if e[0] != e[1]}
                got = [(a, b) for a, b in arrows(rec["raw"], syms)
                       if a != dflt and b != dflt]
                for cn in (rec["kp"], f'{rec["kp"]}|{rec["mode"]}',
                           f'{rec["kp"]}|{rec["shape"]}'):
                    c = agg[cn]
                    c["items"] += 1
                    c["strict"] += int({(a, b) for a, b in got} == set(ents)
                                       and len(got) == len(ents))
                    for a, b in got:
                        if frozenset((a, b)) in un:
                            c["matched"] += 1
                            c["dirok"] += int(un[frozenset((a, b))] == (a, b))
            for cn, c in sorted(agg.items()):
                r["cells"][cn] = {
                    "items": c["items"],
                    "direction": frac(c["dirok"], c["matched"]),
                    "strict_set": frac(c["strict"], c["items"]),
                    "floor": 0.5}
        else:
            fields = {"page_qa_gen": ("strict", "lenient"),
                      "line_emit_gen": ("correct", "well_formed"),
                      }.get(form, ("correct",))
            agg = defaultdict(list)
            for rec in recs:
                for cn in (rec["kp"], f'{rec["kp"]}|{rec["mode"]}',
                           f'{rec["kp"]}|{rec["shape"]}',
                           f'{rec["kp"]}|eight' if rec["eight"] else None):
                    if cn:
                        agg[cn].append(rec)
            for cn, rs in sorted(agg.items()):
                d = {}
                for f in fields:
                    d[f] = frac(sum(x.get(f) or 0 for x in rs), len(rs))
                if form == "line_emit_gen":
                    wf = [x for x in rs if x["well_formed"]]
                    d["direction_given_well_formed"] = frac(
                        sum(x["correct"] for x in wf), len(wf))
                for f in ("picked_first", "refused", "truncated", "said_yes"):
                    if rs and rs[0].get(f) is not None:
                        vals = [x for x in rs if x.get(f) is not None]
                        d[f] = frac(sum(x[f] for x in vals), len(vals))
                d["floor"] = 0.5 if form.startswith("role") else None
                r["cells"][cn] = d
        out["runs"][tag] = r
    dest = "results/role/lfm2/tables.json"
    json.dump(out, open(dest, "w"), indent=1)
    print("wrote", os.path.abspath(dest), len(out["runs"]), "runs")


if __name__ == "__main__":
    main()
