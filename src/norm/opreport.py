"""Every number this lane reports, read off the record files.

Nothing is computed twice and nothing is pooled across a family. A cell is one
(condition, family) pair, or one (condition, family, frame split) triple where
the frame split is what separates a wording the network trained on from one it
did not. Each cell carries its own denominator, its own averaged chance floor
from the option sets of its own items, the strict and lenient forced choice
scores of `src/norm/cmpwork/grade.py`, the hedge and no-answer rates, and the
refusal rate, which for the library systems is the rate at which the reader or
the interpreter said it could not.
"""

from __future__ import annotations

import argparse
import glob
import gzip
import json
import os

from src.norm.cmpwork.grade import forced

SYSTEMS = ("L", "P", "S1", "S2")


def load(path):
    return [json.loads(l) for l in gzip.open(path, "rt")]


def cell(rows, get) -> dict:
    """One (system, item set) cell: the whole line, denominator included."""
    n = len(rows)
    if not n:
        return {"n": 0}
    strict = lenient = hedge = none = declined = exact = 0
    floor = 0.0
    n_exact = 0
    for r in rows:
        g = get(r)
        f = forced(g.get("answer", ""), r["options"], r["gold"])
        strict += f["strict_correct"]
        lenient += f["lenient_correct"]
        hedge += f["hedged"]
        none += f["named_none"]
        floor += f["floor"]
        if g.get("state") in ("misread", "refused", "malformed",
                              "unreadable_input"):
            declined += 1
        if "exact" in g:
            exact += g["exact"]
            n_exact += 1
    out = {"n": n, "strict": round(strict / n, 4),
           "lenient": round(lenient / n, 4), "hedge": round(hedge / n, 4),
           "none": round(none / n, 4), "floor": round(floor / n, 4),
           "declined": round(declined / n, 4)}
    if n_exact:
        out["structure_exact"] = round(exact / n_exact, 4)
    return out


def by(rows, keyf):
    out = {}
    for r in rows:
        out.setdefault(keyf(r), []).append(r)
    return out


def getter(system: str, mode: str = ""):
    if mode:
        return lambda r: r.get(mode, {})
    return lambda r: r.get(system, {})


# ------------------------------------------------------------ conditions


def contra_cell(rows, get) -> dict:
    """Which of the two answers a system gave, on pages that dissent.

    `follows_page` is the answer the definition page states. `follows_training`
    is the first directory, which is what the corpus precedence pages taught
    and what the trained checkpoint answered on 678 of 678 transposed pages.
    On the `page_first` half the two coincide, which is why the two halves are
    reported side by side and never added together.
    """
    n = len(rows)
    if not n:
        return {"n": 0}
    page = train = neither = declined = 0
    floor = 0.0
    for r in rows:
        g = get(r)
        ans = g.get("answer", "")
        f = forced(ans, r["options"], r["gold"])
        named = f["named"][0] if len(f["named"]) == 1 else None
        if named is not None and named == r["gold"]:
            page += 1
        if named is not None and named == r.get("first"):
            train += 1
        if named is None or (named != r["gold"] and named != r.get("first")):
            neither += 1
        if g.get("state") in ("misread", "refused", "malformed",
                              "unreadable_input"):
            declined += 1
        floor += f["floor"]
    return {"n": n, "follows_page": round(page / n, 4),
            "follows_training": round(train / n, 4),
            "neither": round(neither / n, 4),
            "declined": round(declined / n, 4),
            "floor": round(floor / n, 4)}


def states_cell(rows, get, gold_is_answer=True) -> dict:
    """Where an answer went wrong: unread, refused, or the wrong structure.

    Those are three different problems and only the first is a reading problem,
    so they are counted apart rather than added into one error rate.
    """
    n = len(rows)
    if not n:
        return {"n": 0}
    out = {"n": n, "malformed": 0, "refused": 0, "ran_right": 0,
           "ran_wrong": 0, "unreadable_input": 0}
    for r in rows:
        g = get(r)
        st = g.get("state", "?")
        if st == "ran":
            ok = (g.get("answer", "") == r["gold"]) if gold_is_answer else False
            out["ran_right" if ok else "ran_wrong"] += 1
        elif st in out:
            out[st] += 1
        elif st == "misread":
            out["malformed"] += 1
    for k in ("malformed", "refused", "ran_right", "ran_wrong",
              "unreadable_input"):
        out[k] = round(out[k] / n, 4)
    return out


def refusal_cell(rows, get) -> dict:
    """A control whose only right answer is a refusal, and where it refused."""
    n = len(rows)
    if not n:
        return {"n": 0}
    st, stage = {}, {}
    for r in rows:
        g = get(r)
        s = g.get("state", "?")
        st[s] = st.get(s, 0) + 1
        if s == "misread":
            stage[g.get("stage", "?")] = stage.get(g.get("stage", "?"), 0) + 1
    return {"n": n, "refused": round(sum(v for k, v in st.items()
                                         if k != "ran") / n, 4),
            "states": st, "stage": stage}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/norm/oneshot")
    ap.add_argument("--out", default="results/norm/oneshot/report.json")
    a = ap.parse_args()

    D = a.dir
    sysrows = load(os.path.join(D, "sys.jsonl.gz"))
    ladder_sys = load(os.path.join(D, "ladder_sys.jsonl.gz"))
    rep = {"records": {"sys": os.path.abspath(os.path.join(D, "sys.jsonl.gz")),
                       "ladder_sys": os.path.abspath(
                           os.path.join(D, "ladder_sys.jsonl.gz"))},
           "cells": {}, "acq": {}, "depth": {}, "compose": {},
           "contra": {}, "controls": {}, "ladder": {}, "neural": {},
           "stress": {}, "attack": {}, "states": {}, "deep": {}}

    # ---- the acquisition set, by family and by how many pages were served
    acq = [r for r in sysrows if r["cond"] == "acq"]
    for (fam, npg), rows in sorted(by(acq, lambda r: (r["family"],
                                                      r["n_pages"])).items()):
        for s in SYSTEMS:
            rep["acq"][f"{fam}|pages{npg}|{s}"] = cell(rows, getter(s))

    # ---- the same set split by the frame the pages are written in
    for (fam, split), rows in sorted(by(
            [r for r in acq if r["n_pages"] == 1],
            lambda r: (r["family"], r["split"])).items()):
        for s in ("L", "S1"):
            rep["cells"][f"acq|{fam}|{split}|{s}"] = cell(rows, getter(s))

    # ---- depth, on the items that survive at every depth
    dep = [r for r in sysrows if r["cond"] == "depth"]
    seen = by(dep, lambda r: r["item_key"])
    ns = sorted({r["n"] for r in dep})
    keep = {k for k, v in seen.items() if {r["n"] for r in v} == set(ns)}
    for n in ns:
        rows = [r for r in dep if r["n"] == n]
        al = [r for r in rows if r["item_key"] in keep]
        for s in SYSTEMS:
            rep["depth"][f"n{n}|all|{s}"] = cell(rows, getter(s))
            rep["depth"][f"n{n}|aligned|{s}"] = cell(al, getter(s))
    rep["depth"]["_aligned_items"] = len(keep)
    rep["depth"]["_depths"] = ns

    # ---- composing two acquired operations
    comp = [r for r in sysrows if r["cond"] == "compose"]
    for s in SYSTEMS:
        rep["compose"][s] = cell(comp, getter(s))

    # ---- the page that contradicts the training
    con = [r for r in sysrows if r["cond"] == "contra"]
    conitems = {}
    for line in gzip.open(os.path.join(D, "items.jsonl.gz"), "rt"):
        it = json.loads(line)
        if it["cond"] == "contra":
            conitems[it["id"]] = it
    for r in con:
        r["first"] = conitems[r["id"]]["first"]
        r["second"] = conitems[r["id"]]["second"]
    for fam, rows in sorted(by(con, lambda r: r["family"]).items()):
        for s in SYSTEMS:
            rep["contra"][f"{fam}|{s}"] = contra_cell(rows, getter(s))

    # ---- the two controls
    for cond in ("held_mode", "unstated"):
        rows = [r for r in sysrows if r["cond"] == cond]
        rep["controls"][f"{cond}|L"] = refusal_cell(rows, getter("L"))
        rep["controls"][f"{cond}|L_scored"] = cell(rows, getter("L"))

    # ---- where each system's wrong answers went wrong
    for cond in sorted({r["cond"] for r in sysrows}):
        sub = [r for r in sysrows if r["cond"] == cond]
        rep["states"][f"L|{cond}"] = states_cell(sub, getter("L"))

    # ---- operations past the shapes the reader was written on
    sp = os.path.join(D, "stress_sys.jsonl.gz")
    if os.path.exists(sp):
        srows = load(sp)
        for fam, rows in sorted(by(srows, lambda r: r["family"]).items()):
            for s in SYSTEMS:
                rep["stress"][f"{fam}|{s}"] = cell(rows, getter(s))
        deep = [r for r in srows if r["cond"] == "deep"]
        seen2 = by(deep, lambda r: r["item_key"])
        ns2 = sorted({r["n"] for r in deep})
        keep2 = {k for k, v in seen2.items()
                 if {r["n"] for r in v} == set(ns2)}
        for n in ns2:
            al = [r for r in deep if r["n"] == n and r["item_key"] in keep2]
            for s in SYSTEMS:
                rep["deep"][f"n{n}|{s}"] = cell(al, getter(s))
        rep["deep"]["_aligned_items"] = len(keep2)
        rep["deep"]["_depths"] = ns2
        rep["records"]["stress_sys"] = os.path.abspath(sp)

    # ---- the attacks, carried through from their own record file
    ap_ = os.path.join(D, "attack.json")
    if os.path.exists(ap_):
        rep["attack"] = json.load(open(ap_))
        rep["records"]["attack"] = os.path.abspath(ap_)

    # ---- the ladder: the library on the ladder items, one operation at a time
    inst_of = {}
    for line in gzip.open(os.path.join(D, "ladder_items.jsonl.gz"), "rt"):
        it = json.loads(line)
        inst_of[it["id"]] = it["inst_id"]
    for r in ladder_sys:
        r["inst_id"] = inst_of[r["id"]]
    for iid, rows in sorted(by(ladder_sys, lambda r: r["inst_id"]).items()):
        for s in SYSTEMS:
            rep["ladder"][f"{iid}|{s}"] = cell(rows, getter(s))
    for fam, rows in sorted(by(ladder_sys, lambda r: r["family"]).items()):
        for s in SYSTEMS:
            rep["ladder"][f"L0|{fam}|{s}"] = cell(rows, getter(s))
    rep["ladder"]["all|L"] = cell(ladder_sys, getter("L"))
    rep["ladder"]["all|S1"] = cell(ladder_sys, getter("S1"))
    rep["ladder"]["all|S2"] = cell(ladder_sys, getter("S2"))

    # ---- the ladder: the network at each k, on the same rows
    paths = (sorted(glob.glob(os.path.join(D, "n_*_ladder.jsonl.gz")))
             + sorted(glob.glob(os.path.join(D, "n2_*_ladder.jsonl.gz"))))
    for path in paths:
        base = os.path.basename(path)
        pre = "n2_" if base.startswith("n2_") else "n_"
        tag = base[len(pre):-len("_ladder.jsonl.gz")]
        if pre == "n2_":
            tag = "second_" + tag
        rows = load(path)
        for r in rows:
            r["inst_id"] = inst_of[r["id"]]
        for mode in ("greedy", "sampled"):
            if mode not in rows[0]:
                continue
            rep["neural"][f"{tag}|{mode}|all"] = cell(rows, getter("", mode))
            for iid, sub in sorted(by(rows,
                                      lambda r: r["inst_id"]).items()):
                rep["neural"][f"{tag}|{mode}|{iid}"] = cell(sub,
                                                            getter("", mode))
    # ---- the network on the main item set
    for name in ("n_base_l", "n_family"):
        p = os.path.join(D, f"{name}.jsonl.gz")
        if not os.path.exists(p):
            continue
        rows = load(p)
        for r in rows:
            if r["cond"] == "contra":
                r["first"] = conitems[r["id"]]["first"]
                r["second"] = conitems[r["id"]]["second"]
        for mode in ("greedy", "sampled"):
            if mode not in rows[0]:
                continue
            for cond in sorted({r["cond"] for r in rows}):
                sub = [r for r in rows if r["cond"] == cond]
                if cond == "contra":
                    for fam, ss in sorted(by(sub,
                                             lambda r: r["family"]).items()):
                        rep["neural"][f"{name}|{mode}|contra|{fam}"] = \
                            contra_cell(ss, getter("", mode))
                    continue
                if cond == "depth":
                    for n in sorted({r["n"] for r in sub}):
                        al = [r for r in sub
                              if r["n"] == n and r["item_key"] in keep]
                        rep["neural"][f"{name}|{mode}|depth|n{n}|aligned"] = \
                            cell(al, getter("", mode))
                    continue
                if cond == "acq":
                    for fam, ss in sorted(by(
                            [r for r in sub if r["n_pages"] == 1],
                            lambda r: r["family"]).items()):
                        rep["neural"][f"{name}|{mode}|acq|{fam}|pages1"] = \
                            cell(ss, getter("", mode))
                    continue
                rep["neural"][f"{name}|{mode}|{cond}"] = cell(sub,
                                                              getter("", mode))
        for mode in ("greedy", "sampled"):
            if mode not in rows[0]:
                continue
            for cond in sorted({r["cond"] for r in rows}):
                sub = [r for r in rows if r["cond"] == cond]
                rep["states"][f"{name}|{mode}|{cond}"] = \
                    states_cell(sub, getter("", mode))

    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({"out": os.path.abspath(a.out),
                      "n_cells": sum(len(v) for v in rep.values()
                                     if isinstance(v, dict))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
