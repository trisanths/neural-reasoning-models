"""Checks 1, 2 and 4 of the operator-graph audit. CPU only.

Check 1 re-derives every gold answer from the page prose with
src.audit.refprose, which shares no code with the generator, and reports every
disagreement.

Check 2 counts how often the answer to a depth d question is also something a
shorter or lazier computation would have produced: an intermediate value, an
operand, the answer to the same question truncated to k operands, or the answer
you get by reading the chain the other way round.

Check 4 reports, per cell, the size and entropy of the answer distribution, the
uniform-over-the-modulus floor, the best-constant floor, and the collision
floors, so a flat accuracy curve can be read against a floor that moves.

Everything is written to one JSON file. Nothing here needs a GPU.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.expanduser("~/opg"))

from src.audit.refprose import ProseError, RefWorld, answer_question, parse_evaluate  # noqa: E402
from src.opgraph.data import eval_worlds, make_item  # noqa: E402
from src.opgraph.invent import copyable  # noqa: E402

GRID = {
    "sequential": [1, 2, 3, 4, 5, 6, 7, 8],
    "breadth": [1, 2, 3, 4, 5, 6],
    "novel": [2, 3, 4, 5, 6],
    "sequential_paren": [2, 3, 4, 5, 6],
    "same_page_pair": [2],
    "units": [1],
}


def build(kind, depth, n, style):
    breadth = depth if kind == "breadth" else 3
    ws = eval_worlds(kind, n, breadth=breadth, style=style)
    return [make_item(kind, w, depth, i) for i, w in enumerate(ws)]


def entropy(counter, n):
    return -sum((c / n) * math.log2(c / n) for c in counter.values() if c)


def truncations(text, world, assoc_glyph):
    """Answers to the same flat chain cut off after k operators, k = 1..d-1."""
    import re
    m = re.match(r"^Evaluate\s+(.*?)\.$", text.strip())
    parts = m.group(1).split()
    vals = parts[0::2]
    glyphs = parts[1::2]
    out = []
    if len(set(glyphs)) != 1:
        return out
    for k in range(1, len(glyphs)):
        sub = "Evaluate " + f" {glyphs[0]} ".join(vals[:k + 1]) + "."
        try:
            out.append(answer_question(sub, world))
        except ProseError:
            pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--out", default="results/audit_gold.json")
    ap.add_argument("--kinds", default=",".join(GRID))
    ap.add_argument("--styles", default="0,1")
    args = ap.parse_args()

    report = {"n": args.n, "cells": {}, "page_example_failures": [],
              "world_read_failures": []}
    per_item = []

    for style in [int(s) for s in args.styles.split(",")]:
        for kind in args.kinds.split(","):
            for depth in GRID[kind]:
                items = build(kind, depth, args.n, style)
                cell = {"n": len(items), "disagree": 0, "unreadable": 0,
                        "mod_reading_differs": 0, "trunc_reading_differs": 0,
                        "assoc_free": 0, "operand_collision": 0,
                        "intermediate_collision": 0, "truncation_collision": 0,
                        "copyable": 0, "examples": []}
                golds = Counter()
                mods = []
                forms = Counter()
                for it in items:
                    pages = [p.text for p in it.world.shuffled_pages()]
                    try:
                        w = RefWorld.read(pages)
                    except ProseError as exc:
                        cell["unreadable"] += 1
                        report["world_read_failures"].append(
                            {"kind": kind, "depth": depth, "style": style,
                             "seed": it.world.seed, "why": str(exc)[:200]})
                        continue
                    bad = w.check_examples()
                    if bad:
                        report["page_example_failures"].append(
                            {"seed": it.world.seed, "style": style,
                             "cases": bad[:4]})
                    rec = []
                    try:
                        got = answer_question(it.text, w, record=rec) \
                            if it.text.startswith("Evaluate ") \
                            else answer_question(it.text, w)
                    except ProseError as exc:
                        cell["unreadable"] += 1
                        cell["examples"].append(
                            {"why": str(exc)[:160], "q": it.text[:120],
                             "gold": it.gold})
                        continue
                    if got != it.gold:
                        cell["disagree"] += 1
                        if len(cell["examples"]) < 6:
                            cell["examples"].append(
                                {"q": it.text[:160], "gold": it.gold, "ref": got,
                                 "seed": it.world.seed})
                    golds[it.gold] += 1
                    if copyable(it.gold, it.text):
                        cell["copyable"] += 1

                    if it.text.startswith("Evaluate "):
                        gl = sorted({g for g, _, _, _ in rec})
                        b = w.binops[gl[0]]
                        mods.append(b.modulus)
                        forms[b.form] += 1
                        try:
                            end = answer_question(it.text, w, mode="reduce_end")
                            if end != got:
                                cell["mod_reading_differs"] += 1
                        except ProseError:
                            pass
                        try:
                            tr = answer_question(it.text, w, trunc=True)
                            if tr != got:
                                cell["trunc_reading_differs"] += 1
                        except ProseError:
                            pass
                        other = "right" if b.assoc == "left" else "left"
                        try:
                            oa = answer_question(it.text, w, force_assoc=other)
                            if oa == got:
                                cell["assoc_free"] += 1
                        except ProseError:
                            oa = None
                        inter = [str(v) for (_, _, _, v) in rec[:-1]]
                        operands = [t for t in it.text.replace(".", "").split()
                                    if t.lstrip("-").isdigit()]
                        if it.gold in operands:
                            cell["operand_collision"] += 1
                        if it.gold in inter:
                            cell["intermediate_collision"] += 1
                        trs = []
                        if kind == "sequential" and depth >= 2:
                            trs = truncations(it.text, w, b.glyph)
                            if it.gold in trs:
                                cell["truncation_collision"] += 1
                        per_item.append(
                            {"kind": kind, "style": style, "depth": depth,
                             "seed": it.world.seed, "q": it.text,
                             "gold": it.gold, "ref": got,
                             "assoc": b.assoc, "modulus": b.modulus,
                             "form": b.form, "intermediates": inter,
                             "truncations": trs,
                             "wrong_assoc_answer": oa,
                             "operands": operands})
                    else:
                        per_item.append(
                            {"kind": kind, "style": style, "depth": depth,
                             "seed": it.world.seed, "q": it.text,
                             "gold": it.gold, "ref": got})

                n = max(1, sum(golds.values()))
                cell["support"] = len(golds)
                cell["entropy_bits"] = round(entropy(golds, n), 4)
                cell["best_constant"] = round(max(golds.values()) / n, 4) if golds else 0
                cell["best_constant_value"] = golds.most_common(1)[0][0] if golds else None
                if mods:
                    cell["uniform_floor"] = round(sum(1.0 / m for m in mods) / len(mods), 5)
                    cell["forms"] = dict(forms)
                report["cells"][f"{kind}|{depth}|s{style}"] = cell
                print(f"[{kind} d{depth} s{style}] n={cell['n']} "
                      f"disagree={cell['disagree']} unread={cell['unreadable']} "
                      f"modreading={cell['mod_reading_differs']} "
                      f"assocfree={cell['assoc_free']} "
                      f"inter={cell['intermediate_collision']} "
                      f"trunc={cell['truncation_collision']} "
                      f"support={cell['support']} H={cell['entropy_bits']}",
                      flush=True)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1)
    with open(args.out.replace(".json", "_items.json"), "w") as fh:
        json.dump(per_item, fh)
    print(f"[written] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
