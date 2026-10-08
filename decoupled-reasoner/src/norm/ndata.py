"""Training pairs for the normalizer, and the frame split they respect.

A pair is one rendered page set with its question on the input side and the
typed structure that wrote it on the target side. The structure comes first and
the text is derived from it, so the target is exact by construction and no
labelling step stands between them. That is the whole reason the perception
task is trainable: unlimited data, exact targets, and a supervision signal that
is a translation rather than a reward.

The frame split. Three disjoint kinds of frame are withheld from training:

  question frame   the corpus's own held-out band, every eighth frame of
                   `src/corpus/frames_default.py`, which is exactly the
                   frames whose question form is `wh` and whose scope sits
                   first. Both axis values appear in training, never together.
  lexicon          every frame of the `signal` lexicon. Its English nouns are
                   in the tokenizer's word list but the network never reads a
                   sentence written with them.
  statement mode   every frame in `relative_clause`. The network never reads
                   a rule stated in that sentence shape.

That leaves 490 training frames of 768. Structures are drawn fresh for every
example from `src/norm/gen.py`, so an evaluation item is new on its structure
as well as on its frame.
"""

from __future__ import annotations

import argparse
import gzip
import json
import multiprocessing as mp
import os
import random
import time

import numpy as np

from src.norm import gen
from src.norm.lang import program_json
from src.norm.ntok import (InputVocab, MAX_SLOTS, OutVocab, TokenizeError,
                           english_from_frames, serialize)
from src.norm.render import SHAPES, render, frames

HELD_LEXICON = os.environ.get("NORM_HELD_LEXICON", "signal")
HELD_MODE = os.environ.get("NORM_HELD_MODE", "relative_clause")
HELD_QFORM = os.environ.get("NORM_HELD_QFORM", "")
BAND_STRIDE = 8

MAX_IN = 1280
MAX_OUT = 320


def split_frames():
    """(train, and the four withheld groups) as lists of frame ids."""
    fr, _ = frames()
    groups = {"train": [], "qframe": [], "lexicon": [], "mode": [], "mixed": []}
    for i, f in enumerate(fr):
        band = ((f.fid.split(".")[3] == HELD_QFORM) if HELD_QFORM
                else (i % BAND_STRIDE == 0))
        lex = (f.lexicon == HELD_LEXICON)
        mod = (f.mode == HELD_MODE)
        n_new = int(band) + int(lex) + int(mod)
        if n_new == 0:
            groups["train"].append(f.fid)
        elif n_new > 1:
            groups["mixed"].append(f.fid)
        elif band:
            groups["qframe"].append(f.fid)
        elif lex:
            groups["lexicon"].append(f.fid)
        else:
            groups["mode"].append(f.fid)
    return groups


_VOCAB = None
_OUT = None


def _vocab():
    global _VOCAB, _OUT
    if _VOCAB is None:
        fr, _ = frames()
        _VOCAB = InputVocab(english_from_frames(fr))
        _OUT = OutVocab()
    return _VOCAB, _OUT


def build_example(fid: str, shape: str, seed: int, preamble: int):
    """One (text ids, target ids, slots, program) pair, or None if unusable."""
    iv, ov = _vocab()
    rng = random.Random(seed)
    lex = gen.lexicon_for(fid, rng)
    p = gen.make(shape, rng, lex)
    r = render(p, fid, preamble)
    try:
        ids, slots, n_unk = iv.encode(r["text"])
    except TokenizeError:
        return None
    if n_unk:
        return None
    if len(ids) > MAX_IN:
        r = render(p, fid, 0)
        try:
            ids, slots, n_unk = iv.encode(r["text"])
        except TokenizeError:
            return None
        if n_unk or len(ids) > MAX_IN:
            return None
    try:
        toks = serialize(p, slots)
    except TokenizeError:
        return None
    if len(toks) + 2 > MAX_OUT:
        return None
    return {"in": ids, "out": [ov.bos] + ov.encode(toks) + [ov.eos],
            "slots": slots, "prog": p, "fid": fid, "shape": shape,
            "text": r["text"]}


def _worker(job):
    fids, shapes, seed, n, keep_text, stratify = job
    rng = random.Random(seed)
    rows, dropped = [], 0
    while len(rows) < n:
        if stratify:
            shape = shapes[len(rows) % len(shapes)]
            fid = fids[(len(rows) // len(shapes)) % len(fids)]
        else:
            fid = rng.choice(fids)
            shape = rng.choice(shapes)
        s = rng.randrange(1 << 60)
        e = build_example(fid, shape, s, rng.randrange(0, 9))
        if e is None:
            dropped += 1
            continue
        rec = {"in": e["in"], "out": e["out"], "fid": fid, "shape": shape,
               "slots": e["slots"]}
        if keep_text:
            rec["prog"] = program_json(e["prog"])
            rec["text"] = e["text"]
        rows.append(rec)
    return rows, dropped


def generate(fids, n, seed, procs=4, keep_text=False, stratify=False):
    per = max(1, n // procs)
    fl = list(fids)
    jobs = [(fl[i::procs] if stratify and len(fl) >= procs else fl,
             list(SHAPES), seed + 7919 * i, per, keep_text, stratify)
            for i in range(procs)]
    rows, dropped = [], 0
    ctx = mp.get_context("fork")
    with ctx.Pool(procs) as pool:
        for r, d in pool.imap_unordered(_worker, jobs):
            rows.extend(r)
            dropped += d
    return rows, dropped


def write_split(path: str, rows, keep_text: bool):
    """A flat token store, plus a gzipped sidecar for anything not an id."""
    ins = np.concatenate([np.asarray(r["in"], dtype=np.uint16) for r in rows])
    outs = np.concatenate([np.asarray(r["out"], dtype=np.uint16) for r in rows])
    ioff = np.cumsum([0] + [len(r["in"]) for r in rows]).astype(np.int64)
    ooff = np.cumsum([0] + [len(r["out"]) for r in rows]).astype(np.int64)
    np.savez(path + ".npz", ins=ins, outs=outs, ioff=ioff, ooff=ooff)
    with gzip.open(path + ".meta.jsonl.gz", "wt") as fh:
        for r in rows:
            m = {"fid": r["fid"], "shape": r["shape"], "slots": r["slots"]}
            if keep_text:
                m["prog"] = r["prog"]
                m["text"] = r["text"]
            fh.write(json.dumps(m) + "\n")


def load_split(path: str):
    z = np.load(path + ".npz")
    return z["ins"], z["outs"], z["ioff"], z["ooff"]


def load_meta(path: str):
    out = []
    with gzip.open(path + ".meta.jsonl.gz", "rt") as fh:
        for line in fh:
            out.append(json.loads(line))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/norm")
    ap.add_argument("--train", type=int, default=300000)
    ap.add_argument("--eval", type=int, default=6000)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20260830)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    groups = split_frames()
    iv, ov = _vocab()
    report = {"held": {"lexicon": HELD_LEXICON, "mode": HELD_MODE,
                       "qframe": HELD_QFORM or f"band, every {BAND_STRIDE}th"},
              "frames": {k: len(v) for k, v in groups.items()},
              "in_vocab": len(iv), "out_vocab": len(ov),
              "max_slots": MAX_SLOTS, "max_in": MAX_IN, "max_out": MAX_OUT,
              "shapes": list(SHAPES), "splits": {}}
    print(json.dumps(report["frames"]))

    t0 = time.time()
    rows, dropped = generate(groups["train"], a.train, a.seed, a.procs, False)
    write_split(os.path.join(a.out, "train"), rows, False)
    report["splits"]["train"] = {
        "n": len(rows), "dropped": dropped,
        "in_len_mean": float(np.mean([len(r["in"]) for r in rows])),
        "in_len_max": int(np.max([len(r["in"]) for r in rows])),
        "out_len_mean": float(np.mean([len(r["out"]) for r in rows])),
        "out_len_max": int(np.max([len(r["out"]) for r in rows])),
        "seconds": round(time.time() - t0, 1)}
    print("train", json.dumps(report["splits"]["train"]))

    for i, name in enumerate(("train_frames_eval", "qframe", "lexicon",
                              "mode", "mixed")):
        fids = groups["train"] if name == "train_frames_eval" else groups[name]
        t1 = time.time()
        rows, dropped = generate(fids, a.eval, a.seed + 91 + (i + 1) * 137,
                                 a.procs, True, True)
        write_split(os.path.join(a.out, name), rows, True)
        report["splits"][name] = {
            "n": len(rows), "dropped": dropped, "frames": len(fids),
            "in_len_mean": float(np.mean([len(r["in"]) for r in rows])),
            "in_len_max": int(np.max([len(r["in"]) for r in rows])),
            "seconds": round(time.time() - t1, 1)}
        print(name, json.dumps(report["splits"][name]))

    with open(os.path.join(a.out, "manifest.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    print("wrote", os.path.join(a.out, "manifest.json"))


if __name__ == "__main__":
    main()
