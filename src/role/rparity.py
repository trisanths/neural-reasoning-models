"""Can the role be had from the slot number instead of from the sentence.

Copy slots are numbered by order of first appearance, so on a page whose rule
lines each name one new key and one new value the keys land on one parity of
slot index and the values on the other, and which parity it is follows the
frame's key position. If that rule fits the training draw, then both the
structure objective and the auxiliary objective can be satisfied without ever
reading the wording, and an auxiliary head is not forced to represent anything
the decoder was not already using.

Measured over the slots the structure gives exactly one role, since a compose
chain's middle level has both and no parity rule can be right or wrong about it.
The rule is fitted per key position on the trained frames and then applied
unchanged, so what it scores on a held-out sentence mode is transfer and not
fit.
"""

from __future__ import annotations

import json
import os
from collections import Counter

import numpy as np

from src.norm import ndata

SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode")
out = {}
for sp in SPLITS:
    path = os.path.join("data/norm", sp)
    meta = ndata.load_meta(path)
    roles = np.load(path + ".roles.npy")
    c = Counter()
    for i, m in enumerate(meta):
        kp = m["fid"].split(".")[2]
        for s in range(len(m["slots"])):
            b = int(roles[i, s])
            if b not in (1, 2):
                continue
            # the rule: on a key-first page the odd slots are the keys
            guess = 1 if (s % 2 == 1) == (kp == "key_first") else 2
            c[(kp, "n")] += 1
            c[(kp, "hit")] += int(guess == b)
    out[sp] = {kp: {"n_one_role_slots": c[(kp, "n")],
                    "parity_rule_accuracy": round(c[(kp, "hit")] / c[(kp, "n")],
                                                  4)}
               for kp in ("key_first", "value_first")}
    print(sp, json.dumps(out[sp]))
os.makedirs("results/role", exist_ok=True)
dest = "results/role/parity_shortcut.json"
with open(dest, "w") as fh:
    json.dump({"rule": "on a key-first page the odd slot indices are the keys, "
                       "reversed on a value-first page",
               "scope": "slots the structure gives exactly one role",
               "cells": out}, fh, indent=1)
print("wrote", os.path.abspath(dest))
