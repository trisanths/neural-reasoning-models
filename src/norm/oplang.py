"""An operation the system has never seen, written as a structure.

The corpus holds four relation structures out: two_key, exclusion,
priority_list and agreement. This module builds operations of the fourth kind.
An agreement operation reads one item in two or three directories and decides
what to answer from whether those readings agree. Nothing in this project could
state that before: `src/norm/shapes.py` has no shape for it, `src/norm/render.py`
cannot write it, `src/norm/parse.py` cannot read it, and the normalizer's target
vocabulary in `src/norm/ntok.py` has no token for an operator definition at all.

What a page may state is fixed here; which operator it states is not. A
definition names its own operator, says which directories it reads and in what
order, and gives an ordered list of clauses, each a condition on the readings
and a result. The condition and result vocabularies are small and closed. The
operators they compose are not: `enumerate_space` writes out every operation
statable with one clause, 165 of them, and that whole set is what the
acquisition measurement runs over rather than a hand-picked example.

Nothing here evaluates an operator. Gold answers and option sets both come from
`src/norm/interp.py` running the assembled program, so this lane has one
evaluator instead of two that could disagree.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.norm.interp import run
from src.norm.lang import NormError, OpDef, Program, Ref, Step, Table
from src.opgraph.opdef import Call, Var

# A condition is one of
#     ("all_same",)          every reading is the same
#     ("all_diff",)          no two readings are the same
#     ("same", i, j)         readings i and j are the same        (1 based)
#     ("diff", i, j)         readings i and j are not the same
# A result is one of
#     ("src", i)             the reading from directory i
#     ("shared", i)          the reading the condition just found shared
#     ("word", w)            a word the page states outright


def conds_for(m: int) -> list:
    """The conditions statable over m readings.

    With two readings `same(1,2)` is `all_same` and `diff(1,2)` is `all_diff`,
    so the pair forms are not offered: a page would be stating one condition in
    two ways and the space would double with nothing in it.
    """
    if m == 2:
        return [("all_same",), ("all_diff",)]
    pairs = [(i, j) for i in range(1, m + 1) for j in range(i + 1, m + 1)]
    return ([("all_same",), ("all_diff",)]
            + [("same", i, j) for i, j in pairs]
            + [("diff", i, j) for i, j in pairs])


def is_same_cond(c) -> bool:
    return c[0] in ("all_same", "same")


def shared_index(c) -> int:
    """Which reading `that shared reading` names, given the condition."""
    return 1 if c[0] == "all_same" else c[1]


def results_for(m: int, cond) -> list:
    """The results statable after a condition. `shared` needs a same-condition."""
    out = [("src", i) for i in range(1, m + 1)]
    if cond is not None and is_same_cond(cond):
        out.append(("shared", shared_index(cond)))
    out.append(("word", None))
    return out


@dataclass(frozen=True)
class OpSpec:
    """One operation: its name, the directories it reads, its clauses."""

    name: str
    sources: tuple = ()
    clauses: tuple = ()          # ((cond, result), ...) tried in order
    fallback: object = None      # the result when no clause fires

    @property
    def arity(self) -> int:
        return len(self.sources)

    @property
    def skeleton(self) -> tuple:
        """The operation with its invented words taken out."""
        cl = tuple((c, (r[0], r[1]) if r[0] != "word" else ("word", None))
                   for c, r in self.clauses)
        fb = (self.fallback[0], self.fallback[1]) \
            if self.fallback[0] != "word" else ("word", None)
        return (self.arity, cl, fb)


# ------------------------------------------------------------ the space


def enumerate_space(m: int, n_clauses: int = 1) -> list:
    """Every (clauses, fallback) skeleton of m readings and n_clauses clauses.

    A skeleton is the operation without its words: which conditions in which
    order, and which results. Two skeletons that differ only in an invented
    word are one skeleton, because the page states the word either way.
    """
    conds = conds_for(m)
    fbs = [("src", i) for i in range(1, m + 1)] + [("word", None)]
    out = []
    if n_clauses == 1:
        for c in conds:
            for r in results_for(m, c):
                for fb in fbs:
                    out.append((((c, r),), fb))
        return out
    for c1 in conds:
        for r1 in results_for(m, c1):
            for c2 in conds:
                if c2 == c1:
                    continue
                for r2 in results_for(m, c2):
                    for fb in fbs:
                        out.append((((c1, r1), (c2, r2)), fb))
    return out


def arity_of(skeleton) -> int:
    """How many readings a skeleton needs, read off its own indices.

    A skeleton drawn from the three reading enumeration that never names a
    third reading is a two reading operation, and is the same operation as the
    one the two reading enumeration writes. `distinct_space` is what removes
    that double count.
    """
    clauses, fb = skeleton
    idx = [1, 2]
    for c, r in clauses:
        if c[0] in ("same", "diff"):
            idx += [c[1], c[2]]
        if r[0] in ("src", "shared"):
            idx.append(r[1])
    if fb[0] in ("src", "shared"):
        idx.append(fb[1])
    return max(idx)


def distinct_space(n_clauses: int = 1) -> list:
    """Every distinct operation of that clause count, over two or three
    readings, with the duplicates between the two enumerations removed."""
    seen, out = set(), []
    for m in (2, 3):
        for sk in enumerate_space(m, n_clauses):
            if sk in seen:
                continue
            seen.add(sk)
            out.append(sk)
    return out


def sample_space(m: int, n_clauses: int, n: int, seed: int) -> list:
    """n skeletons drawn without replacement from a space too big to walk."""
    full = enumerate_space(m, n_clauses)
    rng = random.Random(seed)
    rng.shuffle(full)
    return full[:n]


def sample_clauses(m: int, n_clauses: int, n: int, seed: int) -> list:
    """n skeletons of any clause count, drawn rather than enumerated.

    Three and four clause operations, and operations over four and five
    readings, are past what `enumerate_space` was ever asked to write out. They
    are here to ask whether the reader is general over the definition grammar
    or was fitted to the shapes it was developed on.
    """
    rng = random.Random(seed)
    conds = conds_for(m)
    fbs = [("src", i) for i in range(1, m + 1)] + [("word", None)]
    seen, out = set(), []
    for _ in range(n * 40):
        if len(out) >= n:
            break
        picked = rng.sample(conds, min(n_clauses, len(conds)))
        cl = tuple((c, rng.choice(results_for(m, c))) for c in picked)
        sk = (cl, rng.choice(fbs))
        if sk in seen or arity_of(sk) != m:
            continue
        seen.add(sk)
        out.append(sk)
    return out


# --------------------------------------------------------- to a structure


def _cond_expr(cond, m: int):
    if cond[0] == "all_same":
        parts = [Call("=", (Var(f"a{i}"), Var(f"a{i + 1}")))
                 for i in range(1, m)]
        return parts[0] if len(parts) == 1 else Call("and", tuple(parts))
    if cond[0] == "all_diff":
        parts = [Call("!=", (Var(f"a{i}"), Var(f"a{j}")))
                 for i in range(1, m + 1) for j in range(i + 1, m + 1)]
        return parts[0] if len(parts) == 1 else Call("and", tuple(parts))
    if cond[0] == "same":
        return Call("=", (Var(f"a{cond[1]}"), Var(f"a{cond[2]}")))
    if cond[0] == "diff":
        return Call("!=", (Var(f"a{cond[1]}"), Var(f"a{cond[2]}")))
    raise NormError(f"unknown condition {cond!r}")


def _res_expr(res):
    if res[0] in ("src", "shared"):
        return Var(f"a{res[1]}")
    if res[0] == "word":
        return res[1]
    raise NormError(f"unknown result {res!r}")


def to_opdef(spec: OpSpec) -> OpDef:
    """The typed operator this specification is. No lookups: those are the plan."""
    m = spec.arity
    body = _res_expr(spec.fallback)
    for cond, res in reversed(spec.clauses):
        body = Call("if", (_cond_expr(cond, m), _res_expr(res), body))
    return OpDef(spec.name, tuple(f"a{i}" for i in range(1, m + 1)), body)


def build_spec(skeleton, name: str, sources, words) -> OpSpec:
    """Fill a skeleton with an operator name, directory names and stated words.

    `words` is drawn on first use, so a skeleton naming two stated words gets
    two different ones and a skeleton naming none draws none.
    """
    clauses_sk, fb_sk = skeleton
    it = iter(words)

    def fill(r):
        return ("word", next(it)) if r[0] == "word" else r

    return OpSpec(name, tuple(sources),
                  tuple((c, fill(r)) for c, r in clauses_sk), fill(fb_sk))


# ------------------------------------------------------------- the plans
#
# Lookups are numbered t1.. in the order the plan reads them and calls are
# numbered r1.. in the order the plan makes them, so a program of any depth
# uses names that `src/norm/optok.py` can write.


def _apply(spec: OpSpec, src_from: str, k: int, c: int, tables_named):
    """Steps that read the m directories for one value and call the operator."""
    steps = []
    reads = []
    for j, s in enumerate(spec.sources):
        t = f"t{k + j + 1}"
        steps.append(Step(t, "lookup", (s, Ref(src_from))))
        reads.append(Ref(t))
    out = f"r{c + 1}"
    steps.append(Step(out, "call", (spec.name,) + tuple(reads)))
    return steps, out


def program_single(spec: OpSpec, tables, key) -> Program:
    """Read the directories once, call the operator once."""
    steps, out = _apply(spec, "x", 0, 0, tables)
    return Program(tuple(tables) + (to_opdef(spec),), (("x", key),),
                   tuple(steps), out)


def program_iterate(spec: OpSpec, tables, key, n: int) -> Program:
    """Call the operator n times, feeding each answer back in."""
    steps, prev, k, c = [], "x", 0, 0
    for _ in range(n):
        got, prev = _apply(spec, prev, k, c, tables)
        steps.extend(got)
        k += spec.arity
        c += 1
    return Program(tuple(tables) + (to_opdef(spec),), (("x", key),),
                   tuple(steps), prev)


def program_compose(sp1: OpSpec, t1, sp2: OpSpec, t2, key) -> Program:
    """Two operations acquired from two pages, applied one after the other."""
    a, out1 = _apply(sp1, "x", 0, 0, t1)
    b, out2 = _apply(sp2, out1, sp1.arity, 1, t2)
    return Program(tuple(t1) + tuple(t2)
                   + (to_opdef(sp1), to_opdef(sp2)),
                   (("x", key),), tuple(a) + tuple(b), out2)


# ------------------------------------------------------------ the tables


def make_tables(rng: random.Random, names, keys, values, plant: bool = False):
    """One directory per name, each a total function from the keys.

    Values are drawn from `values`, which for the depth ladder is the key set
    itself so that an answer can be fed back in. Every directory states every
    key, so a refusal in these programs is never a missing row.

    With `plant`, the first three keys are set so that the readings agree
    everywhere, agree in exactly two places, and disagree everywhere. Drawing
    those rows by chance gets unlikely as the number of directories grows, and
    an instance that never makes its readings agree would test one branch of
    the operation and report it as the operation.
    """
    m = len(names)
    rows = {nm: [] for nm in names}
    for i, k in enumerate(keys):
        if plant and i == 0 and len(values) >= 1:
            vals = [values[0]] * m
        elif plant and i == 1 and len(values) > m:
            vals = [values[0], values[0]] + [values[j + 1]
                                             for j in range(m - 2)]
        elif plant and i == 2 and len(values) >= m:
            vals = [values[j] for j in range(m)]
        else:
            vals = [rng.choice(values) for _ in range(m)]
        for nm, v in zip(names, vals):
            rows[nm].append((k, v))
    return tuple(Table(nm, tuple(rows[nm])) for nm in names)


def exercised(tables, keys) -> bool:
    """True when the key set reaches every branch an operation can have.

    The readings have to agree on some key and to disagree on some key, and,
    with three directories or more, to agree in exactly two places somewhere
    and to disagree everywhere somewhere. A draw that fails this leaves a
    clause of the operation never reached, so the item set would test one
    branch and report it as the operation.
    """
    m = len(tables)
    rows = [[dict(t.entries)[k] for t in tables] for k in keys]
    all_same = any(len(set(r)) == 1 for r in rows)
    not_all = any(len(set(r)) > 1 for r in rows)
    if m == 2:
        return all_same and not_all
    two = any(len(set(r)) == m - 1 for r in rows)
    all_diff = any(len(set(r)) == m for r in rows)
    return all_same and two and all_diff


# ----------------------------------------------------------- option sets


def options_for(make_program, keys) -> list:
    """The values the plan's last step could have returned, over the key set.

    Computed by running the interpreter on every key, so it is the plan's own
    reachable set and the chance floor that comes out of it is measured rather
    than assumed.
    """
    out = set()
    for k in keys:
        r = run(make_program(k))
        if r.ok:
            out.add(r.text)
    return sorted(out)


def is_degenerate(spec: OpSpec, tables, keys) -> bool:
    """True when the operation answers exactly what one directory states.

    Such a page states a new operator that computes an old one, so acquiring it
    proves nothing. They are counted and dropped rather than quietly kept.
    """
    got = []
    for k in keys:
        r = run(program_single(spec, tables, k))
        if not r.ok:
            return True
        got.append(r.text)
    for t in tables:
        d = dict(t.entries)
        if all(str(d[k]) == g for k, g in zip(keys, got)):
            return True
    return False


# ------------------------------------------------------------ persisting


def spec_json(spec: OpSpec) -> dict:
    return {"name": spec.name, "sources": list(spec.sources),
            "clauses": [[list(c), list(r)] for c, r in spec.clauses],
            "fallback": list(spec.fallback)}


def spec_load(o: dict) -> OpSpec:
    return OpSpec(o["name"], tuple(o["sources"]),
                  tuple((tuple(c), tuple(r)) for c, r in o["clauses"]),
                  tuple(o["fallback"]))


# --------------------------------------------------------------- library


class Library:
    """Operations an episode has read. Episode scoped, and never a gradient.

    `add` is the whole of learning here: a specification read off a page becomes
    an entry, and a plan that names the entry can then be executed. Nothing is
    fitted, nothing is averaged, and a second page stating the same operation
    changes nothing, which is why the acquisition curve for this system is a
    prediction about the code and not about a training run.

    An entry holds the whole specification, directories included, because which
    directories an operation reads and in what order is part of what the page
    says. Adding one name twice is allowed only when the two readings are
    identical: two pages stating different operations under one name are a
    refusal rather than a silent choice between them.
    """

    def __init__(self):
        self.ops: dict = {}
        self.n_added = 0
        self.n_pages = 0

    def add(self, spec: OpSpec) -> None:
        self.n_pages += 1
        old = self.ops.get(spec.name)
        if old is not None and old != spec:
            raise NormError(f"two pages state different operations "
                            f"called {spec.name}")
        if old is None:
            self.ops[spec.name] = spec
            self.n_added += 1

    def get(self, name: str) -> OpSpec:
        spec = self.ops.get(name)
        if spec is None:
            raise NormError(f"no page defines an operation called {name}")
        return spec

    def __len__(self) -> int:
        return len(self.ops)
