"""The transposed operand test, scored the way the original was.

Each item is one page and one question. `gold` is what the page in front of the
reader says. `alt` is what the other version of that same page says, which on a
transposed page is the reading the page had before the edit. A reader that
reads the page answers `gold`. A reader that answers from something other than
the page in front of it answers `alt`.

The published result this replies to is 0 of 678 toward the page and 678 of 678
toward the training identity, from `src/audit/VERDICT.md` check 8.

Scoring is the same forced choice the rest of this lane uses, over the nine
cells of the grid, so the floor is 1/9 and a system that names two cells is
counted as naming neither.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
from collections import defaultdict

from src.norm.cmpwork.grade import forced
from src.norm.cmpwork.report import extras, systems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="results/norm/compare/x_items.jsonl.gz")
    ap.add_argument("--stem", default="x")
    ap.add_argument("--out", default="results/norm/compare/report_transpose.json")
    a = ap.parse_args()

    items = {}
    for l in gzip.open(a.items, "rt"):
        r = json.loads(l)
        items[r["id"]] = r
    ans = systems(a.stem)
    ext = extras(a.stem)
    names = sorted({s for v in ans.values() for s in v})

    cells = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for i, it in items.items():
        for s in names:
            if s not in ans.get(i, {}):
                continue
            g = forced(ans[i][s], it["options"], it["gold"])
            b = forced(ans[i][s], it["options"], it["alt"])
            for k in ("split", "all"):
                key = (it["version"], it["split"] if k == "split" else "all")
                c = cells[key][s]
                c["n"] += 1
                c["page"] += g["strict_correct"]
                c["alt"] += b["strict_correct"]
                c["hedge"] += g["hedged"]
                c["none"] += g["named_none"]
                c["floor_sum"] += g["floor"]
                e = ext.get(i, {}).get(s) or {}
                if e.get("state") in ("refused", "malformed", "unreadable_input"):
                    c["declined"] += 1
                if "exact" in e:
                    c["exact"] += e["exact"]
                    c["exact_n"] += 1

    rep = {"items": os.path.abspath(a.items), "systems": names, "cells": {}}
    for (ver, split), per in sorted(cells.items()):
        row = {}
        for s, c in per.items():
            n = c["n"]
            r = {"n": n, "follows_page": round(c["page"] / n, 4),
                 "follows_alt": round(c["alt"] / n, 4),
                 "neither": round((n - c["page"] - c["alt"]) / n, 4),
                 "hedge": round(c["hedge"] / n, 4),
                 "none": round(c["none"] / n, 4),
                 "floor": round(c["floor_sum"] / n, 4),
                 "declined": round(c.get("declined", 0) / n, 4),
                 "page_count": f"{c['page']} / {n}",
                 "alt_count": f"{c['alt']} / {n}"}
            if c.get("exact_n"):
                r["structure_exact"] = round(c["exact"] / c["exact_n"], 4)
            row[s] = r
        rep["cells"][f"{ver}|{split}"] = row
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    hdr = f"{'cell':22s} {'system':14s} {'n':>5s} {'page':>7s} {'alt':>7s} {'neither':>8s} {'none':>7s}"
    print(hdr)
    for k, row in rep["cells"].items():
        for s, r in sorted(row.items()):
            print(f"{k:22s} {s:14s} {r['n']:5d} {r['follows_page']:7.4f} "
                  f"{r['follows_alt']:7.4f} {r['neither']:8.4f} {r['none']:7.4f}")
    print("wrote", os.path.abspath(a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
