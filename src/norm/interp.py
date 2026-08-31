"""The exact interpreter. Not learned, not sampled, and never a guess.

It executes a `src/norm/lang.py` program against its inputs and returns either
an answer or a refusal with a reason. There is no third outcome: the
interpreter does not emit a value it did not compute.

Two properties matter and both are properties of the code rather than of a
training run.

Composition depth is unbounded. A plan is a straight line list, execution is a
`for` over that list, and there is no step cap anywhere in this module.
`src/opgraph/plan.py` caps at MAX_STEPS 128 and that limit is not inherited.
Expression evaluation inside an operator is done with an explicit stack rather
than by Python recursion, so a deeply nested body does not hit the interpreter
stack either; `src/opgraph/opdef.py` caps expression nesting at MAX_DEPTH 64
and that limit is not inherited.

Refusal is exact. Every failure path raises `Cannot` with a reason naming the
step and what was missing, and `run` returns it as `Result(ok=False)`. A key
that is absent with no default stated, an inversion that is not unique, a
precondition that does not hold, an operator that was never defined, an
argument of the wrong type: each is a refusal, not a wrong answer.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass

from src.norm.lang import (Affine, Bands, Lit, NormError, OpDef, Program, Ref,
                           Rule, Step, Table, Weights, typeof)
from src.opgraph.opdef import Call, Var

MAX_ABS = 10 ** 15


class Cannot(Exception):
    """The interpreter cannot execute this. Carries why."""


@dataclass(frozen=True)
class Result:
    ok: bool
    value: object = None
    reason: str = ""
    trace: tuple = ()

    @property
    def text(self) -> str:
        """How an executed value is written down for comparison against gold."""
        if not self.ok:
            return ""
        if isinstance(self.value, bool):
            return "true" if self.value else "false"
        return str(self.value)


# ------------------------------------------------------------- expressions


def _num(v, head):
    if isinstance(v, bool) or not isinstance(v, int):
        raise Cannot(f"{head} needs a number, got {v!r}")
    return v


def _guard(v):
    if isinstance(v, int) and not isinstance(v, bool) and abs(v) > MAX_ABS:
        raise Cannot("value out of range")
    return v


def _builtin(head: str, vals: list):
    if head == "and":
        return all(bool(v) for v in vals)
    if head == "or":
        return any(bool(v) for v in vals)
    if head == "not":
        return not bool(vals[0])
    if head == "=":
        return vals[0] == vals[1]
    if head == "!=":
        return vals[0] != vals[1]
    nums = [_num(v, head) for v in vals]
    if head == "+":
        return _guard(sum(nums))
    if head == "*":
        out = 1
        for v in nums:
            out *= v
        return _guard(out)
    if head == "-":
        return _guard(nums[0] - nums[1])
    if head == "neg":
        return _guard(-nums[0])
    if head == "//":
        if nums[1] == 0:
            raise Cannot("division by zero")
        return _guard(nums[0] // nums[1])
    if head == "%":
        if nums[1] == 0:
            raise Cannot("modulo by zero")
        return _guard(nums[0] % nums[1])
    if head == ">=":
        return nums[0] >= nums[1]
    if head == "<=":
        return nums[0] <= nums[1]
    if head == ">":
        return nums[0] > nums[1]
    if head == "<":
        return nums[0] < nums[1]
    if head == "min":
        return min(nums)
    if head == "max":
        return max(nums)
    raise Cannot(f"unknown expression head {head!r}")


def eval_expr(e, env: dict):
    """Evaluate one expression with an explicit stack, so nesting is unbounded."""
    stack = [(e, False)]
    vals: list = []
    while stack:
        node, done = stack.pop()
        if done:
            if isinstance(node, tuple) and node and node[0] == "__if__":
                cond = vals.pop()
                call = node[1]
                stack.append((call.args[1 if cond else 2], False))
                continue
            n = len(node.args)
            args = vals[len(vals) - n:]
            del vals[len(vals) - n:]
            vals.append(_builtin(node.head, args))
            continue
        if isinstance(node, (bool, int, str)):
            vals.append(node)
        elif isinstance(node, Var):
            if node.name not in env:
                raise Cannot(f"unbound variable {node.name}")
            vals.append(env[node.name])
        elif isinstance(node, Call):
            if node.head == "if":
                stack.append((("__if__", node), True))
                stack.append((node.args[0], False))
            else:
                stack.append((node, True))
                for a in reversed(node.args):
                    stack.append((a, False))
        else:
            raise Cannot(f"cannot evaluate {node!r}")
    if len(vals) != 1:
        raise Cannot("expression did not reduce to one value")
    return vals[0]


# ---------------------------------------------------------------- operations
#
# `defs` is the number of leading definition-name arguments an operation takes
# and `kinds` says which definition kind each one must be. `args` is the
# permitted count of value arguments.

OPS = {
    "lookup":        {"kinds": ("table",), "args": (1, 2)},
    "lookup_ordered": {"kinds": ("table",), "args": (1,)},
    "invert":        {"kinds": ("table",), "args": (1,)},
    "odd_one_out":   {"kinds": ("table",), "args": (1,)},
    "prefer":        {"kinds": ("table", "table"), "args": (1,)},
    "band":          {"kinds": ("bands",), "args": (1,)},
    "weigh":         {"kinds": ("weights",), "args": (1,)},
    "rule":          {"kinds": ("rule",), "args": (1,)},
    "step":          {"kinds": ("affine",), "args": (1,)},
    "call":          {"kinds": ("op",), "args": None},
    "add":           {"kinds": (), "args": (2,)},
    "sub":           {"kinds": (), "args": (2,)},
    "mul":           {"kinds": (), "args": (2,)},
}


def _table_get(t: Table, key):
    """The value the table states for a key.

    A page that lists one key twice with two values states two answers, and
    picking either one is a guess. Both the first row and the last row have
    been someone's convention; neither is stated. So this refuses.
    """
    hits = [v for k, v in t.entries if k == key]
    if len({str(v) for v in hits}) > 1:
        raise Cannot(f"table {t.name} states {len(hits)} different values "
                     f"for {key!r}")
    if hits:
        return True, hits[0]
    if t.default is not None:
        return True, t.default
    return False, None


def _apply(op: str, defs: list, vals: list):
    if op == "lookup":
        t = defs[0]
        key = vals[0] if len(vals) == 1 else tuple(vals)
        if t.ordered:
            raise Cannot(f"table {t.name} is ordered; use lookup_ordered")
        hit, v = _table_get(t, key)
        if not hit:
            raise Cannot(f"table {t.name} has no entry for {key!r} "
                         f"and states no default")
        return v
    if op == "lookup_ordered":
        t = defs[0]
        memb = vals[0]
        if typeof(memb) != "set":
            raise Cannot("lookup_ordered needs a set of keys")
        for k, v in t.entries:
            if k in memb:
                return v
        if t.default is not None:
            return t.default
        raise Cannot(f"table {t.name} matched none of {memb!r}")
    if op == "invert":
        t = defs[0]
        hits = [k for k, v in t.entries if v == vals[0]]
        if len(hits) == 1:
            return hits[0]
        raise Cannot(f"table {t.name} inverts {vals[0]!r} to {len(hits)} keys")
    if op == "odd_one_out":
        t = defs[0]
        hits = [k for k, v in t.entries if v != vals[0]]
        if len(hits) == 1:
            return hits[0]
        raise Cannot(f"table {t.name} has {len(hits)} keys away from "
                     f"{vals[0]!r}, not one")
    if op == "prefer":
        a, b = defs
        hit, v = _table_get(a, vals[0])
        if hit:
            return v
        hit, v = _table_get(b, vals[0])
        if hit:
            return v
        raise Cannot(f"neither {a.name} nor {b.name} states {vals[0]!r}")
    if op == "band":
        bd = defs[0]
        x = vals[0]
        if typeof(x) != "int":
            raise Cannot(f"band needs a number, got {x!r}")
        if len(bd.labels) != len(bd.cuts) + 1:
            raise Cannot(f"bands {bd.name} has {len(bd.labels)} labels for "
                         f"{len(bd.cuts)} cuts")
        return bd.labels[bisect_right(bd.cuts, x)]
    if op == "weigh":
        w = defs[0]
        for k, v in w.entries:
            if k == vals[0]:
                return v
        raise Cannot(f"weights {w.name} has no entry for {vals[0]!r}")
    if op == "rule":
        r = defs[0]
        for k, v in r.exceptions:
            if k == vals[0]:
                return v
        if r.general is None:
            raise Cannot(f"rule {r.name} states no general value")
        return r.general
    if op == "step":
        af = defs[0]
        x = vals[0]
        if typeof(x) != "int":
            raise Cannot(f"step needs a number, got {x!r}")
        v = af.a * x + af.b
        return v % af.m if af.m else v
    if op == "call":
        od = defs[0]
        if len(vals) != len(od.params):
            raise Cannot(f"operator {od.name} takes {len(od.params)} "
                         f"arguments, got {len(vals)}")
        env = dict(zip(od.params, vals))
        for c in od.pre:
            if not eval_expr(c, env):
                raise Cannot(f"operator {od.name} precondition does not hold")
        out = eval_expr(od.body, env)
        env = dict(env)
        env["r"] = out
        for c in od.post:
            if not eval_expr(c, env):
                raise Cannot(f"operator {od.name} postcondition does not hold")
        return out
    if op in ("add", "sub", "mul"):
        a = _num(vals[0], op)
        b = _num(vals[1], op)
        return _guard(a + b if op == "add" else a - b if op == "sub" else a * b)
    raise Cannot(f"unknown operation {op!r}")


# ------------------------------------------------------------------- runner


def index_defs(program: Program) -> dict:
    """Definitions addressed by (kind, name). Duplicates are a refusal."""
    out: dict = {}
    for d in program.defs:
        key = (d.kind, d.name)
        if key in out:
            raise Cannot(f"two definitions named {d.name} of kind {d.kind}")
        out[key] = d
    return out


def run(program: Program) -> Result:
    """Execute the plan. No step cap: depth is the length of a list."""
    trace: list = []
    try:
        table = index_defs(program)
        env: dict = {}
        for n, v in program.inputs:
            if n in env:
                raise Cannot(f"input {n} bound twice")
            env[n] = v
        for i, s in enumerate(program.steps):
            spec = OPS.get(s.op)
            if spec is None:
                raise Cannot(f"step {i} names unknown operation {s.op!r}")
            nd = len(spec["kinds"])
            head, tail = list(s.args[:nd]), list(s.args[nd:])
            if len(head) != nd:
                raise Cannot(f"step {i} ({s.op}) needs {nd} definition names")
            defs = []
            for want, name in zip(spec["kinds"], head):
                if not isinstance(name, str):
                    raise Cannot(f"step {i} ({s.op}) wants a definition name")
                d = table.get((want, name))
                if d is None:
                    raise Cannot(f"step {i} ({s.op}) names no {want} "
                                 f"called {name!r}")
                defs.append(d)
            if spec["args"] is not None and len(tail) not in spec["args"]:
                raise Cannot(f"step {i} ({s.op}) takes "
                             f"{spec['args']} values, got {len(tail)}")
            vals = []
            for a in tail:
                if isinstance(a, Lit):
                    vals.append(a.value)
                elif isinstance(a, Ref):
                    if a.name not in env:
                        raise Cannot(f"step {i} reads {a.name} "
                                     f"before it is written")
                    vals.append(env[a.name])
                else:
                    raise Cannot(f"step {i} has an argument that is not a "
                                 f"value: {a!r}")
            if s.out in env:
                raise Cannot(f"step {i} writes {s.out}, already written")
            env[s.out] = _apply(s.op, defs, vals)
            trace.append((s.out, s.op, env[s.out]))
        if program.answer not in env:
            raise Cannot(f"the answer names {program.answer!r}, never written")
        return Result(True, env[program.answer], "", tuple(trace))
    except Cannot as exc:
        return Result(False, None, str(exc), tuple(trace))
    except NormError as exc:
        return Result(False, None, f"malformed structure: {exc}", tuple(trace))
