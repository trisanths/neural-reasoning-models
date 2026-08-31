"""How far each corpus frame is from the nearest frame the normalizer trained on.

`src/frames/distance.py` measures a frame two ways and refuses to mix them:
`shape_distance` is Levenshtein over a delexicalised token sequence divided by
the longer length, and `lex_distance` is one minus the Jaccard overlap of the
open-class words that delexicalisation removed. Both functions, and
`delexicalise` itself, are imported unchanged.

What that module cannot supply here is the surface. Its `surface` renders the
156 frame bank of `src/frames/generate.py` for the three
`src/skillacq/simple.py` families. The frames this comparison runs over are the
768 corpus frames, so the surface is produced by rendering one fixed structure
into each of them with `src/norm/render.py`, and the nonce map is read off that
structure: definition and page names become NAME, keys become KEY, values and
band labels become VAL. Everything else the two paths do is the imported code.

Distance is reported to the nearest training frame, minimised on the shape axis,
with the lexical distance to that same nearest frame carried beside it and the
minimum lexical distance over all training frames reported separately.
"""
from __future__ import annotations

import argparse
import json
import os
from multiprocessing import Pool

from src.frames.distance import delexicalise, lex_distance, shape_distance
from src.norm import gen, ndata, render
from src.norm.lang import Bands, Rule, Table, Weights

SHAPE = "lookup"
SEED = 4242
PREAMBLE = 1


def nonce_map(p, pages) -> dict:
    m = {}
    for d in p.defs:
        m[str(d.name).lower()] = "NAME"
        if isinstance(d, Table):
            for k, v in d.entries:
                ks = k if isinstance(k, tuple) else (k,)
                for kk in ks:
                    m.setdefault(str(kk).lower(), "KEY")
                m[str(v).lower()] = "VAL"
            if d.default is not None:
                m[str(d.default).lower()] = "VAL"
        elif isinstance(d, Bands):
            m[str(d.attr).lower()] = "KEY"
            for lb in d.labels:
                m[str(lb).lower()] = "VAL"
        elif isinstance(d, Rule):
            m[str(d.general).lower()] = "VAL"
            for k, v in d.exceptions:
                m.setdefault(str(k).lower(), "KEY")
                m[str(v).lower()] = "VAL"
        elif isinstance(d, Weights):
            for k, _ in d.entries:
                m.setdefault(str(k).lower(), "KEY")
    for name, val in p.inputs:
        if isinstance(val, str):
            m.setdefault(val.lower(), "KEY")
        elif isinstance(val, tuple):
            for v in val:
                m.setdefault(str(v).lower(), "KEY")
    return m


def signature(fid: str):
    p = gen.make_for(fid, SHAPE, SEED)
    d = render.render(p, fid, PREAMBLE)
    sk, wd = delexicalise(d["text"], nonce_map(p, d["pages"]))
    return {"skeleton": sk, "words": sorted(wd)}


_SIGS = None
_TRAIN = None


def _init(sigs, train):
    global _SIGS, _TRAIN
    _SIGS, _TRAIN = sigs, train


def _row(fid):
    a = _SIGS[fid]
    best_shape, best_fid, best_lex_at = 2.0, "", 1.0
    min_lex = 1.0
    for t in _TRAIN:
        b = _SIGS[t]
        s = shape_distance(a["skeleton"], b["skeleton"])
        lx = lex_distance(set(a["words"]), set(b["words"]))
        if lx < min_lex:
            min_lex = lx
        if s < best_shape or (s == best_shape and lx < best_lex_at):
            best_shape, best_fid, best_lex_at = s, t, lx
    return fid, {"shape_distance": round(best_shape, 6),
                 "lex_distance_at_nearest": round(best_lex_at, 6),
                 "min_lex_distance": round(min_lex, 6),
                 "nearest_train_frame": best_fid,
                 "n_skeleton_tokens": len(a["skeleton"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/norm/compare/frame_distance.json")
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    sp = ndata.split_frames()
    train = sorted(sp["train"])
    allf = sorted(f for v in sp.values() for f in v)
    sigs = {}
    for f in allf:
        sigs[f] = signature(f)
    print("signatures", len(sigs), "median tokens",
          sorted(len(s["skeleton"]) for s in sigs.values())[len(sigs) // 2],
          flush=True)
    targets = [f for f in allf if f not in sp["train"]]
    with Pool(a.procs, initializer=_init, initargs=(sigs, train)) as pool:
        rows = dict(pool.map(_row, targets, chunksize=4))
    for f in train:
        rows[f] = {"shape_distance": 0.0, "lex_distance_at_nearest": 0.0,
                   "min_lex_distance": 0.0, "nearest_train_frame": f,
                   "n_skeleton_tokens": len(sigs[f]["skeleton"])}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    payload = {"shape": SHAPE, "seed": SEED, "preamble_level": PREAMBLE,
               "n_frames": len(rows), "n_train_frames": len(train),
               "frames": rows}
    with open(a.out, "w") as fh:
        json.dump(payload, fh, indent=1)
    import statistics as st
    for grp in ("qframe", "lexicon", "mode", "mixed"):
        vs = [rows[f]["shape_distance"] for f in sorted(sp[grp])]
        ls = [rows[f]["lex_distance_at_nearest"] for f in sorted(sp[grp])]
        print(f"{grp:8s} n={len(vs)} shape min={min(vs):.4f} "
              f"median={st.median(vs):.4f} max={max(vs):.4f} | "
              f"lex median={st.median(ls):.4f} max={max(ls):.4f}")
    print("wrote", os.path.abspath(a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
