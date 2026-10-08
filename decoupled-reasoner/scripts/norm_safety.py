"""The safe against dangerous failure table for src/norm/TRAIN.md."""
import json, os, sys
tags = sys.argv[1:]
print("| size | split | exact | malformed | refused | wrong (executes) | dangerous : safe |")
print("|---|---|---|---|---|---|---|")
for sp in ("train_frames_eval", "qframe", "lexicon", "mode", "mixed"):
    for t in tags:
        p = f"results/norm/eval/{t}/summary.json"
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        if sp not in d["splits"]:
            continue
        g = d["splits"][sp]["modes"]["greedy"]["pooled_do_not_headline"]
        safe = g["malformed"] + g["refused"]
        ratio = "all dangerous" if safe == 0 else (
            "%.0f : 1" % (g["wrong"] / safe) if g["wrong"] / safe >= 10
            else "%.1f : 1" % (g["wrong"] / safe))
        print("| %s | `%s` | %.4f | %.4f | %.4f | %.4f | %s |"
              % (t, sp, g["exact"], g["malformed"], g["refused"], g["wrong"],
                 ratio))
