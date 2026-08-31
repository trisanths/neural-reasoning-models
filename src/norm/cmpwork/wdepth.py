"""Separating plan depth from page width on the iterate shape.

A ring of width w makes depth n and depth n mod w the same answer, so an
alias-free depth needs w > n. Widening the ring to reach a deeper question also
lengthens the page, and the generator only ever writes rings of width
max(4, n + 2) for n up to 8. Depth and width therefore move together unless
they are crossed on purpose, which is what this does: every (width, depth) cell
with depth < width, forty items each, on training frames.

Read down a column to see what depth costs at a fixed page. Read across a row
to see what the page costs at a fixed depth. The interpreter's own column is
constant by construction and is measured rather than asserted: `interp` is the
gold structure executed, which is 1.000 in every cell or the cell is broken.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import time

import numpy as np
import torch

from src.norm import gen, ndata, neval, nmodel, render
from src.norm.cmpwork.grade import forced
from src.norm.interp import run
from src.norm.lang import Table
from src.norm.neval import candidates
from src.norm.ntok import TokenizeError, deserialize, serialize
from src.norm.parse import parse
from src.norm.shapes import assemble

WIDTHS = (4, 6, 8, 10, 12, 14, 17, 20, 24, 32, 49)
DEPTHS = (2, 4, 8, 12, 16, 20, 24, 32, 48)


def case(fid, seed, n, width):
    rng = random.Random(seed)
    lex = gen.lexicon_for(fid, rng)
    name = lex.name()
    ring = lex.words(width)
    rng.shuffle(ring)
    t = Table(name, tuple((ring[i], ring[(i + 1) % width])
                          for i in range(width)))
    return assemble("iterate", tables=[t],
                    inputs=(("x", rng.choice(ring)),), n=n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="results/norm/train/ckpt_l.pt")
    ap.add_argument("--split", default="train")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--out", default="results/norm/compare/wdepth.json")
    a = ap.parse_args()

    iv, ov = ndata._vocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    model = nmodel.build(ck["size"], len(iv), len(ov)).cuda()
    model.load_state_dict(ck["state"])
    model.eval()
    fids = sorted(ndata.split_frames()[a.split])

    rep = {"ckpt": os.path.abspath(a.ckpt), "size": ck["size"],
           "split": a.split, "n_per_cell": a.n, "cells": {}}
    t0 = time.time()
    for w in WIDTHS:
        for d in DEPTHS:
            if d >= w:
                continue                    # aliased, not a depth cell
            items, encs = [], []
            for s in range(a.n):
                fid = fids[s % len(fids)]
                p = case(fid, 30011 + s * 7919 + w * 101 + d, d, w)
                doc = render.render(p, fid, s % 5)
                r = run(p)
                cs = candidates(p)
                if not r.ok or cs is None or r.text not in cs:
                    continue
                try:
                    ids, slots, n_unk = iv.encode(doc["text"])
                except TokenizeError:
                    continue
                over = n_unk or len(ids) > ndata.MAX_IN
                try:
                    serialize(p, slots)
                    writable = True
                except Exception:
                    writable = False
                pr = parse(doc["text"], fid)
                items.append({"prog": p, "gold": r.text,
                              "options": sorted(str(c) for c in cs),
                              "over": bool(over), "writable": writable,
                              "parser_ok": bool(pr.ok and pr.program == p),
                              "in_tokens": len(ids)})
                encs.append(None if over else
                            {"ids": np.asarray(ids, dtype=np.int64),
                             "slots": slots})
            if not items:
                continue
            live = [i for i, e in enumerate(encs) if e is not None]
            hits = exact = 0
            if live:
                em = neval.emit(model, [{"ids": encs[i]["ids"]} for i in live],
                                ov, "cuda", "greedy", batch=32,
                                max_len=ndata.MAX_OUT, seed=0)
                for k, i in enumerate(live):
                    try:
                        prog = deserialize(ov.decode(em[k]), encs[i]["slots"])
                    except Exception:
                        continue
                    exact += int(prog == items[i]["prog"])
                    rr = run(prog)
                    if rr.ok:
                        hits += forced(rr.text, items[i]["options"],
                                       items[i]["gold"])["strict_correct"]
            n = len(items)
            rep["cells"][f"{w}|{d}"] = {
                "width": w, "depth": d, "n": n,
                "floor": round(sum(1 / len(it["options"]) for it in items) / n, 4),
                "C_strict": round(hits / n, 4),
                "C_structure_exact": round(exact / n, 4),
                "parser_exact": round(sum(it["parser_ok"] for it in items) / n, 4),
                "seam_can_write": round(sum(it["writable"] for it in items) / n, 4),
                "input_over_cap": round(sum(it["over"] for it in items) / n, 4),
                "median_input_tokens": int(np.median([it["in_tokens"] for it in items]))}
            c = rep["cells"][f"{w}|{d}"]
            print(f"width {w:3d} depth {d:3d} n={n:3d} floor={c['floor']:.3f} "
                  f"C={c['C_strict']:.4f} exact={c['C_structure_exact']:.4f} "
                  f"parser={c['parser_exact']:.4f} writable={c['seam_can_write']:.2f} "
                  f"tokens={c['median_input_tokens']}", flush=True)
    rep["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print("wrote", os.path.abspath(a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
