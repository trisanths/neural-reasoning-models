"""Attacks on the library result, and operations past what the reader was built on.

A system that answers 1.0000 everywhere is a bug until it survives being
attacked, so this module tries to break the one in `src/norm/opread.py` five
ways and reports what each one did.

    mutate     the same episode twice, differing only in what the last case of
               the definition says. If the answer does not move with it, the
               reader is not reading the clause.
    strip      the definition page taken out. The only correct behaviour is a
               refusal, because nothing then defines the operation.
    rename     the operation renamed on the page and in the question together.
               The answer must not change, because the name is read.
    reword     a directory row changed. The answer must move to the new row.
    stress     operations with three and four clauses, and operations over four
               and five directories. None of these were generated while the
               reader was written; `enumerate_space` was only ever asked for one
               and two clause operations over two and three directories.

`stress` writes its own item file rather than joining the main one, so the item
set the network was decoded on stays exactly what it was.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random

from src.norm import oplang, opitems, opread, opsay
from src.norm.interp import run
from src.norm.lang import def_load, program_json


def _instance(row):
    b = row["inst"]
    return {"spec": oplang.spec_load(b["spec"]),
            "tables": tuple(def_load(t) for t in b["tables"]),
            "keys": list(b["keys"]), "page_name": b["page_name"]}


def _ask(text, fid):
    return opread.answer(text, fid)


# ------------------------------------------------------------- attacks


def attack_mutate(rows, n=200):
    """Move the last case of the definition and see whether the answer moves."""
    out = {"n": 0, "moved": 0, "followed_new": 0, "followed_old": 0,
           "declined": 0, "gold_differs": 0}
    for row in rows[:n]:
        inst = _instance(row)
        spec = inst["spec"]
        alts = [("src", i) for i in range(1, spec.arity + 1)
                if ("src", i) != spec.fallback
                and ("shared", i) != spec.fallback]
        if not alts:
            continue
        new = oplang.OpSpec(spec.name, spec.sources, spec.clauses, alts[0])
        inst2 = dict(inst, spec=new)
        a = opitems.episode(inst, row["fid"], "single", row["ask_key"],
                            mode=row["mode"], def_pos=row["def_pos"])
        b = opitems.episode(inst2, row["fid"], "single", row["ask_key"],
                            mode=row["mode"], def_pos=row["def_pos"])
        if a is None or b is None:
            continue
        out["n"] += 1
        if a["gold"] != b["gold"]:
            out["gold_differs"] += 1
        got = _ask(b["text"], row["fid"])
        if got["state"] != "ran":
            out["declined"] += 1
            continue
        if got["answer"] == b["gold"]:
            out["followed_new"] += 1
        elif got["answer"] == a["gold"]:
            out["followed_old"] += 1
        if a["gold"] != b["gold"] and got["answer"] != a["gold"]:
            out["moved"] += 1
    return out


def attack_strip(rows, n=200):
    """Take the definition page away. A refusal is the only right answer."""
    out = {"n": 0, "refused": 0, "answered": 0, "stages": {}}
    for row in rows[:n]:
        inst = _instance(row)
        pages = [opsay.directory_page(t, row["fid"]) for t in inst["tables"]]
        q = opsay.question_single(inst["spec"], row["fid"], row["ask_key"])
        text = opsay.episode_text(pages, [], q, row["def_pos"])
        got = _ask(text, row["fid"])
        out["n"] += 1
        if got["state"] == "ran":
            out["answered"] += 1
        else:
            out["refused"] += 1
            st = got.get("stage", "?")
            out["stages"][st] = out["stages"].get(st, 0) + 1
    return out


def attack_rename(rows, n=200):
    """Rename the operation on the page and in the question, together."""
    out = {"n": 0, "same_answer": 0, "declined": 0, "other": 0}
    for i, row in enumerate(rows[:n]):
        inst = _instance(row)
        spec = inst["spec"]
        new_name = "zz" + spec.name[::-1]
        inst2 = dict(inst, spec=oplang.OpSpec(new_name, spec.sources,
                                              spec.clauses, spec.fallback))
        a = opitems.episode(inst, row["fid"], "single", row["ask_key"],
                            mode=row["mode"], def_pos=row["def_pos"])
        b = opitems.episode(inst2, row["fid"], "single", row["ask_key"],
                            mode=row["mode"], def_pos=row["def_pos"])
        if a is None or b is None:
            continue
        out["n"] += 1
        got = _ask(b["text"], row["fid"])
        if got["state"] != "ran":
            out["declined"] += 1
        elif got["answer"] == a["gold"]:
            out["same_answer"] += 1
        else:
            out["other"] += 1
    return out


def attack_row(rows, n=200):
    """Change one directory row and see whether the answer follows the row."""
    out = {"n": 0, "followed_new": 0, "followed_old": 0, "declined": 0,
           "gold_differs": 0}
    rng = random.Random(17)
    for row in rows[:n]:
        inst = _instance(row)
        tables = list(inst["tables"])
        vals = sorted({v for t in tables for _, v in t.entries})
        ent = list(tables[0].entries)
        j = [i for i, (k, _) in enumerate(ent) if k == row["ask_key"]]
        if not j or len(vals) < 2:
            continue
        j = j[0]
        alt = [v for v in vals if v != ent[j][1]][0]
        ent[j] = (ent[j][0], alt)
        tables[0] = type(tables[0])(tables[0].name, tuple(ent))
        inst2 = dict(inst, tables=tuple(tables))
        a = opitems.episode(inst, row["fid"], "single", row["ask_key"],
                            mode=row["mode"], def_pos=row["def_pos"])
        b = opitems.episode(inst2, row["fid"], "single", row["ask_key"],
                            mode=row["mode"], def_pos=row["def_pos"])
        if a is None or b is None:
            continue
        out["n"] += 1
        if a["gold"] != b["gold"]:
            out["gold_differs"] += 1
        got = _ask(b["text"], row["fid"])
        if got["state"] != "ran":
            out["declined"] += 1
        elif got["answer"] == b["gold"]:
            out["followed_new"] += 1
        elif got["answer"] == a["gold"]:
            out["followed_old"] += 1
    return out


# ---------------------------------------------------------------- stress


STRESS = (("c3", 3, 3), ("c4", 4, 3), ("a4", 1, 4), ("a5", 1, 5))


def build_stress(seed0=515151, per=40, keys_asked=3):
    """Operations past the shapes the reader was developed on."""
    rows, drops = [], {}
    pool = opitems.frame_pool()
    si = 0
    for name, n_clauses, arity in STRESS:
        got = 0
        for sk in oplang.sample_clauses(arity, n_clauses, per * 4,
                                        seed0 + hash(name) % 9973):
            if got >= per:
                break
            si += 1
            fid, split = pool[(si * 23) % len(pool)]
            inst = _stress_instance(sk, fid, seed0 + si * 4441, arity)
            if inst is None:
                drops[name] = drops.get(name, 0) + 1
                continue
            if oplang.is_degenerate(inst["spec"], inst["tables"],
                                    inst["keys"]):
                continue
            got += 1
            mode = opsay.READ_MODES[si % len(opsay.READ_MODES)]
            for ki, key in enumerate(inst["keys"][:keys_asked]):
                e = opitems.episode(inst, fid, "single", key, mode=mode,
                                    def_pos=("first", "last")[si % 2])
                if e is None:
                    continue
                e.update({"cond": "stress", "family": name, "fid": fid,
                          "split": split, "skeleton": repr(sk),
                          "arity": arity, "n_clauses": n_clauses,
                          "id": f"stress/{name}/{si}/{ki}",
                          "item_key": f"stress/{name}/{si}/{ki}"})
                rows.append(e)
    return rows, drops


def _stress_instance(sk, fid, seed, arity):
    from src.norm import gen
    rng = random.Random(seed)
    lex = gen.lexicon_for(fid, rng)
    keys = lex.words(opitems.N_KEYS)
    values = lex.words(max(4, arity + 1))
    names = [lex.name() for _ in range(arity)]
    clauses_sk, fb_sk = sk
    n_words = (sum(1 for _, r in clauses_sk if r[0] == "word")
               + (1 if fb_sk[0] == "word" else 0))
    words = lex.words(n_words) if n_words else []
    spec = oplang.build_spec(sk, lex.word(), names, words)
    tables = oplang.make_tables(rng, names, keys, values, plant=True)
    if not oplang.exercised(tables, keys):
        return None
    return {"spec": spec, "tables": tables, "keys": keys, "lex": lex,
            "page_name": lex.name()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="results/norm/oneshot/items.jsonl.gz")
    ap.add_argument("--dir", default="results/norm/oneshot")
    ap.add_argument("--n", type=int, default=300)
    a = ap.parse_args()

    items = [json.loads(l) for l in gzip.open(a.items, "rt")]
    acq = [r for r in items if r["cond"] == "acq" and r["n_pages"] == 1]
    out = {"items": os.path.abspath(a.items), "n_acq": len(acq),
           "mutate": attack_mutate(acq, a.n),
           "strip": attack_strip(acq, a.n),
           "rename": attack_rename(acq, a.n),
           "row": attack_row(acq, a.n)}

    rows, drops = build_stress()
    path = os.path.join(a.dir, "stress_items.jsonl.gz")
    with gzip.open(path, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    out["stress"] = {"n_items": len(rows), "drops": drops,
                     "path": os.path.abspath(path),
                     "by_family": {f: sum(1 for r in rows
                                          if r["family"] == f)
                                   for f, _, _ in STRESS}}
    with open(os.path.join(a.dir, "attack.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
