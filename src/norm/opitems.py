"""The item sets for the acquisition measurement.

One episode is a set of directory pages written by the corpus frame, one or
more pages defining an operation, and a question that names the operation. The
gold answer is what `src/norm/interp.py` returns for the program the generator
built, and the option set is what that program can return over the episode's
own key set, so the chance floor is 1 over the size of that set and is measured
rather than assumed.

Six conditions are built, and they are never pooled:

    acq        every operation statable with one clause, 165 of them, plus a
               sample of the two clause space, each with one, two and four
               definition pages over the same question items
    depth      one operation applied 1, 2, 4, 8 and 16 times over, on
               directories closed under their own values so the answer can be
               fed back in
    compose    two operations from two pages, applied one after the other
    contra     a page whose operation contradicts what the trained model was
               shown: pages shaped exactly like the corpus precedence pages,
               with a definition saying the second directory wins
    held_mode  the same episodes with the definition page in the wording mode
               the reader was never written for
    unstated   a question naming an operation no page defines, which has no
               answer and must be refused rather than guessed
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random

from src.norm import gen, ndata, oplang, opsay
from src.norm.interp import run
from src.norm.lang import def_json, program_json

N_KEYS = 8
N_ASK = 5
KEY_SEED = 20260831

_FRAMES = None


def frame_pool():
    """Every frame with the split it belongs to, in a fixed order."""
    global _FRAMES
    if _FRAMES is None:
        sp = ndata.split_frames()
        out = []
        for split in ("train", "qframe", "lexicon", "mode", "mixed"):
            for fid in sorted(sp[split]):
                out.append((fid, split))
        _FRAMES = out
    return _FRAMES


def draw_instance(skeleton, fid: str, seed: int, closed: bool = False,
                  n_keys: int = N_KEYS, keys=None, taken=()):
    """One operation, its directories and its keys, drawn for one frame.

    `keys` is passed when a second operation has to read the answers of a
    first, which is what makes a composition of two acquired operations
    possible at all.
    """
    rng = random.Random(seed)
    lex = gen.lexicon_for(fid, rng)
    for w in taken:
        lex.taken.add(w)
    clauses_sk, fb_sk = skeleton
    n_sources = _arity_of(skeleton)
    keys = list(keys) if keys is not None else lex.words(n_keys)
    values = list(keys) if closed else lex.words(4)
    names = [lex.name() for _ in range(n_sources)]
    n_words = sum(1 for _, r in clauses_sk if r[0] == "word") \
        + (1 if fb_sk[0] == "word" else 0)
    # A stated word has to be a key when the directories must stay closed
    # under their own values, or the answer could not be fed back in.
    if n_words and closed:
        words = [keys[(i * 2 + 1) % len(keys)] for i in range(n_words)]
    else:
        words = lex.words(n_words) if n_words else []
    spec = oplang.build_spec(skeleton, lex.word(), names, words)
    tables = None
    for _ in range(40):
        cand = oplang.make_tables(rng, names, keys, values)
        if oplang.exercised(cand, keys):
            tables = cand
            break
    if tables is None:
        return None
    return {"spec": spec, "tables": tables, "keys": keys, "lex": lex,
            "page_name": lex.name(), "rng": rng}


_arity_of = oplang.arity_of


def _defs_pages(inst, fid, mode, n_pages):
    """n pages stating the one operation, each in its own wording mode.

    Two pages of the same operation are two wordings of it, not two operations,
    which is what makes the second page carry no information the first did not.
    """
    modes = [mode]
    others = [m for m in opsay.READ_MODES if m != mode]
    while len(modes) < n_pages:
        modes.append(others[(len(modes) - 1) % len(others)])
    out = []
    for i, m in enumerate(modes):
        nm = inst["page_name"] if i == 0 else inst["lex"].name()
        out.append(opsay.definition_page(inst["spec"], fid, m, nm))
    return out


def episode(inst, fid: str, kind: str, key: str, *, mode="protocol",
            n_pages=1, def_pos="last", n=1, second=None, distractor=None,
            op_name=None):
    """One item: its text, its gold answer, its option set, its floor."""
    spec = inst["spec"]
    tables = inst["tables"]
    keys = inst["keys"]
    if kind == "single":
        make = lambda k: oplang.program_single(spec, tables, k)
        q = opsay.question_single(spec, fid, key)
    elif kind == "iterate":
        make = lambda k: oplang.program_iterate(spec, tables, k, n)
        q = opsay.question_iterate(spec, fid, key, n)
    elif kind == "compose":
        s2, t2 = second["spec"], second["tables"]
        make = lambda k: oplang.program_compose(spec, tables, s2, t2, k)
        q = opsay.question_compose(spec, s2, fid, key)
    elif kind == "unstated":
        make = lambda k: oplang.program_single(spec, tables, k)
        q = opsay.question_single(
            oplang.OpSpec(op_name, spec.sources, spec.clauses, spec.fallback),
            fid, key)
    else:
        raise ValueError(kind)
    prog = make(key)
    r = run(prog)
    if not r.ok:
        return None
    options = oplang.options_for(make, keys)
    if len(options) < 2 or r.text not in options:
        return None
    pages = [opsay.directory_page(t, fid) for t in tables]
    if kind == "compose":
        pages += [opsay.directory_page(t, fid) for t in second["tables"]]
    if distractor is not None:
        pages.append(opsay.directory_page(distractor, fid))
    defs = _defs_pages(inst, fid, mode, n_pages)
    if kind == "compose":
        defs = defs + _defs_pages(second, fid, mode, 1)
    text = opsay.episode_text(pages, defs, q, def_pos)
    inst_blob = {"spec": oplang.spec_json(spec),
                 "tables": [def_json(t) for t in tables],
                 "keys": list(keys), "page_name": inst["page_name"]}
    if kind == "compose":
        inst_blob["second"] = {"spec": oplang.spec_json(second["spec"]),
                               "tables": [def_json(t)
                                          for t in second["tables"]],
                               "keys": list(second["keys"]),
                               "page_name": second["page_name"]}
    return {"text": text, "gold": r.text, "options": options,
            "floor": 1.0 / len(options), "prog": program_json(prog),
            "question": q, "n_pages": n_pages, "mode": mode, "kind": kind,
            "def_pos": def_pos, "depth": len(prog.steps), "n": n,
            "ask_key": key, "inst": inst_blob}


# ------------------------------------------------------------ the sets


def skeletons():
    """The operation space this lane measures over.

    Every distinct operation statable with one clause, and a sample of the two
    clause space. A family label is the operation's arity and clause count, so
    a cell is never a mix of two and three reading operations.
    """
    one = [(f"a{oplang.arity_of(s)}c1", s)
           for s in oplang.distinct_space(1)]
    two = [(f"a{oplang.arity_of(s)}c2", s)
           for s in oplang.sample_space(3, 2, 120, 4242)]
    return one, two


def build_acq(seed0, n_pages_list=(1, 2, 4)):
    rows, dropped = [], {"instance": 0, "degenerate": 0, "item": 0}
    pool = frame_pool()
    one, two = skeletons()
    allsk = one + two
    for si, (family, sk) in enumerate(allsk):
        fid, split = pool[(si * 7) % len(pool)]
        inst = draw_instance(sk, fid, seed0 + si * 9173)
        if inst is None:
            dropped["instance"] += 1
            continue
        if oplang.is_degenerate(inst["spec"], inst["tables"], inst["keys"]):
            dropped["degenerate"] += 1
            continue
        mode = opsay.READ_MODES[si % len(opsay.READ_MODES)]
        pos = ("first", "last")[si % 2]
        for ki, key in enumerate(inst["keys"][:N_ASK]):
            for npg in n_pages_list:
                e = episode(inst, fid, "single", key, mode=mode,
                            n_pages=npg, def_pos=pos)
                if e is None:
                    dropped["item"] += 1
                    continue
                e.update({"cond": "acq", "family": family, "fid": fid,
                          "split": split, "skeleton": repr(sk),
                          "arity": _arity_of(sk),
                          "id": f"acq/{family}/{si}/{ki}/p{npg}",
                          "item_key": f"acq/{family}/{si}/{ki}"})
                rows.append(e)
    return rows, dropped


def build_depth(seed0, depths=(1, 2, 4, 8, 16), reps=4):
    """One operation applied n times over, on directories closed under
    their own values.

    Most agreement operations whose every result is a directory read are
    extensionally one of those directories, so they are dropped: acquiring an
    operation that computes a trained one proves nothing. What survives is
    counted here and reported.
    """
    rows, dropped = [], {"instance": 0, "degenerate": 0, "item": 0}
    pool = frame_pool()
    closed = list(oplang.distinct_space(1))
    rng = random.Random(seed0)
    rng.shuffle(closed)
    si = 0
    for rep in range(reps):
        for sk in closed:
            si += 1
            fid, split = pool[(si * 31) % len(pool)]
            inst = draw_instance(sk, fid, seed0 + si * 7717, closed=True)
            if inst is None:
                dropped["instance"] += 1
                continue
            if oplang.is_degenerate(inst["spec"], inst["tables"],
                                    inst["keys"]):
                dropped["degenerate"] += 1
                continue
            mode = opsay.READ_MODES[si % len(opsay.READ_MODES)]
            for ki, key in enumerate(inst["keys"][:3]):
                for n in depths:
                    e = episode(inst, fid, "iterate", key, mode=mode, n=n)
                    if e is None:
                        dropped["item"] += 1
                        continue
                    e.update({"cond": "depth", "family": f"n{n}", "fid": fid,
                              "split": split, "skeleton": repr(sk),
                              "arity": _arity_of(sk),
                              "id": f"depth/{si}/{ki}/n{n}",
                              "item_key": f"depth/{si}/{ki}"})
                    rows.append(e)
    return rows, dropped


def build_compose(seed0, n_pairs=80):
    """Two operations from two pages, the second reading the first's answers."""
    rows, dropped = [], {"instance": 0, "degenerate": 0, "item": 0}
    pool = frame_pool()
    closed = oplang.distinct_space(1)
    rng = random.Random(seed0 + 5)
    si = 0
    while len(rows) < n_pairs * 3 and si < n_pairs * 12:
        si += 1
        fid, split = pool[(si * 53) % len(pool)]
        a = draw_instance(rng.choice(closed), fid, seed0 + si * 3319,
                          closed=True)
        if a is None:
            dropped["instance"] += 1
            continue
        b = draw_instance(rng.choice(closed), fid, seed0 + si * 3319 + 11,
                          closed=True, keys=a["keys"],
                          taken=a["lex"].taken)
        if b is None:
            dropped["instance"] += 1
            continue
        if a["spec"].name == b["spec"].name:
            continue
        if {t.name for t in b["tables"]} & {t.name for t in a["tables"]}:
            continue
        # The second operation reads the first one's answers, so its
        # directories are keyed by the first one's key set and its stated
        # words are drawn from it too.
        if not oplang.exercised(b["tables"], a["keys"]):
            continue
        if (oplang.is_degenerate(a["spec"], a["tables"], a["keys"])
                or oplang.is_degenerate(b["spec"], b["tables"], b["keys"])):
            dropped["degenerate"] += 1
            continue
        mode = opsay.READ_MODES[si % len(opsay.READ_MODES)]
        for ki, key in enumerate(a["keys"][:3]):
            e = episode(a, fid, "compose", key, mode=mode, second=b)
            if e is None:
                dropped["item"] += 1
                continue
            e.update({"cond": "compose", "family": "two_ops", "fid": fid,
                      "split": split, "skeleton": "compose",
                      "arity": a["spec"].arity, "id": f"compose/{si}/{ki}",
                      "item_key": f"compose/{si}/{ki}"})
            rows.append(e)
    return rows, dropped


CONTRA = {
    "page_second": ((( ("all_same",), ("shared", 1)),), ("src", 2)),
    "page_first": ((( ("all_same",), ("shared", 1)),), ("src", 1)),
}


def build_contra(seed0, n_inst=100):
    """Pages shaped like the trained precedence shape, with the page dissenting.

    Both directions are built. A system that answers the first directory under
    both is following what it was trained on; a system that answers what the
    page says under both is following the page. One direction alone cannot tell
    those apart, which is why neither is reported alone.
    """
    rows, dropped = [], {"instance": 0, "item": 0}
    pool = frame_pool()
    for si in range(n_inst):
        fid, split = pool[(si * 17) % len(pool)]
        for name, sk in CONTRA.items():
            inst = draw_instance(sk, fid, seed0 + si * 2657)
            if inst is None:
                dropped["instance"] += 1
                continue
            mode = opsay.READ_MODES[si % len(opsay.READ_MODES)]
            for ki, key in enumerate(inst["keys"][:3]):
                d = {t.name: dict(t.entries) for t in inst["tables"]}
                first = d[inst["tables"][0].name][key]
                secondv = d[inst["tables"][1].name][key]
                if first == secondv:
                    continue
                e = episode(inst, fid, "single", key, mode=mode)
                if e is None:
                    dropped["item"] += 1
                    continue
                e.update({"cond": "contra", "family": name, "fid": fid,
                          "split": split, "skeleton": repr(sk), "arity": 2,
                          "first": first, "second": secondv,
                          "id": f"contra/{name}/{si}/{ki}",
                          "item_key": f"contra/{si}/{ki}"})
                rows.append(e)
    return rows, dropped


def build_controls(seed0, n_inst=60):
    """Two refusals that must stay refusals, and one wording the reader lacks."""
    rows = []
    pool = frame_pool()
    one, _ = skeletons()
    for si, (family, sk) in enumerate(one[:n_inst]):
        fid, split = pool[(si * 11) % len(pool)]
        inst = draw_instance(sk, fid, seed0 + si * 6113)
        if inst is None:
            continue
        for key in inst["keys"][:2]:
            e = episode(inst, fid, "single", key, mode=opsay.HELD_MODE)
            if e is not None:
                e.update({"cond": "held_mode", "family": opsay.HELD_MODE,
                          "fid": fid, "split": split, "skeleton": repr(sk),
                          "arity": _arity_of(sk),
                          "id": f"held/{si}/{key}",
                          "item_key": f"held/{si}/{key}"})
                rows.append(e)
            e = episode(inst, fid, "unstated", key,
                        mode=opsay.READ_MODES[si % 3],
                        op_name=inst["lex"].word())
            if e is not None:
                e.update({"cond": "unstated", "family": "no_such_op",
                          "fid": fid, "split": split, "skeleton": repr(sk),
                          "arity": _arity_of(sk), "gold": "",
                          "id": f"unstated/{si}/{key}",
                          "item_key": f"unstated/{si}/{key}"})
                rows.append(e)
    return rows, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/norm/oneshot/items.jsonl.gz")
    ap.add_argument("--seed", type=int, default=20260831)
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    rows, drops = [], {}
    for name, fn in (("acq", build_acq), ("depth", build_depth),
                     ("compose", build_compose), ("contra", build_contra),
                     ("controls", build_controls)):
        got, d = fn(a.seed)
        rows.extend(got)
        drops[name] = d
        print(f"{name:10s} {len(got):6d} {json.dumps(d)}", flush=True)
    with gzip.open(a.out, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    one, two = skeletons()
    meta = {"n_items": len(rows), "seed": a.seed, "drops": drops,
            "space": {"one_clause_distinct": len(one),
                      "one_clause_arity2": sum(1 for f, _ in one
                                               if f.startswith("a2")),
                      "one_clause_arity3": sum(1 for f, _ in one
                                               if f.startswith("a3")),
                      "two_clause_sampled": len(two),
                      "two_clause_total": len(oplang.enumerate_space(3, 2))},
            "conds": sorted({r["cond"] for r in rows}),
            "n_by_cond": {c: sum(1 for r in rows if r["cond"] == c)
                          for c in sorted({r["cond"] for r in rows})},
            "out": os.path.abspath(a.out)}
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
