"""The trivial program for the plan task: parse the question, write the plan.

Reads only what the model reads, the prompt. Pulls the expression out of the
question frame, parses it as fully parenthesised infix with prefix unary calls,
which is what `src/corpus/plans.py:render_tree` writes, and serialises the plan
with `src/opgraph/plan.py:serialize_plan`. No page, no model, no answer key.

A hand-written parser has matched or beaten the model on every task family
measured on this project, and the point of running it here is that plan length
is a property of the question that a parser reads off directly. If the parser
writes a 96-step plan and the model writes three, the length is not in the
question's difficulty.
"""

from __future__ import annotations

import argparse
import json
import re

from src.corpus.plans import PLAN_QUESTION_FRAMES
from src.opgraph.plan import Plan, Step, serialize_plan

TOKEN = re.compile(r"\(|\)|-?\d+|[^\s()]+")


def expression_of(question: str, qframe: str) -> str:
    """The expression the frame wraps, taken by the frame's own template."""
    tmpl = PLAN_QUESTION_FRAMES[qframe]
    head, _, tail = tmpl.partition("{expr}")
    if not question.startswith(head) or not question.endswith(tail):
        raise ValueError("question does not match its frame")
    return question[len(head): len(question) - len(tail)] if tail \
        else question[len(head):]


def _parse(toks, i):
    """One operand, then any run of infix operators at this level."""
    left, i = _atom(toks, i)
    while i < len(toks) and toks[i] not in (")",):
        sym = toks[i]
        right, i = _atom(toks, i + 1)
        left = (sym, [left, right])
    return left, i


def _atom(toks, i):
    if i >= len(toks):
        raise ValueError("expression ended early")
    t = toks[i]
    if t == "(":
        node, i = _parse(toks, i + 1)
        if i >= len(toks) or toks[i] != ")":
            raise ValueError("missing )")
        return node, i + 1
    if re.fullmatch(r"-?\d+", t):
        return int(t), i + 1
    # a prefix call: name ( arg )
    if i + 1 < len(toks) and toks[i + 1] == "(":
        arg, j = _parse(toks, i + 2)
        if j >= len(toks) or toks[j] != ")":
            raise ValueError("missing ) after prefix call")
        return (t, [arg]), j + 1
    raise ValueError(f"cannot read atom {t!r}")


def parse_expression(text: str):
    toks = TOKEN.findall(text)
    node, i = _parse(toks, 0)
    if i != len(toks):
        raise ValueError("trailing tokens")
    return node


def plan_text(node) -> str:
    steps: list = []
    counter = [0]

    def walk(nd):
        if isinstance(nd, int):
            return nd
        sym, kids = nd
        args = [walk(k) for k in kids]
        counter[0] += 1
        t = f"t{counter[0]}"
        steps.append(Step(t, sym, tuple(args)))
        return t

    last = walk(node)
    return serialize_plan(Plan(tuple(steps), str(last)))


QUESTION = re.compile(r"<\|q\|> plan (.*?) <\|a\|>", re.S)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    n = declined = 0
    with open(args.out, "w") as sink:
        for line in open(args.records):
            if not line.strip():
                continue
            r = json.loads(line)
            m = QUESTION.search(r["prompt"])
            try:
                expr = expression_of(m.group(1), r["qframe"])
                emitted = plan_text(parse_expression(expr))
            except Exception:
                emitted = ""
                declined += 1
            n += 1
            out = dict(r)
            out.pop("prompt", None)
            out["decode"] = "parser"
            out["emitted"] = emitted
            sink.write(json.dumps(out) + "\n")
    print(json.dumps({"out": args.out, "n": n, "declined": declined}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
