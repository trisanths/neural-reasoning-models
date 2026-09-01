"""The control draw: the same content twice, contrasted on a different axis.

Arm B does two things at once. It puts the same structure in front of the
network twice, and it makes the two renderings disagree about key position. If
arm B moves the held-out sentence mode, the first of those is the confound: a
structure seen twice, adjacent, is a different training signal whatever axis
the two renderings differ on.

So this builds the same draw against the question form instead. One structure,
two frames that agree on lexicon, statement mode, key position and scope
position and differ only in which of the four question forms the question is
written in, adjacent in the batch. Same volume, same shape mix, same code path;
the only change is which field of the frame id moves. A gain that survives here
is a gain from seeing the content twice and not from the role contrast.

The withheld question-form band is `wh` with the scope first, so a scope-first
training frame has three question forms available and a scope-last one has
four. The partner is the next one in that frame's own list, which keeps both
members inside the training group.

Question form reaches every page, and key position reaches only some, so a
control that paired everything would hold twice as many structures twice as
often as arm B does. It therefore pairs exactly where arm B pairs: on the
shapes whose page carries the key position axis, and on `lookup_then_band`
only in `table_row`, where the axis reaches the column header. Everywhere else
it draws two independent items, as arm B does. The counts it produces are
checked against arm B's own manifest.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter

import numpy as np

from src.norm import ndata
from src.norm.render import SHAPES
from src.role import rdata

AXIS = 3

# The shapes whose page changes when key position changes. `ASSOC` is the only
# fact sentence the axis selects, and `HEADERS` the only other thing, so a page
# with no assoc fact and no table_row header is byte identical in the two
# frames. Checked against the counts in data/role/paired_train.manifest.json.
ASSOC_SHAPES = frozenset((
    "band_then_lookup", "compose", "exclusion", "inverse", "iterate", "lookup",
    "precedence", "priority", "sum_chain"))


def key_position_reaches(shape: str, mode: str) -> bool:
    if shape in ASSOC_SHAPES:
        return True
    if shape == "lookup_then_band":       # only through the column header
        return mode == "table_row"
    return False


def partners(fids):
    """(fid, the next question form of the same frame) for every frame."""
    by = {}
    for f in sorted(fids):
        p = f.split(".")
        by.setdefault(tuple(p[:AXIS] + p[AXIS + 1:]), []).append(p[AXIS])
    out = []
    for base, qs in sorted(by.items()):
        if len(qs) < 2:
            continue
        for i, q in enumerate(qs):
            a = list(base[:AXIS]) + [q] + list(base[AXIS:])
            b = list(base[:AXIS]) + [qs[(i + 1) % len(qs)]] + list(base[AXIS:])
            out.append((".".join(a), ".".join(b)))
    return out


def _worker(job):
    pairs, fids, shapes, seed, n_pairs, keep_text = job
    import random
    rng = random.Random(seed)
    rows = []
    c = Counter()
    while len(rows) < 2 * n_pairs:
        pr = rng.choice(pairs)
        shape = rng.choice(shapes)
        mode = pr[0].split(".")[1]
        seed = rng.randrange(1 << 60)
        pre = rng.randrange(0, 9)
        got = (rdata.build_pair(pr, shape, seed, pre)
               if key_position_reaches(shape, mode) else None)
        if got is not None and got[0]["text"] != got[1]["text"]:
            c["paired"] += 1
            c["paired|" + shape] += 1
            rows.extend(rdata._rec(r, keep_text, True) for r in got)
            continue
        solo = [ndata.build_example(rng.choice(fids), shape,
                                    rng.randrange(1 << 60), rng.randrange(0, 9))
                for _ in range(2)]
        if any(s is None for s in solo):
            c["dropped"] += 1
            continue
        c["unpaired"] += 1
        c["unpaired|" + shape] += 1
        rows.extend(rdata._rec(r, keep_text, False) for r in solo)
    return rows, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/role")
    ap.add_argument("--name", default="qpaired_train")
    ap.add_argument("--pairs", type=int, default=600000)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260830)
    ap.add_argument("--keep-text", type=int, default=0)
    a = ap.parse_args()

    import multiprocessing as mp
    os.makedirs(a.out, exist_ok=True)
    groups = ndata.split_frames()
    pr = partners(groups["train"])
    per = max(1, a.pairs // a.procs)
    jobs = [(pr, groups["train"], list(SHAPES), a.seed + 7919 * i, per,
             bool(a.keep_text)) for i in range(a.procs)]
    rows, tot = [], Counter()
    t0 = time.time()
    ctx = mp.get_context("fork")
    with ctx.Pool(a.procs) as pool:
        for r, c in pool.imap_unordered(_worker, jobs):
            rows.extend(r)
            tot += c
    path = os.path.join(a.out, a.name)
    rdata.write_split(path, rows, bool(a.keep_text))
    np.save(path + ".paired.npy",
            np.array([r["paired"] for r in rows[::2]], dtype=bool))
    bad = 0
    for i in range(0, len(rows), 2):
        if not rows[i]["paired"]:
            continue
        x, y = rows[i]["fid"].split("."), rows[i + 1]["fid"].split(".")
        if [k for k in range(5) if x[k] != y[k]] != [AXIS]:
            bad += 1
    rep = {"path": os.path.abspath(path), "n_items": len(rows),
           "axis": "question form, field 3 of the frame id",
           "n_slots_of_two": len(rows) // 2,
           "pairs": int(tot["paired"]),
           "independent_because_the_shape_ignores_the_axis":
               int(tot["unpaired"]),
           "dropped_draws": int(tot["dropped"]),
           "adjacent_rows_that_differ_elsewhere": bad,
           "frame_partners": len(pr),
           "by_shape": {k: int(v) for k, v in sorted(tot.items()) if "|" in k},
           "in_len_mean": float(np.mean([len(r["in"]) for r in rows])),
           "out_len_mean": float(np.mean([len(r["out"]) for r in rows])),
           "seed": a.seed, "seconds": round(time.time() - t0, 1)}
    with open(path + ".manifest.json", "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
