"""The transposed-rule test, rebuilt.

`src/audit/VERDICT.md` check 8: take a style 0 binary operator page, keep the
glyph, the constants, the modulus and the associativity sentence, swap the two
operand roles inside the rule sentence, and recompute the page's own worked
examples so the page states the swapped rule twice. A model that reads the page
answers with the swapped rule. A model that matched a template answers with the
canonical binding the template always had. On record: 0 of 678 toward the page,
678 of 678 toward training.

Two conditions, because generation and preference are different measurements
and the first can be empty for reasons that have nothing to do with reading.

  gen   the retrieval loop of `src/rl/env.py`, page served, answer graded by
        which candidate it names under digit boundaries
  mc    the page in the prompt, candidates scored by summed negative log
        likelihood with `src/evals/mc.py`, so a policy that generates nothing
        usable still expresses a preference

Both carry the same five candidates and the same 0.200 floor. Reported
alongside is a trivial program: the prose reader of `src/audit/refprose.py`
extended with the four transposed rule sentences, which reads the swapped page
and runs the plan. If the program follows the page and the model does not, the
page carries the answer and the model is not reading it.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re

from src.opgraph.invent import make_world, seq_flat
from src.opgraph.opdef import Call, Operator, Var
from src.opgraph.plan import run_plan

SEED0 = 730_000_000          # outside every range RESERVED_SEED_RANGES names
DEPTHS = (1, 2, 3, 4, 8)
N_CANDIDATES = 5


# ------------------------------------------------------------- transposition


def swap_xy(e):
    """The same expression with the two parameter roles exchanged."""
    if isinstance(e, Var):
        if e.name == "x":
            return Var("y")
        if e.name == "y":
            return Var("x")
        return e
    if isinstance(e, Call):
        return Call(e.head, tuple(swap_xy(a) for a in e.args))
    return e


_XY = re.compile(r"(?<![A-Za-z])([xy])(?![A-Za-z])")


def _swap_words(s: str) -> str:
    return _XY.sub(lambda m: "y" if m.group(1) == "x" else "x", s)


_WORKED = re.compile(r"^Worked example: (-?\d+) (\S+) (-?\d+) = (-?\d+)\.$", re.M)


def transpose_page(page):
    """Return (transposed page text, transposed operator).

    The rule line is the one line that opens `To evaluate x G y,`. Everything
    before its first comma is left alone, so the page still declares the same
    operand order; only the roles the rule binds them to move. The worked
    examples are recomputed, so the page asserts the swapped rule twice.
    """
    op = page.ops[0]
    t_op = Operator(op.symbol, op.params, swap_xy(op.body),
                    examples=tuple((a, None) for a, _ in op.examples),
                    assoc=op.assoc)
    t_op = Operator(op.symbol, op.params, swap_xy(op.body),
                    examples=tuple((a, t_op(*a)) for a, _ in op.examples),
                    assoc=op.assoc)

    lines = page.text.split("\n")
    rule_i = None
    for i, ln in enumerate(lines):
        if ln.startswith("To evaluate "):
            rule_i = i
            break
    if rule_i is None:
        raise ValueError("no rule line on this page")
    head, sep, tail = lines[rule_i].partition(", ")
    if not sep:
        raise ValueError("rule line has no clause after the operand order")
    lines[rule_i] = head + sep + _swap_words(tail)

    n_examples = 0
    for i, ln in enumerate(lines):
        m = _WORKED.match(ln)
        if m:
            a, g, b = int(m.group(1)), m.group(2), int(m.group(3))
            lines[i] = f"Worked example: {a} {g} {b} = {t_op(a, b)}."
            n_examples += 1
    if n_examples < 2:
        raise ValueError("page did not state two worked examples")
    return "\n".join(lines), t_op


# --------------------------------------------------- trivial program on prose

_T_LINEAR = re.compile(
    r"multiply y by (\d+), multiply x by (\d+), add the two products, then add (\d+)")
_T_SQUARE = re.compile(r"square y, add (\d+) times x, then subtract (\d+)")
_T_DIFF = re.compile(
    r"subtract x from y, multiply that difference by (\d+), then add (\d+)")
_T_GUARD = re.compile(
    r"first compare\. If y is at least x, the result is y plus (\d+)\. "
    r"Otherwise the result is (\d+) times x")
_MOD = re.compile(r"reduced modulo (\d+)")
_ASSOC = re.compile(r"associates (left to right|right to left)")


def parse_transposed_page(text: str) -> Operator:
    """Read a transposed page with nothing but regexes, and return its operator."""
    m = _MOD.search(text)
    if not m:
        raise ValueError("no modulus on the page")
    mod = int(m.group(1))
    a = _ASSOC.search(text)
    if not a:
        raise ValueError("no associativity on the page")
    assoc = "left" if a.group(1) == "left to right" else "right"
    g = _WORKED.search(text)
    if not g:
        raise ValueError("no worked example on the page")
    glyph = g.group(2)

    x, y = Var("x"), Var("y")
    m = _T_LINEAR.search(text)
    if m:
        ca, cb, cc = (int(m.group(i)) for i in (1, 2, 3))
        inner = Call("+", (Call("*", (ca, y)), Call("*", (cb, x)), cc))
    elif (m := _T_SQUARE.search(text)):
        cb, cc = int(m.group(1)), int(m.group(2))
        inner = Call("-", (Call("+", (Call("*", (y, y)), Call("*", (cb, x)))), cc))
    elif (m := _T_DIFF.search(text)):
        ca, cc = int(m.group(1)), int(m.group(2))
        inner = Call("+", (Call("*", (ca, Call("-", (y, x)))), cc))
    elif (m := _T_GUARD.search(text)):
        cc, cb = int(m.group(1)), int(m.group(2))
        inner = Call("if", (Call(">=", (y, x)), Call("+", (y, cc)),
                            Call("*", (cb, x))))
    else:
        raise ValueError("no transposed rule sentence this reader recognises")
    return Operator(glyph, ("x", "y"), Call("%", (inner, mod)), assoc=assoc)


# --------------------------------------------------------------------- items


def _distractors(rng: random.Random, keep: set[int], modulus: int, k: int):
    out: list[int] = []
    while len(out) < k:
        v = rng.randrange(0, modulus)
        if v in keep or v in out:
            continue
        out.append(v)
    return out


def build(n_worlds: int, depths=DEPTHS, seed0: int = SEED0) -> tuple[list[dict], dict]:
    """One episode per (world, depth). Returns (episodes, audit counters)."""
    episodes = []
    stats = {"proposed": 0, "indistinguishable": 0, "copyable": 0,
             "kept": 0, "parser_agrees": 0, "parser_failed": 0,
             "operators": 0, "operators_distinguishable": 0}
    for w in range(n_worlds):
        seed = seed0 + w
        world = make_world(seed, breadth=3, style=0)
        binops = [p for p in world.pages if p.key.startswith("binop:")]
        t_text, t_ops, page_by_glyph = {}, {}, {}
        for p in binops:
            text, top = transpose_page(p)
            t_text[p.glyph] = text
            t_ops[p.glyph] = top
            page_by_glyph[p.glyph] = p
            stats["operators"] += 1
            probes = [(7, 4), (12, 5), (5, 9), (8, 3), (2, 11), (11, 2),
                      (6, 6), (9, 1)]
            if any(top(*pr) != p.ops[0](*pr) for pr in probes):
                stats["operators_distinguishable"] += 1
            # the trivial reader must recover the operator from the prose
            try:
                back = parse_transposed_page(text)
                if all(back(*pr) == top(*pr) for pr in probes):
                    stats["parser_agrees"] += 1
                else:
                    stats["parser_failed"] += 1
            except Exception:
                stats["parser_failed"] += 1

        train_ops = world.ops
        page_ops = dict(train_ops)
        page_ops.update(t_ops)
        for depth in depths:
            rng = random.Random(seed * 131 + depth)
            item = seq_flat(world, rng, depth)
            stats["proposed"] += 1
            glyph = item.symbols[0]
            try:
                train_ans = str(run_plan(item.plan, train_ops))
                page_ans = str(run_plan(item.plan, page_ops))
            except Exception:
                continue
            if train_ans == page_ans:
                stats["indistinguishable"] += 1
                continue
            if re.search(rf"(?<!\d){re.escape(page_ans)}(?!\d)", item.text):
                stats["copyable"] += 1
                continue
            modulus = 1000
            m = _MOD.search(t_text[glyph])
            if m:
                modulus = int(m.group(1))
            keep = {int(train_ans), int(page_ans)}
            dis = _distractors(random.Random(seed * 977 + depth), keep, modulus,
                               N_CANDIDATES - 2)
            cands = [page_ans, train_ans] + [str(d) for d in dis]
            random.Random(seed * 31 + depth).shuffle(cands)
            docs = [{"text": t_text[p.glyph]} for p in binops]
            episodes.append({
                "world": {"domain": "opgraph"},
                "n_context": 0,
                "documents": docs,
                "seed": seed, "depth": depth, "glyph": glyph,
                "n_docs": len(docs),
                "questions": [{
                    "qid": f"w{seed}d{depth}",
                    "text": item.text,
                    "answer": page_ans,
                    "page_answer": page_ans,
                    "train_answer": train_ans,
                    "candidates": cands,
                    "plan": [f"step{i}" for i in range(depth)],
                    "depth": depth,
                    "chance": 1.0 / len(cands),
                }],
            })
            stats["kept"] += 1
    return episodes, stats


# -------------------------------------------------------------------- graders

def named_numbers(answer: str, candidates: list[str]) -> list[str]:
    """Candidates named in the answer under digit boundaries, first occurrence
    order. A digit boundary, not a letter boundary: the letter-boundary rule
    used elsewhere on this project matches 51 inside 351."""
    hits = []
    for c in candidates:
        m = re.search(rf"(?<!\d){re.escape(c)}(?!\d)", answer)
        if m:
            hits.append((m.start(), c))
    hits.sort()
    seen, out = set(), []
    for _, c in hits:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def classify(answer: str, q: dict) -> dict:
    hits = named_numbers(answer, q["candidates"])
    page, train = q["page_answer"], q["train_answer"]
    return {
        "n_named": len(hits),
        "none": not hits,
        "hedge": len(hits) > 1,
        "forced_page": len(hits) == 1 and hits[0] == page,
        "forced_train": len(hits) == 1 and hits[0] == train,
        "forced_other": len(hits) == 1 and hits[0] not in (page, train),
        "first_page": bool(hits) and hits[0] == page,
        "first_train": bool(hits) and hits[0] == train,
    }


def cmd_build(args) -> int:
    episodes, stats = build(args.worlds)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        for ep in episodes:
            fh.write(json.dumps(ep) + "\n")
    incontext = args.out + ".incontext"
    with open(incontext, "w") as fh:
        for ep in episodes:
            e = dict(ep)
            e["n_context"] = len(e["documents"])
            fh.write(json.dumps(e) + "\n")
    stats["out"] = args.out
    stats["incontext"] = incontext
    stats["n_episodes"] = len(episodes)
    with open(args.out + ".audit.json", "w") as fh:
        json.dump(stats, fh, indent=1)
    print(json.dumps(stats, indent=1))
    return 0


def cmd_parsers(args) -> int:
    """The trivial program: read the served page, run the plan, answer."""
    rows = []
    for line in open(args.episodes):
        ep = json.loads(line)
        q = ep["questions"][0]
        world = make_world(ep["seed"], breadth=3, style=0)
        ops = {}
        failed = False
        for d in ep["documents"]:
            try:
                o = parse_transposed_page(d["text"])
                ops[o.symbol] = o
            except Exception:
                failed = True
        item_rng = random.Random(ep["seed"] * 131 + ep["depth"])
        item = seq_flat(world, item_rng, ep["depth"])
        try:
            ans = str(run_plan(item.plan, ops))
        except Exception:
            ans = ""
            failed = True
        rows.append({"qid": q["qid"], "depth": ep["depth"], "answer": ans,
                     "parse_failed": failed, **classify(ans, q),
                     "chance": q["chance"]})
    with open(args.out, "w") as fh:
        json.dump(rows, fh)
    n = len(rows)
    print(json.dumps({
        "n": n,
        "forced_page": sum(r["forced_page"] for r in rows) / n,
        "forced_train": sum(r["forced_train"] for r in rows) / n,
        "none": sum(r["none"] for r in rows) / n,
        "parse_failed": sum(r["parse_failed"] for r in rows) / n,
        "chance": sum(r["chance"] for r in rows) / n,
    }, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--worlds", type=int, default=150)
    b.add_argument("--out", required=True)
    b.set_defaults(fn=cmd_build)
    p = sub.add_parser("parsers")
    p.add_argument("--episodes", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_parsers)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
