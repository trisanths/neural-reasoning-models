"""Operators as executable objects, written in a tiny typed expression form.

An operator induced from a page is not advice in prose. It is a callable with a
symbol, a parameter list, a body in a small prefix expression language, the
preconditions and postconditions the page states, and the page's worked
examples, which double as its verification procedure.

The expression language is deliberately narrow. It has integers, string
literals, booleans, variables, n-ary arithmetic, comparison, boolean
connectives, and a three-armed conditional. It has no loops, no recursion, and
no way to name a new function, so evaluation always terminates and a malformed
induction raises rather than hanging. Everything a page in this project can
state fits inside it, and nothing else does.

The text form is what the language model reads and writes:

    (defop @ (x y) (% (+ (* 3 x) (* 7 y) 2) 100) (ex (7 4) 51) (ex (12 5) 73))

Round tripping that string through parse_operator and serialize is exact, which
is what lets a model's induction be compared against the truth by string
equality as well as by behaviour.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# n-ary where the arity is None, otherwise fixed.
BUILTINS: dict[str, int | None] = {
    "+": None, "*": None, "-": 2, "//": 2, "%": 2, "neg": 1,
    ">=": 2, "<=": 2, ">": 2, "<": 2, "=": 2, "!=": 2,
    "and": None, "or": None, "not": 1,
    "if": 3, "min": 2, "max": 2,
}

MAX_ABS = 10 ** 12
MAX_DEPTH = 64

_TOKEN_RE = re.compile(r"\(|\)|'[^\s()]+|[^\s()]+")
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


class OpError(Exception):
    """Malformed operator text, or an execution that could not complete."""


# --------------------------------------------------------------- expressions

@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Call:
    head: str
    args: tuple


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text)


def _parse_expr(toks: list[str], i: int) -> tuple[object, int]:
    if i >= len(toks):
        raise OpError("expression ended early")
    t = toks[i]
    if t == ")":
        raise OpError("unexpected )")
    if t != "(":
        return _atom(t), i + 1
    i += 1
    if i >= len(toks):
        raise OpError("expression ended early")
    head = toks[i]
    if head in ("(", ")"):
        raise OpError("call head must be a symbol")
    i += 1
    args: list = []
    while i < len(toks) and toks[i] != ")":
        a, i = _parse_expr(toks, i)
        args.append(a)
    if i >= len(toks):
        raise OpError("missing )")
    n = BUILTINS.get(head, "unknown")
    if n == "unknown":
        raise OpError(f"unknown expression head {head!r}")
    if n is not None and len(args) != n:
        raise OpError(f"{head} takes {n} arguments, got {len(args)}")
    if n is None and len(args) < 2:
        raise OpError(f"{head} takes at least two arguments")
    return Call(head, tuple(args)), i + 1


def _atom(t: str):
    if t.startswith("'"):
        return t[1:]
    if t in ("true", "false"):
        return t == "true"
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if _IDENT_RE.match(t):
        return Var(t)
    raise OpError(f"bad atom {t!r}")


def parse_expr(text: str):
    toks = _tokenize(text)
    e, i = _parse_expr(toks, 0)
    if i != len(toks):
        raise OpError("trailing tokens after expression")
    return e


def serialize_expr(e) -> str:
    if isinstance(e, Var):
        return e.name
    if isinstance(e, bool):
        return "true" if e else "false"
    if isinstance(e, int):
        return str(e)
    if isinstance(e, str):
        return "'" + e
    if isinstance(e, Call):
        return "(" + e.head + " " + " ".join(serialize_expr(a) for a in e.args) + ")"
    raise OpError(f"cannot serialize {e!r}")


def _guard(v):
    if isinstance(v, int) and not isinstance(v, bool) and abs(v) > MAX_ABS:
        raise OpError("value out of range")
    return v


def eval_expr(e, env: dict, depth: int = 0):
    """Evaluate one expression in an environment of parameter bindings."""
    if depth > MAX_DEPTH:
        raise OpError("expression too deep")
    if isinstance(e, (bool, int, str)):
        return e
    if isinstance(e, Var):
        if e.name not in env:
            raise OpError(f"unbound variable {e.name}")
        return env[e.name]
    if not isinstance(e, Call):
        raise OpError(f"cannot evaluate {e!r}")
    h = e.head
    if h == "if":
        c = eval_expr(e.args[0], env, depth + 1)
        return eval_expr(e.args[1 if c else 2], env, depth + 1)
    vals = [eval_expr(a, env, depth + 1) for a in e.args]
    if h == "and":
        return all(bool(v) for v in vals)
    if h == "or":
        return any(bool(v) for v in vals)
    if h == "not":
        return not bool(vals[0])
    if h == "=":
        return vals[0] == vals[1]
    if h == "!=":
        return vals[0] != vals[1]
    nums = [v for v in vals if isinstance(v, int) and not isinstance(v, bool)]
    if len(nums) != len(vals):
        raise OpError(f"{h} needs numbers, got {vals!r}")
    if h == "+":
        return _guard(sum(vals))
    if h == "*":
        out = 1
        for v in vals:
            out *= v
        return _guard(out)
    if h == "-":
        return _guard(vals[0] - vals[1])
    if h == "neg":
        return _guard(-vals[0])
    if h == "//":
        if vals[1] == 0:
            raise OpError("division by zero")
        return _guard(vals[0] // vals[1])
    if h == "%":
        if vals[1] == 0:
            raise OpError("modulo by zero")
        return _guard(vals[0] % vals[1])
    if h == ">=":
        return vals[0] >= vals[1]
    if h == "<=":
        return vals[0] <= vals[1]
    if h == ">":
        return vals[0] > vals[1]
    if h == "<":
        return vals[0] < vals[1]
    if h == "min":
        return min(vals)
    if h == "max":
        return max(vals)
    raise OpError(f"unknown head {h}")


# ----------------------------------------------------------------- operators

@dataclass(frozen=True)
class Operator:
    """One induced operation: what it is called, what it takes, what it does."""

    symbol: str
    params: tuple[str, ...]
    body: object
    pre: tuple = field(default=())
    post: tuple = field(default=())
    examples: tuple = field(default=())

    @property
    def arity(self) -> int:
        return len(self.params)

    def __call__(self, *args):
        if len(args) != self.arity:
            raise OpError(f"{self.symbol} takes {self.arity} arguments, got {len(args)}")
        env = dict(zip(self.params, args))
        for c in self.pre:
            if not eval_expr(c, env):
                raise OpError(f"{self.symbol} precondition failed")
        r = eval_expr(self.body, env)
        env = dict(env)
        env["r"] = r
        for c in self.post:
            if not eval_expr(c, env):
                raise OpError(f"{self.symbol} postcondition failed")
        return r


def serialize(op: Operator) -> str:
    parts = [f"(defop {op.symbol} ({' '.join(op.params)}) {serialize_expr(op.body)}"]
    for c in op.pre:
        parts.append(f"(pre {serialize_expr(c)})")
    for c in op.post:
        parts.append(f"(post {serialize_expr(c)})")
    for args, res in op.examples:
        inner = " ".join(serialize_expr(a) for a in args)
        parts.append(f"(ex ({inner}) {serialize_expr(res)})")
    return " ".join(parts) + ")"


def parse_operator(text: str) -> Operator:
    """Strict parse. Anything that is not exactly the defop form raises."""
    toks = _tokenize(text)
    if len(toks) < 4 or toks[0] != "(" or toks[1] != "defop":
        raise OpError("not a defop form")
    symbol = toks[2]
    if symbol in ("(", ")"):
        raise OpError("missing operator symbol")
    i = 3
    if toks[i] != "(":
        raise OpError("missing parameter list")
    i += 1
    params: list[str] = []
    while i < len(toks) and toks[i] != ")":
        if not _IDENT_RE.match(toks[i]):
            raise OpError(f"bad parameter {toks[i]!r}")
        params.append(toks[i])
        i += 1
    if i >= len(toks):
        raise OpError("missing ) after parameters")
    i += 1
    body, i = _parse_expr(toks, i)
    pre: list = []
    post: list = []
    examples: list = []
    while i < len(toks) and toks[i] != ")":
        if toks[i] != "(":
            raise OpError("expected a clause")
        kind = toks[i + 1]
        if kind == "ex":
            j = i + 2
            if toks[j] != "(":
                raise OpError("ex needs an argument list")
            j += 1
            args: list = []
            while j < len(toks) and toks[j] != ")":
                a, j = _parse_expr(toks, j)
                args.append(a)
            j += 1
            res, j = _parse_expr(toks, j)
            if j >= len(toks) or toks[j] != ")":
                raise OpError("missing ) after ex")
            examples.append((tuple(args), res))
            i = j + 1
        elif kind in ("pre", "post"):
            c, j = _parse_expr(toks, i + 2)
            if j >= len(toks) or toks[j] != ")":
                raise OpError(f"missing ) after {kind}")
            (pre if kind == "pre" else post).append(c)
            i = j + 1
        else:
            raise OpError(f"unknown clause {kind!r}")
    if i >= len(toks) or toks[i] != ")":
        raise OpError("missing final )")
    if i + 1 != len(toks):
        raise OpError("trailing tokens after defop")
    free = _free_vars(body) | {v for c in pre for v in _free_vars(c)}
    unknown = free - set(params)
    if unknown:
        raise OpError(f"body mentions unbound {sorted(unknown)}")
    return Operator(symbol, tuple(params), body, tuple(pre), tuple(post), tuple(examples))


def parse_operators(text: str) -> list[Operator]:
    """Parse a whitespace separated run of defop forms.

    A page may define more than one operator, so induction from a page emits a
    list. Splitting is by paren balance rather than by regex, so an operator
    body containing parentheses cannot break the split.
    """
    out: list[Operator] = []
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            if depth == 0:
                raise OpError("unbalanced )")
            depth -= 1
            if depth == 0:
                out.append(parse_operator(text[start:i + 1]))
    if depth != 0:
        raise OpError("unbalanced (")
    if not out:
        raise OpError("no defop found")
    return out


def serialize_all(ops) -> str:
    return " ".join(serialize(o) for o in ops)


def _free_vars(e) -> set:
    if isinstance(e, Var):
        return {e.name}
    if isinstance(e, Call):
        out: set = set()
        for a in e.args:
            out |= _free_vars(a)
        return out
    return set()


# -------------------------------------------------------------- verification

def verify(op: Operator) -> tuple[bool, list[bool]]:
    """Run the operator against the worked examples the page stated.

    This is the only correctness signal available at inference, when the true
    operator is unknown. It returns whether every example reproduced and the
    per example outcome, so a caller can report partial agreement.
    """
    outcomes: list[bool] = []
    for args, expected in op.examples:
        try:
            outcomes.append(op(*args) == expected)
        except OpError:
            outcomes.append(False)
    return (all(outcomes) if outcomes else False), outcomes


def behaviourally_equal(a: Operator, b: Operator, probes) -> bool:
    """Same symbol, same arity, and the same output on every probe tuple."""
    if a.symbol != b.symbol or a.arity != b.arity:
        return False
    for args in probes:
        try:
            va = a(*args)
        except OpError:
            va = "__err__"
        try:
            vb = b(*args)
        except OpError:
            vb = "__err__"
        if va != vb:
            return False
    return True
