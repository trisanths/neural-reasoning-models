"""A second reading of the textbook pages, written from the prose alone.

Nothing here imports an operator object, a plan, or an evaluator from
src.opgraph. The only things taken from the generator are the strings a reader
would see: the text of each page in a world, and the text of each question. The
answer is re-derived from those strings by regular expressions over the English
and a small expression evaluator written here.

The point is that the shipped gold answers are produced by the same code that
lays out the question tree, so a mistake in that code is invisible to itself. If
this module and the generator agree on every item, the gold is at least not a
private convention. Where they disagree, the prose is the arbiter, because the
prose is all a reader of the page ever gets.

Three readings of the page are kept apart on purpose, because the prose does not
settle them:

  reduce_each   the modulus is taken after every application of the operator
  reduce_end    the modulus is taken once, on the value finally reported
  trunc_rem     remainder with the sign of the dividend rather than of the
                divisor, which only matters when an intermediate goes negative

The style 0 wording says "Every result in this system is reduced modulo m. After
computing a value, divide it by m and keep only the remainder", which reads as
reduce_each. The style 1 wording says "Take the remainder on division by m at
the end", which reads as reduce_end. Both readings are computed for every item
and the disagreements are counted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


class ProseError(Exception):
    """The page did not say something this reader could act on."""


# --------------------------------------------------------------------- binop

_EX_STYLE0 = re.compile(r"^Worked example: (-?\d+) (\S+) (-?\d+) = (-?\d+)\.$", re.M)
_EX_STYLE1 = re.compile(r"^For instance (-?\d+) (\S+) (-?\d+) comes to (-?\d+)\.$", re.M)

_MOD_PATS = [re.compile(r"reduced modulo (\d+)"),
             re.compile(r"remainder on division by (\d+)")]
_ASSOC_PATS = [re.compile(r"associates (left to right|right to left)"),
               re.compile(r"is read (left to right|right to left)")]

_RULE_LINEAR = re.compile(
    r"multiply x by (\d+), multiply y by (\d+), add the two products, then add (\d+)")
_RULE_SQUARE = re.compile(r"square x, add (\d+) times y, then subtract (\d+)")
_RULE_DIFF = re.compile(
    r"subtract y from x, multiply that difference by (\d+), then add (\d+)")
_RULE_GUARD = re.compile(
    r"first compare\. If x is at least y, the result is x plus (\d+)\. "
    r"Otherwise the result is (\d+) times y")


@dataclass
class BinOp:
    glyph: str
    modulus: int
    assoc: str            # "left" or "right"
    form: str
    coef: tuple
    examples: list = field(default_factory=list)

    def raw(self, x: int, y: int) -> int:
        """The value the rule sentence describes, before any remainder."""
        if self.form == "linear":
            a, b, c = self.coef
            return a * x + b * y + c
        if self.form == "square":
            b, c = self.coef
            return x * x + b * y - c
        if self.form == "diff":
            a, c = self.coef
            return a * (x - y) + c
        if self.form == "guarded":
            c, b = self.coef
            return x + c if x >= y else b * y
        raise ProseError(f"no rule for {self.form}")


def _rem(v: int, m: int, trunc: bool) -> int:
    if not trunc:
        return v % m
    r = abs(v) % m
    return -r if v < 0 else r


def parse_binop_page(text: str) -> BinOp:
    ex = [(int(a), g, int(b), int(v)) for a, g, b, v in _EX_STYLE0.findall(text)]
    ex += [(int(a), g, int(b), int(v)) for a, g, b, v in _EX_STYLE1.findall(text)]
    if not ex:
        raise ProseError("no worked example of the form int glyph int")
    glyphs = {g for _, g, _, _ in ex}
    if len(glyphs) != 1:
        raise ProseError(f"worked examples disagree on the glyph: {glyphs}")
    glyph = glyphs.pop()

    mod = None
    for p in _MOD_PATS:
        m = p.search(text)
        if m:
            mod = int(m.group(1))
            break
    if mod is None:
        raise ProseError("the page never states a modulus")

    assoc = None
    for p in _ASSOC_PATS:
        m = p.search(text)
        if m:
            assoc = "left" if m.group(1) == "left to right" else "right"
            break
    if assoc is None:
        raise ProseError("the page never states an associativity")

    m = _RULE_LINEAR.search(text)
    if m:
        form, coef = "linear", (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    else:
        m = _RULE_SQUARE.search(text)
        if m:
            form, coef = "square", (int(m.group(1)), int(m.group(2)))
        else:
            m = _RULE_DIFF.search(text)
            if m:
                form, coef = "diff", (int(m.group(1)), int(m.group(2)))
            else:
                m = _RULE_GUARD.search(text)
                if m:
                    form, coef = "guarded", (int(m.group(1)), int(m.group(2)))
                else:
                    raise ProseError("no rule sentence this reader recognises")
    return BinOp(glyph, mod, assoc, form, coef,
                 [((a, b), v) for a, _, b, v in ex])


# --------------------------------------------------------------------- units

_U_S0_MID = re.compile(r"One (\w+) equals (\d+) (\w+)\.")
_U_S0_BIG = re.compile(r"One (\w+) equals (\d+) (\w+), which is (\d+) (\w+)\.")
_U_S1 = re.compile(r"Multiply by (\d+) to turn a (\w+) count into (\w+); "
                   r"multiply by (\d+) to turn a (\w+) count into (\w+)\.")


@dataclass
class Units:
    base: str
    factor: dict


def parse_units_page(text: str) -> Units:
    m = _U_S1.search(text)
    if m:
        k1, mid, base1, k2, big, base2 = m.groups()
        if base1 != base2:
            raise ProseError("the two conversions name different small units")
        return Units(base1, {mid: int(k1), big: int(k2)})
    big = _U_S0_BIG.search(text)
    if not big:
        raise ProseError("no large unit sentence")
    b_name, _, b_mid, b_to_base, b_base = big.groups()
    mid = None
    for mm in _U_S0_MID.finditer(text):
        if mm.group(1) == b_mid:
            mid = mm
            break
    if mid is None:
        raise ProseError("no middle unit sentence")
    if mid.group(3) != b_base:
        raise ProseError("the two sentences name different small units")
    return Units(b_base, {b_mid: int(mid.group(2)), b_name: int(b_to_base)})


# ----------------------------------------------------------------- procedure

_P_COND_S0 = re.compile(r"If the application is marked (\w+), (add|subtract) (\d+)\.")
_P_COND_S1 = re.compile(r"Marked (\w+)\? Then (add|subtract) (\d+)\.")
_P_CUT_S0 = re.compile(r"accepted when its adjusted value is at least (\d+)")
_P_CUT_S1 = re.compile(r"Refuse the application if the number you end on is under (\d+)")
_P_ATTR_S0 = re.compile(r"Each application carries a (\w+) value")
_P_ATTR_S1 = re.compile(r"The starting number is the (\w+) value")


@dataclass
class Procedure:
    attr: str
    delta: dict
    cutoff: int


def parse_procedure_page(text: str) -> Procedure:
    conds = [(w, s, int(d)) for w, s, d in _P_COND_S0.findall(text)]
    conds += [(w, s, int(d)) for w, s, d in _P_COND_S1.findall(text)]
    if not conds:
        raise ProseError("no adjustment lines")
    delta = {w: (d if s == "add" else -d) for w, s, d in conds}
    if len(delta) != len(conds):
        raise ProseError("two adjustment lines share a mark")
    cut = _P_CUT_S0.search(text) or _P_CUT_S1.search(text)
    if not cut:
        raise ProseError("no cutoff sentence")
    attr = _P_ATTR_S0.search(text) or _P_ATTR_S1.search(text)
    if not attr:
        raise ProseError("no starting value sentence")
    return Procedure(attr.group(1), delta, int(cut.group(1)))


# --------------------------------------------------------------------- world

@dataclass
class RefWorld:
    binops: dict = field(default_factory=dict)
    units: Units | None = None
    proc: Procedure | None = None

    @classmethod
    def read(cls, page_texts) -> "RefWorld":
        w = cls()
        for t in page_texts:
            got = 0
            try:
                b = parse_binop_page(t)
                w.binops[b.glyph] = b
                got += 1
            except ProseError:
                pass
            try:
                u = parse_units_page(t)
                w.units = u
                got += 1
            except ProseError:
                pass
            try:
                p = parse_procedure_page(t)
                w.proc = p
                got += 1
            except ProseError:
                pass
            if got != 1:
                raise ProseError(f"page read {got} ways, not once:\n{t[:120]}")
        return w

    def check_examples(self, trunc=False):
        """Reproduce every worked example the pages print. Returns failures.

        One application, so the two modulus readings coincide here and only the
        remainder convention can move the number.
        """
        bad = []
        for b in self.binops.values():
            for (x, y), v in b.examples:
                got = _rem(b.raw(x, y), b.modulus, trunc)
                if got != v:
                    bad.append((b.glyph, (x, y), v, got))
        return bad


# ---------------------------------------------------------------- expressions

_TOK = re.compile(r"\(|\)|-?\d+|[^\s()]+")


def _tokens(s: str):
    return _TOK.findall(s)


def parse_evaluate(text: str):
    """'Evaluate (3 @ 5) @ 7.' -> a tree of ('op', glyph, left, right) or ints.

    A flat run of one glyph is left unresolved here and folded later, because
    which way it folds is a fact about the page, not about the question.
    """
    s = text.strip()
    m = re.match(r"^Evaluate\s+(.*?)\.$", s, re.S)
    if not m:
        raise ProseError(f"not an Evaluate question: {s[:60]!r}")
    toks = _tokens(m.group(1))
    node, i = _parse_run(toks, 0)
    if i != len(toks):
        raise ProseError("trailing tokens in the expression")
    return node


def _parse_run(toks, i):
    items = []
    glyphs = []
    node, i = _parse_atom(toks, i)
    items.append(node)
    while i < len(toks) and toks[i] != ")":
        g = toks[i]
        if re.fullmatch(r"-?\d+", g) or g == "(":
            raise ProseError("two operands with no operator between them")
        glyphs.append(g)
        node, i = _parse_atom(toks, i + 1)
        items.append(node)
    if not glyphs:
        return items[0], i
    if len(set(glyphs)) != 1:
        raise ProseError(f"a bracket-free run mixes operators {sorted(set(glyphs))}, "
                         f"which no page gives a precedence for")
    return ("run", glyphs[0], items), i


def _parse_atom(toks, i):
    if i >= len(toks):
        raise ProseError("expression ended early")
    t = toks[i]
    if t == "(":
        node, j = _parse_run(toks, i + 1)
        if j >= len(toks) or toks[j] != ")":
            raise ProseError("missing )")
        return node, j + 1
    if re.fullmatch(r"-?\d+", t):
        return int(t), i + 1
    raise ProseError(f"bad operand {t!r}")


def eval_tree(node, world: RefWorld, mode="reduce_each", trunc=False,
              force_assoc=None, record=None):
    """Value of a parsed expression under one reading of the page.

    `record`, when given a list, collects (glyph, x, y, value) for every
    application in evaluation order, which is what the collision check needs.
    """
    if isinstance(node, int):
        return node
    _, glyph, items = node
    b = world.binops.get(glyph)
    if b is None:
        raise ProseError(f"no page defines {glyph!r}")
    vals = [eval_tree(k, world, mode, trunc, force_assoc, record) for k in items]
    assoc = force_assoc or b.assoc

    def apply(x, y):
        v = b.raw(x, y)
        if mode == "reduce_each":
            v = _rem(v, b.modulus, trunc)
        if record is not None:
            record.append((glyph, x, y, v))
        return v

    if assoc == "left":
        acc = vals[0]
        for v in vals[1:]:
            acc = apply(acc, v)
    else:
        acc = vals[-1]
        for v in reversed(vals[:-1]):
            acc = apply(v, acc)
    return acc


def answer_evaluate(text: str, world: RefWorld, mode="reduce_each", trunc=False,
                    force_assoc=None, record=None) -> str:
    tree = parse_evaluate(text)
    v = eval_tree(tree, world, mode, trunc, force_assoc, record)
    if mode == "reduce_end":
        mods = {world.binops[g].modulus for g in _glyphs_in(tree)}
        if len(mods) != 1:
            raise ProseError("two moduli in one expression and no page orders them")
        v = _rem(v, mods.pop(), trunc)
    return str(v)


def _glyphs_in(node):
    if isinstance(node, int):
        return set()
    _, g, items = node
    out = {g}
    for k in items:
        out |= _glyphs_in(k)
    return out


# ------------------------------------------------------------ other questions

_Q_UNITS = re.compile(r"^How many (\w+) are (\d+) (\w+)\?$")
_Q_APP = re.compile(r"^An application has a (\w+) value of (\d+)\.\s*(.*?)\s*"
                    r"(What is its adjusted value\?|Is it accepted or refused\?)$", re.S)
_Q_MARK = re.compile(r"It is (not marked|marked) (\w+)\.")


def answer_units(text: str, world: RefWorld) -> str:
    m = _Q_UNITS.match(text.strip())
    if not m:
        raise ProseError("not a unit question")
    base, q, unit = m.group(1), int(m.group(2)), m.group(3)
    u = world.units
    if u is None:
        raise ProseError("no page states a unit convention")
    if base != u.base:
        raise ProseError(f"question asks for {base!r}, page's small unit is {u.base!r}")
    if unit not in u.factor:
        raise ProseError(f"no conversion stated for {unit!r}")
    return str(q * u.factor[unit])


def answer_application(text: str, world: RefWorld) -> str:
    m = _Q_APP.match(text.strip())
    if not m:
        raise ProseError("not an application question")
    attr, base, body, ask = m.group(1), int(m.group(2)), m.group(3), m.group(4)
    p = world.proc
    if p is None:
        raise ProseError("no page states an assessment")
    if attr != p.attr:
        raise ProseError(f"question names {attr!r}, page names {p.attr!r}")
    marks = _Q_MARK.findall(body)
    if len(marks) != len(p.delta):
        raise ProseError(f"question states {len(marks)} marks, page lists {len(p.delta)}")
    total = base
    for state, w in marks:
        if w not in p.delta:
            raise ProseError(f"question mentions mark {w!r} the page never defines")
        if state == "marked":
            total += p.delta[w]
    if ask.startswith("What"):
        return str(total)
    return "accepted" if total >= p.cutoff else "refused"


def answer_question(text: str, world: RefWorld, **kw) -> str:
    s = text.strip()
    if s.startswith("Evaluate "):
        return answer_evaluate(s, world, **kw)
    if s.startswith("How many "):
        return answer_units(s, world)
    if s.startswith("An application "):
        return answer_application(s, world)
    raise ProseError(f"unrecognised question form: {s[:60]!r}")
