"""The typed structure language: what a page says, with the prose taken out.

A structure here is a program. It has a set of typed definitions, a set of
named inputs, and a straight line plan over the definitions. Nothing in it is
prose and nothing in it is learned. `src/norm/render.py` turns one into English
through the corpus frame grammar and `src/norm/parse.py` turns the English back
into one, so a structure and a page are two views of a single object.

The six definition kinds were chosen by reading what the existing families
express, not by inventing a language nothing uses:

    Table     a keyed lookup, optionally with a default, optionally ordered so
              that the first matching row wins. Keys may be tuples, which is
              how a two coordinate grid is written.
              src/corpus/relations.py substitution, inverse_table, chain_rule,
              transitive, two_key, priority_list, exclusion, agreement
    Bands     a threshold test: n-1 cut points and n labels over one attribute.
              relations.threshold, band_rule
    Rule      one general value with stated exceptions.
              relations.exception_rule, skillacq/simple.ExceptionRule
    Weights   a key to integer table, kept apart from Table because the frame
              grammar writes it with a different sentence and because its
              values are numbers.
              relations.lookup_then_band, weighted_chain
    Affine    one arithmetic step, x -> (a x + b) mod m.
              relations.modular_apply
    OpDef     a typed operator over parameters, written in the prefix
              expression language of src/opgraph/opdef.py, with preconditions
              and postconditions. This is the kind that carries several
              simultaneous conditions in one operator.
              skillacq/systems.py BinaryOpSystem, UnitSystem, ProcedureSystem

A plan is a list of steps. Each step names a temporary, an operation, and its
arguments. There is no branching and no looping in a plan, so a plan always
terminates, and there is no bound on how long one may be. Depth 48 and depth 2
are the same object with a different list length.

Definitions are addressed by (kind, name), so a Table and a Weights written on
the same page may share that page's name, which is what `weighted_chain` does.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.opgraph.opdef import Call, OpError, Var, parse_expr, serialize_expr

# ------------------------------------------------------------------- types

INT = "int"
SYM = "sym"
BOOL = "bool"
SET = "set"


class NormError(Exception):
    """A structure that is malformed, or text that is not one."""


def typeof(v) -> str:
    """The type of a value. Booleans are checked before integers."""
    if isinstance(v, bool):
        return BOOL
    if isinstance(v, int):
        return INT
    if isinstance(v, str):
        return SYM
    if isinstance(v, tuple):
        return SET
    raise NormError(f"value of no type: {v!r}")


# ------------------------------------------------------------- definitions


@dataclass(frozen=True)
class Table:
    """key -> value, in stated order. `ordered` means first match wins."""

    name: str
    entries: tuple = ()
    default: object = None
    ordered: bool = False
    kind = "table"

    @property
    def key_arity(self) -> int:
        k = self.entries[0][0] if self.entries else ""
        return len(k) if isinstance(k, tuple) else 1


@dataclass(frozen=True)
class Bands:
    """n labels over n-1 ascending cut points, on one named attribute.

    Band i covers cuts[i-1] <= x < cuts[i], with the ends unbounded.
    """

    name: str
    attr: str
    cuts: tuple = ()
    labels: tuple = ()
    kind = "bands"


@dataclass(frozen=True)
class Rule:
    """One general value, overridden by the stated exceptions."""

    name: str
    general: object = None
    exceptions: tuple = ()
    kind = "rule"


@dataclass(frozen=True)
class Weights:
    """key -> integer."""

    name: str
    entries: tuple = ()
    kind = "weights"


@dataclass(frozen=True)
class Affine:
    """x -> (a x + b) mod m."""

    name: str
    a: int = 1
    b: int = 0
    m: int = 0
    kind = "affine"


@dataclass(frozen=True)
class OpDef:
    """A typed operator: parameters, a body, and the conditions it states.

    The body is an expression of src/opgraph/opdef.py. `pre` holds the
    conditions that must hold of the arguments and `post` the conditions that
    must hold of the result, which is bound to `r`. Several simultaneous
    conditions are written as one `and`, or as several `pre` clauses.
    """

    name: str
    params: tuple = ()
    body: object = None
    pre: tuple = ()
    post: tuple = ()
    kind = "op"


DEF_KINDS = {"table": Table, "bands": Bands, "rule": Rule,
             "weights": Weights, "affine": Affine, "op": OpDef}


# -------------------------------------------------------------------- plan


@dataclass(frozen=True)
class Ref:
    """A read of a temporary or of a named input."""

    name: str


@dataclass(frozen=True)
class Lit:
    """A literal value written into the plan."""

    value: object


@dataclass(frozen=True)
class Step:
    """One line of a plan: a temporary, an operation, its arguments."""

    out: str
    op: str
    args: tuple = ()


@dataclass(frozen=True)
class Program:
    """One structure: its definitions, its inputs, its plan, its answer."""

    defs: tuple = ()
    inputs: tuple = ()
    steps: tuple = ()
    answer: str = ""

    @property
    def depth(self) -> int:
        return len(self.steps)

    def by_kind(self, kind: str) -> list:
        return [d for d in self.defs if d.kind == kind]

    def distinct_ops(self) -> int:
        """Distinct plan operations used, e.g. lookup and band count as two."""
        return len({s.op for s in self.steps})

    def distinct_operators(self) -> int:
        """Distinct definitions invoked, which is what a plan calls.

        Two `call` steps naming two different operators are two operators even
        though both steps read `call`, and two `lookup` steps on one table are
        one operator even though the plan is two steps long.
        """
        out = set()
        for s in self.steps:
            names = tuple(a for a in s.args if isinstance(a, str))
            out.add((s.op, names) if names else (s.op, ()))
        return len(out)


# ----------------------------------------------------------- serialisation
#
# JSON is the canonical persisted form. It is exact for every value the
# language holds and round trips by construction, which is what a record file
# has to do.


def _val_json(v):
    if isinstance(v, tuple):
        return {"$tuple": [_val_json(x) for x in v]}
    return v


def _val_load(v):
    if isinstance(v, dict) and "$tuple" in v:
        return tuple(_val_load(x) for x in v["$tuple"])
    return v


def def_json(d) -> dict:
    if d.kind == "table":
        return {"kind": "table", "name": d.name,
                "entries": [[_val_json(k), _val_json(v)] for k, v in d.entries],
                "default": _val_json(d.default), "ordered": d.ordered}
    if d.kind == "bands":
        return {"kind": "bands", "name": d.name, "attr": d.attr,
                "cuts": list(d.cuts), "labels": list(d.labels)}
    if d.kind == "rule":
        return {"kind": "rule", "name": d.name, "general": _val_json(d.general),
                "exceptions": [[k, _val_json(v)] for k, v in d.exceptions]}
    if d.kind == "weights":
        return {"kind": "weights", "name": d.name,
                "entries": [[k, v] for k, v in d.entries]}
    if d.kind == "affine":
        return {"kind": "affine", "name": d.name, "a": d.a, "b": d.b, "m": d.m}
    if d.kind == "op":
        return {"kind": "op", "name": d.name, "params": list(d.params),
                "body": serialize_expr(d.body),
                "pre": [serialize_expr(c) for c in d.pre],
                "post": [serialize_expr(c) for c in d.post]}
    raise NormError(f"unknown definition kind {d.kind!r}")


def def_load(o: dict):
    k = o["kind"]
    if k == "table":
        return Table(o["name"],
                     tuple((_val_load(a), _val_load(b)) for a, b in o["entries"]),
                     _val_load(o.get("default")), bool(o.get("ordered", False)))
    if k == "bands":
        return Bands(o["name"], o["attr"], tuple(o["cuts"]), tuple(o["labels"]))
    if k == "rule":
        return Rule(o["name"], _val_load(o["general"]),
                    tuple((a, _val_load(b)) for a, b in o["exceptions"]))
    if k == "weights":
        return Weights(o["name"], tuple((a, b) for a, b in o["entries"]))
    if k == "affine":
        return Affine(o["name"], o["a"], o["b"], o["m"])
    if k == "op":
        return OpDef(o["name"], tuple(o["params"]), parse_expr(o["body"]),
                     tuple(parse_expr(c) for c in o["pre"]),
                     tuple(parse_expr(c) for c in o["post"]))
    raise NormError(f"unknown definition kind {k!r}")


def _arg_json(a):
    if isinstance(a, Ref):
        return {"ref": a.name}
    if isinstance(a, Lit):
        return {"lit": _val_json(a.value)}
    if isinstance(a, str):
        return {"def": a}
    raise NormError(f"unknown argument {a!r}")


def _arg_load(o):
    if "ref" in o:
        return Ref(o["ref"])
    if "lit" in o:
        return Lit(_val_load(o["lit"]))
    if "def" in o:
        return o["def"]
    raise NormError(f"unknown argument {o!r}")


def program_json(p: Program) -> dict:
    return {
        "defs": [def_json(d) for d in p.defs],
        "inputs": [[n, _val_json(v)] for n, v in p.inputs],
        "steps": [{"out": s.out, "op": s.op,
                   "args": [_arg_json(a) for a in s.args]} for s in p.steps],
        "answer": p.answer,
    }


def program_load(o: dict) -> Program:
    return Program(
        tuple(def_load(d) for d in o["defs"]),
        tuple((n, _val_load(v)) for n, v in o["inputs"]),
        tuple(Step(s["out"], s["op"], tuple(_arg_load(a) for a in s["args"]))
              for s in o["steps"]),
        o["answer"],
    )


# ------------------------------------------------------------------ pretty


def _v(x) -> str:
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    if isinstance(x, tuple):
        return "[" + " ".join(_v(y) for y in x) + "]"
    return str(x)


def pretty_def(d) -> str:
    if d.kind == "table":
        rows = " ".join(f"({_v(k)} => {_v(v)})" for k, v in d.entries)
        tail = f" (default => {_v(d.default)})" if d.default is not None else ""
        head = "table/ordered" if d.ordered else "table"
        return f"({head} {d.name} {rows}{tail})"
    if d.kind == "bands":
        return (f"(bands {d.name} {d.attr} (cuts {' '.join(map(str, d.cuts))})"
                f" (labels {' '.join(d.labels)}))")
    if d.kind == "rule":
        exc = " ".join(f"(except {k} => {_v(v)})" for k, v in d.exceptions)
        return f"(rule {d.name} (general {_v(d.general)}) {exc})"
    if d.kind == "weights":
        rows = " ".join(f"({k} => {v})" for k, v in d.entries)
        return f"(weights {d.name} {rows})"
    if d.kind == "affine":
        return f"(affine {d.name} {d.a} {d.b} {d.m})"
    if d.kind == "op":
        pre = "".join(f" (pre {serialize_expr(c)})" for c in d.pre)
        post = "".join(f" (post {serialize_expr(c)})" for c in d.post)
        return (f"(op {d.name} ({' '.join(d.params)}) "
                f"{serialize_expr(d.body)}{pre}{post})")
    raise NormError(d.kind)


def pretty(p: Program) -> str:
    lines = [pretty_def(d) for d in p.defs]
    lines += [f"(in {n} {_v(v)})" for n, v in p.inputs]
    for s in p.steps:
        args = " ".join(a.name if isinstance(a, Ref)
                        else _v(a.value) if isinstance(a, Lit) else a
                        for a in s.args)
        lines.append(f"({s.out} = {s.op} {args})")
    lines.append(f"(ans {p.answer})")
    return "\n".join(lines)
