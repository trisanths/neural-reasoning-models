"""Invented finite algebraic structures with a reference implementation.

A universe starts here. We sample a signature (an invented name for the objects,
one or two operations written with invented glyphs, one invented relation) and a
finite carrier of invented element names, then we sample a concrete model over
that carrier from a menu of algebraic templates.

Sampling the model first, rather than sampling a list of axioms and hoping they
can be satisfied together, is what buys consistency and decidability:

* Consistency is by construction. The declared axiom set is exactly the set of
  menu axioms that the sampled model satisfies, checked exhaustively. A set of
  sentences with a model cannot be contradictory, so no pair of declared axioms
  can conflict.
* Decidability is by finiteness. The carrier has three to six elements, so every
  axiom, every relation instance and every equation between closed terms is
  settled by enumerating the carrier.

The `Structure` class is the reference implementation. It parses an expression
in the invented notation, evaluates it to a carrier element, and decides any
stated relation. Everything downstream (theorems, worked examples, exercise
answers) is computed here and never written by hand.
"""

from __future__ import annotations

import itertools
import random
import re
from dataclasses import dataclass, field

# Glyphs for operations. "^" and "'" are reserved for powers and inverses, and
# parentheses are reserved for grouping, so none of them appear here.
OP_GLYPHS = ["@", "#", "$", "%", "&", "*", "~", "|", "!", "?", "<>", "><",
             "+", "-", ":", ";", "=|", "|="]

# Glyphs for the relation. Multi character glyphs are fine; the expression
# tokenizer matches longest first.
REL_GLYPHS = ["<|", "|>", "-<", ">-", "~>", "<~", "=<", "::", "%%", "<<", ">>"]

SYLLABLES = [
    "ka", "vor", "mi", "zel", "tu", "bra", "qen", "sol", "dri", "fex",
    "lum", "nak", "pyr", "tez", "ovi", "wren", "xil", "yuk", "zam", "clo",
    "thra", "gel", "sib", "morn", "vash", "keld", "pon", "hurn", "azt", "reld",
    "glim", "vex", "korr", "duth", "espa", "fal", "grix", "hob", "isk", "jen",
    "lorn", "mux", "nyr", "opal", "quil", "rast", "shen", "tarn", "umb", "vint",
]

OP_VERBS = ["blending", "welding", "folding", "meshing", "binding", "grafting",
            "layering", "twining", "casting", "seaming", "knotting", "fusing"]

REL_VERBS = ["precedes", "supports", "dominates", "refines", "covers",
            "answers to", "yields to", "underlies", "shadows", "governs"]


def coin_word(rng: random.Random, syllables: int = 2, used: set | None = None) -> str:
    """Invent a pronounceable word not already handed out."""
    for _ in range(200):
        w = "".join(rng.choice(SYLLABLES) for _ in range(syllables))
        if used is None or w not in used:
            if used is not None:
                used.add(w)
            return w
    raise RuntimeError("ran out of invented words")


# ---------------------------------------------------------------------------
# Model templates
# ---------------------------------------------------------------------------
#
# Each template returns (size, primary_table, secondary_table_or_None, tag).
# Tables are square lists of lists of integer indices into the carrier.


def _cyclic(n: int):
    """The cyclic group of order n. Associative, commutative, all inverses."""
    return [[(i + j) % n for j in range(n)] for i in range(n)]


def _mult_mod(n: int):
    """Multiplication modulo n. Associative and commutative, few inverses."""
    return [[(i * j) % n for j in range(n)] for i in range(n)]


def _chain_meet(n: int):
    """Minimum on a chain. A semilattice: associative, commutative, idempotent."""
    return [[min(i, j) for j in range(n)] for i in range(n)]


def _chain_join(n: int):
    """Maximum on a chain, the order dual of the meet."""
    return [[max(i, j) for j in range(n)] for i in range(n)]


def _left_projection(n: int):
    """x op y = x. Associative and idempotent, not commutative, no identity."""
    return [[i for _ in range(n)] for i in range(n)]


def _right_projection(n: int):
    return [[j for j in range(n)] for _ in range(n)]


def _truncated_difference(n: int):
    """max(x - y, 0). Deliberately non-associative, to vary the axiom profile."""
    return [[max(i - j, 0) for j in range(n)] for i in range(n)]


def _bounded_sum(n: int):
    """min(x + y, n - 1). Associative and commutative with an identity at 0."""
    return [[min(i + j, n - 1) for j in range(n)] for i in range(n)]


def _symmetric_group_3():
    """S_3 as permutations of three points. Associative, non-commutative group."""
    perms = sorted(itertools.permutations(range(3)))
    index = {p: k for k, p in enumerate(perms)}
    table = []
    for p in perms:
        row = []
        for q in perms:
            comp = tuple(p[q[k]] for k in range(3))
            row.append(index[comp])
        table.append(row)
    return table


def _klein_four():
    """The Klein four group. Every element is its own inverse."""
    table = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            table[i][j] = i ^ j
    return table


def _divisor_lattice(n: int):
    """Divisors of n under gcd and lcm, a distributive lattice.

    Unlike a chain, a lattice on the divisors of 6 or 12 can send a pair to a
    third element: the meet of 2 and 3 is 1. That matters, because an operation
    that always returns one of its own arguments makes every evaluation
    exercise answerable by copying, and the necessity filter throws all of them
    away. Chain meets and joins are kept as second operations only.
    """
    els = [d for d in range(1, n + 1) if n % d == 0]
    idx = {v: k for k, v in enumerate(els)}

    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    meet = [[idx[gcd(a, b)] for b in els] for a in els]
    join = [[idx[a * b // gcd(a, b)] for b in els] for a in els]
    return meet, join


def _powerset_lattice(k: int):
    """Subsets of a k element set under intersection and union."""
    n = 1 << k
    meet = [[i & j for j in range(n)] for i in range(n)]
    join = [[i | j for j in range(n)] for i in range(n)]
    return meet, join


def build_catalogue() -> list[dict]:
    """Every model the sampler can reach, as an explicit list.

    An explicit catalogue rather than rejection sampling, because the sibling
    construction has to ask for every model of a given carrier size and
    operation count and must never come up empty.

    Two families are deliberately barred from the first operation: chain meets
    and joins, and the two projections. Each of them always returns one of its
    own arguments, so every evaluation over them is answerable by copying and
    the necessity filter in `exercises` discards the lot. They appear as second
    operations, where they still carry absorption, order compatibility and the
    rest of their structure.
    """
    out: list[dict] = []

    def add(size, primary, secondary, tag):
        out.append({"size": size, "primary": primary, "secondary": secondary,
                    "tag": tag})

    for n in (3, 4, 5, 6):
        add(n, _cyclic(n), None, f"cyclic_{n}")
        add(n, _mult_mod(n), None, f"mult_mod_{n}")
        add(n, _bounded_sum(n), None, f"bounded_sum_{n}")
        add(n, _truncated_difference(n), None, f"truncated_difference_{n}")
        add(n, _cyclic(n), _mult_mod(n), f"ring_mod_{n}")
        add(n, _mult_mod(n), _cyclic(n), f"mult_over_add_mod_{n}")
        add(n, _cyclic(n), _chain_join(n), f"cyclic_with_join_{n}")
        add(n, _mult_mod(n), _chain_meet(n), f"mult_with_meet_{n}")
        add(n, _bounded_sum(n), _chain_meet(n), f"bounded_sum_with_meet_{n}")
        add(n, _truncated_difference(n), _chain_join(n),
            f"truncated_difference_with_join_{n}")
        add(n, _cyclic(n), _left_projection(n), f"cyclic_with_left_{n}")
        add(n, _bounded_sum(n), _right_projection(n), f"bounded_sum_with_right_{n}")

    add(6, _symmetric_group_3(), None, "symmetric_3")
    add(6, _symmetric_group_3(), _chain_join(6), "symmetric_3_with_join")
    add(4, _klein_four(), None, "klein_four")
    add(4, _klein_four(), _chain_meet(4), "klein_four_with_meet")

    for n, size in ((6, 4), (12, 6)):
        meet, join = _divisor_lattice(n)
        add(size, meet, None, f"divisor_meet_{n}")
        add(size, join, None, f"divisor_join_{n}")
        add(size, meet, join, f"divisor_lattice_{n}")
        add(size, join, meet, f"divisor_lattice_{n}_dual")

    meet, join = _powerset_lattice(2)
    add(4, meet, None, "powerset_2_meet")
    add(4, join, None, "powerset_2_join")
    add(4, meet, join, "powerset_2")
    add(4, join, meet, "powerset_2_dual")
    return out


CATALOGUE = build_catalogue()


def models_matching(size: int, two_ops: bool) -> list[dict]:
    """Every catalogued model with this carrier size and operation count."""
    return [m for m in CATALOGUE
            if m["size"] == size and (m["secondary"] is not None) == two_ops]


def sample_model(rng: random.Random) -> dict:
    """Choose a concrete finite model. Returns tables plus a provenance tag."""
    return rng.choice(CATALOGUE)


# ---------------------------------------------------------------------------
# Relations
# ---------------------------------------------------------------------------

RELATION_KINDS = ["order_from_primary", "order_from_index", "divides",
                  "commutes", "absorbed_by"]


def _relation_pairs(kind: str, size: int, primary, secondary) -> set:
    pairs = set()
    if kind == "order_from_primary":
        # x R y exactly when x op y = x, the canonical order of a meet semilattice.
        for i in range(size):
            for j in range(size):
                if primary[i][j] == i:
                    pairs.add((i, j))
    elif kind == "order_from_index":
        for i in range(size):
            for j in range(size):
                if i <= j:
                    pairs.add((i, j))
    elif kind == "divides":
        for i in range(size):
            for j in range(size):
                if any(primary[i][k] == j for k in range(size)):
                    pairs.add((i, j))
    elif kind == "commutes":
        for i in range(size):
            for j in range(size):
                if primary[i][j] == primary[j][i]:
                    pairs.add((i, j))
    else:  # absorbed_by
        table = secondary if secondary is not None else primary
        for i in range(size):
            for j in range(size):
                if table[i][j] == j:
                    pairs.add((i, j))
    return pairs


# ---------------------------------------------------------------------------
# The structure itself
# ---------------------------------------------------------------------------


class ParseError(ValueError):
    """Raised when an expression is not well formed in this system's notation."""


@dataclass
class Structure:
    """A finite algebra with invented names, plus the machinery to compute in it.

    All computation goes through `evaluate` and `decide`, and every downstream
    answer in the universe is produced by one of them.
    """

    system_name: str
    object_name: str
    object_plural: str
    elements: list[str]
    op_glyphs: list[str]
    op_names: list[str]
    tables: list[list[list[int]]]
    rel_glyph: str
    rel_name: str
    rel_kind: str
    rel_pairs: set
    tag: str
    seed: int = 0

    index: dict = field(init=False)

    def __post_init__(self):
        self.index = {name: i for i, name in enumerate(self.elements)}

    # -- basic accessors ---------------------------------------------------

    @property
    def size(self) -> int:
        return len(self.elements)

    def op(self, k: int, i: int, j: int) -> int:
        return self.tables[k][i][j]

    def name(self, i: int) -> str:
        return self.elements[i]

    def decide(self, i: int, j: int) -> bool:
        """Decide the invented relation on a pair. Total, because the carrier is finite."""
        return (i, j) in self.rel_pairs

    # -- notation ----------------------------------------------------------

    @property
    def has_two_ops(self) -> bool:
        return len(self.op_glyphs) == 2

    def identity_of(self, k: int) -> int | None:
        """The two sided identity of operation k, or None when there is none."""
        for e in range(self.size):
            if all(self.op(k, e, x) == x and self.op(k, x, e) == x
                   for x in range(self.size)):
                return e
        return None

    def inverse_of(self, i: int, k: int = 0) -> int | None:
        e = self.identity_of(k)
        if e is None:
            return None
        for j in range(self.size):
            if self.op(k, i, j) == e and self.op(k, j, i) == e:
                return j
        return None

    @property
    def has_inverses(self) -> bool:
        """True when every element has a two sided inverse under the first operation."""
        if self.identity_of(0) is None:
            return False
        return all(self.inverse_of(i, 0) is not None for i in range(self.size))

    # -- parsing and evaluation -------------------------------------------

    def _token_pattern(self) -> re.Pattern:
        glyphs = sorted(self.op_glyphs, key=len, reverse=True)
        parts = [re.escape(g) for g in glyphs]
        parts += [re.escape(self.rel_glyph)]
        parts += [r"\(", r"\)", r"'", r"\^\d+"]
        parts += [r"[A-Za-z_][A-Za-z_0-9]*"]
        return re.compile("|".join(parts))

    def tokenize(self, text: str) -> list[str]:
        pat = self._token_pattern()
        toks: list[str] = []
        pos = 0
        s = text.strip()
        while pos < len(s):
            if s[pos].isspace():
                pos += 1
                continue
            m = pat.match(s, pos)
            if not m:
                raise ParseError(f"cannot read {s[pos:]!r} in {self.system_name}")
            toks.append(m.group(0))
            pos = m.end()
        return toks

    def parse(self, text: str):
        """Parse an expression into a tuple tree, using this system's notation.

        Grammar, with the precedence the textbook states:

            expr   := term ( op0 term )*        left associative
            term   := factor ( op1 factor )*    left associative, binds tighter
            factor := atom ( "'" | "^k" )*
            atom   := element | "(" expr ")"
        """
        toks = self.tokenize(text)
        pos = 0

        def peek():
            return toks[pos] if pos < len(toks) else None

        def eat(tok=None):
            nonlocal pos
            if pos >= len(toks):
                raise ParseError(f"expression ended early: {text!r}")
            got = toks[pos]
            if tok is not None and got != tok:
                raise ParseError(f"expected {tok!r} got {got!r} in {text!r}")
            pos += 1
            return got

        def atom():
            t = peek()
            if t == "(":
                eat("(")
                node = expr()
                eat(")")
                return node
            if t is None:
                raise ParseError(f"expression ended early: {text!r}")
            if t in self.index:
                eat()
                return ("el", self.index[t])
            raise ParseError(f"{t!r} is not a {self.object_name} of {self.system_name}")

        def factor():
            node = atom()
            while True:
                t = peek()
                if t == "'":
                    eat("'")
                    node = ("inv", node)
                elif t is not None and t.startswith("^"):
                    eat()
                    node = ("pow", node, int(t[1:]))
                else:
                    break
            return node

        def term():
            node = factor()
            if self.has_two_ops:
                while peek() == self.op_glyphs[1]:
                    eat()
                    node = ("op", 1, node, factor())
            return node

        def expr():
            node = term()
            while peek() == self.op_glyphs[0]:
                eat()
                node = ("op", 0, node, term())
            return node

        tree = expr()
        if pos != len(toks):
            raise ParseError(f"trailing input {toks[pos:]!r} in {text!r}")
        return tree

    def eval_tree(self, node) -> int:
        kind = node[0]
        if kind == "el":
            return node[1]
        if kind == "op":
            _, k, a, b = node
            return self.op(k, self.eval_tree(a), self.eval_tree(b))
        if kind == "inv":
            v = self.eval_tree(node[1])
            inv = self.inverse_of(v, 0)
            if inv is None:
                raise ParseError(f"{self.name(v)} has no inverse in {self.system_name}")
            return inv
        if kind == "pow":
            _, a, k = node
            if k < 1:
                raise ParseError("powers start at one in this notation")
            v = self.eval_tree(a)
            acc = v
            for _ in range(k - 1):
                acc = self.op(0, acc, v)
            return acc
        raise ParseError(f"bad node {node!r}")

    def evaluate(self, text: str) -> str:
        """Evaluate a written expression and return the element name it denotes."""
        return self.name(self.eval_tree(self.parse(text)))

    def render_tree(self, node) -> str:
        """Write a parse tree back out in this system's notation."""
        kind = node[0]
        if kind == "el":
            return self.name(node[1])
        if kind == "op":
            _, k, a, b = node
            return f"({self.render_tree(a)} {self.op_glyphs[k]} {self.render_tree(b)})"
        if kind == "inv":
            return f"{self.render_tree(node[1])}'"
        if kind == "pow":
            return f"{self.render_tree(node[1])}^{node[2]}"
        raise ParseError(f"bad node {node!r}")

    def eval_trace(self, text: str) -> list[dict]:
        """Every intermediate step of an evaluation, innermost first.

        Worked examples in the textbook are built from this and re-derived from
        it during verification, so a printed example can never drift away from
        what the operation tables actually say.
        """
        steps: list[dict] = []

        def walk(node) -> int:
            kind = node[0]
            if kind == "el":
                return node[1]
            if kind == "op":
                _, k, a, b = node
                left, right = walk(a), walk(b)
                value = self.op(k, left, right)
                steps.append({
                    "expression": f"{self.name(left)} {self.op_glyphs[k]} {self.name(right)}",
                    "value": self.name(value),
                    "reason": f"the table for {self.op_glyphs[k]}",
                })
                return value
            if kind == "inv":
                inner = walk(node[1])
                value = self.inverse_of(inner, 0)
                if value is None:
                    raise ParseError(f"{self.name(inner)} has no inverse")
                steps.append({"expression": f"{self.name(inner)}'",
                              "value": self.name(value),
                              "reason": "reversal under the first operation"})
                return value
            if kind == "pow":
                _, a, k = node
                base = walk(a)
                acc = base
                for _ in range(k - 1):
                    nxt = self.op(0, acc, base)
                    steps.append({
                        "expression": f"{self.name(acc)} {self.op_glyphs[0]} {self.name(base)}",
                        "value": self.name(nxt),
                        "reason": f"the table for {self.op_glyphs[0]}"})
                    acc = nxt
                return acc
            raise ParseError(f"bad node {node!r}")

        walk(self.parse(text))
        return steps

    def decide_written(self, text: str) -> bool:
        """Decide a written relation statement of the form 'lhs REL rhs'."""
        parts = text.split(self.rel_glyph)
        if len(parts) != 2:
            raise ParseError(f"{text!r} is not a single {self.rel_glyph} statement")
        return self.decide(self.eval_tree(self.parse(parts[0])),
                           self.eval_tree(self.parse(parts[1])))

    # -- variants used for the necessity witnesses -------------------------

    def sibling(self, offset: int = 1) -> "Structure":
        """A different system wearing exactly the same names and glyphs.

        The point of this is evidence, not variety. An exercise whose answer is
        the same in this structure and in its sibling cannot be testing anything
        the textbook says, since the two textbooks differ only in content and not
        in surface form. Every exercise we emit must separate the two.
        """
        candidates = [m for m in models_matching(self.size, self.has_two_ops)
                      if m["primary"] != self.tables[0]]
        if not candidates:
            raise RuntimeError(
                f"no sibling model for size {self.size} with "
                f"{len(self.op_glyphs)} operations")
        model = candidates[offset % len(candidates)]
        tables = [model["primary"]]
        if self.has_two_ops:
            tables.append(model["secondary"])
        pairs = _relation_pairs(self.rel_kind, self.size, tables[0],
                                tables[1] if self.has_two_ops else None)
        return Structure(
            system_name=self.system_name, object_name=self.object_name,
            object_plural=self.object_plural, elements=list(self.elements),
            op_glyphs=list(self.op_glyphs), op_names=list(self.op_names),
            tables=[[row[:] for row in t] for t in tables],
            rel_glyph=self.rel_glyph, rel_name=self.rel_name,
            rel_kind=self.rel_kind, rel_pairs=pairs,
            tag=model["tag"] + "_sibling", seed=self.seed ^ (offset << 8),
        )

    def n_siblings(self) -> int:
        """How many distinct rival systems share this exact surface notation."""
        return len([m for m in models_matching(self.size, self.has_two_ops)
                    if m["primary"] != self.tables[0]])

    def as_dict(self) -> dict:
        return {
            "system_name": self.system_name,
            "object_name": self.object_name,
            "object_plural": self.object_plural,
            "elements": list(self.elements),
            "op_glyphs": list(self.op_glyphs),
            "op_names": list(self.op_names),
            "tables": [[row[:] for row in t] for t in self.tables],
            "relation": {"glyph": self.rel_glyph, "name": self.rel_name,
                         "kind": self.rel_kind,
                         "pairs": [[self.elements[i], self.elements[j]]
                                   for i, j in sorted(self.rel_pairs)]},
            "template_tag": self.tag,
            "seed": self.seed,
        }


# ---------------------------------------------------------------------------
# The axiom menu, checked exhaustively
# ---------------------------------------------------------------------------


def _triples(n):
    return itertools.product(range(n), repeat=3)


def _pairs(n):
    return itertools.product(range(n), repeat=2)


def check_closure(s: Structure, k: int):
    for i, j in _pairs(s.size):
        if not 0 <= s.op(k, i, j) < s.size:
            return False, {"x": s.name(i), "y": s.name(j)}
    return True, None


def check_associative(s: Structure, k: int):
    for i, j, m in _triples(s.size):
        if s.op(k, s.op(k, i, j), m) != s.op(k, i, s.op(k, j, m)):
            return False, {"x": s.name(i), "y": s.name(j), "z": s.name(m),
                           "left": s.name(s.op(k, s.op(k, i, j), m)),
                           "right": s.name(s.op(k, i, s.op(k, j, m)))}
    return True, None


def check_commutative(s: Structure, k: int):
    for i, j in _pairs(s.size):
        if s.op(k, i, j) != s.op(k, j, i):
            return False, {"x": s.name(i), "y": s.name(j),
                           "left": s.name(s.op(k, i, j)),
                           "right": s.name(s.op(k, j, i))}
    return True, None


def check_identity(s: Structure, k: int):
    e = s.identity_of(k)
    if e is None:
        return False, {"reason": "no two sided identity exists"}
    return True, {"identity": s.name(e)}


def check_inverses(s: Structure, k: int):
    e = s.identity_of(k)
    if e is None:
        return False, {"reason": "no identity, so inverses are not defined"}
    for i in range(s.size):
        if s.inverse_of(i, k) is None:
            return False, {"x": s.name(i)}
    return True, {"identity": s.name(e)}


def check_idempotent(s: Structure, k: int):
    for i in range(s.size):
        if s.op(k, i, i) != i:
            return False, {"x": s.name(i), "value": s.name(s.op(k, i, i))}
    return True, None


def check_cancellation(s: Structure, k: int):
    for i, j, m in _triples(s.size):
        if s.op(k, i, j) == s.op(k, i, m) and j != m:
            return False, {"x": s.name(i), "y": s.name(j), "z": s.name(m)}
    return True, None


def check_absorbing(s: Structure, k: int):
    """An absorbing element z with z op x = x op z = z for every x."""
    for z in range(s.size):
        if all(s.op(k, z, x) == z and s.op(k, x, z) == z for x in range(s.size)):
            return True, {"absorbing": s.name(z)}
    return False, {"reason": "no absorbing element"}


def check_distributive(s: Structure):
    """Operation one distributes over operation zero, on both sides."""
    if not s.has_two_ops:
        return False, {"reason": "the system has only one operation"}
    for i, j, m in _triples(s.size):
        lhs = s.op(1, i, s.op(0, j, m))
        rhs = s.op(0, s.op(1, i, j), s.op(1, i, m))
        if lhs != rhs:
            return False, {"x": s.name(i), "y": s.name(j), "z": s.name(m),
                           "left": s.name(lhs), "right": s.name(rhs)}
        lhs = s.op(1, s.op(0, j, m), i)
        rhs = s.op(0, s.op(1, j, i), s.op(1, m, i))
        if lhs != rhs:
            return False, {"x": s.name(i), "y": s.name(j), "z": s.name(m),
                           "left": s.name(lhs), "right": s.name(rhs)}
    return True, None


def check_absorption_laws(s: Structure):
    """x op0 (x op1 y) = x and x op1 (x op0 y) = x, the lattice absorption pair."""
    if not s.has_two_ops:
        return False, {"reason": "the system has only one operation"}
    for i, j in _pairs(s.size):
        if s.op(0, i, s.op(1, i, j)) != i:
            return False, {"x": s.name(i), "y": s.name(j),
                           "value": s.name(s.op(0, i, s.op(1, i, j)))}
        if s.op(1, i, s.op(0, i, j)) != i:
            return False, {"x": s.name(i), "y": s.name(j),
                           "value": s.name(s.op(1, i, s.op(0, i, j)))}
    return True, None


def check_rel_reflexive(s: Structure):
    for i in range(s.size):
        if not s.decide(i, i):
            return False, {"x": s.name(i)}
    return True, None


def check_rel_antisymmetric(s: Structure):
    for i, j in _pairs(s.size):
        if i != j and s.decide(i, j) and s.decide(j, i):
            return False, {"x": s.name(i), "y": s.name(j)}
    return True, None


def check_rel_transitive(s: Structure):
    for i, j, m in _triples(s.size):
        if s.decide(i, j) and s.decide(j, m) and not s.decide(i, m):
            return False, {"x": s.name(i), "y": s.name(j), "z": s.name(m)}
    return True, None


def check_rel_total(s: Structure):
    for i, j in _pairs(s.size):
        if not s.decide(i, j) and not s.decide(j, i):
            return False, {"x": s.name(i), "y": s.name(j)}
    return True, None


def check_rel_compatible(s: Structure, k: int):
    """x R y implies (z op x) R (z op y) and (x op z) R (y op z)."""
    for i, j in _pairs(s.size):
        if not s.decide(i, j):
            continue
        for m in range(s.size):
            if not s.decide(s.op(k, m, i), s.op(k, m, j)):
                return False, {"x": s.name(i), "y": s.name(j), "z": s.name(m),
                               "side": "left"}
            if not s.decide(s.op(k, i, m), s.op(k, j, m)):
                return False, {"x": s.name(i), "y": s.name(j), "z": s.name(m),
                               "side": "right"}
    return True, None


AXIOM_MENU = [
    ("closure_first", lambda s: check_closure(s, 0)),
    ("associativity_first", lambda s: check_associative(s, 0)),
    ("commutativity_first", lambda s: check_commutative(s, 0)),
    ("identity_first", lambda s: check_identity(s, 0)),
    ("inverses_first", lambda s: check_inverses(s, 0)),
    ("idempotence_first", lambda s: check_idempotent(s, 0)),
    ("cancellation_first", lambda s: check_cancellation(s, 0)),
    ("absorbing_first", lambda s: check_absorbing(s, 0)),
    ("closure_second", lambda s: check_closure(s, 1) if s.has_two_ops else (False, {"reason": "one operation only"})),
    ("associativity_second", lambda s: check_associative(s, 1) if s.has_two_ops else (False, {"reason": "one operation only"})),
    ("commutativity_second", lambda s: check_commutative(s, 1) if s.has_two_ops else (False, {"reason": "one operation only"})),
    ("identity_second", lambda s: check_identity(s, 1) if s.has_two_ops else (False, {"reason": "one operation only"})),
    ("idempotence_second", lambda s: check_idempotent(s, 1) if s.has_two_ops else (False, {"reason": "one operation only"})),
    ("distributivity", check_distributive),
    ("absorption", check_absorption_laws),
    ("relation_reflexive", check_rel_reflexive),
    ("relation_antisymmetric", check_rel_antisymmetric),
    ("relation_transitive", check_rel_transitive),
    ("relation_total", check_rel_total),
    ("relation_compatible_first", lambda s: check_rel_compatible(s, 0)),
    ("relation_compatible_second", lambda s: check_rel_compatible(s, 1) if s.has_two_ops else (False, {"reason": "one operation only"})),
]

# Axioms that are meaningless when the named operation is absent, so their
# failure should not be reported as a refuted claim about the system.
_SECOND_OP_AXIOMS = {"closure_second", "associativity_second", "commutativity_second",
                     "identity_second", "idempotence_second", "distributivity",
                     "absorption", "relation_compatible_second"}


def axiom_profile(s: Structure) -> dict:
    """Run the whole menu exhaustively. Returns holds, fails, and witnesses."""
    holds: dict = {}
    fails: dict = {}
    for name, fn in AXIOM_MENU:
        ok, witness = fn(s)
        if name in _SECOND_OP_AXIOMS and not s.has_two_ops:
            continue
        if ok:
            holds[name] = witness
        else:
            fails[name] = witness
    return {"holds": holds, "fails": fails}


def consistency_report(s: Structure, profile: dict) -> dict:
    """Confirm the declared axiom set is satisfiable and internally coherent.

    Three separate things are checked. First, every declared axiom is re-verified
    exhaustively against the reference implementation, so the declaration and the
    model agree. Second, no axiom appears in both the declared and the refuted
    list, which would be a direct contradiction. Third, the known implication
    pairs are honoured: an axiom set that claims inverses without an identity, or
    absorption without both operations, would be flagged here even though no
    single check failed.
    """
    problems: list[str] = []
    lookup = dict(AXIOM_MENU)
    for name in profile["holds"]:
        ok, _ = lookup[name](s)
        if not ok:
            problems.append(f"declared axiom {name} does not hold in the model")
    for name in profile["fails"]:
        ok, _ = lookup[name](s)
        if ok:
            problems.append(f"refuted axiom {name} actually holds in the model")
    overlap = set(profile["holds"]) & set(profile["fails"])
    if overlap:
        problems.append(f"axioms both declared and refuted: {sorted(overlap)}")
    implications = [
        ("inverses_first", "identity_first"),
        ("absorption", "closure_second"),
        ("distributivity", "closure_second"),
        ("relation_total", "relation_reflexive"),
    ]
    for premise, conclusion in implications:
        if premise in profile["holds"] and conclusion not in profile["holds"]:
            problems.append(f"{premise} holds but {conclusion} does not, which is impossible")
    return {"ok": not problems, "problems": problems,
            "model_tag": s.tag, "carrier_size": s.size,
            "axioms_declared": len(profile["holds"]),
            "axioms_refuted": len(profile["fails"])}


# ---------------------------------------------------------------------------
# Signature sampling and the public entry point
# ---------------------------------------------------------------------------


def sample_structure(seed: int) -> Structure:
    """Sample a whole invented system, deterministically from the seed."""
    rng = random.Random(seed)
    used: set = set()
    object_name = coin_word(rng, 2, used)
    object_plural = object_name + "s"
    system_name = coin_word(rng, 2, used).capitalize()

    model = sample_model(rng)
    size = model["size"]
    # Two syllables rather than one. With fifty syllables in the pool a single
    # syllable would repeat across universes often enough to inflate the symbol
    # overlap that the novelty audit reports, and the names are what a reader
    # would notice first.
    elements = [coin_word(rng, 2, used) for _ in range(size)]

    glyphs = rng.sample(OP_GLYPHS, 2)
    tables = [model["primary"]]
    op_names = [rng.choice(OP_VERBS)]
    if model["secondary"] is not None:
        tables.append(model["secondary"])
        op_names.append(rng.choice([v for v in OP_VERBS if v != op_names[0]]))
        glyphs = glyphs[:2]
    else:
        glyphs = glyphs[:1]

    rel_kind = rng.choice(RELATION_KINDS)
    rel_glyph = rng.choice(REL_GLYPHS)
    rel_name = rng.choice(REL_VERBS)
    rel_pairs = _relation_pairs(rel_kind, size, tables[0],
                                tables[1] if len(tables) > 1 else None)

    return Structure(
        system_name=system_name, object_name=object_name,
        object_plural=object_plural, elements=elements, op_glyphs=glyphs,
        op_names=op_names, tables=tables, rel_glyph=rel_glyph,
        rel_name=rel_name, rel_kind=rel_kind, rel_pairs=rel_pairs,
        tag=model["tag"], seed=seed,
    )
