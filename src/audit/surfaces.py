"""Re-rendering an invented world's pages, and transposing what its operators mean.

Two things live here, and they share the same machinery because both need to
take a world apart and put it back together with everything except one chosen
property held fixed.

`restyle_world` rewrites every page of a world in a surface form the arms never
trained on. The seed, the page count, the operator objects, the questions, the
gold plans and the gold answers are all unchanged; only the prose changes.
Style 0 is reproduced byte for byte from `src/opgraph/invent.py`, which is the
self test that the rewriting is faithful.

`transpose_world` leaves the surface form at style 0 and swaps the two operand
roles inside every binary operator's rule, so the glyph, the page skeleton, the
sentence shape and the worked-example format all stay identical while the
function the page defines becomes a different function. The page's own worked
examples are recomputed, so the page is internally consistent and states the
transposed rule twice over. Anything that answers with the untransposed
function is following the identity the operator had during training rather than
the page in front of it.

Nothing in this module imports or modifies anything under `src/opgraph` beyond
reading it.
"""

from __future__ import annotations

import copy
import re

from src.opgraph.invent import Page, World, make_world
from src.opgraph.opdef import Call, Operator, Var

X, Y, N, V, S = Var("x"), Var("y"), Var("n"), Var("v"), Var("s")

STYLES = (0, 2, 3, 4)

STYLE_NAMES = {
    0: "trained wording",
    2: "spec sheet",
    3: "letter",
    4: "examples first",
}


# ------------------------------------------------------------- reading a page

def _is(e, head, n=None) -> bool:
    return isinstance(e, Call) and e.head == head and (n is None or len(e.args) == n)


def binop_params(op: Operator) -> dict:
    """Recover the generator's parameters from a gold binary operator body.

    The four bodies `_binop_page` can build are structurally distinct, so this
    is a total function on them and raises on anything else.
    """
    body = op.body
    if not _is(body, "%", 2):
        raise ValueError(f"not a reduced binop body: {body!r}")
    inner, m = body.args
    if _is(inner, "+", 3):
        t1, t2, c = inner.args
        return {"form": "linear", "a": t1.args[0], "b": t2.args[0], "c": c, "m": m}
    if _is(inner, "-", 2):
        s, c = inner.args
        return {"form": "square_first", "a": None, "b": s.args[1].args[0],
                "c": c, "m": m}
    if _is(inner, "+", 2):
        t, c = inner.args
        return {"form": "diff_scaled", "a": t.args[0], "b": None, "c": c, "m": m}
    if _is(inner, "if", 3):
        _, then, els = inner.args
        return {"form": "guarded", "a": None, "b": els.args[0],
                "c": then.args[1], "m": m}
    raise ValueError(f"unrecognised binop body: {inner!r}")


def _title_name(page: Page) -> str:
    head = page.text.split("\n")[0]
    for pat in (r"^The (\w+) System\.$", r"^Measures in the (\w+) convention\.$",
                r"^The (\w+) assessment\.$"):
        m = re.match(pat, head)
        if m:
            return m.group(1)
    raise ValueError(f"cannot read a name off {head!r}")


def binop_body(form: str, a, b, c, m, swap: bool = False):
    """The body the page states, with the two operand roles optionally swapped."""
    p, q = (Y, X) if swap else (X, Y)
    if form == "linear":
        inner = Call("+", (Call("*", (a, p)), Call("*", (b, q)), c))
    elif form == "square_first":
        inner = Call("-", (Call("+", (Call("*", (p, p)), Call("*", (b, q)))), c))
    elif form == "diff_scaled":
        inner = Call("+", (Call("*", (a, Call("-", (p, q)))), c))
    elif form == "guarded":
        inner = Call("if", (Call(">=", (p, q)), Call("+", (p, c)), Call("*", (b, q))))
    else:
        raise ValueError(form)
    return Call("%", (inner, m))


# ------------------------------------------------------------- rule sentences

def _rule_s0(form, a, b, c, glyph, lhs="x", rhs="y") -> str:
    """The trained sentence, with the two operand names supplied by the caller."""
    if form == "linear":
        return (f"To evaluate x {glyph} y, multiply {lhs} by {a}, multiply {rhs} by {b}, "
                f"add the two products, then add {c}.")
    if form == "square_first":
        return (f"To evaluate x {glyph} y, square {lhs}, add {b} times {rhs}, "
                f"then subtract {c}.")
    if form == "diff_scaled":
        return (f"To evaluate x {glyph} y, subtract {rhs} from {lhs}, multiply that "
                f"difference by {a}, then add {c}.")
    return (f"To evaluate x {glyph} y, first compare. If {lhs} is at least {rhs}, the "
            f"result is {lhs} plus {c}. Otherwise the result is {b} times {rhs}.")


def _rule_s2(form, a, b, c, lhs="x", rhs="y") -> str:
    if form == "linear":
        return f"{a} lots of {lhs} plus {b} lots of {rhs} plus {c}."
    if form == "square_first":
        return f"{lhs} times {lhs}, plus {b} lots of {rhs}, less {c}."
    if form == "diff_scaled":
        return f"{lhs} less {rhs}, scaled by {a}, plus {c}."
    return (f"if {lhs} is not below {rhs} then {lhs} plus {c}, "
            f"otherwise {b} lots of {rhs}.")


def _rule_s3(form, a, b, c, first="first", second="second") -> str:
    if form == "linear":
        return (f"Multiply the {first} number by {a}. Multiply the {second} number "
                f"by {b}. Add those two results together, and then add {c} on top.")
    if form == "square_first":
        return (f"Multiply the {first} number by itself. Add {b} times the {second} "
                f"number. Then take {c} away.")
    if form == "diff_scaled":
        return (f"Take the {second} number away from the {first} number. Multiply "
                f"what is left by {a}. Then add {c}.")
    return (f"Compare the two. When the {first} number is not smaller than the "
            f"{second} number, the answer is the {first} number plus {c}. When it "
            f"is smaller, the answer is {b} times the {second} number.")


def _rule_s4(form, a, b, c, lhs="x", rhs="y") -> str:
    if form == "linear":
        return (f"Form {a} times {lhs}. Form {b} times {rhs}. Add the two, "
                f"and add a further {c}.")
    if form == "square_first":
        return (f"Form {lhs} times {lhs}. Add {b} times {rhs}. "
                f"Remove {c} from the total.")
    if form == "diff_scaled":
        return (f"Form {lhs} minus {rhs}. Multiply that by {a}. "
                f"Add a further {c}.")
    return (f"Check whether {lhs} falls below {rhs}. If it does not, the total is "
            f"{lhs} plus {c}. If it does, the total is {b} times {rhs}.")


ASSOC_WORDS = {
    0: {"left": "left to right", "right": "right to left"},
    2: {"left": "from the left", "right": "from the right"},
    3: {"left": "starting at the left end", "right": "starting at the right end"},
    4: {"left": "in left-to-right order", "right": "in right-to-left order"},
}


# --------------------------------------------------------------- binop page

def render_binop(name, glyph, form, a, b, c, m, right_assoc, op, style) -> str:
    assoc = ASSOC_WORDS[style]["right" if right_assoc else "left"]
    v1, v2 = op(7, 4), op(12, 5)
    if style == 0:
        return "\n".join([
            f"The {name} System.",
            "",
            f"The {name} system introduces an operator written {glyph}. It combines "
            f"two whole numbers and produces a whole number.",
            _rule_s0(form, a, b, c, glyph, *_roles(op)),
            f"Every result in this system is reduced modulo {m}. After computing a "
            f"value, divide it by {m} and keep only the remainder.",
            f"When an expression contains more than one {glyph} and no parentheses, "
            f"{glyph} associates {assoc}. "
            f"Parentheses, where written, are evaluated first.",
            f"Worked example: 7 {glyph} 4 = {v1}.",
            f"Worked example: 12 {glyph} 5 = {v2}.",
        ])
    lhs, rhs = _roles(op)
    if style == 2:
        return "\n".join([
            f"{name} operator sheet.",
            "",
            f"symbol {glyph}: two whole numbers in, one whole number out.",
            f"operands: x is the number written left of {glyph}, y the number "
            f"written right of it.",
            f"value: {_rule_s2(form, a, b, c, lhs, rhs)}",
            f"reduction: divide that value by {m} and report only the remainder.",
            f"grouping: brackets first; an unbracketed run of {glyph} groups {assoc}.",
            f"check: x=7, y=4 gives {v1}",
            f"check: x=12, y=5 gives {v2}",
        ])
    if style == 3:
        first, second = ("second", "first") if lhs == "y" else ("first", "second")
        return "\n".join([
            f"A letter about {name}.",
            "",
            f"You asked what the sign {glyph} does. It joins two whole numbers and "
            f"hands back a whole number.",
            f"Here is the rule. {_rule_s3(form, a, b, c, first, second)}",
            f"Do not report that number as it stands. Divide it by {m} and report "
            f"only what is left over.",
            f"Where {glyph} appears more than once and nobody has written brackets, "
            f"work {assoc}. Brackets, where they appear, are settled before "
            f"anything else.",
            f"I checked it. Seven {glyph} four came out {v1}. "
            f"Twelve {glyph} five came out {v2}.",
        ])
    if style == 4:
        return "\n".join([
            f"{glyph} in {name}.",
            "",
            f"7 {glyph} 4 = {v1}",
            f"12 {glyph} 5 = {v2}",
            f"Both lines follow one rule, and here it is. Write the number left of "
            f"{glyph} as x and the number right of it as y. "
            f"{_rule_s4(form, a, b, c, lhs, rhs)}",
            f"Then reduce: divide by {m} and keep the remainder.",
            f"A bracket-free run of {glyph} is grouped {assoc}. Brackets are done "
            f"before anything else.",
        ])
    raise ValueError(style)


def _roles(op: Operator) -> tuple[str, str]:
    """Which operand the rule names first, read off the body itself.

    A transposed operator's body mentions y where the trained one mentions x,
    so the sentence that describes it has to swap the two names too.
    """
    return ("y", "x") if _transposed(op.body) else ("x", "y")


def _transposed(body) -> bool:
    inner = body.args[0]
    if _is(inner, "+", 3):
        return inner.args[0].args[1] == Y
    if _is(inner, "-", 2):
        return inner.args[0].args[0].args[0] == Y
    if _is(inner, "+", 2):
        return inner.args[0].args[1].args[0] == Y
    if _is(inner, "if", 3):
        return inner.args[0].args[0] == Y
    raise ValueError(inner)


# --------------------------------------------------------------- units page

def render_units(name, base, mid, big, k1, k2, e1, e2, style) -> str:
    if style == 0:
        return "\n".join([
            f"Measures in the {name} convention.",
            "",
            f"The {name} convention measures length in three units. The smallest is "
            f"the {base}. Next is the {mid}. The largest is the {big}.",
            f"One {mid} equals {k1} {base}. One {big} equals {k2} {mid}, "
            f"which is {k1 * k2} {base}.",
            f"To reduce a quantity to {base}, multiply a {mid} count by {k1}, "
            f"and a {big} count by {k1 * k2}.",
            f"Worked example: {e1} {mid} = {e1 * k1} {base}.",
            f"Worked example: {e2} {big} = {e2 * k1 * k2} {base}.",
        ])
    if style == 2:
        return "\n".join([
            f"{name} lengths: a table.",
            "",
            f"{base}: the smallest unit.",
            f"{mid}: {k1} {base}.",
            f"{big}: {k2} {mid}, which comes to {k1 * k2} {base}.",
            f"conversion: a {mid} count times {k1} gives {base}; a {big} count "
            f"times {k1 * k2} gives {base}.",
            f"check {e1} {mid} = {e1 * k1} {base}",
            f"check {e2} {big} = {e2 * k1 * k2} {base}",
        ])
    if style == 3:
        return "\n".join([
            f"A letter about {name} lengths.",
            "",
            f"There are three units here, and the {base} is the small one. Above it "
            f"sits the {mid}, and above that the {big}.",
            f"It takes {k1} {base} to make one {mid}, and {k2} {mid} to make one "
            f"{big}, so a {big} is {k1 * k2} {base}.",
            f"When you want an answer in {base}, take a count of {mid} and multiply "
            f"by {k1}, or take a count of {big} and multiply by {k1 * k2}.",
            f"I worked two out. {e1} {mid} is {e1 * k1} {base}, and {e2} {big} is "
            f"{e2 * k1 * k2} {base}.",
        ])
    if style == 4:
        return "\n".join([
            f"Lengths in {name}.",
            "",
            f"{e1} {mid} = {e1 * k1} {base}",
            f"{e2} {big} = {e2 * k1 * k2} {base}",
            f"Those two lines come from the sizes of the units. The {base} is the "
            f"smallest, the {mid} is next, the {big} is the largest.",
            f"A {mid} is {k1} {base}. A {big} is {k2} {mid}, that is {k1 * k2} "
            f"{base}.",
            f"So a count of {mid} becomes {base} on multiplying by {k1}, and a "
            f"count of {big} becomes {base} on multiplying by {k1 * k2}.",
        ])
    raise ValueError(style)


# ----------------------------------------------------------- procedure page

def render_procedure(name, attr, flags, cutoff, ex_base, ex_flags, ex_value,
                     style) -> str:
    ex_desc = ", ".join(("marked " if f else "not marked ") + flags[i][0]
                        for i, f in enumerate(ex_flags))
    if style == 0:
        lines = [f"If the application is marked {w}, "
                 f"{'add' if d > 0 else 'subtract'} {abs(d)}." for w, d in flags]
        return "\n".join([
            f"The {name} assessment.",
            "",
            f"Each application carries a {attr} value, a whole number. The "
            f"assessment starts from that value and adjusts it.",
            f"The adjustments are applied in the order written here, and every one "
            f"whose condition holds is applied.",
            *lines,
            f"An application is accepted when its adjusted value is at least "
            f"{cutoff}, and refused otherwise.",
            f"Worked example: a {attr} value of {ex_base}, {ex_desc}, "
            f"adjusts to {ex_value}.",
        ])
    if style == 2:
        lines = [f"{w}: {'+' if d > 0 else '-'}{abs(d)}" for w, d in flags]
        return "\n".join([
            f"{name} assessment sheet.",
            "",
            f"input: the {attr} value on the application, a whole number.",
            f"adjustments, in the order listed, each applied when its mark is "
            f"present:",
            *lines,
            f"threshold {cutoff}: at or above it the application is accepted, "
            f"below it refused.",
            f"check: {attr} {ex_base}, {ex_desc}, ends at {ex_value}",
        ])
    if style == 3:
        lines = [f"Where the application is marked {w}, "
                 f"{'raise' if d > 0 else 'lower'} the running number by {abs(d)}."
                 for w, d in flags]
        return "\n".join([
            f"A letter about the {name} assessment.",
            "",
            f"You begin with the {attr} value printed on the application, which is "
            f"a whole number, and you move it up and down as follows.",
            f"Take the lines in the order I have written them, and apply every one "
            f"whose mark the application carries.",
            *lines,
            f"The number you finish on decides it. At {cutoff} or above the "
            f"application is accepted; below {cutoff} it is refused.",
            f"For instance: a {attr} value of {ex_base}, {ex_desc}. You finish on "
            f"{ex_value}.",
        ])
    if style == 4:
        lines = [f"marked {w} -> {'add' if d > 0 else 'subtract'} {abs(d)}"
                 for w, d in flags]
        return "\n".join([
            f"{name}: judging an application.",
            "",
            f"Example. A {attr} value of {ex_base}, {ex_desc}. The number reached "
            f"is {ex_value}.",
            f"That example follows the lines below, which are applied in the order "
            f"printed, every one whose mark is present, starting from the {attr} "
            f"value on the application.",
            *lines,
            f"Accept when the number reached is {cutoff} or more. Otherwise refuse.",
        ])
    raise ValueError(style)


# -------------------------------------------------------------- whole worlds

def _rebuild(world: World, style: int, swap: bool) -> World:
    """One world with every page re-rendered, and operators optionally transposed."""
    pages: list[Page] = []
    for p in world.pages:
        if p.key.startswith("binop:"):
            gold = p.ops[0]
            prm = binop_params(gold)
            body = binop_body(prm["form"], prm["a"], prm["b"], prm["c"], prm["m"],
                              swap=swap)
            bare = Operator(gold.symbol, ("x", "y"), body)
            op = Operator(gold.symbol, ("x", "y"), body,
                          examples=((( 7, 4), bare(7, 4)), ((12, 5), bare(12, 5))),
                          assoc=gold.assoc)
            text = render_binop(_title_name(p), p.glyph, prm["form"], prm["a"],
                                prm["b"], prm["c"], prm["m"], p.right_assoc, op,
                                style)
            q = Page(p.key, text, [op])
            q.right_assoc = p.right_assoc
            q.glyph = p.glyph
            pages.append(q)
            continue
        if p.key == "units":
            mid_op, big_op = p.ops
            k1 = mid_op.body.args[1]
            k2 = big_op.body.args[1] // k1
            e1 = mid_op.examples[0][0][0]
            e2 = big_op.examples[0][0][0]
            text = render_units(_title_name(p), p.base, p.mid, p.big, k1, k2,
                                e1, e2, style)
            q = Page(p.key, text, list(p.ops))
            q.base, q.mid, q.big = p.base, p.mid, p.big
            pages.append(q)
            continue
        if p.key == "procedure":
            score = p.ops[0]
            ex_args, ex_value = score.examples[0]
            text = render_procedure(_title_name(p), p.attr, p.flags, p.cutoff,
                                    ex_args[0], ex_args[1:], ex_value, style)
            q = Page(p.key, text, list(p.ops))
            q.attr, q.flags, q.cutoff = p.attr, p.flags, p.cutoff
            pages.append(q)
            continue
        raise ValueError(p.key)
    return World(world.seed, pages, list(world.order))


def restyle_world(world: World, style: int) -> World:
    """Same operators, same questions, same seed; different prose."""
    return _rebuild(world, style, swap=False)


def transpose_world(world: World) -> World:
    """Trained prose, trained glyphs, the two operand roles swapped.

    Only the binary operators move. The unit and procedure pages are untouched,
    which keeps the rest of the context identical to the control.
    """
    return _rebuild(world, 0, swap=True)


def selftest(n: int = 60) -> None:
    """restyle_world(w, 0) must reproduce invent.py byte for byte."""
    bad = 0
    for seed in range(n):
        for breadth in (1, 2, 3):
            w = make_world(900_000_000 + seed, breadth=breadth, style=0)
            r = restyle_world(w, 0)
            for p, q in zip(w.pages, r.pages):
                if p.text != q.text:
                    bad += 1
                    print("MISMATCH", p.key, seed, breadth)
                    print(repr(p.text))
                    print(repr(q.text))
                    return
            t = transpose_world(w)
            for p, q in zip(w.pages, t.pages):
                if p.key.startswith("binop:"):
                    continue
                assert p.text == q.text, (p.key, seed)
    print(f"selftest ok, {n} seeds x 3 breadths, {bad} mismatches")


if __name__ == "__main__":
    selftest()
