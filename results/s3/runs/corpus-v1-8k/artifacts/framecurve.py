"""Accuracy against frame distance, per family, for both checkpoints.

Cells are (frame, family). A cell is seen when the corpus trained that frame
and held out otherwise; a held-out cell's distance is the smallest distance to
any of the 72 frames the corpus trained on. Shape and lexicon are reported
apart. Nothing is pooled across families, and the macro over frames inside a
family is given in both aggregation orders.
"""
import json, os, sys, collections
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")
from src.frames.generate import FRAMES, split_frames
from src.frames.distance import signature, shape_distance, lex_distance
from src.frames import score as sc

R = "/home/ec2-user/retrain/frames"
sp = split_frames("both")
TRAIN = set(sp["train"])

SETS = {
    "sweep20": ("/home/ec2-user/sweep/eval/gen", "score_%s-%s.json"),
    "ext12": (R + "/gen_ext", "scoreext_%s-%s.json"),
}
BINS = [(0.0, 0.0001, "seen"), (0.0001, 0.05, "0.00-0.05"),
        (0.05, 0.12, "0.05-0.12"), (0.12, 0.22, "0.12-0.22"),
        (0.22, 0.30, "0.22-0.30"), (0.30, 1.01, "0.30+")]


def bucket(seen, shape):
    if seen:
        return "seen"
    for lo, hi, name in BINS[1:]:
        if lo <= shape < hi:
            return name
    return "0.30+"


sig_cache = {}
def dist(frame, fam):
    key = (frame, fam)
    if key in sig_cache:
        return sig_cache[key]
    if frame in TRAIN:
        sig_cache[key] = (True, 0.0, 0.0, frame)
        return sig_cache[key]
    s = signature(FRAMES[frame], fam)
    best = None
    for tr in TRAIN:
        t = signature(FRAMES[tr], fam)
        sd = shape_distance(s["skeleton"], t["skeleton"])
        ld = lex_distance(set(s["words"]), set(t["words"]))
        if best is None or (sd, ld) < best[:2]:
            best = (sd, ld, tr)
    sig_cache[key] = (False, best[0], best[1], best[2])
    return sig_cache[key]


rows = []
for setname, (_, tmpl) in SETS.items():
    for who in ("base", "new"):
        for dec in ("greedy", "t07"):
            path = os.path.join(R, tmpl % (who, dec))
            if not os.path.exists(path):
                continue
            recs = json.load(open(path))["records"]
            for key, s in recs.items():
                frame, family, condition = key.split("|")
                seen, sd, ld, near = dist(frame, family)
                rows.append({"set": setname, "who": who, "decode": dec,
                             "frame": frame, "family": family,
                             "seen": seen, "shape": round(sd, 4),
                             "lex": round(ld, 4), "nearest": near,
                             "bucket": bucket(seen, sd), **s})

out = {"cells": rows, "buckets": {}}
print("%-6s %-6s %-18s %-11s %6s %6s %7s %7s %7s %6s %6s %7s"
      % ("who", "dec", "family", "bucket", "frames", "n", "forced",
         "first", "chance", "hedge", "none", "served"))
for who in ("base", "new"):
    for dec in ("greedy", "t07"):
        for fam in sorted({r["family"] for r in rows}):
            for _, _, bname in BINS:
                sel = [r for r in rows if r["who"] == who and r["decode"] == dec
                       and r["family"] == fam and r["bucket"] == bname]
                if not sel:
                    continue
                n = sum(r["n"] for r in sel)
                agg = {k: sum(r[k] * r["n"] for r in sel) / n
                       for k in ("acc_forced", "acc_first", "chance_cand",
                                 "hedge_rate", "none_rate", "served_rate")}
                macro = sc.macro_both_orders([(r["acc_forced"], r["chance_cand"])
                                              for r in sel])
                out["buckets"][f"{who}|{dec}|{fam}|{bname}"] = {
                    "frames": len(sel), "n": n,
                    "frame_names": sorted(r["frame"] for r in sel),
                    "shape_range": [min(r["shape"] for r in sel),
                                    max(r["shape"] for r in sel)],
                    "lex_range": [min(r["lex"] for r in sel),
                                  max(r["lex"] for r in sel)],
                    **{k: round(v, 4) for k, v in agg.items()},
                    "macro_both_orders": macro}
                print("%-6s %-6s %-18s %-11s %6d %6d %7.3f %7.3f %7.3f %6.3f %6.3f %7.3f"
                      % (who, dec, fam, bname, len(sel), n, agg["acc_forced"],
                         agg["acc_first"], agg["chance_cand"], agg["hedge_rate"],
                         agg["none_rate"], agg["served_rate"]))
path = os.path.join(R, "curve.json")
json.dump(out, open(path, "w"), indent=1)
print("wrote", path)
