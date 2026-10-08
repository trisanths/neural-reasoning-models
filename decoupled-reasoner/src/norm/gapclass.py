"""What the reader wrote instead, classified, on the shapes the axis reaches.

`src/norm/gap.py` re-emits the structures and gates the pass on reproducing the
committed record file item by item. This script reads those records and sorts
every failure into the six outcomes the decision needs, and it computes the two
cross-cutting diagnostics that the six-way sort on its own would hide.

The sort, first match winning:

    exact          the emitted structure is the gold structure
    malformed      the token stream is not a structure, so nothing parses
    refused        it parses and `src/norm/interp.run` declines it
    wrong kind     it runs, and its definition kinds, their key arities or its
                   plan operations are not gold's
    wrong binding  it runs, the kinds and the plan match, and the emitted
                   structure holds exactly gold's own symbols in a different
                   arrangement, so the reader read the page's words and bound
                   them to the wrong slots
    wrong content  the kinds and the plan match and some symbol or number is
                   not one of gold's
    downstream     the structure is gold's and the answer is not, which is
                   empty by construction and counted anyway

`wrong binding` is a multiset test over every scalar in the structure rather
than a field by field comparison, because a table read backwards carries its
default and its question key backwards too, and a field comparison put those in
`wrong content`.

The two diagnostics cut across the sort.

    tables transposed  every binding-bearing definition is gold's with key and
                       value reversed. This is positional binding in its
                       cleanest form and it appears in three of the six
                       outcomes, because a reader that transposes a table and
                       then compensates with `invert` for `lookup` is scored
                       `wrong kind` while doing the same thing.
    answer matches     the structure is not gold's and it executes to gold's
                       answer anyway.

Nothing is pooled across key position or across shape.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import time
from collections import Counter, defaultdict

from src.norm import ndata, neval
from src.norm.lang import program_json
from src.norm.parse import parse
from src.role.rshapes import GROUPS

CATS = ("exact", "malformed", "refused", "wrong kind", "wrong binding",
        "wrong content", "downstream")


def wilson(k, n, z=1.959964):
    if not n:
        return [0.0, 0.0]
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def cell(k, n):
    return {"k": k, "n": n, "share": round(k / n, 4) if n else None,
            "ci": wilson(k, n)}


def leaves(o, out):
    """Every scalar in a serialised structure, ignoring the kind tags."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k != "kind":
                leaves(v, out)
    elif isinstance(o, list):
        for v in o:
            leaves(v, out)
    elif o is not None:
        out[repr(o)] += 1
    return out


def arity(d):
    if d.get("kind") in ("table", "weights") and d.get("entries"):
        k = d["entries"][0][0]
        return len(k["$tuple"]) if isinstance(k, dict) else 1
    return 0


def sig(pj):
    return (tuple((d["kind"], arity(d)) for d in pj["defs"]),
            tuple(s["op"] for s in pj["steps"]))


def entries(pj):
    c = Counter()
    for d in pj["defs"]:
        for k, v in d.get("entries", []) or []:
            c[(d.get("name"), d["kind"], repr(k), repr(v))] += 1
        for k, v in d.get("exceptions", []) or []:
            c[(d.get("name"), "exc", repr(k), repr(v))] += 1
    return c


def tables_transposed(pj, gj):
    if len(pj["defs"]) != len(gj["defs"]):
        return False
    any_rev = False
    for dp, dg in zip(pj["defs"], gj["defs"]):
        if dp["kind"] != dg["kind"]:
            return False
        if dp["kind"] not in ("table", "weights"):
            continue
        ep, eg = dp["entries"], dg["entries"]
        if Counter(map(repr, ep)) == Counter(map(repr, eg)):
            continue
        if Counter(map(repr, ep)) != Counter(map(repr,
                                                 [[v, k] for k, v in eg])):
            return False
        any_rev = True
    return any_rev


def category(rec, gj):
    if rec["exact"]:
        return "exact"
    if rec["malformed"]:
        return "malformed"
    if rec["refused"]:
        return "refused"
    pj = rec["emitted"]
    if sig(pj) != sig(gj):
        return "wrong kind"
    if leaves(pj, Counter()) == leaves(gj, Counter()):
        return "wrong binding"
    return "wrong content"


def baselines(items, shapes):
    """The parser and the modal-by-shape floor on the same cells."""
    iv, ov = ndata._vocab()
    golds = [it["gold_ids"][1:-1].tolist() for it in items]
    modal_shape = neval.modal_by_shape(items, golds)
    modal_all = Counter(tuple(g) for g in golds).most_common(1)[0][0]
    rows = defaultdict(Counter)
    for it in items:
        if it["shape"] not in shapes:
            continue
        c = rows[(it["shape"], it["fid"].split(".")[2])]
        c["n"] += 1
        pp = parse(it["text"], it["fid"])
        c["parser_exact"] += int(pp.ok and pp.program == it["prog"])
        for name, seq in (("modal", modal_all),
                          ("modal_shape", modal_shape[it["shape"]])):
            mr = neval.classify_emission(ov.decode(list(seq)), it["slots"],
                                         it["prog"])
            c[name + "_exact"] += int(mr["exact"])
    return rows


def sizes(items, shapes):
    out = defaultdict(Counter)
    for it in items:
        if it["shape"] not in shapes:
            continue
        pj = program_json(it["prog"])
        c = out[it["shape"]]
        c["items"] += 1
        c["defs"] += len(pj["defs"])
        c["steps"] += len(pj["steps"])
        c["entries"] += sum(len(d.get("entries", []) or [])
                            + len(d.get("exceptions", []) or [])
                            for d in pj["defs"])
    return {s: {"mean_defs": round(c["defs"] / c["items"], 2),
                "mean_steps": round(c["steps"] / c["items"], 2),
                "mean_entries": round(c["entries"] / c["items"], 2)}
            for s, c in out.items()}


def summarise(rs):
    n = len(rs)
    c = Counter(x["cat"] for x in rs)
    row = {"n": n, "outcomes": {}, "of_failures": {}}
    fails = [x for x in rs if x["cat"] != "exact"]
    nf = len(fails)
    for k in CATS:
        row["outcomes"][k] = cell(c.get(k, 0), n)
        row["of_failures"][k] = cell(c.get(k, 0), nf) if k != "exact" else None
    row["n_failures"] = nf
    row["failures_tables_transposed"] = cell(
        sum(1 for x in fails if x["transposed"]), nf)
    row["failures_answer_matches_gold"] = cell(
        sum(1 for x in fails if x["answer_ok"]), nf)
    parsed = [x for x in fails if x["entries_gold"] is not None]
    tot = sum(x["entries_gold"] for x in parsed)
    row["entry_error"] = {
        "n_failures_that_parsed": len(parsed),
        "mean_share_of_entries_wrong": (round(sum(x["entries_wrong"]
                                                  for x in parsed) / tot, 4)
                                        if tot else None),
        "every_entry_wrong": cell(sum(1 for x in parsed
                                      if x["entries_wrong"]
                                      == x["entries_gold"] > 0), len(parsed)),
        "at_most_two_entries_wrong": cell(
            sum(1 for x in parsed if 1 <= x["entries_wrong"] <= 2),
            len(parsed))}
    row["transposed_within_outcome"] = {
        k: sum(1 for x in fails if x["cat"] == k and x["transposed"])
        for k in CATS[1:]}
    row["answer_matches_within_outcome"] = {
        k: sum(1 for x in fails if x["cat"] == k and x["answer_ok"])
        for k in CATS[1:]}
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--mode", default="greedy")
    ap.add_argument("--split", default="mode")
    ap.add_argument("--group", default="new keys")
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--dir", default="results/norm/gap")
    a = ap.parse_args()

    shapes = GROUPS[a.group]
    items = neval.load_eval(os.path.join(a.data, a.split), 7000)
    gold = [program_json(it["prog"]) for it in items]
    path = os.path.join(a.dir, "records_%s_%s_%s.jsonl.gz"
                        % (a.tag, a.split, a.mode))
    recs = [json.loads(l) for l in gzip.open(path, "rt")]
    if len(recs) != len(items):
        raise SystemExit("record file and eval split disagree on length")

    rows = defaultdict(list)
    for i, r in enumerate(recs):
        if r["fid"] != items[i]["fid"] or r["shape"] != items[i]["shape"]:
            raise SystemExit("record %d is not the eval item %d" % (i, i))
        if r["shape"] not in shapes:
            continue
        gj, pj = gold[i], r.get("emitted")
        eg = entries(gj)
        x = {"cat": category(r, gj),
             "transposed": bool(pj) and tables_transposed(pj, gj),
             "answer_ok": bool(r["answer"]) and r["answer"] == r["gold_answer"],
             "entries_gold": sum(eg.values()) if pj else None,
             "entries_wrong": (sum((eg - entries(pj)).values()) if pj
                               else None)}
        rows[(r["shape"], r["key_position"])].append(x)

    base = baselines(items, shapes)
    out = {"tag": a.tag, "mode": a.mode, "split": a.split, "group": a.group,
           "shapes": list(shapes),
           "built": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
           "record_file": os.path.abspath(path),
           "record_written": time.strftime("%Y-%m-%d %H:%M UTC",
                                           time.gmtime(
                                               os.path.getmtime(path))),
           "gold_structure_size": sizes(items, shapes),
           "by_shape_position": {}, "group_by_position": {}}
    grp = defaultdict(list)
    for (sh, kp), rs in sorted(rows.items()):
        c = summarise(rs)
        b = base[(sh, kp)]
        c["parser_exact"] = cell(b["parser_exact"], b["n"])
        c["modal_exact"] = cell(b["modal_exact"], b["n"])
        c["modal_shape_exact"] = cell(b["modal_shape_exact"], b["n"])
        out["by_shape_position"].setdefault(sh, {})[kp] = c
        grp[kp].extend(rs)
    for kp, rs in grp.items():
        c = summarise(rs)
        tot = Counter()
        for (sh, k), b in base.items():
            if k == kp:
                tot += b
        c["parser_exact"] = cell(tot["parser_exact"], tot["n"])
        c["modal_exact"] = cell(tot["modal_exact"], tot["n"])
        c["modal_shape_exact"] = cell(tot["modal_shape_exact"], tot["n"])
        out["group_by_position"][kp] = c

    dest = os.path.join(a.dir, "class_%s_%s_%s.json"
                        % (a.tag, a.split, a.mode))
    json.dump(out, open(dest, "w"), indent=1)
    print("wrote", os.path.abspath(dest))
    for kp in ("key_first", "value_first"):
        c = out["group_by_position"][kp]
        print("%s  n=%d  exact %.4f %s  parser %.4f  modal/shape %.4f"
              % (kp, c["n"], c["outcomes"]["exact"]["share"],
                 c["outcomes"]["exact"]["ci"], c["parser_exact"]["share"],
                 c["modal_shape_exact"]["share"]))
        for k in CATS[1:]:
            o, f = c["outcomes"][k], c["of_failures"][k]
            print("    %-14s %4d  %.4f of items %s  %.4f of failures"
                  % (k, o["k"], o["share"], o["ci"], f["share"]))
        print("    tables transposed %d of %d failures = %.4f %s"
              % (c["failures_tables_transposed"]["k"], c["n_failures"],
                 c["failures_tables_transposed"]["share"],
                 c["failures_tables_transposed"]["ci"]))
        print("    answer matches gold on %d of %d failures = %.4f"
              % (c["failures_answer_matches_gold"]["k"], c["n_failures"],
                 c["failures_answer_matches_gold"]["share"]))
        print("    transposed within outcome:",
              c["transposed_within_outcome"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
