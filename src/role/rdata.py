"""The minimal pair training draw: one structure, both key positions, adjacent.

`data/norm/train` carries both key positions, near enough half and half inside
every sentence mode, but never for the same content. Every item is a fresh
structure in one frame, so "the key is the invented word that appears first" is
never contradicted by a neighbour; it is only contradicted across items that
share nothing else. A rule keyed on the frame's own template fits that draw
perfectly.

This draw removes that. One structure is rendered twice, in two frames that
agree on lexicon, statement mode, question form and scope position and differ
only in key position, and the two renderings sit next to each other in the same
batch. The gold targets are correspondingly different: slots are numbered by
order of first appearance, so the same table is written `W1 W2` in one member
and `W2 W1` in the other. A reader that binds role to position emits one
sequence for both and can be right about at most one of them.

The frame split is `src/norm/ndata.py:split_frames` unchanged. Key position is
not one of the three withheld axes and no group is defined by it, so every
training frame's key position sibling is also a training frame: 490 training
frames are 245 sibling pairs. Nothing held out is touched.

Key position does not reach every shape. It selects the `ASSOC` sentence and
the `table_row` header and nothing else, so a `classify` page, an `apply_n`
page, a `lookup_general` page and a `pair` page come out byte identical in the
two frames. Rendering those twice would put a literal duplicate in the batch
and halve the distinct content for no contrast, so a draw whose two renderings
agree is thrown away and replaced by two independent items of that same shape,
drawn the way `src/norm/ndata.py` draws them. Every pair in the file therefore
differs, and the shape mix is unchanged.

The volume matches the baseline. 600,000 slots of two are 1,200,000 items,
which is what `data/norm/train` holds, so the two arms see the same number of
items over the same number of steps. Half as many distinct structures on the
paired shapes is the price of the manipulation and is stated rather than
hidden.
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

from collections import Counter

from src.norm import gen, ndata
from src.norm.lang import program_json
from src.norm.ntok import TokenizeError, serialize
from src.norm.render import SHAPES, render

FLIP = {"key_first": "value_first", "value_first": "key_first"}


def sibling(fid: str) -> str:
    """The frame that differs from this one only in key position."""
    p = fid.split(".")
    p[2] = FLIP[p[2]]
    return ".".join(p)


def sibling_pairs(fids):
    """(key_first fid, value_first fid) for every frame in the list.

    Raises if a frame's sibling is not in the same group, which would mean the
    pair straddles the train/held-out boundary.
    """
    s = set(fids)
    out = []
    for f in sorted(s):
        if f.split(".")[2] != "key_first":
            continue
        v = sibling(f)
        if v not in s:
            raise ValueError(f"{f} has no sibling inside this group")
        out.append((f, v))
    if 2 * len(out) != len(s):
        raise ValueError("the group is not closed under the key position flip")
    return out


def write_split(path: str, rows, keep_text: bool):
    """`src/norm/ndata.py:write_split` with the pair flag kept beside it.

    The token store is the same file in the same layout, so the trainer and the
    grader read this split with the norm lane's own loaders. The sidecar gains
    one field and nothing loses a field.
    """
    ins = np.concatenate([np.asarray(r["in"], dtype=np.uint16) for r in rows])
    outs = np.concatenate([np.asarray(r["out"], dtype=np.uint16) for r in rows])
    ioff = np.cumsum([0] + [len(r["in"]) for r in rows]).astype(np.int64)
    ooff = np.cumsum([0] + [len(r["out"]) for r in rows]).astype(np.int64)
    np.savez(path + ".npz", ins=ins, outs=outs, ioff=ioff, ooff=ooff)
    with gzip.open(path + ".meta.jsonl.gz", "wt") as fh:
        for r in rows:
            m = {"fid": r["fid"], "shape": r["shape"], "slots": r["slots"],
                 "paired": r["paired"]}
            if keep_text:
                m["prog"] = r["prog"]
                m["text"] = r["text"]
            fh.write(json.dumps(m) + "\n")


def build_pair(pair, shape: str, seed: int, preamble: int):
    """Two items for one structure, or None if either side is unusable.

    The structure is drawn once, against the key_first member's reserved words.
    An invented word avoids the union of every frame's reserved set as well, so
    it is a nonce word in both members and the draw is not tilted toward either.
    """
    iv, ov = ndata._vocab()
    rng = random.Random(seed)
    lex = gen.lexicon_for(pair[0], rng)
    p = gen.make(shape, rng, lex)
    for level in (preamble, 0):
        rows, ok = [], True
        for fid in pair:
            r = render(p, fid, level)
            try:
                ids, slots, n_unk = iv.encode(r["text"])
            except TokenizeError:
                return None
            if n_unk or len(ids) > ndata.MAX_IN:
                ok = False
                break
            try:
                toks = serialize(p, slots)
            except TokenizeError:
                return None
            if len(toks) + 2 > ndata.MAX_OUT:
                return None
            rows.append({"in": ids, "out": [ov.bos] + ov.encode(toks) + [ov.eos],
                         "fid": fid, "shape": shape, "slots": slots,
                         "text": r["text"], "prog": p})
        if ok:
            return rows
        if level == 0:
            return None
    return None


def _rec(r, keep_text, paired):
    rec = {"in": r["in"], "out": r["out"], "fid": r["fid"],
           "shape": r["shape"], "slots": r["slots"], "paired": paired}
    if keep_text:
        rec["prog"] = r["prog"] if isinstance(r["prog"], dict) \
            else program_json(r["prog"])
        rec["text"] = r["text"]
    return rec


def _worker(job):
    pairs, fids, shapes, seed, n_pairs, keep_text = job
    rng = random.Random(seed)
    rows = []
    c = Counter()
    while len(rows) < 2 * n_pairs:
        pr = rng.choice(pairs)
        shape = rng.choice(shapes)
        got = build_pair(pr, shape, rng.randrange(1 << 60), rng.randrange(0, 9))
        if got is None:
            c["dropped"] += 1
            continue
        if got[0]["text"] != got[1]["text"]:
            c["paired"] += 1
            c["paired|" + shape] += 1
            rows.extend(_rec(r, keep_text, True) for r in got)
            continue
        # This shape's page does not carry the key position axis at all, so a
        # pair of it would be a duplicate. Two independent items instead.
        solo = [ndata.build_example(rng.choice(fids), shape,
                                    rng.randrange(1 << 60), rng.randrange(0, 9))
                for _ in range(2)]
        if any(s is None for s in solo):
            c["dropped"] += 1
            continue
        c["unpaired"] += 1
        c["unpaired|" + shape] += 1
        rows.extend(_rec(r, keep_text, False) for r in solo)
    return rows, c


def generate(pairs, fids, n_pairs, seed, procs=3, keep_text=False):
    per = max(1, n_pairs // procs)
    jobs = [(pairs, fids, list(SHAPES), seed + 7919 * i, per, keep_text)
            for i in range(procs)]
    rows, tot = [], Counter()
    ctx = mp.get_context("fork")
    with ctx.Pool(procs) as pool:
        for r, c in pool.imap_unordered(_worker, jobs):
            rows.extend(r)
            tot += c
    return rows, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/role")
    ap.add_argument("--name", default="paired_train")
    ap.add_argument("--pairs", type=int, default=600000)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260830)
    ap.add_argument("--keep-text", type=int, default=0)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    groups = ndata.split_frames()
    pairs = sibling_pairs(groups["train"])
    t0 = time.time()
    rows, c = generate(pairs, groups["train"], a.pairs, a.seed, a.procs,
                       bool(a.keep_text))
    path = os.path.join(a.out, a.name)
    write_split(path, rows, bool(a.keep_text))
    np.save(path + ".paired.npy",
            np.array([r["paired"] for r in rows[::2]], dtype=bool))
    bad = [i for i in range(0, len(rows), 2)
           if rows[i]["paired"] and sibling(rows[i]["fid"]) != rows[i + 1]["fid"]]
    rep = {"path": os.path.abspath(path), "n_items": len(rows),
           "n_slots_of_two": len(rows) // 2,
           "minimal_pairs": int(c["paired"]),
           "independent_because_the_shape_ignores_key_position":
               int(c["unpaired"]),
           "dropped_draws": int(c["dropped"]),
           "by_shape": {k: int(v) for k, v in sorted(c.items()) if "|" in k},
           "training_frames": len(groups["train"]),
           "sibling_pairs_of_frames": len(pairs),
           "adjacent_rows_that_are_not_siblings": len(bad),
           "layout": "pair k is rows 2k and 2k+1, key_first then value_first",
           "in_len_mean": float(np.mean([len(r["in"]) for r in rows])),
           "in_len_max": int(np.max([len(r["in"]) for r in rows])),
           "out_len_mean": float(np.mean([len(r["out"]) for r in rows])),
           "out_len_max": int(np.max([len(r["out"]) for r in rows])),
           "seed": a.seed, "seconds": round(time.time() - t0, 1)}
    with open(path + ".manifest.json", "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
