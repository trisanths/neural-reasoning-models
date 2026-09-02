"""Cells for every LFM2 run, split by key position and never pooled across it.

Each cell carries its n, its accuracy, a Wilson 95 percent interval and the
chance floor of the formulation, because a fraction of a few thousand items
without both ends stated is not readable. The parser figure beside it comes
from `results/role/lfm2/items/items_summary.json`, which recorded what the
hand written parser in `src/norm/parse.py` scores on the same items.

`picked_first` is the readout that says whether a cell is positional: the rate
at which the answer is whichever of the two symbols the sentence names first.
A reader that takes role from position sits near 1.0 in one key position cell
and near 0.0 in the other, whatever its accuracy happens to be.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import math
import os
from collections import Counter, defaultdict

POS = ("key_first", "value_first")


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))


def cell(rows, field="correct"):
    rows = [r for r in rows if r.get(field) is not None]
    n = len(rows)
    k = sum(r[field] for r in rows)
    lo, hi = wilson(k, n)
    return {"n": n, "k": k, "acc": round(k / n, 4) if n else None,
            "lo": round(lo, 4), "hi": round(hi, 4)}


def group(recs, key, field="correct"):
    g = defaultdict(list)
    for r in recs:
        g[key(r)].append(r)
    return {str(k): cell(v, field) for k, v in sorted(g.items())}


FLOOR = {"role_letter_ll": 0.5, "role_word_ll": 0.5, "role_letter_gen": 0.5,
         "role_open_gen": 0.5, "role_verify_ll": 0.5, "line_emit_gen": 0.5,
         "page_qa_gen": None, "table_emit_gen": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="results/role/lfm2/runs")
    ap.add_argument("--out", default="results/role/lfm2/report.json")
    ap.add_argument("--glob", default="*.jsonl.gz")
    a = ap.parse_args()

    items = json.load(open("results/role/lfm2/items/items_summary.json"))
    rep = {"items_summary": "results/role/lfm2/items/items_summary.json",
           "runs": {}}
    for path in sorted(glob.glob(os.path.join(a.runs, a.glob))):
        tag = os.path.basename(path)[:-len(".jsonl.gz")]
        mpath = os.path.join(a.runs, tag + ".meta.json")
        meta = json.load(open(mpath)) if os.path.exists(mpath) else {}
        recs = [json.loads(l) for l in gzip.open(path, "rt")]
        form = meta.get("form", tag.split("_ll")[0])
        primary = {"page_qa_gen": "strict",
                   "table_emit_gen": "strict_nodefault"}.get(form, "correct")
        fields = [primary]
        for extra in ("correct", "correct_norm", "strict", "strict_nodefault",
                      "lenient", "well_formed", "picked_first", "said_yes",
                      "refused", "truncated"):
            if extra == primary:
                continue
            if extra in fields:
                continue
            if recs and extra in recs[0] and recs[0][extra] is not None:
                fields.append(extra)
        r = {"path": os.path.abspath(path), "n": len(recs),
             "form": form, "split": meta.get("split"),
             "direction": meta.get("direction"),
             "phrasing": meta.get("phrasing"), "decode": meta.get("decode"),
             "floor": FLOOR.get(form), "seconds": meta.get("seconds"),
             "by_key_position": {}, "by_mode": {}, "by_shape": {},
             "by_lexicon": {}}
        for kp in POS:
            sub = [x for x in recs if x["kp"] == kp]
            if not sub:
                continue
            d = {f: cell(sub, f) for f in fields}
            d["correct"] = d[primary]
            d["eight_shapes"] = cell([x for x in sub if x["eight"]], primary)
            r["by_key_position"][kp] = d
        for kp in POS:
            sub = [x for x in recs if x["kp"] == kp]
            if not sub:
                continue
            r["by_mode"][kp] = group(sub, lambda x: x["mode"], primary)
            r["by_shape"][kp] = group(sub, lambda x: x["shape"], primary)
            r["by_lexicon"][kp] = group(sub, lambda x: x["fid"].split(".")[0],
                                        primary)
            if "picked_first" in fields:
                r["by_mode_picked_first"] = r.get("by_mode_picked_first", {})
                r["by_mode_picked_first"][kp] = group(
                    sub, lambda x: x["mode"], "picked_first")
        if "matched_pairs" in (recs[0] if recs else {}):
            for kp in POS:
                sub = [x for x in recs if x["kp"] == kp]
                m = sum(x["matched_pairs"] for x in sub)
                d = sum(x["direction_correct"] for x in sub)
                lo, hi = wilson(d, m)
                r["by_key_position"][kp]["pair_direction"] = {
                    "matched_pairs": m, "direction_correct": d,
                    "acc": round(d / m, 4) if m else None,
                    "lo": round(lo, 4), "hi": round(hi, 4)}
                r["by_key_position"][kp]["lines_per_item"] = round(
                    sum(x["n_lines"] for x in sub) / max(len(sub), 1), 2)
        rep["runs"][tag] = r
        kf = r["by_key_position"].get("key_first", {}).get("correct", {})
        vf = r["by_key_position"].get("value_first", {}).get("correct", {})
        if kf and vf:
            r["gap_key_first_minus_value_first"] = round(
                kf["acc"] - vf["acc"], 4)
        print(f"{tag}")
        for kp in POS:
            d = r["by_key_position"].get(kp)
            if not d:
                continue
            c = d["correct"]
            extra = ""
            if "picked_first" in d:
                extra = f"  picked_first {d['picked_first']['acc']:.4f}"
            if "pair_direction" in d:
                pd = d["pair_direction"]
                extra += (f"  dir {pd['acc']} [{pd['lo']},{pd['hi']}] "
                          f"n_pairs={pd['matched_pairs']}")
            print(f"   {kp:12s} n={c['n']:5d} acc {c['acc']:.4f} "
                  f"[{c['lo']:.4f},{c['hi']:.4f}]{extra}")
        if "gap_key_first_minus_value_first" in r:
            print(f"   gap {r['gap_key_first_minus_value_first']:+.4f}"
                  f"   floor {r['floor']}")
    rep["parser_cells"] = {sp: v["cells"] for sp, v in
                           items["splits"].items()}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print("wrote", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
