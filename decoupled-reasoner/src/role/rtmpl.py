"""How close the held-out rule sentence is to the ones the network trained on.

Two accounts predict the same aggregate and different details. Under nearest
template the reader carries the binding over from whichever trained sentence
the new one most resembles, so a held-out sentence whose closest trained
neighbour is value-first should be read value-first. Under a default convention
the reader has no representation to carry and falls back on one order whatever
the sentence looks like, so one half of the axis is read and the other is not,
and which half is a property of the run.

This measures the first one. Each of the twelve `ASSOC` sentences is filled
with sentinels for the key and the value, tokenised by the network's own
`src/norm/ntok.py:text_tokens`, and compared to every sentence in the training
modes. Similarity is over the English words alone, with the two sentinels
dropped, so a match is a match of wording and not of where the blanks sit.
"""

from __future__ import annotations

import difflib
import json
import os

from src.corpus.frames_default import ASSOC, LEXICONS, MODES
from src.norm.ndata import HELD_MODE
from src.norm.ntok import text_tokens

LEX = LEXICONS["routing"]
SENT = "QQQQ"


def words(mode, kp):
    d = dict(LEX)
    d.update(k=SENT, v=SENT)
    return [t for t in text_tokens(ASSOC[(mode, kp)].format(**d))
            if t != SENT]


def order(mode, kp):
    """Where the key sits among the two blanks, as the sentence writes them."""
    d = dict(LEX)
    d.update(k="KKKK", v="VVVV")
    toks = [t for t in text_tokens(ASSOC[(mode, kp)].format(**d))
            if t in ("KKKK", "VVVV")]
    return "key first" if toks[0] == "KKKK" else "value first"


trained = [(m, kp) for m in MODES if m != HELD_MODE
           for kp in ("key_first", "value_first")]
out = {}
for kp in ("key_first", "value_first"):
    me = words(HELD_MODE, kp)
    scores = sorted(
        ((round(difflib.SequenceMatcher(None, me, words(*t)).ratio(), 4), t)
         for t in trained), reverse=True)
    best = scores[0]
    out[f"{HELD_MODE}.{kp}"] = {
        "sentence": ASSOC[(HELD_MODE, kp)],
        "surface_order": order(HELD_MODE, kp),
        "nearest_trained": f"{best[1][0]}.{best[1][1]}",
        "nearest_trained_sentence": ASSOC[best[1]],
        "similarity": best[0],
        "nearest_agrees_on_key_position": best[1][1] == kp,
        "top_five": [{"template": f"{t[0]}.{t[1]}", "similarity": s,
                      "key_position": t[1]} for s, t in scores[:5]]}
    print(f"{HELD_MODE}.{kp}")
    print(f"  {ASSOC[(HELD_MODE, kp)]}")
    for s, t in scores[:5]:
        print(f"    {s:.4f}  {t[0]}.{t[1]:12s}  {ASSOC[t]}")
os.makedirs("results/role", exist_ok=True)
dest = "results/role/template_distance.json"
with open(dest, "w") as fh:
    json.dump({"held_mode": HELD_MODE, "lexicon_used": "routing",
               "similarity": "difflib.SequenceMatcher over the English words, "
                             "both blanks removed",
               "cells": out}, fh, indent=1)
print("wrote", os.path.abspath(dest))
