"""Pick held-out frames spanning the shape-distance range, for a second cell."""
import json, sys, collections
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")
from src.frames.generate import FRAMES, split_frames
from src.frames.distance import signature, shape_distance, lex_distance

sp = split_frames("both")
TRAIN = set(sp["train"])
HELD = sorted(set(sp["test"]) | set(sp["bridge"]))
already = set(json.load(open("/home/ec2-user/retrain/frames/frame_distance.json"))["eval_frames"])
fam = "substitution_rule"
sig = {n: signature(FRAMES[n], fam) for n in set(HELD) | TRAIN}
rows = []
for ev in HELD:
    best = None
    for tr in TRAIN:
        sd = shape_distance(sig[ev]["skeleton"], sig[tr]["skeleton"])
        ld = lex_distance(set(sig[ev]["words"]), set(sig[tr]["words"]))
        if best is None or (sd, ld) < best[0]:
            best = ((sd, ld), tr)
    rows.append({"frame": ev, "shape": round(best[0][0], 4),
                 "lex": round(best[0][1], 4), "nearest": best[1],
                 "split": "test" if ev in set(sp["test"]) else "bridge",
                 "in_eval": ev in already})
rows.sort(key=lambda r: r["shape"])
bins = [(0.0, 0.05), (0.05, 0.12), (0.12, 0.20), (0.20, 0.28), (0.28, 0.40), (0.40, 1.01)]
pick = []
for lo, hi in bins:
    cand = [r for r in rows if lo <= r["shape"] < hi and not r["in_eval"]]
    step = max(1, len(cand) // 3)
    pick.extend(cand[::step][:3])
print("held out frames:", len(rows), "already evaluated:", sum(r["in_eval"] for r in rows))
print("shape distance spread:", rows[0]["shape"], "to", rows[-1]["shape"])
print("bins:", {f"{lo}-{hi}": sum(lo <= r["shape"] < hi for r in rows) for lo, hi in bins})
print("picked", len(pick))
for r in pick:
    print("  %-26s %-7s shape %.3f lex %.3f  near %s"
          % (r["frame"], r["split"], r["shape"], r["lex"], r["nearest"]))
json.dump({"picked": [r["frame"] for r in pick], "rows": rows},
          open("/home/ec2-user/retrain/frames/pick.json", "w"), indent=1)
print(",".join(r["frame"] for r in pick))
