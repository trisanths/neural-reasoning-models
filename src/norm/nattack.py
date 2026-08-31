"""Attacks on the normalizer's exact match number.

An accuracy is a bug until it has survived something. The failure mode this
lane exists to catch is a network that has learned the canonical structure for
each shape and emits it without reading the page. Such a network scores well on
items drawn from the generator and is worthless, and it would be invisible in
`src/norm/nreport.py`.

Each attack edits the text and then asks what the edited text now says. The
oracle for that is `src/norm/parse.py`, the reference parser, which is handed
the frame id and reads the edited text from scratch. Items where the parser
refuses are counted and dropped rather than guessed at.

    value      one invented word in one rule line is replaced by a word that
               appears nowhere else. The structure the page states changes.
    delete     one line of one page is removed. Whether that changes the
               structure depends on whether the line carried any, so the
               parser decides, and the two cases are counted apart.
    truncate   the question is cut off. There is no structure to emit and the
               only right answer is a refusal.
    strip      every rule line is removed and the padding is left. Same.

`silently_original` is the number that matters: the edited text no longer says
the original structure and the network emitted it anyway.
"""

from __future__ import annotations

import argparse
import json
import os
import random
from collections import Counter

import numpy as np

import torch

from src.norm import ndata, neval, nmodel
from src.norm.ntok import TokenizeError, deserialize
from src.norm.lang import NormError
from src.norm.parse import parse

SYL = ["kresh", "lorn", "muth", "nevi", "okra", "prav", "quil", "rham",
       "stiv", "thox", "ulm", "vand", "wisk", "xanth", "ybor", "zunt"]


def _fresh(rng, text):
    for _ in range(200):
        w = rng.choice(SYL) + rng.choice(SYL) + rng.choice(SYL)
        if w not in text and w.capitalize() not in text:
            return w
    raise RuntimeError("no fresh word")


def _blocks(text):
    return text.split("\n\n")


def _rule_lines(bl):
    """(block index, line index) for the short stated lines, not the heads."""
    out = []
    for bi, b in enumerate(bl[:-1]):
        lines = b.split("\n")
        if len(lines) < 2:
            continue
        for li, ln in enumerate(lines):
            if li and 0 < len(ln.split()) <= 14:
                out.append((bi, li))
    return out


def perturb_value(rng, item, iv=None):
    """Replace one invented word in one stated line by a word used nowhere."""
    bl = _blocks(item["text"])
    cands = [(bi, li) for bi, li in _rule_lines(bl)
             if any(iv.is_nonce(t.strip(".,;:")) for t in
                    bl[bi].split("\n")[li].split())]
    if not cands:
        return None
    bi, li = rng.choice(cands)
    lines = bl[bi].split("\n")
    toks = lines[li].split()
    pos = [i for i, t in enumerate(toks) if iv.is_nonce(t.strip(".,;:"))]
    if not pos:
        return None
    p = rng.choice(pos)
    old = toks[p]
    tail = ""
    while old and not old[-1].isalpha():
        tail = old[-1] + tail
        old = old[:-1]
    new = _fresh(rng, item["text"])
    toks[p] = (new.capitalize() if old[:1].isupper() else new) + tail
    lines[li] = " ".join(toks)
    bl[bi] = "\n".join(lines)
    return "\n\n".join(bl)


def perturb_delete(rng, item, iv=None):
    """Remove one stated line from one page."""
    bl = _blocks(item["text"])
    cands = _rule_lines(bl)
    if not cands:
        return None
    bi, li = rng.choice(cands)
    lines = bl[bi].split("\n")
    del lines[li]
    bl[bi] = "\n".join(lines)
    return "\n\n".join(bl)


def perturb_truncate(rng, item, iv=None):
    bl = _blocks(item["text"])
    return "\n\n".join(bl[:-1]) if len(bl) > 1 else None


def perturb_strip(rng, item, iv=None):
    """Keep the page heads and the padding, drop every stated line."""
    bl = _blocks(item["text"])
    if len(bl) < 2:
        return None
    out = []
    for b in bl[:-1]:
        lines = b.split("\n")
        out.append("\n".join(lines[:1] + [ln for ln in lines[1:]
                                          if len(ln.split()) > 14]))
    return "\n\n".join(out + [bl[-1]])


ATTACKS = {"value": perturb_value, "delete": perturb_delete,
           "truncate": perturb_truncate, "strip": perturb_strip}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--split", default="qframe")
    ap.add_argument("--out", default="results/norm/nattack")
    ap.add_argument("--n", type=int, default=1400)
    ap.add_argument("--seed", type=int, default=5)
    a = ap.parse_args()

    device = "cuda"
    iv, ov = ndata._vocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    model = nmodel.build(ck["size"], len(iv), len(ov)).to(device)
    model.load_state_dict(ck["state"])
    items = neval.load_eval(os.path.join(a.data, a.split), a.n)
    rng = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)

    report = {"ckpt": os.path.abspath(a.ckpt), "size": ck["size"],
              "params": ck["params"], "split": a.split, "attacks": {}}
    for name, fn in ATTACKS.items():
        rows, keep = [], []
        for it in items:
            t = fn(rng, it, iv)
            if t is None:
                continue
            try:
                ids, slots, n_unk = iv.encode(t)
            except TokenizeError:
                continue
            keep.append({"ids": np.asarray(ids),
                         "slots": slots, "shape": it["shape"],
                         "fid": it["fid"], "text": t, "prog": it["prog"]})
        em = neval.emit(model, keep, ov, device, "greedy", batch=48)
        c = Counter()
        per_shape = {}
        for it, e in zip(keep, em):
            c["n"] += 1
            pp = parse(it["text"], it["fid"]) if name in ("value", "delete") \
                else None
            try:
                got = deserialize(ov.decode(e), it["slots"])
            except (NormError, Exception):
                got = None
            if name in ("truncate", "strip"):
                ok = got is None or not neval.run(got).ok
                c["refused_or_malformed" if ok else "answered_anyway"] += 1
                continue
            if pp is None or not pp.ok:
                c["oracle_refused"] += 1
                continue
            neutral = (pp.program == it["prog"])
            c["neutral_edit" if neutral else "structure_edit"] += 1
            if got is None:
                c["malformed"] += 1
                continue
            if neutral:
                c["neutral_kept_original"] += int(got == it["prog"])
            else:
                if got == it["prog"]:
                    c["silently_original"] += 1
                c["followed_edit_exactly"] += int(got == pp.program)
                c["changed"] += int(got != it["prog"])
        report["attacks"][name] = dict(c)
        print(name, json.dumps(dict(c)), flush=True)

    path = os.path.join(a.out, f"{os.path.basename(a.ckpt)}.json")
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1)
    print("wrote", os.path.abspath(path))


if __name__ == "__main__":
    main()
