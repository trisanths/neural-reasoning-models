"""The examples ladder table for src/norm/TRAIN.md, one row per rung."""
import json, os, sys
rungs = [("e30000", "30,000"), ("e120000", "120,000"),
         ("e480000", "480,000"), ("s", "1,200,000")]
print("| unique examples | shapes at 1.000 on training frames, of 14 | train frames | held-out question band | held-out lexicon | held-out mode |")
print("|---|---|---|---|---|---|")
for tag, label in rungs:
    p = f"results/norm/eval/{tag}/summary.json"
    if not os.path.exists(p):
        print("| %s | pending | | | | |" % label)
        continue
    d = json.load(open(p))
    bs = d["splits"]["train_frames_eval"]["modes"]["greedy"]["by_shape"]
    ceil = sum(1 for r in bs.values() if r["exact"] == 1.0)
    cells = []
    for sp in ("train_frames_eval", "qframe", "lexicon", "mode"):
        g = d["splits"][sp]["modes"]["greedy"]["pooled_do_not_headline"]
        cells.append("%.4f" % g["exact"])
    print("| %s | %d | %s |" % (label, ceil, " | ".join(cells)))
print()
print("Every rung is the `s` size at 1.0e-3 for 30,000 steps, scored on 2,800")
print("items per split, 200 per shape. The four right hand columns are pooled")
print("across shape and are here only because the ladder is a secondary axis;")
print("the per shape rows are in each `summary.json`.")
