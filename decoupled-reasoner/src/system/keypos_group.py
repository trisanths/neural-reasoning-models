"""Key position inside every frame group, not only the held-out one.

If the reader is exact on value-first items of the groups whose sentence mode
it trained on, then it represents that order and fails to carry it to a new
mode. If it is not, the failure is elsewhere. The two readings are different
enough that the number goes in the document.
"""
import json
import os

ROOT = os.path.expanduser("~/decoupled-reasoner")
SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode", "mixed")
out = {}
for tag in ("l45", "xl93"):
    p = os.path.join(ROOT, f"results/system/eval/{tag}/summary.json")
    if not os.path.exists(p):
        continue
    s = json.load(open(p))
    print("===", tag)
    out[tag] = {}
    for sp in SPLITS:
        ax = s["splits"][sp]["modes"]["greedy"]["by_axis"].get("key_pos", {})
        kf = ax.get("key_first", {})
        vf = ax.get("value_first", {})
        if not kf or not vf:
            continue
        print("  %-18s key_first %.4f (n=%d)   value_first %.4f (n=%d)"
              % (sp, kf["exact"], kf["n"], vf["exact"], vf["n"]))
        out[tag][sp] = {"key_first": kf, "value_first": vf}
dest = os.path.join(ROOT, "results/system/keypos_by_group.json")
with open(dest, "w") as fh:
    json.dump({"source": "results/system/eval/*/summary.json by_axis key_pos",
               "cells": out}, fh, indent=1)
print("wrote", dest)
