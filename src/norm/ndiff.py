"""Where the emitted structure and the gold structure differ.

`exact` is a hard metric and a hard metric can be hard for the wrong reason. A
network that writes a table's rows in a different order, or names a temporary
differently, would score zero on every such item while having read the page
correctly. This file separates that case from a genuine misreading.

Four buckets, checked in order, on every item the network gets wrong:

    order_only    the two programs are equal once every definition's entry
                  list, every input list and every definition list is sorted.
                  The reading is right and the serialisation order is not.
    same_answer   the structures differ and the interpreter returns the same
                  text for both. A downstream user cannot tell them apart on
                  this question, though another question would.
    shape_slip    the plan's operation sequence differs from the gold plan's.
                  The network read a different kind of page.
    value_slip    the plan matches and a definition's contents do not. The
                  network read the right kind of page and got a row wrong.

Nothing here is used as a headline. It exists so the exact match number can be
read for what it is.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict

import torch

from src.norm import ndata, neval, nmodel
from src.norm.interp import run
from src.norm.lang import NormError, Program
from src.norm.ntok import deserialize


def _canon_def(d):
    """A definition with every stated order removed, for the order_only test."""
    if d.kind == "table":
        if d.ordered:                      # first match wins, order is meaning
            return ("table", d.name, d.entries, d.default, True)
        return ("table", d.name, tuple(sorted(map(repr, d.entries))),
                repr(d.default), False)
    if d.kind == "bands":                  # cuts are ordered by construction
        return ("bands", d.name, d.attr, d.cuts, d.labels)
    if d.kind == "rule":
        return ("rule", d.name, repr(d.general),
                tuple(sorted(map(repr, d.exceptions))))
    if d.kind == "weights":
        return ("weights", d.name, tuple(sorted(map(repr, d.entries))))
    if d.kind == "affine":
        return ("affine", d.name, d.a, d.b, d.m)
    return (d.kind, repr(d))


def canon(p: Program):
    return (tuple(sorted(map(repr, map(_canon_def, p.defs)))),
            tuple(sorted(map(repr, p.inputs))),
            tuple((s.out, s.op, tuple(map(repr, s.args))) for s in p.steps),
            p.answer)


def plan_ops(p: Program):
    return tuple(s.op for s in p.steps)


def bucket(got: Program, gold: Program) -> str:
    if got == gold:
        return "exact"
    if canon(got) == canon(gold):
        return "order_only"
    a, b = run(got), run(gold)
    if a.ok and b.ok and a.text == b.text:
        return "same_answer"
    if plan_ops(got) != plan_ops(gold):
        return "shape_slip"
    return "value_slip"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--out", default="results/norm/ndiff")
    ap.add_argument("--splits", default="train_frames_eval,qframe,lexicon,mode")
    ap.add_argument("--n", type=int, default=2800)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--examples", type=int, default=3)
    a = ap.parse_args()

    device = "cuda"
    iv, ov = ndata._vocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    model = nmodel.build(ck["size"], len(iv), len(ov)).to(device)
    model.load_state_dict(ck["state"])
    tag = os.path.basename(a.ckpt).replace("ckpt_", "").replace(".pt", "")
    os.makedirs(a.out, exist_ok=True)

    report = {"ckpt": os.path.abspath(a.ckpt), "size": ck["size"],
              "params": ck["params"], "splits": {}}
    for sp in a.splits.split(","):
        items = neval.load_eval(os.path.join(a.data, sp), a.n)
        em = neval.emit(model, items, ov, device, "greedy", batch=a.batch)
        rows = defaultdict(Counter)
        show = defaultdict(list)
        for it, e in zip(items, em):
            c = rows[it["shape"]]
            c["n"] += 1
            try:
                got = deserialize(ov.decode(e), it["slots"])
            except (NormError, Exception):
                c["malformed"] += 1
                continue
            b = bucket(got, it["prog"])
            c[b] += 1
            if b in ("value_slip", "shape_slip", "same_answer") \
                    and len(show[it["shape"]]) < a.examples:
                show[it["shape"]].append(
                    {"bucket": b, "fid": it["fid"],
                     "gold_ops": list(plan_ops(it["prog"])),
                     "got_ops": list(plan_ops(got)),
                     "gold_defs": [repr(d) for d in it["prog"].defs],
                     "got_defs": [repr(d) for d in got.defs],
                     "gold_steps": [repr(s) for s in it["prog"].steps],
                     "got_steps": [repr(s) for s in got.steps]})
        out = {}
        for sh, c in sorted(rows.items()):
            n = c["n"]
            out[sh] = {"n": n, **{k: round(c[k] / n, 4) for k in
                                  ("exact", "order_only", "same_answer",
                                   "shape_slip", "value_slip", "malformed")}}
        report["splits"][sp] = {"by_shape": out, "examples": dict(show)}
        print(sp, json.dumps({k: v for k, v in out.items()}), flush=True)
    path = os.path.join(a.out, f"{tag}.json")
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1)
    print("wrote", os.path.abspath(path))


if __name__ == "__main__":
    main()
