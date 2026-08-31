"""The operator families: typed operators read out of an invented textbook.

`src/corpus/relations.py` states rules as tables and bands. `src/skillacq/
systems.py` states them as arithmetic, which is the other half of what the
existing families express and what the `OpDef` definition kind is for:

    binary_op   one invented infix operator over two integers, plus a stated
                reduction modulus and a stated associativity, so a run of two
                needs the notation as well as the arithmetic
    units       two stated conversion factors that compose, and a sum question
                whose plan calls two distinct operators and then adds
    procedure   one operator carrying several simultaneous conditions, a bonus
                and a penalty that both apply when both hold, and a second
                operator that turns the score into a stated verdict

Episodes come from `src/skillacq/systems.py:generate_episode` unchanged,
including its distractor page from another family and its rejection of
answers that could be copied out of the question. The reader below is handed
the pages and the question text and nothing else: the glyph, the coefficients,
the modulus, the associativity, the conversion factors, the bonus, the penalty
and the cutoff are all read off the page.

`solve_for` items are counted and excluded. They ask for an inverse of the
operator over an unstated domain, which is a search rather than a composition,
and this language does not express a search. Saying so is the point of having
a language: what it cannot say, it does not pretend to say.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter

from src.norm.interp import run
from src.norm.lang import Lit, OpDef, Program, Ref, Step
from src.opgraph.opdef import parse_expr
from src.skillacq.systems import generate_episode

FAMILIES = ("binary_op", "units", "procedure")


def _prog(defs, inputs, steps, answer):
    return Program(tuple(defs), tuple(inputs), tuple(steps), answer)


# ------------------------------------------------------------- binary_op

RE_GLYPH = re.compile(r"introduces a single operator written (\S+)\.")
RE_MOD = re.compile(r"is reduced modulo (\d+)\.")
RE_ASSOC = re.compile(r"the operator associates (left to right|right to left)")
RE_LIN = re.compile(r"multiply x by (\d+), multiply y by (\d+), add the two "
                    r"products, then add (\d+)\.")
RE_SQ = re.compile(r"square x, then add (\d+) times y, then subtract (\d+)\.")
RE_DIFF = re.compile(r"subtract y from x, multiply the difference by (\d+), "
                     r"then add (\d+)\.")


def read_binary_op(pages: str):
    g = RE_GLYPH.search(pages)
    if not g:
        return None, None, "no operator glyph on the pages"
    glyph = g.group(1)
    m = RE_MOD.search(pages)
    mod = int(m.group(1)) if m else 0
    a = RE_ASSOC.search(pages)
    if not a:
        return None, None, "the pages do not state the associativity"
    assoc = "left" if a.group(1) == "left to right" else "right"
    lin, sq, df = RE_LIN.search(pages), RE_SQ.search(pages), RE_DIFF.search(pages)
    if lin:
        body = f"(+ (* {lin.group(1)} x) (* {lin.group(2)} y) {lin.group(3)})"
    elif sq:
        body = f"(- (+ (* x x) (* {sq.group(1)} y)) {sq.group(2)})"
    elif df:
        body = f"(+ (* {df.group(1)} (- x y)) {df.group(2)})"
    else:
        return None, None, "no rule sentence on the pages"
    if mod:
        body = f"(% {body} {mod})"
    return OpDef("op", ("x", "y"), parse_expr(body)), (glyph, assoc), None


def binary_op_program(op, glyph, assoc, text):
    esc = re.escape(glyph)
    m = re.fullmatch(rf"Evaluate (-?\d+) {esc} (-?\d+) {esc} (-?\d+)\.", text)
    if m:
        x, y, z = (int(v) for v in m.groups())
        ins = (("x", x), ("y", y), ("z", z))
        if assoc == "left":
            steps = (Step("t1", "call", ("op", Ref("x"), Ref("y"))),
                     Step("t2", "call", ("op", Ref("t1"), Ref("z"))))
        else:
            steps = (Step("t1", "call", ("op", Ref("y"), Ref("z"))),
                     Step("t2", "call", ("op", Ref("x"), Ref("t1"))))
        return _prog([op], ins, steps, "t2"), None
    m = re.fullmatch(rf"Evaluate (-?\d+) {esc} (-?\d+)\.", text)
    if m:
        x, y = (int(v) for v in m.groups())
        return _prog([op], (("x", x), ("y", y)),
                     (Step("t1", "call", ("op", Ref("x"), Ref("y"))),), "t1"), None
    if " y equals " in text:
        return None, "solve_for"
    return None, "the question does not read"


# ----------------------------------------------------------------- units

RE_UNITS = re.compile(r"The smallest is the (\w+)\. Next is the (\w+)\. "
                      r"The largest is the (\w+)\.")
RE_CONV = re.compile(r"One (\w+) equals (\d+) (\w+)\. One (\w+) equals "
                     r"(\d+) (\w+)\.")


def read_units(pages: str):
    u = RE_UNITS.search(pages)
    c = RE_CONV.search(pages)
    if not u or not c:
        return None, None, "the pages do not state the units"
    base, mid, big = u.groups()
    if len({base, mid, big}) < 3:
        # UnitSystem draws its three unit names independently and repeats one
        # in 0.0072 of draws. The page is then circular, "One A equals k B.
        # One B equals m A.", and a question naming the repeated word does not
        # say which unit it means.
        return None, None, "the pages give two units the same name"
    if c.group(1) != mid or c.group(3) != base or c.group(4) != big:
        return None, None, "the conversions do not name the stated units"
    k1, k2 = int(c.group(2)), int(c.group(5))
    defs = [OpDef("mid_to_base", ("n",), parse_expr(f"(* {k1} n)")),
            OpDef("big_to_base", ("n",), parse_expr(f"(* {k1 * k2} n)"))]
    return defs, (base, mid, big), None


def units_program(defs, base, mid, big, text):
    m = re.fullmatch(rf"How many {base} are (-?\d+) (\w+)\?", text)
    if m:
        q, unit = int(m.group(1)), m.group(2)
        if unit == mid:
            op = "mid_to_base"
        elif unit == big:
            op = "big_to_base"
        elif unit == base:
            return _prog(defs, (("x", q),), (), "x"), None
        else:
            return None, "the question names an unstated unit"
        return _prog(defs, (("x", q),),
                     (Step("t1", "call", (op, Ref("x"))),), "t1"), None
    m = re.fullmatch(rf"A distance is (-?\d+) {mid} plus (-?\d+) {big}\. "
                     rf"Express the total in {base}\.", text)
    if m:
        q1, q2 = int(m.group(1)), int(m.group(2))
        steps = (Step("t1", "call", ("mid_to_base", Ref("x"))),
                 Step("t2", "call", ("big_to_base", Ref("y"))),
                 Step("t3", "add", (Ref("t1"), Ref("t2"))))
        return _prog(defs, (("x", q1), ("y", q2)), steps, "t3"), None
    return None, "the question does not read"


# ------------------------------------------------------------- procedure

RE_ADJ = re.compile(r"If the application is marked (\w+), add (\d+) to the "
                    r"value\. If the application is flagged, subtract (\d+)\.")
RE_CUT = re.compile(r"An application is accepted when its adjusted value is "
                    r"at least (\d+)\.")
RE_ATTR = re.compile(r"Each application carries a (\w+) value, a whole number\.")


def read_procedure(pages: str):
    adj, cut, at = (RE_ADJ.search(pages), RE_CUT.search(pages),
                    RE_ATTR.search(pages))
    if not adj or not cut or not at:
        return None, None, "the pages do not state the procedure"
    mark, bonus, pen = adj.group(1), int(adj.group(2)), int(adj.group(3))
    cutoff = int(cut.group(1))
    # One operator, both conditions, both applying when both hold. The
    # precondition is the page's own statement that the value is a whole
    # number that the assessment begins from.
    score = OpDef("score", ("base", "marked", "flagged"),
                  parse_expr(f"(+ base (if marked {bonus} 0) "
                             f"(if flagged {-pen} 0))"),
                  pre=(parse_expr("(>= base 0)"),))
    verdict = OpDef("verdict", ("s",),
                    parse_expr(f"(if (>= s {cutoff}) 'accepted 'refused)"))
    return [score, verdict], (at.group(1), mark), None


def procedure_program(defs, attr, mark, text):
    m = re.match(rf"An application has a {attr} value of (-?\d+)\. "
                 rf"It is (not marked {mark}|marked {mark})\. "
                 rf"It is (not flagged|flagged)\. (.*)$", text)
    if not m:
        return None, "the question does not read"
    base = int(m.group(1))
    marked = not m.group(2).startswith("not")
    flagged = not m.group(3).startswith("not")
    tail = m.group(4)
    ins = (("base", base), ("marked", marked), ("flagged", flagged))
    s = Step("t1", "call", ("score", Ref("base"), Ref("marked"),
                            Ref("flagged")))
    if tail == "What is its adjusted value?":
        return _prog(defs, ins, (s,), "t1"), None
    if tail == "Is it accepted or refused?":
        return _prog(defs, ins,
                     (s, Step("t2", "call", ("verdict", Ref("t1")))), "t2"), None
    return None, "the question does not read"


# -------------------------------------------------------------- the lane


def structure_for(family: str, pages: str, text: str):
    if family == "binary_op":
        op, meta, why = read_binary_op(pages)
        if op is None:
            return None, why
        return binary_op_program(op, meta[0], meta[1], text)
    if family == "units":
        defs, meta, why = read_units(pages)
        if defs is None:
            return None, why
        return units_program(defs, *meta, text)
    if family == "procedure":
        defs, meta, why = read_procedure(pages)
        if defs is None:
            return None, why
        return procedure_program(defs, meta[0], meta[1], text)
    return None, f"no reader for {family}"


def decide_cell(episodes: int, seed0: int, problems: int) -> dict:
    """The `decide` questions, which `generate_episode` never lets through.

    Every `decide` item states its own answer in the question, "Is it accepted
    or refused?", so `_answer_is_copyable` rejects all of them and the family
    only ever emits `score` items in a built episode. They are the two
    operator plan for this family, so they are run here against
    `ProcedureSystem.eligible`, which is the same reference implementation the
    generator would have used, and reported in their own cell.
    """
    import random as _r
    from src.skillacq.systems import ProcedureSystem
    c = Counter()
    for s in range(seed0, seed0 + episodes):
        sysm = ProcedureSystem(_r.Random(s))
        pages = "\n\n".join(sysm.describe())
        for q in sysm.problems(_r.Random(s + 1), problems):
            if q["kind"] != "decide":
                continue
            c["n"] += 1
            prog, why = structure_for("procedure", pages, q["text"])
            if prog is None:
                c["unread"] += 1
                continue
            r = run(prog)
            c["refused"] += int(not r.ok)
            c["exact"] += int(r.text == q["answer"])
            c["distinct_ops"] += prog.distinct_ops()
            c["distinct_operators"] += prog.distinct_operators()
            c["steps"] += len(prog.steps)
    return {"n": c["n"],
            "exact": round(c["exact"] / c["n"], 6) if c["n"] else None,
            "unread": c["unread"], "refused": c["refused"],
            "out_of_scope": 0,
            "mean_steps": round(c["steps"] / c["n"], 3) if c["n"] else None,
            "mean_distinct_ops": (round(c["distinct_ops"] / c["n"], 3)
                                  if c["n"] else None),
            "mean_distinct_operators": (
                round(c["distinct_operators"] / c["n"], 3) if c["n"] else None),
            "n_read": c["n"] - c["unread"],
            "exact_on_read": (round(c["exact"] / (c["n"] - c["unread"]), 6)
                              if c["n"] - c["unread"] else None),
            "note": ("built straight from ProcedureSystem; generate_episode "
                     "rejects every one of these because the question states "
                     "both candidate answers")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/norm/skillacq")
    ap.add_argument("--episodes", type=int, default=400)
    ap.add_argument("--problems", type=int, default=8)
    ap.add_argument("--seed0", type=int, default=910000)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    cells = {}
    reasons = Counter()
    t0 = time.time()
    with open(os.path.join(args.out, "records.jsonl"), "w") as sink:
        for family in FAMILIES:
            by_kind = {}
            for s in range(args.seed0, args.seed0 + args.episodes):
                ep = generate_episode(s, family=family,
                                      n_problems=args.problems)
                pages = "\n\n".join(ep.textbook)
                for p in ep.problems:
                    prog, why = structure_for(family, pages, p["text"])
                    kind = p["kind"]
                    c = by_kind.setdefault(kind, Counter())
                    if why == "solve_for":
                        c["out_of_scope"] += 1
                        continue
                    c["n"] += 1
                    if prog is None:
                        c["unread"] += 1
                        reasons[f"{family}: {why}"[:100]] += 1
                        ans, ok = "", False
                    else:
                        r = run(prog)
                        ans, ok = r.text, r.ok
                        if not ok:
                            c["refused"] += 1
                            reasons[f"{family}: {r.reason}"[:100]] += 1
                    c["exact"] += int(ans == p["answer"])
                    c["distinct_ops"] += (0 if prog is None
                                          else prog.distinct_ops())
                    c["distinct_operators"] += (0 if prog is None
                                               else prog.distinct_operators())
                    c["read"] += int(prog is not None)
                    c["exact_read"] += int(prog is not None
                                           and ans == p["answer"])
                    sink.write(json.dumps(
                        {"family": family, "kind": kind, "seed": s,
                         "qid": p["qid"], "gold": p["answer"],
                         "answer": ans, "exact": ans == p["answer"],
                         "steps": 0 if prog is None else len(prog.steps),
                         "reason": "" if prog is not None and ok else (why or "")}
                    ) + "\n")
            for kind, c in sorted(by_kind.items()):
                cells[f"{family}/{kind}"] = {
                    "n": c["n"], "exact": round(c["exact"] / c["n"], 6) if c["n"] else None,
                    "unread": c["unread"], "refused": c["refused"],
                    "out_of_scope": c["out_of_scope"],
                    "mean_distinct_ops": (round(c["distinct_ops"] / c["n"], 3)
                                          if c["n"] else None),
                    "mean_distinct_operators": (
                        round(c["distinct_operators"] / c["n"], 3)
                        if c["n"] else None),
                    "n_read": c["read"],
                    "exact_on_read": (round(c["exact_read"] / c["read"], 6)
                                      if c["read"] else None),
                }
    cells["procedure/decide_rejected"] = decide_cell(
        args.episodes, args.seed0, args.problems)
    out = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "episodes_per_family": args.episodes,
        "seconds": round(time.time() - t0, 1),
        "note": ("gold is src/skillacq/systems.py own reference answer; the "
                 "reader is handed the textbook pages and the question text"),
        "per_family_kind": cells,
        "reasons": reasons.most_common(10),
        "records": os.path.abspath(os.path.join(args.out, "records.jsonl")),
    }
    with open(os.path.join(args.out, "summary.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
