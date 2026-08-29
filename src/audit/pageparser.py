"""A hand written parser and executor that reads only the pages and the question.

No model, no gold operator, no gold plan, no gold answer. It is handed exactly
what `direct_all` is handed, the four pages of a world concatenated in the order
the retriever shuffled them plus the question string, and it returns an answer.

What it does is the whole of the task as stated: find the page that mentions the
glyph in the question, read the modulus off it, read which way a run of the
glyph associates off it, read the arithmetic rule off it, then fold the question's
operands in the stated direction.

The rule patterns are per wording. There are four wordings and four rule shapes,
so sixteen regexes, and the file is about a hundred and forty lines. Running it
with only the trained wording's patterns enabled measures the same thing the
model is measured on: how far one wording's reader carries to another.
"""

from __future__ import annotations

import re

# name in a rule sentence -> which operand of the infix expression it refers to
_SLOT = {"x": 0, "y": 1, "first": 0, "second": 1}

# (style, form, regex). Group names: p and q are operand names, a b c are the
# constants the rule states.
PATTERNS: list[tuple[int, str, str]] = [
    (0, "linear",
     r"multiply (?P<p>[xy]) by (?P<a>\d+), multiply (?P<q>[xy]) by (?P<b>\d+), "
     r"add the two products, then add (?P<c>\d+)"),
    (0, "square",
     r"square (?P<p>[xy]), add (?P<b>\d+) times (?P<q>[xy]), then subtract (?P<c>\d+)"),
    (0, "diff",
     r"subtract (?P<q>[xy]) from (?P<p>[xy]), multiply that difference by "
     r"(?P<a>\d+), then add (?P<c>\d+)"),
    (0, "guard",
     r"If (?P<p>[xy]) is at least (?P<q>[xy]), the result is [xy] plus (?P<c>\d+)\. "
     r"Otherwise the result is (?P<b>\d+) times [xy]"),
    (2, "linear",
     r"(?P<a>\d+) lots of (?P<p>[xy]) plus (?P<b>\d+) lots of (?P<q>[xy]) plus "
     r"(?P<c>\d+)"),
    (2, "square",
     r"(?P<p>[xy]) times [xy], plus (?P<b>\d+) lots of (?P<q>[xy]), less (?P<c>\d+)"),
    (2, "diff",
     r"(?P<p>[xy]) less (?P<q>[xy]), scaled by (?P<a>\d+), plus (?P<c>\d+)"),
    (2, "guard",
     r"if (?P<p>[xy]) is not below (?P<q>[xy]) then [xy] plus (?P<c>\d+), "
     r"otherwise (?P<b>\d+) lots of [xy]"),
    (3, "linear",
     r"Multiply the (?P<p>first|second) number by (?P<a>\d+)\. Multiply the "
     r"(?P<q>first|second) number by (?P<b>\d+)\. Add those two results together, "
     r"and then add (?P<c>\d+) on top"),
    (3, "square",
     r"Multiply the (?P<p>first|second) number by itself\. Add (?P<b>\d+) times "
     r"the (?P<q>first|second) number\. Then take (?P<c>\d+) away"),
    (3, "diff",
     r"Take the (?P<q>first|second) number away from the (?P<p>first|second) "
     r"number\. Multiply what is left by (?P<a>\d+)\. Then add (?P<c>\d+)"),
    (3, "guard",
     r"When the (?P<p>first|second) number is not smaller than the "
     r"(?P<q>first|second) number, the answer is the (?:first|second) number plus "
     r"(?P<c>\d+)\. When it is smaller, the answer is (?P<b>\d+) times the "
     r"(?:first|second) number"),
    (4, "linear",
     r"Form (?P<a>\d+) times (?P<p>[xy])\. Form (?P<b>\d+) times (?P<q>[xy])\. "
     r"Add the two, and add a further (?P<c>\d+)"),
    (4, "square",
     r"Form (?P<p>[xy]) times [xy]\. Add (?P<b>\d+) times (?P<q>[xy])\. "
     r"Remove (?P<c>\d+) from the total"),
    (4, "diff",
     r"Form (?P<p>[xy]) minus (?P<q>[xy])\. Multiply that by "
     r"(?P<a>\d+)\. Add a further (?P<c>\d+)"),
    (4, "guard",
     r"Check whether (?P<p>[xy]) falls below (?P<q>[xy])\. If it does not, the "
     r"total is [xy] plus (?P<c>\d+)\. If it does, the total is (?P<b>\d+) times [xy]"),
]

_MOD = re.compile(r"modulo (\d+)|divide (?:that value |it )?by (\d+)|"
                  r"divide by (\d+)|Divide it by (\d+)")

_ASSOC_LINE = re.compile(r"associat|group|work starting at")
_LEFT = ("left to right", "from the left", "left end", "left-to-right")
_RIGHT = ("right to left", "from the right", "right end", "right-to-left")


class Unreadable(Exception):
    """The parser could not find what it needed on the page."""


def read_rule(page: str, styles) -> tuple[str, dict]:
    for st, form, pat in PATTERNS:
        if st not in styles:
            continue
        m = re.search(pat, page)
        if m:
            return form, m.groupdict()
    raise Unreadable("no rule sentence matched")


def read_modulus(page: str) -> int:
    m = _MOD.search(page)
    if not m:
        raise Unreadable("no modulus")
    return int(next(g for g in m.groups() if g))


def read_assoc(page: str) -> str:
    for line in page.split("\n"):
        if not _ASSOC_LINE.search(line):
            continue
        low = line.lower()
        hit_l = min((low.find(w) for w in _LEFT if w in low), default=-1)
        hit_r = min((low.find(w) for w in _RIGHT if w in low), default=-1)
        if hit_l >= 0 and (hit_r < 0 or hit_l < hit_r):
            return "left"
        if hit_r >= 0:
            return "right"
    raise Unreadable("no associativity")


def build_op(form: str, g: dict, m: int):
    pi, qi = _SLOT[g["p"]], _SLOT[g["q"]]
    a = int(g["a"]) if g.get("a") else 0
    b = int(g["b"]) if g.get("b") else 0
    c = int(g["c"])

    def run(x, y):
        o = (x, y)
        p, q = o[pi], o[qi]
        if form == "linear":
            v = a * p + b * q + c
        elif form == "square":
            v = p * p + b * q - c
        elif form == "diff":
            v = a * (p - q) + c
        else:
            v = p + c if p >= q else b * q
        return v % m

    return run


def find_page(context: str, glyph: str, styles) -> str:
    """The page that defines the glyph, out of the retrieved set."""
    best = None
    for page in context.split(" <|doc|> "):
        if glyph not in page:
            continue
        try:
            read_rule(page, styles)
        except Unreadable:
            continue
        best = page
    if best is None:
        raise Unreadable("no page defines the glyph")
    return best


def answer(context: str, question: str, styles=(0, 2, 3, 4)) -> str:
    """The parser's answer to one flat sequential question, as a string."""
    body = question.strip()
    if body.startswith("Evaluate "):
        body = body[len("Evaluate "):]
    body = body.rstrip(".")
    toks = body.split()
    if len(toks) < 3 or len(toks) % 2 == 0:
        raise Unreadable("not a flat infix chain")
    glyph = toks[1]
    vals = [int(t) for t in toks[0::2]]
    if any(t != glyph for t in toks[1::2]):
        raise Unreadable("mixed glyphs")
    page = find_page(context, glyph, styles)
    form, g = read_rule(page, styles)
    op = build_op(form, g, read_modulus(page))
    if read_assoc(page) == "left":
        acc = vals[0]
        for v in vals[1:]:
            acc = op(acc, v)
    else:
        acc = vals[-1]
        for v in reversed(vals[:-1]):
            acc = op(v, acc)
    return str(acc)


def score(items, styles=(0, 2, 3, 4), oracle_page: bool = False):
    """Correctness per item, plus how many items it refused to answer."""
    ok, refused = [], 0
    for it in items:
        keys = set(it.pages) if oracle_page else None
        try:
            got = answer(it.world.context(keys), it.text, styles)
        except (Unreadable, ValueError, ZeroDivisionError):
            ok.append(False)
            refused += 1
            continue
        ok.append(got == it.gold)
    return ok, refused
