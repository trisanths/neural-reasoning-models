"""Invented worlds whose pages define operators, and questions of known depth.

Every world is generated fresh from a seed: new glyphs, new names, new
constants, so memorising any particular rule has zero expected value and the
only thing that can transfer is the ability to read a page and use what it
says. This follows src/skillacq/systems.py, and borrows its vocabulary, but
differs in two ways that the depth curve needs.

First, each page is self contained. Scattered definitions are a known and
separate retrieval coverage failure, and mixing it in here would make the
depth curve unreadable.

Second, every question carries the reference program that answers it, so a
question has a gold answer, a gold plan, and a gold operator table. That is
what makes the oracle conditions possible: the composition can be supplied
while the induction is withheld, and the other way round.

Binary operators always reduce modulo a stated modulus. Without that, a depth
eight chain produces a thirty digit integer and the depth curve becomes a
measurement of digit length. With it, answers stay one to four digits at every
depth, so depth is the only thing that changes along the curve.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

import re

from src.opgraph.opdef import Call, Operator, Var, serialize_all
from src.opgraph.plan import Plan, Step, serialize_plan
from src.skillacq.systems import GLYPHS, NAME_SYLLABLES

# The equals sign is dropped from the glyph pool because a worked example is
# written "7 @ 4 = 51", and an operator also written = would make that line
# ambiguous to a reader and to the model.
OP_GLYPHS = [g for g in GLYPHS if g != "="]

X, Y, N, V, S = Var("x"), Var("y"), Var("n"), Var("v"), Var("s")


def copyable(answer: str, text: str) -> bool:
    """True when the answer stands alone in the question and could be echoed."""
    return re.search(rf"(?<![\w.]){re.escape(answer)}(?![\w.])", text) is not None


def _reject_copyable(build, rng: random.Random, tries: int = 60):
    """Resample a question until its answer cannot be read out of its own text.

    Without this a depth eight chain over small integers hands back an answer
    that also appears as an operand often enough to put a floor under every
    condition, and the floor would be echoing rather than composing.
    """
    last = None
    for _ in range(tries):
        item = build(rng)
        last = item
        if not copyable(item.gold, item.text):
            return item
    return last


def _word(rng: random.Random, k: int = 2) -> str:
    return "".join(rng.choice(NAME_SYLLABLES) for _ in range(k))


# ------------------------------------------------------------------- pages

@dataclass
class Page:
    """One textbook page and the operators it defines."""

    key: str
    text: str
    ops: list[Operator] = field(default_factory=list)


def _binop_page(rng: random.Random, glyph: str, style: int = 0) -> Page:
    name = _word(rng).capitalize()
    a = rng.choice([2, 3, 4, 5])
    b = rng.choice([2, 3, 6, 7])
    c = rng.choice([1, 2, 5, 10])
    m = rng.choice([100, 1000])
    form = rng.choice(["linear", "square_first", "diff_scaled", "guarded"])
    if form == "linear":
        inner = Call("+", (Call("*", (a, X)), Call("*", (b, Y)), c))
        rule = (f"To evaluate x {glyph} y, multiply x by {a}, multiply y by {b}, "
                f"add the two products, then add {c}.")
    elif form == "square_first":
        inner = Call("-", (Call("+", (Call("*", (X, X)), Call("*", (b, Y)))), c))
        rule = (f"To evaluate x {glyph} y, square x, add {b} times y, "
                f"then subtract {c}.")
    elif form == "diff_scaled":
        inner = Call("+", (Call("*", (a, Call("-", (X, Y)))), c))
        rule = (f"To evaluate x {glyph} y, subtract y from x, multiply that "
                f"difference by {a}, then add {c}.")
    else:
        inner = Call("if", (Call(">=", (X, Y)), Call("+", (X, c)), Call("*", (b, Y))))
        rule = (f"To evaluate x {glyph} y, first compare. If x is at least y, the "
                f"result is x plus {c}. Otherwise the result is {b} times y.")
    body = Call("%", (inner, m))
    op = Operator(glyph, ("x", "y"), body)
    right = rng.random() < 0.5
    pair = ((7, 4), (12, 5)) if style == 0 else ((5, 9), (8, 3))
    op = Operator(glyph, ("x", "y"), body,
                  examples=tuple((a, op(*a)) for a in pair),
                  assoc="right" if right else "left")
    assoc = "right to left" if right else "left to right"
    if style == 0:
        text = "\n".join([
            f"The {name} System.",
            "",
            f"The {name} system introduces an operator written {glyph}. It combines "
            f"two whole numbers and produces a whole number.",
            rule,
            f"Every result in this system is reduced modulo {m}. After computing a "
            f"value, divide it by {m} and keep only the remainder.",
            f"When an expression contains more than one {glyph} and no parentheses, "
            f"{glyph} associates {assoc}. "
            f"Parentheses, where written, are evaluated first.",
            f"Worked example: 7 {glyph} 4 = {op(7, 4)}.",
            f"Worked example: 12 {glyph} 5 = {op(12, 5)}.",
        ])
    else:
        text = "\n".join([
            f"Notes on {name} arithmetic.",
            "",
            f"Bracketing binds first. A run of {glyph} with no brackets is read "
            f"{assoc}.",
            f"Take the remainder on division by {m} at the end, so the value "
            f"reported always lies below {m}.",
            f"Here {glyph} is a sign for a rule on pairs of whole numbers, and "
            f"the rule is this. Given {rule[len('To evaluate '):]}",
            f"For instance {pair[0][0]} {glyph} {pair[0][1]} comes to {op(*pair[0])}.",
            f"For instance {pair[1][0]} {glyph} {pair[1][1]} comes to {op(*pair[1])}.",
        ])
    p = Page(f"binop:{glyph}", text, [op])
    p.right_assoc = right  # type: ignore[attr-defined]
    p.glyph = glyph  # type: ignore[attr-defined]
    return p


def _units_page(rng: random.Random, style: int = 0) -> Page:
    name = _word(rng).capitalize()
    base, mid, big = _word(rng), _word(rng), _word(rng)
    k1 = rng.choice([4, 5, 8, 12, 16])
    k2 = rng.choice([3, 6, 10, 20])
    e1, e2 = (3, 2) if style == 0 else (6, 4)
    mid_op = Operator(mid, ("n",), Call("*", (N, k1)), examples=(((e1,), e1 * k1),))
    big_op = Operator(big, ("n",), Call("*", (N, k1 * k2)),
                      examples=(((e2,), e2 * k1 * k2),))
    if style == 1:
        text = "\n".join([
            f"{name}: a note on length.",
            "",
            f"Multiply by {k1} to turn a {mid} count into {base}; multiply by "
            f"{k1 * k2} to turn a {big} count into {base}.",
            f"Three units are in use. The small one is the {base}, the middle "
            f"one the {mid}, the large one the {big}.",
            f"The middle unit is {k1} of the small. The large unit is {k2} of the "
            f"middle.",
            f"So {e1} {mid} comes to {e1 * k1} {base}.",
            f"So {e2} {big} comes to {e2 * k1 * k2} {base}.",
        ])
        p = Page("units", text, [mid_op, big_op])
        p.base, p.mid, p.big = base, mid, big  # type: ignore[attr-defined]
        return p
    text = "\n".join([
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
    p = Page("units", text, [mid_op, big_op])
    p.base, p.mid, p.big = base, mid, big  # type: ignore[attr-defined]
    return p


def _procedure_page(rng: random.Random, breadth: int, style: int = 0) -> Page:
    name = _word(rng).capitalize()
    attr = _word(rng)
    flags = []
    used: set = set()
    while len(flags) < breadth:
        w = _word(rng)
        if w in used:
            continue
        used.add(w)
        flags.append((w, rng.choice([-10, -5, 5, 10, 15])))
    cutoff = rng.choice([45, 55, 65])
    params = ("v",) + tuple(f"f{i + 1}" for i in range(breadth))
    terms = [V] + [Call("if", (Var(f"f{i + 1}"), d, 0)) for i, (_, d) in enumerate(flags)]
    score_body = Call("+", tuple(terms)) if len(terms) > 1 else V
    score = Operator("score", params, score_body)
    ex_flags = tuple(bool((i % 2) == (0 if style == 0 else 1))
                     for i in range(breadth))
    ex_base = 50 if style == 0 else 42
    score = Operator("score", params, score_body,
                     examples=(((ex_base,) + ex_flags,
                                score(ex_base, *ex_flags)),))
    decide = Operator("decide", ("s",),
                      Call("if", (Call(">=", (S, cutoff)), "accepted", "refused")),
                      examples=(((cutoff,), "accepted"), ((cutoff - 1,), "refused")))
    cond_lines = []
    for w, d in flags:
        verb = "add" if d > 0 else "subtract"
        if style == 0:
            cond_lines.append(f"If the application is marked {w}, {verb} {abs(d)}.")
        else:
            cond_lines.append(f"Marked {w}? Then {verb} {abs(d)}.")
    ex_desc = ", ".join(("marked " if f else "not marked ") + flags[i][0]
                        for i, f in enumerate(ex_flags))
    if style == 0:
        text = "\n".join([
            f"The {name} assessment.",
            "",
            f"Each application carries a {attr} value, a whole number. The "
            f"assessment starts from that value and adjusts it.",
            f"The adjustments are applied in the order written here, and every one "
            f"whose condition holds is applied.",
            *cond_lines,
            f"An application is accepted when its adjusted value is at least "
            f"{cutoff}, and refused otherwise.",
            f"Worked example: a {attr} value of {ex_base}, {ex_desc}, "
            f"adjusts to {score(ex_base, *ex_flags)}.",
        ])
    else:
        text = "\n".join([
            f"{name}: how an application is judged.",
            "",
            f"Work down the list below. Apply every line whose condition is met, "
            f"in the order printed.",
            *cond_lines,
            f"The starting number is the {attr} value on the application, which is "
            f"a whole number.",
            f"Refuse the application if the number you end on is under {cutoff}. "
            f"Otherwise accept it.",
            f"Say the {attr} value is {ex_base} and the application is {ex_desc}. "
            f"The number you end on is {score(ex_base, *ex_flags)}.",
        ])
    p = Page("procedure", text, [score, decide])
    p.attr, p.flags, p.cutoff = attr, flags, cutoff  # type: ignore[attr-defined]
    return p


# ------------------------------------------------------------------- worlds

@dataclass
class World:
    seed: int
    pages: list[Page]
    order: list[int]

    @property
    def ops(self) -> dict[str, Operator]:
        return {o.symbol: o for p in self.pages for o in p.ops}

    def page_of(self, symbol: str) -> Page:
        for p in self.pages:
            if any(o.symbol == symbol for o in p.ops):
                return p
        raise KeyError(symbol)

    def shuffled_pages(self) -> list[Page]:
        return [self.pages[i] for i in self.order]

    def context(self, keys=None) -> str:
        pages = [p for p in self.shuffled_pages() if keys is None or p.key in keys]
        return "".join(" <|doc|> " + p.text for p in pages)


def make_world(seed: int, breadth: int = 3, style: int = 0) -> World:
    """One invented world. style 1 rewrites every page in different prose.

    The two styles state exactly the same rules and imply exactly the same
    operators. Training only ever sees style 0, so induction on style 1 asks
    whether the induction step reads a page or matches a template.
    """
    rng = random.Random(seed * 7919 + 13)
    g1, g2 = rng.sample(OP_GLYPHS, 2)
    pages = [_binop_page(rng, g1, style), _binop_page(rng, g2, style),
             _units_page(rng, style), _procedure_page(rng, breadth, style)]
    order = list(range(len(pages)))
    rng.shuffle(order)
    return World(seed, pages, order)


# ---------------------------------------------------------------- questions

@dataclass
class Item:
    """One question with everything needed to grade any condition on it."""

    world: World
    kind: str
    depth: int
    text: str
    gold: str
    plan: Plan
    pages: list[str]
    symbols: list[str]


def _steps_from_tree(node, ops, counter, steps):
    """Post order emission. Returns the temporary or literal holding the value."""
    if isinstance(node, int):
        return node
    sym, kids = node
    args = [_steps_from_tree(k, ops, counter, steps) for k in kids]
    counter[0] += 1
    t = f"t{counter[0]}"
    steps.append(Step(t, sym, tuple(args)))
    return t


def _eval_tree(node, ops):
    if isinstance(node, int):
        return node
    sym, kids = node
    return ops[sym](*[_eval_tree(k, ops) for k in kids])


def _plan_for(tree, ops) -> Plan:
    steps: list[Step] = []
    last = _steps_from_tree(tree, ops, [0], steps)
    return Plan(tuple(steps), str(last))


def _render_tree(node, top: bool = True) -> str:
    if isinstance(node, int):
        return str(node)
    sym, kids = node
    inner = f"{_render_tree(kids[0], False)} {sym} {_render_tree(kids[1], False)}"
    return inner if top else f"({inner})"


def seq_flat(world: World, rng: random.Random, depth: int) -> Item:
    """A chain of one operator written without parentheses, depth applications."""
    return _reject_copyable(lambda r: _seq_flat(world, r, depth), rng)


def _seq_flat(world: World, rng: random.Random, depth: int) -> Item:
    page = rng.choice([p for p in world.pages if p.key.startswith("binop:")])
    g = page.glyph  # type: ignore[attr-defined]
    vals = [rng.randint(1, 12) for _ in range(depth + 1)]
    if page.right_assoc:  # type: ignore[attr-defined]
        tree: object = vals[-1]
        for v in reversed(vals[:-1]):
            tree = (g, [v, tree])
    else:
        tree = vals[0]
        for v in vals[1:]:
            tree = (g, [tree, v])
    ops = world.ops
    text = "Evaluate " + f" {g} ".join(str(v) for v in vals) + "."
    return Item(world, "sequential", depth, text, str(_eval_tree(tree, ops)),
                _plan_for(tree, ops), [page.key], [g])


def seq_paren(world: World, rng: random.Random, depth: int) -> Item:
    """A parenthesised tree over a single operator, depth applications."""
    return _reject_copyable(lambda r: _seq_paren(world, r, depth), rng)


def _seq_paren(world: World, rng: random.Random, depth: int) -> Item:
    page = rng.choice([p for p in world.pages if p.key.startswith("binop:")])
    g = page.glyph  # type: ignore[attr-defined]
    tree = _random_tree(rng, depth, [g])
    ops = world.ops
    return Item(world, "sequential_paren", depth, f"Evaluate {_render_tree(tree)}.",
                str(_eval_tree(tree, ops)), _plan_for(tree, ops), [page.key], [g])


def _random_tree(rng: random.Random, n_apps: int, symbols: list[str]):
    """A binary tree with exactly n_apps internal nodes, symbols drawn at random."""
    node: object = (rng.choice(symbols), [rng.randint(1, 12), rng.randint(1, 12)])
    for _ in range(n_apps - 1):
        node = _graft(node, rng, symbols)
    return node


def _graft(node, rng: random.Random, symbols: list[str]):
    """Replace one uniformly chosen integer leaf with a new application."""
    leaves: list = []

    def walk(nd, path):
        if isinstance(nd, int):
            leaves.append(tuple(path))
            return
        for i, k in enumerate(nd[1]):
            walk(k, path + [i])

    walk(node, [])
    target = rng.choice(leaves)
    new = (rng.choice(symbols), [rng.randint(1, 12), rng.randint(1, 12)])

    def rebuild(nd, path, idx):
        if idx == len(path):
            return new
        sym, kids = nd
        kids = list(kids)
        kids[path[idx]] = rebuild(kids[path[idx]], path, idx + 1)
        return (sym, kids)

    return rebuild(node, target, 0)


def novel(world: World, rng: random.Random, depth: int) -> Item:
    """A parenthesised tree that requires both binary operators.

    Each operator is defined on its own page and every worked example on that
    page uses it alone. A question that needs both is a composition of two
    procedures learned independently and never seen combined.
    """
    return _reject_copyable(lambda r: _novel(world, r, depth), rng)


def _novel(world: World, rng: random.Random, depth: int) -> Item:
    if depth < 2:
        raise ValueError("novel composition needs at least two applications")
    bpages = [p for p in world.pages if p.key.startswith("binop:")]
    syms = [p.glyph for p in bpages]  # type: ignore[attr-defined]
    for _ in range(200):
        tree = _random_tree(rng, depth, syms)
        used = _symbols_in(tree)
        if len(used) == 2:
            break
    else:
        raise RuntimeError("could not build a mixed tree")
    ops = world.ops
    return Item(world, "novel", depth, f"Evaluate {_render_tree(tree)}.",
                str(_eval_tree(tree, ops)), _plan_for(tree, ops),
                [p.key for p in bpages], sorted(used))


def _symbols_in(node) -> set:
    if isinstance(node, int):
        return set()
    sym, kids = node
    out = {sym}
    for k in kids:
        out |= _symbols_in(k)
    return out


def breadth_item(world: World, rng: random.Random, breadth: int) -> Item:
    """A procedure question integrating `breadth` simultaneous conditions.

    The answer is the adjusted numeric value rather than the accept or refuse
    decision, so the curve has no chance floor to climb over.
    """
    return _reject_copyable(lambda r: _breadth_item(world, r, breadth), rng)


def _breadth_item(world: World, rng: random.Random, breadth: int) -> Item:
    page = world.page_of("score")
    flags = page.flags  # type: ignore[attr-defined]
    assert len(flags) == breadth
    base = rng.randint(20, 80)
    bits = [rng.random() < 0.5 for _ in flags]
    ops = world.ops
    desc = " ".join(
        f"It is {'marked' if b else 'not marked'} {flags[i][0]}."
        for i, b in enumerate(bits))
    text = (f"An application has a {page.attr} value of {base}. {desc} "  # type: ignore[attr-defined]
            f"What is its adjusted value?")
    plan = Plan((Step("t1", "score", (base,) + tuple(bits)),), "t1")
    return Item(world, "breadth", breadth, text,
                str(ops["score"](base, *bits)), plan, [page.key], ["score"])


def units_item(world: World, rng: random.Random) -> Item:
    """A single unit conversion, one operator application."""
    return _reject_copyable(lambda r: _units_item(world, r), rng)


def _units_item(world: World, rng: random.Random) -> Item:
    page = next(p for p in world.pages if p.key == "units")
    unit = rng.choice([page.mid, page.big])  # type: ignore[attr-defined]
    q = rng.randint(2, 15)
    ops = world.ops
    text = f"How many {page.base} are {q} {unit}?"  # type: ignore[attr-defined]
    plan = Plan((Step("t1", unit, (q,)),), "t1")
    return Item(world, "units", 1, text, str(ops[unit](q)), plan, ["units"], [unit])


def decide_item(world: World, rng: random.Random) -> Item:
    """Score then decide: two operators, but both defined on the same page."""
    page = world.page_of("score")
    flags = page.flags  # type: ignore[attr-defined]
    base = rng.randint(20, 80)
    bits = [rng.random() < 0.5 for _ in flags]
    ops = world.ops
    desc = " ".join(
        f"It is {'marked' if b else 'not marked'} {flags[i][0]}."
        for i, b in enumerate(bits))
    text = (f"An application has a {page.attr} value of {base}. {desc} "  # type: ignore[attr-defined]
            f"Is it accepted or refused?")
    plan = Plan((Step("t1", "score", (base,) + tuple(bits)),
                 Step("t2", "decide", ("t1",))), "t2")
    gold = ops["decide"](ops["score"](base, *bits))
    return Item(world, "same_page_pair", 2, text, str(gold), plan,
                [page.key], ["score", "decide"])


# ------------------------------------------------------------ episode sets

TRAIN_KINDS = ("sequential", "sequential_paren", "breadth", "units")


def training_items(seed: int, rng: random.Random) -> list[Item]:
    """The questions both conditions are trained on: single operator only.

    Nothing here uses two distinct induced symbols in one plan, and nothing
    here goes past depth three. Everything measured later is therefore an
    extrapolation for both conditions equally.
    """
    breadth = rng.choice([1, 2, 3])
    w = make_world(seed, breadth=breadth)
    out = [seq_flat(w, rng, rng.choice([1, 2, 3])),
           seq_paren(w, rng, rng.choice([2, 3])),
           breadth_item(w, rng, breadth),
           units_item(w, rng)]
    return out


def induction_examples(seed: int, rng: random.Random) -> list[tuple[str, str]]:
    """(page text, gold operator text) for every page of one world."""
    w = make_world(seed, breadth=rng.choice([1, 2, 3]))
    return [(p.text, serialize_all(p.ops)) for p in w.pages]


def plan_example(item: Item) -> str:
    return serialize_plan(item.plan)
