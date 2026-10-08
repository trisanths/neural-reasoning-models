"""Probe items for the key position test, built from the norm eval splits.

Nothing here is new data. Every item is one row of `data/norm/<split>.meta`,
which `src/norm/ndata.py` wrote, read with its own `fid`, `shape`, `slots`,
`prog` and `text` untouched. The key position label is `fid.split(".")[2]`,
the same field `src/role/rsplit.py` splits on, so a cell here holds the same
items as the cell of the same name in the arm tables.

What is added is a per item handle on one stated pair. The rule line is found
in the page text by searching for the one line that names both symbols of the
pair, not by re-rendering a template, so the line is byte identical to what a
reader sees. Which of the two symbols the line names first is read off that
line and checked against the frame id, which is what makes `key_first` and
`value_first` mean the same thing here as they do in the arm tables.

Rows are shuffled under a fixed seed before they are written, so a prefix of
the file is a sample of the split and not its first N in file order.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import sys
from collections import Counter

from src.corpus.frames_default import LEXICONS
from src.norm import interp
from src.norm.lang import program_load
from src.norm.parse import parse

SPLITS = ("mode", "train_frames_eval", "qframe", "lexicon")
# The eight shapes whose rule line is the only thing that says which symbol is
# the key, per src/role/ROLE.md.  This is where the 45M collapse lives.
EIGHT = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
         "precedence", "priority")
# Single table shapes, used by the table emission formulation.
ONE_TABLE = ("lookup", "inverse", "iterate", "priority", "exclusion")


def tables_of(prog):
    return [d for d in prog.defs if d.kind == "table"]


def find_line(text, k, v):
    """The one line of the page naming both symbols, or None."""
    hits = [ln for ln in text.split("\n") if k in ln and v in ln]
    return hits[0] if len(hits) == 1 else None


def build(split, root, seed):
    from src.norm.ndata import load_meta
    meta = load_meta(os.path.join(root, split))
    rows = []
    drop = Counter()
    for i, m in enumerate(meta):
        fid, shape, text = m["fid"], m["shape"], m["text"]
        lex, mode, kp, qform, scope = fid.split(".")
        prog = program_load(m["prog"])
        res = interp.run(prog)
        if not res.ok:
            drop["gold_not_executable"] += 1
            continue
        gold = res.text
        pages_text, _, question = text.rpartition("\n\n")
        if "\n" in question:
            drop["question_not_last_paragraph"] += 1
            continue
        tabs = tables_of(prog)
        pairs = [(t.name, k, v) for t in tabs for k, v in t.entries
                 if isinstance(k, str) and isinstance(v, str)]
        rng = random.Random(f"{fid}|{i}|{seed}")
        rec = {"iid": f"{split}/{i}", "split": split, "fid": fid, "lex": lex,
               "mode": mode, "kp": kp, "qform": qform, "scope": scope,
               "shape": shape, "eight": shape in EIGHT,
               "text": text, "pages_text": pages_text, "question": question,
               "gold_answer": gold,
               "item_noun": LEXICONS[lex]["item"],
               "target_noun": LEXICONS[lex]["target"]}
        # one stated pair, sampled
        if pairs:
            name, k, v = rng.choice(pairs)
            line = find_line(text, k, v)
            if line is None:
                drop["rule_line_not_unique"] += 1
            else:
                first = k if line.index(k) < line.index(v) else v
                rec["pair"] = {"table": name, "k": k, "v": v,
                               "line": line.strip(),
                               "first_symbol": first,
                               "surface_key_first": first == k}
                # option order for the forced choice, randomised per item
                opts = [k, v]
                rng.shuffle(opts)
                rec["pair"]["options"] = opts
                rec["pair"]["gold_letter_key"] = "A" if opts[0] == k else "B"
                rec["pair"]["gold_letter_value"] = "A" if opts[0] == v else "B"
        # the whole table, for the emission formulation
        if shape in ONE_TABLE and len(tabs) == 1:
            t = tabs[0]
            ents = [[k, v] for k, v in t.entries
                    if isinstance(k, str) and isinstance(v, str)]
            if len(ents) == len(t.entries):
                rec["table"] = {"name": t.name, "entries": ents,
                                "default": t.default}
        # the hand written parser, on the same item
        p = parse(text, fid)
        pr = {"ok": bool(p.ok), "program_equal": bool(p.ok)
              and p.program == prog}
        if p.ok:
            pres = interp.run(p.program)
            pr["answer"] = pres.text if pres.ok else ""
            pr["answer_exact"] = bool(pres.ok and pres.text == gold)
            ptabs = tables_of(p.program)
            if "pair" in rec:
                want = (rec["pair"]["k"], rec["pair"]["v"])
                got = [(a, b) for t in ptabs for a, b in t.entries
                       if isinstance(a, str) and {a, b} == set(want)]
                pr["role_exact"] = bool(len(got) == 1 and got[0] == want)
            if "table" in rec and len(ptabs) == 1:
                pr["table_exact"] = ([[a, b] for a, b in ptabs[0].entries]
                                     == rec["table"]["entries"])
        else:
            pr["answer"] = ""
            pr["answer_exact"] = False
        rec["parser"] = pr
        rows.append(rec)
    random.Random(seed).shuffle(rows)
    return rows, drop


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/norm")
    ap.add_argument("--out", default="results/role/lfm2/items")
    ap.add_argument("--seed", type=int, default=20260901)
    ap.add_argument("--splits", default=",".join(SPLITS))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    summary = {}
    for sp in a.splits.split(","):
        rows, drop = build(sp, a.root, a.seed)
        dest = os.path.join(a.out, f"{sp}.jsonl.gz")
        with gzip.open(dest, "wt") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        c = Counter()
        for r in rows:
            c[r["kp"]] += 1
            c[(r["kp"], "pair")] += int("pair" in r)
            c[(r["kp"], "table")] += int("table" in r)
            c[(r["kp"], "parser_answer")] += int(r["parser"]["answer_exact"])
            c[(r["kp"], "parser_prog")] += int(r["parser"]["program_equal"])
            if "pair" in r:
                c[(r["kp"], "surface_matches_fid")] += int(
                    r["pair"]["surface_key_first"] == (r["kp"] == "key_first"))
                c[(r["kp"], "parser_role")] += int(
                    r["parser"].get("role_exact", False))
            if "table" in r:
                c[(r["kp"], "parser_table")] += int(
                    r["parser"].get("table_exact", False))
        summary[sp] = {"n": len(rows), "dropped": dict(drop), "path":
                       os.path.abspath(dest),
                       "cells": {f"{k[0]}|{k[1]}" if isinstance(k, tuple)
                                 else k: v for k, v in c.items()}}
        print(sp, json.dumps(summary[sp]["cells"]), flush=True)
    with open(os.path.join(a.out, "items_summary.json"), "w") as fh:
        json.dump({"seed": a.seed, "root": os.path.abspath(a.root),
                   "splits": summary}, fh, indent=1)
    print("wrote", os.path.join(a.out, "items_summary.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
