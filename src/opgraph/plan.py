"""Composition plans, and the executor that runs them exactly.

A plan is a straight line program over induced operators. Nothing branches and
nothing loops; the whole of the control flow a question needs is the order of
its steps and which temporary each step reads. That is the point of the
mechanism: composition depth becomes the length of a list rather than something
the backbone has to hold in its activations.

The text form is one step per semicolon:

    t1 = @ 7 4 ; t2 = # t1 9 ; ans t2

Three arithmetic builtins, add, sub and mul, are always callable. They exist
because a question may say "plus" in its own voice rather than through an
invented operator, and a plan should be able to say so too. They are the only
vocabulary fixed before the page is read, and every result below reports how
often they are used so their contribution stays visible.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.opgraph.opdef import OpError, Operator

BUILTIN_STEPS = {
    "add": (2, lambda a, b: a + b),
    "sub": (2, lambda a, b: a - b),
    "mul": (2, lambda a, b: a * b),
}

MAX_STEPS = 32
_TEMP_RE = re.compile(r"^t\d+$")
_INT_RE = re.compile(r"^-?\d+$")


class PlanError(Exception):
    """Malformed plan text, or a plan that could not be run."""


@dataclass(frozen=True)
class Step:
    target: str
    symbol: str
    args: tuple


@dataclass(frozen=True)
class Plan:
    steps: tuple[Step, ...]
    answer: str

    @property
    def depth(self) -> int:
        return len(self.steps)


def serialize_plan(p: Plan) -> str:
    out = []
    for s in p.steps:
        args = " ".join(_arg_text(a) for a in s.args)
        out.append(f"{s.target} = {s.symbol} {args}")
    out.append(f"ans {p.answer}")
    return " ; ".join(out)


def _arg_text(a) -> str:
    if isinstance(a, bool):
        return "true" if a else "false"
    if isinstance(a, int):
        return str(a)
    if isinstance(a, str) and _TEMP_RE.match(a):
        return a
    return "'" + str(a)


def _parse_arg(tok: str):
    if tok in ("true", "false"):
        return tok == "true"
    if _INT_RE.match(tok):
        return int(tok)
    if _TEMP_RE.match(tok):
        return tok
    if tok.startswith("'"):
        return ("lit", tok[1:])
    raise PlanError(f"bad plan argument {tok!r}")


def parse_plan(text: str) -> Plan:
    """Strict parse of the semicolon form. Nothing is guessed or repaired."""
    chunks = [c.strip() for c in text.strip().split(";")]
    chunks = [c for c in chunks if c]
    if not chunks:
        raise PlanError("empty plan")
    if len(chunks) > MAX_STEPS + 1:
        raise PlanError("plan too long")
    steps: list[Step] = []
    answer = None
    seen: set = set()
    for k, c in enumerate(chunks):
        parts = c.split()
        if parts[0] == "ans":
            if len(parts) != 2 or k != len(chunks) - 1:
                raise PlanError("ans must be the last chunk and take one value")
            answer = parts[1]
            continue
        if len(parts) < 3 or parts[1] != "=":
            raise PlanError(f"bad step {c!r}")
        target = parts[0]
        if not _TEMP_RE.match(target):
            raise PlanError(f"bad temporary {target!r}")
        if target in seen:
            raise PlanError(f"temporary {target} assigned twice")
        seen.add(target)
        symbol = parts[2]
        args = tuple(_parse_arg(t) for t in parts[3:])
        for a in args:
            if isinstance(a, str) and a not in seen and _TEMP_RE.match(a):
                raise PlanError(f"step reads {a} before it is written")
        steps.append(Step(target, symbol, args))
    if answer is None:
        raise PlanError("plan has no ans")
    if _TEMP_RE.match(answer) and answer not in seen:
        raise PlanError("ans names an unwritten temporary")
    return Plan(tuple(steps), answer)


def run_plan(plan: Plan, ops: dict[str, Operator]):
    """Execute a plan against a table of induced operators.

    Raises rather than guessing when a symbol is unknown or an arity is wrong,
    so an execution failure is never mistaken for a wrong answer.
    """
    env: dict[str, object] = {}
    for s in plan.steps:
        args = []
        for a in s.args:
            if isinstance(a, tuple) and a and a[0] == "lit":
                args.append(a[1])
            elif isinstance(a, str) and _TEMP_RE.match(a):
                if a not in env:
                    raise PlanError(f"unwritten temporary {a}")
                args.append(env[a])
            else:
                args.append(a)
        if s.symbol in BUILTIN_STEPS:
            n, fn = BUILTIN_STEPS[s.symbol]
            if len(args) != n:
                raise PlanError(f"{s.symbol} takes {n} arguments")
            try:
                env[s.target] = fn(*args)
            except TypeError as exc:
                raise PlanError(str(exc)) from exc
            continue
        op = ops.get(s.symbol)
        if op is None:
            raise PlanError(f"unknown operator {s.symbol!r}")
        try:
            env[s.target] = op(*args)
        except OpError as exc:
            raise PlanError(f"{s.symbol}: {exc}") from exc
    a = plan.answer
    if _TEMP_RE.match(a):
        return env[a]
    if _INT_RE.match(a):
        return int(a)
    if a.startswith("'"):
        return a[1:]
    return a


def run_plan_trace(plan: Plan, ops: dict[str, Operator]):
    """Run a plan and also return the value each step produced.

    This is what the written out baseline is trained to imitate: the same
    decomposition, the same order, but with every intermediate value spelled
    in tokens instead of computed by the executor.
    """
    env: dict[str, object] = {}
    trace = []
    for s in plan.steps:
        args = []
        for a in s.args:
            if isinstance(a, str) and _TEMP_RE.match(a):
                args.append(env[a])
            elif isinstance(a, tuple) and a and a[0] == "lit":
                args.append(a[1])
            else:
                args.append(a)
        if s.symbol in BUILTIN_STEPS:
            n, fn = BUILTIN_STEPS[s.symbol]
            v = fn(*args)
        else:
            op = ops.get(s.symbol)
            if op is None:
                raise PlanError(f"unknown operator {s.symbol!r}")
            v = op(*args)
        env[s.target] = v
        trace.append((s, v))
    a = plan.answer
    final = env[a] if _TEMP_RE.match(a) else a
    return final, trace


def trace_text(plan: Plan, ops: dict[str, Operator]) -> str:
    """The written out form: every step, then the value it produced."""
    final, trace = run_plan_trace(plan, ops)
    parts = []
    for s, v in trace:
        args = " ".join(_arg_text(x) for x in s.args)
        parts.append(f"{s.target} = {s.symbol} {args} -> {answer_text(v)}")
    parts.append(f"ans {answer_text(final)}")
    return " ; ".join(parts)


def trace_answer(text: str) -> str:
    """The value a written out trace ends on, or the empty string."""
    idx = text.rfind("ans ")
    if idx < 0:
        return ""
    return text[idx + 4:].strip().split(";")[0].strip()


def answer_text(value) -> str:
    """How an executed value is written down for comparison against gold."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def signature_line(ops: dict[str, Operator]) -> str:
    """The operator table as the scheduler sees it: symbols and arities only.

    The scheduler is never shown a body. It plans over what the operators are
    called, how many arguments they take, and, for an infix operator, which way
    a run of it associates, which is the one notational fact a plan cannot be
    written without. Semantics stay hidden, which is what makes the planning
    failure separable from the induction failure.
    """
    out = []
    for k in sorted(ops):
        op = ops[k]
        out.append(f"{k}/{op.arity}/{op.assoc}" if op.assoc else f"{k}/{op.arity}")
    return " ".join(out)
