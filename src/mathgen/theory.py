"""Derive a theory from a sampled structure: definitions, theorems, a real DAG.

The structure in `algebra` fixes what is true. This module decides what gets
said about it, and in what order. Three kinds of node come out:

* definitions, each of which composes notions introduced earlier, so that the
  extension of a later definition cannot be computed without the earlier ones;
* theorems, each a universally quantified statement that the reference
  implementation settles by enumerating the carrier, kept only when it holds;
* refutations, which are the same candidate statements when they turn out false,
  carried with the concrete counterexample the enumeration found.

Refutations are not failures. A textbook that only ever asserts is a textbook
whose exercises can be answered by pattern matching, and the counterexamples are
the material for the "when it does not apply" sections and for the exercises
that ask a reader to distinguish a law from a plausible near miss.

Dependency edges are not decorative. An edge from node B to node A exists when
B's statement mentions a notion that A introduces, so the graph really does say
which earlier material a later chapter needs. `assign_chapters` then lays the
nodes out in an order that respects those edges, and the benchmark's
prerequisite levels are read off the same graph.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field

from src.mathgen.algebra import (AXIOM_MENU, Structure, axiom_profile,
                                 coin_word)

# Words for the notions a universe invents. Drawn per universe, never reused
# inside one, so no two universes name the same idea the same way twice by
# anything other than chance.
NOTION_KEYS = ["steady", "anchor", "regular", "agree", "core", "sealed",
               "span", "reach", "ridge", "floor", "shadow", "partner",
               "tight", "crest"]

AXIOM_TITLES = {
    "closure_first": "closure under the first operation",
    "associativity_first": "association of the first operation",
    "commutativity_first": "commutation of the first operation",
    "identity_first": "a neutral object for the first operation",
    "inverses_first": "reversal under the first operation",
    "idempotence_first": "self combination under the first operation",
    "cancellation_first": "cancellation in the first operation",
    "absorbing_first": "an absorbing object for the first operation",
    "closure_second": "closure under the second operation",
    "associativity_second": "association of the second operation",
    "commutativity_second": "commutation of the second operation",
    "identity_second": "a neutral object for the second operation",
    "idempotence_second": "self combination under the second operation",
    "distributivity": "spreading of the second operation over the first",
    "absorption": "the absorption pair",
    "relation_reflexive": "reflexivity of the relation",
    "relation_antisymmetric": "antisymmetry of the relation",
    "relation_transitive": "transitivity of the relation",
    "relation_total": "comparability of every pair",
    "relation_compatible_first": "agreement of the relation with the first operation",
    "relation_compatible_second": "agreement of the relation with the second operation",
}


@dataclass
class Node:
    """One numbered result. `payload` carries everything a machine needs."""

    node_id: str
    kind: str            # signature, axiom, definition, theorem, refutation
    key: str             # stable schema key, seed independent
    theme: str
    title: str
    statement: str
    depends_on: list[str] = field(default_factory=list)
    payload: dict = field(default_factory=dict)
    layer: int = 0
    chapter: int = 0

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id, "kind": self.kind, "key": self.key,
            "theme": self.theme, "title": self.title, "statement": self.statement,
            "depends_on": list(self.depends_on), "layer": self.layer,
            "chapter": self.chapter, "payload": self.payload,
        }


# ---------------------------------------------------------------------------
# Extensions: what each defined notion actually picks out, computed from tables
# ---------------------------------------------------------------------------


def ext_steady(s: Structure) -> frozenset:
    return frozenset(i for i in range(s.size) if s.op(0, i, i) == i)


def ext_regular(s: Structure) -> frozenset:
    e = s.identity_of(0)
    if e is None:
        return frozenset()
    return frozenset(i for i in range(s.size) if s.op(0, i, i) == e)


def ext_core(s: Structure) -> frozenset:
    return frozenset(i for i in range(s.size)
                     if all(s.op(0, i, j) == s.op(0, j, i) for j in range(s.size)))


def is_sealed(s: Structure, subset: frozenset) -> bool:
    return all(s.op(0, i, j) in subset for i in subset for j in subset)


def span_of(s: Structure, i: int) -> frozenset:
    """Closure of {i} under the first operation. Finite, so this terminates."""
    cur = {i}
    while True:
        nxt = set(cur)
        for a in cur:
            for b in cur:
                nxt.add(s.op(0, a, b))
        if nxt == cur:
            return frozenset(cur)
        cur = nxt


def reach_of(s: Structure, i: int) -> int:
    return len(span_of(s, i))


def ext_floor(s: Structure) -> frozenset:
    return frozenset(i for i in range(s.size)
                     if all(s.decide(i, j) for j in range(s.size)))


def shadow_of(s: Structure, i: int) -> frozenset:
    return frozenset(j for j in range(s.size) if s.decide(i, j))


def ext_tight(s: Structure) -> frozenset:
    """Pairs related in both directions, flattened to the elements involved."""
    return frozenset(i for i in range(s.size)
                     if any(i != j and s.decide(i, j) and s.decide(j, i)
                            for j in range(s.size)))


def names(s: Structure, subset) -> list[str]:
    return [s.name(i) for i in sorted(subset)]


# ---------------------------------------------------------------------------
# The theory
# ---------------------------------------------------------------------------


@dataclass
class Theory:
    structure: Structure
    profile: dict
    nodes: dict
    order: list
    notion_names: dict

    def node(self, node_id: str) -> Node:
        return self.nodes[node_id]

    def by_key(self, key: str) -> Node | None:
        for nid in self.order:
            if self.nodes[nid].key == key:
                return self.nodes[nid]
        return None

    def edges(self) -> list[tuple]:
        return [(dep, nid) for nid in self.order
                for dep in self.nodes[nid].depends_on]

    def depth(self) -> int:
        """Longest path in the dependency graph, counted in edges."""
        return max(self.nodes[nid].layer for nid in self.order)

    def prerequisites(self, node_id: str) -> set:
        """Transitive closure of what a node needs, node itself excluded."""
        seen: set = set()
        stack = list(self.nodes[node_id].depends_on)
        while stack:
            nid = stack.pop()
            if nid in seen:
                continue
            seen.add(nid)
            stack.extend(self.nodes[nid].depends_on)
        return seen

    def to_graph(self) -> dict:
        return {
            "system": self.structure.system_name,
            "seed": self.structure.seed,
            "nodes": [self.nodes[nid].to_dict() for nid in self.order],
            "edges": [{"from": a, "to": b} for a, b in self.edges()],
            "depth": self.depth(),
            "counts": {
                kind: sum(1 for nid in self.order if self.nodes[nid].kind == kind)
                for kind in ("signature", "axiom", "definition", "theorem", "refutation")
            },
        }


class _Builder:
    def __init__(self, structure: Structure, profile: dict, rng: random.Random):
        self.s = structure
        self.profile = profile
        self.rng = rng
        self.nodes: dict = {}
        self.order: list = []
        self.by_key_map: dict = {}
        self.counters = {"signature": 0, "axiom": 0, "definition": 0,
                         "theorem": 0, "refutation": 0}
        self.prefix = {"signature": "S", "axiom": "A", "definition": "D",
                       "theorem": "T", "refutation": "R"}

    def add(self, kind, key, theme, title, statement, deps, payload=None) -> Node:
        self.counters[kind] += 1
        nid = f"{self.prefix[kind]}{self.counters[kind]}"
        deps = [d for d in deps if d]
        layer = 0
        for d in deps:
            layer = max(layer, self.nodes[d].layer + 1)
        node = Node(node_id=nid, kind=kind, key=key, theme=theme, title=title,
                    statement=statement, depends_on=deps, payload=payload or {},
                    layer=layer)
        self.nodes[nid] = node
        self.order.append(nid)
        self.by_key_map[key] = nid
        return node

    def id_of(self, key: str) -> str | None:
        return self.by_key_map.get(key)

    def has(self, key: str) -> bool:
        return key in self.by_key_map


def _axiom_statement(s: Structure, name: str, witness) -> str:
    g0 = s.op_glyphs[0]
    g1 = s.op_glyphs[1] if s.has_two_ops else None
    o = s.object_plural
    r = s.rel_glyph
    table = {
        "closure_first": f"For all {o} x and y, x {g0} y is again a {s.object_name}.",
        "associativity_first": f"For all {o} x, y, z: (x {g0} y) {g0} z = x {g0} (y {g0} z).",
        "commutativity_first": f"For all {o} x and y: x {g0} y = y {g0} x.",
        "identity_first": (f"There is a {s.object_name} "
                           f"{witness.get('identity') if witness else '?'} with "
                           f"{witness.get('identity') if witness else '?'} {g0} x = x {g0} "
                           f"{witness.get('identity') if witness else '?'} = x for every x."),
        "inverses_first": (f"For every {s.object_name} x there is a {s.object_name} y "
                           f"with x {g0} y = y {g0} x = "
                           f"{witness.get('identity') if witness else '?'}."),
        "idempotence_first": f"For every {s.object_name} x: x {g0} x = x.",
        "cancellation_first": (f"For all {o} x, y, z: if x {g0} y = x {g0} z then y = z."),
        "absorbing_first": (f"There is a {s.object_name} "
                            f"{witness.get('absorbing') if witness else '?'} with "
                            f"{witness.get('absorbing') if witness else '?'} {g0} x = x {g0} "
                            f"{witness.get('absorbing') if witness else '?'} = "
                            f"{witness.get('absorbing') if witness else '?'} for every x."),
        "closure_second": f"For all {o} x and y, x {g1} y is again a {s.object_name}.",
        "associativity_second": f"For all {o} x, y, z: (x {g1} y) {g1} z = x {g1} (y {g1} z).",
        "commutativity_second": f"For all {o} x and y: x {g1} y = y {g1} x.",
        "identity_second": (f"There is a {s.object_name} "
                            f"{witness.get('identity') if witness else '?'} with "
                            f"{witness.get('identity') if witness else '?'} {g1} x = x for every x."),
        "idempotence_second": f"For every {s.object_name} x: x {g1} x = x.",
        "distributivity": (f"For all {o} x, y, z: x {g1} (y {g0} z) = (x {g1} y) {g0} "
                           f"(x {g1} z), and the same on the right."),
        "absorption": (f"For all {o} x and y: x {g0} (x {g1} y) = x and "
                       f"x {g1} (x {g0} y) = x."),
        "relation_reflexive": f"For every {s.object_name} x: x {r} x.",
        "relation_antisymmetric": (f"For all {o} x and y: if x {r} y and y {r} x "
                                   f"then x = y."),
        "relation_transitive": f"For all {o} x, y, z: if x {r} y and y {r} z then x {r} z.",
        "relation_total": f"For all {o} x and y, at least one of x {r} y and y {r} x holds.",
        "relation_compatible_first": (f"For all {o} x, y, z: if x {r} y then "
                                      f"(z {g0} x) {r} (z {g0} y) and (x {g0} z) {r} (y {g0} z)."),
        "relation_compatible_second": (f"For all {o} x, y, z: if x {r} y then "
                                       f"(z {g1} x) {r} (z {g1} y) and (x {g1} z) {r} (y {g1} z)."),
    }
    return table[name]


AXIOM_THEMES = {
    "closure_first": "operations", "associativity_first": "operations",
    "commutativity_first": "operations", "identity_first": "neutral",
    "inverses_first": "neutral", "idempotence_first": "operations",
    "cancellation_first": "operations", "absorbing_first": "neutral",
    "closure_second": "second_operation", "associativity_second": "second_operation",
    "commutativity_second": "second_operation", "identity_second": "second_operation",
    "idempotence_second": "second_operation", "distributivity": "second_operation",
    "absorption": "second_operation", "relation_reflexive": "relation",
    "relation_antisymmetric": "relation", "relation_transitive": "relation",
    "relation_total": "relation", "relation_compatible_first": "relation",
    "relation_compatible_second": "relation",
}


def _cases_pairs(n):
    return n * n


def _cases_triples(n):
    return n * n * n


# ---------------------------------------------------------------------------
# Theorem schemas. Each returns (holds, witness, cases, domain).
# ---------------------------------------------------------------------------


def _axiom_statement_negative(s: Structure, name: str) -> str:
    """State a menu axiom that this system fails, without leaning on a witness."""
    g0 = s.op_glyphs[0]
    obj = s.object_name
    special = {
        "identity_first": (f"There is no {obj} e with e {g0} x = x {g0} e = x for "
                           f"every {obj} x."),
        "inverses_first": (f"Some {obj} x admits no {obj} y for which x {g0} y and "
                           f"y {g0} x both land on a neutral object."),
        "absorbing_first": (f"There is no {obj} z with z {g0} x = x {g0} z = z for "
                            f"every {obj} x."),
        "identity_second": (f"There is no {obj} that leaves every {obj} unchanged "
                            f"under the second operation."),
    }
    if name in special:
        return special[name]
    return "It is not the case that: " + _axiom_statement(s, name, {})


def _disproof_steps(s: Structure, tables_id: str, witness) -> list[dict]:
    """The proof of a refutation is its counterexample, read off the tables."""
    if not witness:
        return [{"cites": tables_id,
                 "text": ("Running the claim over every case in the tables turns up "
                          "at least one case where it fails.")}]
    parts = ", ".join(f"{k} = {v}" for k, v in witness.items())
    return [
        {"cites": tables_id,
         "text": f"Take the case {parts}, read straight from the tables."},
        {"cites": tables_id,
         "text": ("The two sides of the claim come apart on that case, so the "
                  "claim cannot hold for every case.")},
        {"cites": None,
         "text": ("One counterexample is enough. Note that the claim may still "
                  "hold for many particular objects; what fails is the "
                  "universal reading.")},
    ]


def _chk_anchor_unique(s):
    ids = [i for i in range(s.size)
           if all(s.op(0, i, x) == x and s.op(0, x, i) == x for x in range(s.size))]
    return len(ids) == 1, {"identities": names(s, ids)}, s.size * s.size, "every object paired with every object"


def _chk_partner_unique(s):
    e = s.identity_of(0)
    for i in range(s.size):
        partners = [j for j in range(s.size)
                    if s.op(0, i, j) == e and s.op(0, j, i) == e]
        if len(partners) > 1:
            return False, {"x": s.name(i), "partners": names(s, partners)}, _cases_pairs(s.size), "every ordered pair"
    return True, None, _cases_pairs(s.size), "every ordered pair"


def _chk_core_sealed(s):
    core = ext_core(s)
    for i in core:
        for j in core:
            if s.op(0, i, j) not in core:
                return (False, {"x": s.name(i), "y": s.name(j),
                                "value": s.name(s.op(0, i, j))},
                        _cases_pairs(s.size), "every ordered pair drawn from the core")
    return True, {"core": names(s, core)}, _cases_pairs(s.size), "every ordered pair drawn from the core"


def _chk_span_sealed(s):
    for i in range(s.size):
        if not is_sealed(s, span_of(s, i)):
            return False, {"x": s.name(i)}, s.size * _cases_pairs(s.size), "every object, then every pair inside its span"
    return True, None, s.size * _cases_pairs(s.size), "every object, then every pair inside its span"


def _chk_span_is_smallest(s):
    """The span of x sits inside every sealed collection that contains x."""
    all_sets = []
    if s.size <= 6:
        for r in range(1, s.size + 1):
            for combo in itertools.combinations(range(s.size), r):
                fs = frozenset(combo)
                if is_sealed(s, fs):
                    all_sets.append(fs)
    for i in range(s.size):
        sp = span_of(s, i)
        for fs in all_sets:
            if i in fs and not sp <= fs:
                return False, {"x": s.name(i), "set": names(s, fs)}, len(all_sets) * s.size, "every sealed collection against every object"
    return True, {"sealed_count": len(all_sets)}, len(all_sets) * s.size, "every sealed collection against every object"


def _chk_ridge_sealed(s):
    ridge = ext_steady(s)
    for i in ridge:
        for j in ridge:
            if s.op(0, i, j) not in ridge:
                return (False, {"x": s.name(i), "y": s.name(j),
                                "value": s.name(s.op(0, i, j))},
                        _cases_pairs(s.size), "every ordered pair drawn from the ridge")
    return True, {"ridge": names(s, ridge)}, _cases_pairs(s.size), "every ordered pair drawn from the ridge"


def _chk_steady_iff_reach_one(s):
    for i in range(s.size):
        if (reach_of(s, i) == 1) != (s.op(0, i, i) == i):
            return False, {"x": s.name(i), "reach": reach_of(s, i)}, s.size, "every object"
    return True, None, s.size, "every object"


def _chk_reach_divides_size(s):
    for i in range(s.size):
        if s.size % reach_of(s, i) != 0:
            return (False, {"x": s.name(i), "reach": reach_of(s, i), "size": s.size},
                    s.size, "every object")
    return True, None, s.size, "every object"


def _chk_anchor_in_core(s):
    e = s.identity_of(0)
    core = ext_core(s)
    return e in core, {"anchor": s.name(e), "core": names(s, core)}, s.size, "the anchor against every object"


def _chk_regular_is_own_partner(s):
    e = s.identity_of(0)
    for i in range(s.size):
        if s.op(0, i, i) == e:
            inv = s.inverse_of(i, 0)
            if inv != i:
                return False, {"x": s.name(i)}, s.size, "every object"
    return True, None, s.size, "every object"


def _chk_translation_injective(s):
    for a in range(s.size):
        seen = {}
        for x in range(s.size):
            v = s.op(0, a, x)
            if v in seen:
                return (False, {"a": s.name(a), "x": s.name(seen[v]), "y": s.name(x),
                                "value": s.name(v)},
                        _cases_pairs(s.size), "every object translated by every object")
            seen[v] = x
    return True, None, _cases_pairs(s.size), "every object translated by every object"


def _chk_span_inside_core(s):
    core = ext_core(s)
    for i in core:
        if not span_of(s, i) <= core:
            return False, {"x": s.name(i), "span": names(s, span_of(s, i))}, s.size * s.size, "every object of the core, then its span"
    return True, None, s.size * s.size, "every object of the core, then its span"


def _chk_shadow_nested(s):
    for i in range(s.size):
        for j in shadow_of(s, i):
            if not shadow_of(s, j) <= shadow_of(s, i):
                return (False, {"x": s.name(i), "y": s.name(j)},
                        _cases_triples(s.size), "every ordered triple")
    return True, None, _cases_triples(s.size), "every ordered triple"


def _chk_floor_unique(s):
    fl = ext_floor(s)
    return len(fl) <= 1, {"floors": names(s, fl)}, _cases_pairs(s.size), "every candidate against every object"


def _chk_floor_exists(s):
    fl = ext_floor(s)
    return len(fl) >= 1, {"floors": names(s, fl)}, _cases_pairs(s.size), "every candidate against every object"


def _chk_shadow_closed_under_op(s):
    """If x REL y then x REL (y op z) fails or holds; a compatibility restatement."""
    for x in range(s.size):
        for y in shadow_of(s, x):
            for z in range(s.size):
                if not s.decide(s.op(0, x, z), s.op(0, y, z)):
                    return (False, {"x": s.name(x), "y": s.name(y), "z": s.name(z)},
                            _cases_triples(s.size), "every ordered triple")
    return True, None, _cases_triples(s.size), "every ordered triple"


def _chk_absorption_forces_idempotence(s):
    for i in range(s.size):
        if s.op(0, i, i) != i or s.op(1, i, i) != i:
            return False, {"x": s.name(i)}, s.size, "every object under both operations"
    return True, None, s.size, "every object under both operations"


def _chk_distributive_absorbing(s):
    """The absorbing object of the first operation is absorbing for the second."""
    z = None
    for i in range(s.size):
        if all(s.op(0, i, x) == i and s.op(0, x, i) == i for x in range(s.size)):
            z = i
            break
    if z is None:
        return False, {"reason": "no absorbing object"}, s.size, "every object"
    for x in range(s.size):
        if s.op(1, z, x) != z or s.op(1, x, z) != z:
            return (False, {"z": s.name(z), "x": s.name(x),
                            "value": s.name(s.op(1, z, x))},
                    s.size, "every object")
    return True, {"absorbing": s.name(z)}, s.size, "every object"


def _chk_second_op_preserves_core(s):
    core = ext_core(s)
    for i in core:
        for j in core:
            if s.op(1, i, j) not in core:
                return (False, {"x": s.name(i), "y": s.name(j),
                                "value": s.name(s.op(1, i, j))},
                        _cases_pairs(s.size), "every ordered pair from the core")
    return True, None, _cases_pairs(s.size), "every ordered pair from the core"


def _chk_core_is_everything(s):
    core = ext_core(s)
    if len(core) == s.size:
        return True, None, _cases_pairs(s.size), "every ordered pair"
    missing = sorted(set(range(s.size)) - core)[0]
    other = next(j for j in range(s.size)
                 if s.op(0, missing, j) != s.op(0, j, missing))
    return (False, {"x": s.name(missing), "y": s.name(other),
                    "left": s.name(s.op(0, missing, other)),
                    "right": s.name(s.op(0, other, missing))},
            _cases_pairs(s.size), "every ordered pair")


def _chk_ridge_is_everything(s):
    ridge = ext_steady(s)
    if len(ridge) == s.size:
        return True, None, s.size, "every object"
    bad = sorted(set(range(s.size)) - ridge)[0]
    return (False, {"x": s.name(bad), "value": s.name(s.op(0, bad, bad))},
            s.size, "every object")


def _chk_some_object_spans_all(s):
    for i in range(s.size):
        if len(span_of(s, i)) == s.size:
            return True, {"generator": s.name(i)}, s.size, "every object and its span"
    return (False, {"largest_span": max(len(span_of(s, i)) for i in range(s.size)),
                    "size": s.size},
            s.size, "every object and its span")


def _chk_relation_symmetric(s):
    for i, j in itertools.product(range(s.size), repeat=2):
        if s.decide(i, j) and not s.decide(j, i):
            return False, {"x": s.name(i), "y": s.name(j)}, _cases_pairs(s.size), "every ordered pair"
    return True, None, _cases_pairs(s.size), "every ordered pair"


def _chk_anchor_is_absorbing(s):
    e = s.identity_of(0)
    for x in range(s.size):
        if s.op(0, e, x) != e:
            return (False, {"anchor": s.name(e), "x": s.name(x),
                            "value": s.name(s.op(0, e, x))},
                    s.size, "the anchor against every object")
    return True, None, s.size, "the anchor against every object"


def _chk_tight_is_empty(s):
    t = ext_tight(s)
    return len(t) == 0, {"tight": names(s, t)}, _cases_pairs(s.size), "every ordered pair"


# Every candidate keyed by its schema name, so verification can re-run a claim
# from the emitted graph alone without reconstructing the builder's control flow.
THEOREM_CHECKERS = {
    "thm:anchor_unique": _chk_anchor_unique,
    "thm:partner_unique": _chk_partner_unique,
    "thm:regular_own_partner": _chk_regular_is_own_partner,
    "thm:anchor_in_core": _chk_anchor_in_core,
    "thm:core_sealed": _chk_core_sealed,
    "thm:span_sealed": _chk_span_sealed,
    "thm:span_smallest": _chk_span_is_smallest,
    "thm:steady_iff_reach_one": _chk_steady_iff_reach_one,
    "thm:reach_divides_size": _chk_reach_divides_size,
    "thm:span_inside_core": _chk_span_inside_core,
    "thm:ridge_sealed": _chk_ridge_sealed,
    "thm:translation_injective": _chk_translation_injective,
    "thm:shadow_nested": _chk_shadow_nested,
    "thm:floor_unique": _chk_floor_unique,
    "thm:floor_exists": _chk_floor_exists,
    "thm:shadow_compatible": _chk_shadow_closed_under_op,
    "thm:tight_empty": _chk_tight_is_empty,
    "thm:core_is_everything": _chk_core_is_everything,
    "thm:ridge_is_everything": _chk_ridge_is_everything,
    "thm:some_object_spans_all": _chk_some_object_spans_all,
    "thm:relation_symmetric": _chk_relation_symmetric,
    "thm:anchor_is_absorbing": _chk_anchor_is_absorbing,
    "thm:absorption_idempotence": _chk_absorption_forces_idempotence,
    "thm:distributive_absorbing": _chk_distributive_absorbing,
    "thm:second_op_preserves_core": _chk_second_op_preserves_core,
}

# How to recompute the extension a definition claims, keyed the same way.
DEFINITION_EXTENSIONS = {
    "def:steady": lambda s: {"extension": names(s, ext_steady(s))},
    "def:core": lambda s: {"extension": names(s, ext_core(s))},
    "def:ridge": lambda s: {"extension": names(s, ext_steady(s))},
    "def:regular": lambda s: {"extension": names(s, ext_regular(s))},
    "def:floor": lambda s: {"extension": names(s, ext_floor(s))},
    "def:tight": lambda s: {"extension": names(s, ext_tight(s))},
    "def:span": lambda s: {"map": {s.name(i): names(s, span_of(s, i))
                                   for i in range(s.size)}},
    "def:reach": lambda s: {"map": {s.name(i): reach_of(s, i)
                                    for i in range(s.size)}},
    "def:shadow": lambda s: {"map": {s.name(i): names(s, shadow_of(s, i))
                                     for i in range(s.size)}},
    "def:partner": lambda s: {"map": {s.name(i): s.name(s.inverse_of(i, 0))
                                      for i in range(s.size)}},
    "def:anchor": lambda s: {"element": s.name(s.identity_of(0))},
    "def:crest": lambda s: {"extension": names(s, frozenset(
        i for i in range(s.size)
        if reach_of(s, i) == max(reach_of(s, j) for j in range(s.size))))},
    "def:agree": lambda s: {"pairs": [[s.name(i), s.name(j)]
                                      for i in range(s.size) for j in range(s.size)
                                      if s.op(0, i, j) == s.op(0, j, i)]},
}


# ---------------------------------------------------------------------------
# Building the theory
# ---------------------------------------------------------------------------


def build_theory(structure: Structure) -> Theory:
    """Derive the whole layered theory of one structure."""
    s = structure
    profile = axiom_profile(s)
    holds = profile["holds"]
    rng = random.Random(s.seed ^ 0xA11CE)
    used = set(s.elements) | {s.object_name, s.system_name.lower()}
    notion = {k: coin_word(rng, 2, used) for k in NOTION_KEYS}
    b = _Builder(s, profile, rng)

    g0 = s.op_glyphs[0]
    g1 = s.op_glyphs[1] if s.has_two_ops else None
    r = s.rel_glyph
    obj, objs = s.object_name, s.object_plural

    # -- signature ---------------------------------------------------------
    sig = b.add("signature", "signature", "signature",
                f"the {s.system_name} signature",
                (f"The {s.system_name} system concerns objects called {objs}. There "
                 f"are exactly {s.size} of them: {', '.join(s.elements)}. "
                 + (f"Two operations are written {g0} and {g1}. "
                    if s.has_two_ops else f"One operation is written {g0}. ")
                 + f"One relation is written {r}, read as \"{s.rel_name}\"."),
                [],
                {"elements": list(s.elements), "op_glyphs": list(s.op_glyphs),
                 "rel_glyph": r, "size": s.size})
    tables_node = b.add("signature", "tables", "signature",
                        f"the {s.system_name} combination tables",
                        (f"The value of x {g0} y for every pair of {objs} is fixed by "
                         f"the table of the first operation"
                         + (f", and likewise for {g1}." if s.has_two_ops else ".")
                         + f" The pairs standing in the {r} relation are listed "
                           f"in full."),
                        [sig.node_id],
                        {"tables": [[row[:] for row in t] for t in s.tables],
                         "relation_pairs": [[s.name(i), s.name(j)]
                                            for i, j in sorted(s.rel_pairs)]})

    # -- axioms ------------------------------------------------------------
    axiom_ids: dict = {}
    for name, _check in AXIOM_MENU:
        if name not in holds:
            continue
        node = b.add("axiom", f"axiom:{name}", AXIOM_THEMES[name],
                     AXIOM_TITLES[name],
                     _axiom_statement(s, name, holds[name]),
                     [tables_node.node_id],
                     {"axiom": name, "witness": holds[name],
                      "verified_by": "exhaustive enumeration of the carrier"})
        axiom_ids[name] = node.node_id

    # Menu axioms this system fails are carried too, as refutations with the
    # counterexample the enumeration found. They are the honest half of the
    # picture: a chapter that says only what holds gives a reader no way to tell
    # a law of this system from a law they are importing out of habit.
    for name, _check in AXIOM_MENU:
        if name not in profile["fails"]:
            continue
        witness = profile["fails"][name]
        if witness and witness.get("reason") == "one operation only":
            continue
        b.add("refutation", f"axiom_fails:{name}", AXIOM_THEMES[name],
              f"the system does not have {AXIOM_TITLES[name]}",
              _axiom_statement_negative(s, name), [tables_node.node_id],
              {"axiom": name, "witness": witness,
               "verification": {
                   "result": False,
                   "cases_enumerated": s.size ** 3,
                   "domain": "every tuple of the carrier the axiom quantifies over",
                   "method": "exhaustive enumeration by the reference implementation"},
               "proof": _disproof_steps(s, tables_node.node_id, witness)})

    def ax(name):
        return axiom_ids.get(name)

    # -- definitions, layer one -------------------------------------------
    d_steady = b.add("definition", "def:steady", "operations",
                     f"{notion['steady']} {objs}",
                     f"A {obj} x is called {notion['steady']} when x {g0} x = x.",
                     [ax("closure_first") or tables_node.node_id],
                     {"notion": notion["steady"],
                      "extension": names(s, ext_steady(s))})

    d_agree = b.add("definition", "def:agree", "operations",
                    f"{objs} that {notion['agree']}",
                    (f"Two {objs} x and y are said to {notion['agree']} when "
                     f"x {g0} y = y {g0} x."),
                    [ax("closure_first") or tables_node.node_id],
                    {"notion": notion["agree"],
                     "pairs": [[s.name(i), s.name(j)]
                               for i in range(s.size) for j in range(s.size)
                               if s.op(0, i, j) == s.op(0, j, i)]})

    d_sealed = b.add("definition", "def:sealed", "collections",
                     f"{notion['sealed']} collections",
                     (f"A collection S of {objs} is {notion['sealed']} when x {g0} y "
                      f"belongs to S for every pair x, y drawn from S."),
                     [ax("closure_first") or tables_node.node_id],
                     {"notion": notion["sealed"]})

    d_shadow = b.add("definition", "def:shadow", "relation",
                     f"the {notion['shadow']} of a {obj}",
                     (f"The {notion['shadow']} of a {obj} x is the collection of "
                      f"{objs} y for which x {r} y holds."),
                     [tables_node.node_id],
                     {"notion": notion["shadow"],
                      "map": {s.name(i): names(s, shadow_of(s, i))
                              for i in range(s.size)}})

    d_anchor = None
    if "identity_first" in holds:
        e = s.identity_of(0)
        d_anchor = b.add("definition", "def:anchor", "neutral",
                         f"the {notion['anchor']}",
                         (f"The {obj} {s.name(e)} is called the {notion['anchor']} of "
                          f"the system. It is the unique {obj} that leaves every {obj} "
                          f"unchanged under {g0}."),
                         [ax("identity_first")],
                         {"notion": notion["anchor"], "element": s.name(e)})

    # -- definitions, layer two -------------------------------------------
    d_core = b.add("definition", "def:core", "operations",
                   f"the {notion['core']}",
                   (f"The {notion['core']} of the system is the collection of {objs} "
                    f"that {notion['agree']} with every {obj}."),
                   [d_agree.node_id],
                   {"notion": notion["core"], "extension": names(s, ext_core(s))})

    d_ridge = b.add("definition", "def:ridge", "operations",
                    f"the {notion['ridge']}",
                    (f"The {notion['ridge']} is the collection of all "
                     f"{notion['steady']} {objs}."),
                    [d_steady.node_id],
                    {"notion": notion["ridge"], "extension": names(s, ext_steady(s))})

    d_span = b.add("definition", "def:span", "collections",
                   f"the {notion['span']} of a {obj}",
                   (f"The {notion['span']} of a {obj} x, written [x], is the smallest "
                    f"{notion['sealed']} collection that contains x."),
                   [d_sealed.node_id],
                   {"notion": notion["span"],
                    "map": {s.name(i): names(s, span_of(s, i)) for i in range(s.size)}})

    d_floor = b.add("definition", "def:floor", "relation",
                    f"a {notion['floor']}",
                    (f"A {obj} f is a {notion['floor']} when f {r} y holds for every "
                     f"{obj} y, that is, when the {notion['shadow']} of f is the whole "
                     f"system."),
                    [d_shadow.node_id],
                    {"notion": notion["floor"], "extension": names(s, ext_floor(s))})

    d_regular = None
    if d_anchor is not None:
        d_regular = b.add("definition", "def:regular", "neutral",
                          f"{notion['regular']} {objs}",
                          (f"A {obj} x is {notion['regular']} when x {g0} x equals the "
                           f"{notion['anchor']}."),
                          [d_anchor.node_id, d_steady.node_id],
                          {"notion": notion["regular"],
                           "extension": names(s, ext_regular(s))})

    d_partner = None
    if "inverses_first" in holds and d_anchor is not None:
        d_partner = b.add("definition", "def:partner", "neutral",
                          f"the {notion['partner']} of a {obj}",
                          (f"A {notion['partner']} of a {obj} x is a {obj} y with "
                           f"x {g0} y = y {g0} x = {d_anchor.payload['element']}."),
                          [d_anchor.node_id, ax("inverses_first")],
                          {"notion": notion["partner"],
                           "map": {s.name(i): s.name(s.inverse_of(i, 0))
                                   for i in range(s.size)}})

    # -- definitions, layer three -----------------------------------------
    d_reach = b.add("definition", "def:reach", "collections",
                    f"the {notion['reach']} of a {obj}",
                    (f"The {notion['reach']} of a {obj} x is the number of {objs} in "
                     f"its {notion['span']} [x]."),
                    [d_span.node_id],
                    {"notion": notion["reach"],
                     "map": {s.name(i): reach_of(s, i) for i in range(s.size)}})

    d_crest = b.add("definition", "def:crest", "collections",
                    f"the {notion['crest']}",
                    (f"The {notion['crest']} of the system is the collection of {objs} "
                     f"whose {notion['reach']} is largest."),
                    [d_reach.node_id],
                    {"notion": notion["crest"],
                     "extension": names(s, frozenset(
                         i for i in range(s.size)
                         if reach_of(s, i) == max(reach_of(s, j)
                                                  for j in range(s.size))))})

    d_tight = b.add("definition", "def:tight", "relation",
                    f"{notion['tight']} pairs",
                    (f"Two distinct {objs} x and y form a {notion['tight']} pair when "
                     f"x {r} y and y {r} x both hold, that is, when each lies in the "
                     f"{notion['shadow']} of the other."),
                    [d_shadow.node_id],
                    {"notion": notion["tight"], "extension": names(s, ext_tight(s))})

    # -- candidate results -------------------------------------------------
    #
    # Each candidate is settled the moment it is declared, so a later candidate
    # can cite the node id of an earlier one and the dependency edges reflect
    # the order the material is actually developed in. A candidate whose
    # dependencies are absent (an axiom this system does not satisfy) is simply
    # not raised, and `cand` returns None so downstream gates close too.
    def cand(key, theme, title, statement, deps, checker, proof):
        if any(d is None for d in deps):
            return None
        holds_it, witness, cases, domain = checker(s)
        payload = {
            "witness": witness,
            "verification": {
                "result": bool(holds_it),
                "cases_enumerated": cases,
                "domain": domain,
                "method": "exhaustive enumeration by the reference implementation",
            },
        }
        if holds_it:
            payload["proof"] = [{"cites": cite, "text": text}
                                for cite, text in proof(witness)]
            node = b.add("theorem", key, theme, title, statement, deps, payload)
        else:
            payload["proof"] = _disproof_steps(s, tables_node.node_id, witness)
            node = b.add("refutation", key, theme, f"where {title} breaks down",
                         f"It is not the case that: {statement}", deps, payload)
        return node.node_id

    if d_anchor is not None:
        t_anchor_unique = cand("thm:anchor_unique", "neutral",
             f"the {notion['anchor']} is the only one of its kind",
             (f"There is exactly one {obj} e with e {g0} x = x {g0} e = x for every "
              f"{obj} x."),
             [d_anchor.node_id, ax("identity_first")], _chk_anchor_unique,
             lambda w: [
                 (d_anchor.node_id, f"Suppose e and f both leave every {obj} unchanged."),
                 (ax("identity_first"), f"Then e {g0} f = f, reading e as neutral on the left."),
                 (ax("identity_first"), f"And e {g0} f = e, reading f as neutral on the right."),
                 (None, "So e = f, and the two suppositions describe the same object."),
             ])
        t_anchor_in_core = cand("thm:anchor_in_core", "operations",
             f"the {notion['anchor']} lies in the {notion['core']}",
             f"The {notion['anchor']} {notion['agree']}s with every {obj}.",
             [d_anchor.node_id, d_core.node_id], _chk_anchor_in_core,
             lambda w: [
                 (d_anchor.node_id, f"Let e be the {notion['anchor']} and x any {obj}."),
                 (d_anchor.node_id, f"Then e {g0} x = x and x {g0} e = x."),
                 (d_agree.node_id, f"So e {g0} x = x {g0} e, which is what it means to {notion['agree']}."),
                 (d_core.node_id, f"Since x was arbitrary, e belongs to the {notion['core']}."),
             ])

    if d_partner is not None:
        t_partner_unique = cand("thm:partner_unique", "neutral",
             f"a {obj} has only one {notion['partner']}",
             f"For every {obj} x there is exactly one {notion['partner']} of x.",
             [d_partner.node_id, ax("associativity_first"), t_anchor_unique],
             _chk_partner_unique,
             lambda w: [
                 (d_partner.node_id, "Let y and z both be partners of x."),
                 (ax("associativity_first"), f"Then y = y {g0} (x {g0} z) = (y {g0} x) {g0} z."),
                 (d_partner.node_id, "Both bracketed products collapse to the neutral object."),
                 (None, "So y = z."),
             ])
        if d_regular is not None:
            t_regular_own = cand("thm:regular_own_partner", "neutral",
                 f"a {notion['regular']} {obj} is its own {notion['partner']}",
                 (f"If x {g0} x is the {notion['anchor']} then the {notion['partner']} "
                  f"of x is x itself."),
                 [d_regular.node_id, d_partner.node_id, t_partner_unique],
                 _chk_regular_is_own_partner,
                 lambda w: [
                     (d_regular.node_id, f"Let x be {notion['regular']}, so x {g0} x is the {notion['anchor']}."),
                     (d_partner.node_id, "That is exactly the condition for x to be a partner of x."),
                     (t_partner_unique, "Partners are unique, so no other object can be one."),
                 ])

    t_core_sealed = cand("thm:core_sealed", "operations",
         f"the {notion['core']} is {notion['sealed']}",
         (f"If x and y both {notion['agree']} with every {obj}, then so does "
          f"x {g0} y."),
         [d_core.node_id, d_sealed.node_id, ax("associativity_first")],
         _chk_core_sealed,
         lambda w: [
             (d_core.node_id, f"Let x and y lie in the {notion['core']} and let z be any {obj}."),
             (ax("associativity_first"), f"Then (x {g0} y) {g0} z = x {g0} (y {g0} z)."),
             (d_core.node_id, f"Move z past y, then past x, using that each {notion['agree']}s with everything."),
             (d_sealed.node_id, f"So x {g0} y {notion['agree']}s with z, and the {notion['core']} is {notion['sealed']}."),
         ])

    t_span_sealed = cand("thm:span_sealed", "collections",
         f"the {notion['span']} of a {obj} is {notion['sealed']}",
         f"For every {obj} x, the collection [x] is {notion['sealed']}.",
         [d_span.node_id, d_sealed.node_id], _chk_span_sealed,
         lambda w: [
             (d_span.node_id, f"[x] is built by taking x and closing under {g0}."),
             (d_sealed.node_id, "Closing under an operation is exactly the sealing condition."),
             (None, "The carrier is finite, so the closure stops after finitely many rounds."),
         ])

    t_span_smallest = cand("thm:span_smallest", "collections",
         f"the {notion['span']} is contained in every {notion['sealed']} collection",
         (f"If S is {notion['sealed']} and contains x, then S contains all of [x]."),
         [d_span.node_id, t_span_sealed or d_sealed.node_id],
         _chk_span_is_smallest,
         lambda w: [
             (d_span.node_id, "Every member of [x] is reached from x by finitely many applications of the operation."),
             (d_sealed.node_id, "A sealed S containing x is closed under each of those applications."),
             (None, "So each member of [x] is in S, by induction on the number of applications."),
         ])

    t_steady_reach = cand("thm:steady_iff_reach_one", "collections",
         f"a {obj} is {notion['steady']} exactly when its {notion['reach']} is one",
         (f"x {g0} x = x holds if and only if [x] contains x alone."),
         [d_steady.node_id, d_reach.node_id, t_span_sealed],
         _chk_steady_iff_reach_one,
         lambda w: [
             (d_steady.node_id, f"If x {g0} x = x then {{x}} is already closed under {g0}."),
             (t_span_sealed, f"So [x] = {{x}} and the {notion['reach']} is one."),
             (d_reach.node_id, "Conversely a span of one object must contain x {} x, which is then x.".format(g0)),
         ])

    t_reach_div = cand("thm:reach_divides_size", "collections",
         f"the {notion['reach']} divides the number of {objs}",
         (f"For every {obj} x, the {notion['reach']} of x divides {s.size}."),
         [d_reach.node_id, t_span_sealed], _chk_reach_divides_size,
         lambda w: [
             (t_span_sealed, f"[x] is a {notion['sealed']} collection."),
             (d_reach.node_id, f"Its size is the {notion['reach']} of x."),
             (None, f"The claim is that this size always divides {s.size}."),
         ])

    t_span_core = cand("thm:span_inside_core", "operations",
         f"the {notion['span']} of a {notion['core']} {obj} stays in the {notion['core']}",
         (f"If x lies in the {notion['core']} then every {obj} of [x] lies in the "
          f"{notion['core']}."),
         [d_span.node_id, d_core.node_id, t_core_sealed],
         _chk_span_inside_core,
         lambda w: [
             (t_core_sealed, f"The {notion['core']} is {notion['sealed']}."),
             (d_span.node_id, f"[x] is the smallest {notion['sealed']} collection containing x."),
             (None, f"A smallest such collection sits inside any other, and the {notion['core']} is one."),
         ])

    t_ridge_sealed = cand("thm:ridge_sealed", "operations",
         f"the {notion['ridge']} is {notion['sealed']}",
         (f"If x and y are both {notion['steady']} then so is x {g0} y."),
         [d_ridge.node_id, d_sealed.node_id], _chk_ridge_sealed,
         lambda w: [
             (d_ridge.node_id, f"Let x and y be {notion['steady']}."),
             (d_steady.node_id, f"The claim asks whether (x {g0} y) {g0} (x {g0} y) returns x {g0} y."),
             (None, "Whether it does is settled by running the operation table on every such pair."),
         ])

    t_translation = cand("thm:translation_injective", "operations",
         f"combining on the left never merges two {objs}",
         (f"For every {obj} a, the assignment x to a {g0} x sends distinct {objs} to "
          f"distinct {objs}."),
         [ax("cancellation_first"), d_agree.node_id], _chk_translation_injective,
         lambda w: [
             (ax("cancellation_first"), f"Suppose a {g0} x = a {g0} y."),
             (ax("cancellation_first"), "Cancellation on the left gives x = y."),
             (None, "So the assignment is injective, and being injective on a finite carrier it is onto."),
         ])

    t_shadow_nested = cand("thm:shadow_nested", "relation",
         f"{notion['shadow']}s are nested along the relation",
         (f"If y lies in the {notion['shadow']} of x, then the {notion['shadow']} of y "
          f"is contained in the {notion['shadow']} of x."),
         [d_shadow.node_id, ax("relation_transitive")], _chk_shadow_nested,
         lambda w: [
             (d_shadow.node_id, f"Let y satisfy x {r} y and let z satisfy y {r} z."),
             (ax("relation_transitive"), f"Transitivity gives x {r} z."),
             (d_shadow.node_id, f"So every member of the {notion['shadow']} of y is a member of that of x."),
         ])

    t_floor_unique = cand("thm:floor_unique", "relation",
         f"there is at most one {notion['floor']}",
         f"No two distinct {objs} can both be {notion['floor']}s.",
         [d_floor.node_id, ax("relation_antisymmetric")], _chk_floor_unique,
         lambda w: [
             (d_floor.node_id, "Let f and h both be floors."),
             (d_floor.node_id, f"Then f {r} h, since h is any object, and h {r} f likewise."),
             (ax("relation_antisymmetric"), "Antisymmetry forces f = h."),
         ])

    t_floor_exists = cand("thm:floor_exists", "relation",
         f"the system has a {notion['floor']}",
         f"Some {obj} {notion['floor']}s the whole system.",
         [d_floor.node_id, ax("relation_total")], _chk_floor_exists,
         lambda w: [
             (ax("relation_total"), "Every pair is comparable, so the relation orders the objects into a line."),
             (d_floor.node_id, "The claim is that the line has a bottom."),
             (None, "The carrier is finite, so the search over candidates terminates."),
         ])

    t_shadow_compat = cand("thm:shadow_compatible", "relation",
         f"the relation survives combination on the right",
         (f"If x {r} y then (x {g0} z) {r} (y {g0} z) for every {obj} z."),
         [d_shadow.node_id, ax("relation_compatible_first")],
         _chk_shadow_closed_under_op,
         lambda w: [
             (d_shadow.node_id, f"Let y lie in the {notion['shadow']} of x."),
             (ax("relation_compatible_first"), "Compatibility applies the operation to both sides at once."),
             (None, "Nothing else is needed, since z was arbitrary."),
         ])

    t_tight_empty = cand("thm:tight_empty", "relation",
         f"no {notion['tight']} pairs exist",
         f"No two distinct {objs} lie in each other's {notion['shadow']}.",
         [d_tight.node_id, ax("relation_antisymmetric")], _chk_tight_is_empty,
         lambda w: [
             (d_tight.node_id, "Suppose x and y form a tight pair."),
             (ax("relation_antisymmetric"), "Antisymmetry then identifies x with y."),
             (None, "So a tight pair of distinct objects cannot arise."),
         ])

    # Claims a reader might import from arithmetic without checking. Deliberately
    # ungated: whether each holds is a fact about this system, and the ones that
    # fail carry the counterexample a reader needs in order to stop importing it.
    t_core_all = cand("thm:core_is_everything", "operations",
                      f"every {obj} lies in the {notion['core']}",
                      f"Every pair of {objs} {notion['agree']}s.",
                      [d_core.node_id], _chk_core_is_everything,
                      lambda w: [
                          (d_core.node_id, f"The {notion['core']} is defined by {notion['agree']}ing with everything."),
                          (d_agree.node_id, f"The claim is that x {g0} y = y {g0} x for every pair."),
                          (None, "That is settled by scanning the table for a pair that disagrees."),
                      ])

    t_ridge_all = cand("thm:ridge_is_everything", "operations",
                       f"every {obj} is {notion['steady']}",
                       f"x {g0} x = x for every {obj} x.",
                       [d_ridge.node_id], _chk_ridge_is_everything,
                       lambda w: [
                           (d_steady.node_id, f"Being {notion['steady']} is the condition x {g0} x = x."),
                           (d_ridge.node_id, f"The claim is that the {notion['ridge']} is the whole system."),
                           (None, "Only the diagonal of the table is involved."),
                       ])

    t_generator = cand("thm:some_object_spans_all", "collections",
                       f"some {obj} reaches every other",
                       (f"There is a {obj} whose {notion['span']} is the whole system."),
                       [d_span.node_id, d_reach.node_id], _chk_some_object_spans_all,
                       lambda w: [
                           (d_span.node_id, f"Compute [x] for each {obj} in turn."),
                           (d_reach.node_id, f"The claim is that some {notion['reach']} equals {s.size}."),
                           (None, "The search runs over finitely many objects, so it settles."),
                       ])

    t_rel_sym = cand("thm:relation_symmetric", "relation",
                     "the relation reads the same in both directions",
                     f"If x {r} y then y {r} x.",
                     [d_shadow.node_id], _chk_relation_symmetric,
                     lambda w: [
                         (d_shadow.node_id, f"Symmetry would mean y lies in the {notion['shadow']} of x exactly when x lies in that of y."),
                         (None, "The listed pairs settle it directly."),
                     ])

    t_anchor_absorb = None
    if d_anchor is not None:
        t_anchor_absorb = cand("thm:anchor_is_absorbing", "neutral",
                               f"the {notion['anchor']} swallows everything",
                               (f"e {g0} x equals the {notion['anchor']} for every "
                                f"{obj} x."),
                               [d_anchor.node_id], _chk_anchor_is_absorbing,
                               lambda w: [
                                   (d_anchor.node_id, f"The {notion['anchor']} leaves every {obj} unchanged."),
                                   (None, "Leaving unchanged and swallowing are different demands, and only one row of the table is needed to see which holds."),
                               ])

    if s.has_two_ops:
        t_absorb_idem = cand("thm:absorption_idempotence", "second_operation",
             "the absorption pair forces both operations to fix repeats",
             f"For every {obj} x, x {g0} x = x and x {g1} x = x.",
             [ax("absorption"), d_steady.node_id], _chk_absorption_forces_idempotence,
             lambda w: [
                 (ax("absorption"), f"Take y = x {g1} x in the first absorption law."),
                 (ax("absorption"), f"The second law rewrites x {g0} (x {g1} x) as x."),
                 (d_steady.node_id, f"So every {obj} is {notion['steady']} under both operations."),
             ])
        t_dist_absorb = cand("thm:distributive_absorbing", "second_operation",
             "the absorbing object survives the second operation",
             (f"The {obj} that absorbs everything under {g0} also absorbs everything "
              f"under {g1}."),
             [ax("absorbing_first"), ax("distributivity")], _chk_distributive_absorbing,
             lambda w: [
                 (ax("absorbing_first"), f"Let z satisfy z {g0} x = z for every x."),
                 (ax("distributivity"), f"Spread {g1} over a combination that returns z."),
                 (None, "The claim is that the result collapses back to z."),
             ])
        t_second_core = cand("thm:second_op_preserves_core", "second_operation",
             f"the second operation keeps the {notion['core']} intact",
             (f"If x and y lie in the {notion['core']} then so does x {g1} y."),
             [d_core.node_id, ax("closure_second"), t_core_sealed],
             _chk_second_op_preserves_core,
             lambda w: [
                 (t_core_sealed, f"The {notion['core']} is already {notion['sealed']} under {g0}."),
                 (ax("closure_second"), f"The second operation is defined on every pair."),
                 (d_core.node_id, f"The claim is that {g1} respects the {notion['core']} as well."),
             ])

    theory = Theory(structure=s, profile=profile, nodes=b.nodes, order=b.order,
                    notion_names=notion)
    assign_chapters(theory)
    return theory


# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------

THEME_ORDER = ["signature", "operations", "neutral", "collections", "relation",
               "second_operation"]

THEME_TITLES = {
    "signature": "The objects and their notation",
    "operations": "Combining objects",
    "neutral": "Neutral objects and reversal",
    "collections": "Collections that close on themselves",
    "relation": "The relation and what it orders",
    "second_operation": "The second operation and how the two interact",
}


def assign_chapters(theory: Theory, max_nodes: int = 7) -> None:
    """Lay the nodes out in chapters that respect every dependency edge.

    Nodes are sorted by dependency layer first and by theme second, then cut
    into chapters of at most `max_nodes`. Sorting by layer before theme is what
    guarantees the invariant that matters: a node's prerequisites always sit in
    the same chapter or an earlier one, so a reader who has the first k chapters
    has everything the k-th chapter cites.
    """
    nodes = [theory.nodes[nid] for nid in theory.order]
    ordered = sorted(nodes, key=lambda n: (n.layer,
                                           THEME_ORDER.index(n.theme)
                                           if n.theme in THEME_ORDER else 99,
                                           n.node_id))
    chapter = 0
    count = 0
    last_theme = None
    for n in ordered:
        if count >= max_nodes or (last_theme is not None and n.theme != last_theme
                                  and count >= 3):
            chapter += 1
            count = 0
        n.chapter = chapter
        last_theme = n.theme
        count += 1
    # The cut above can only move a node later, never earlier, but check the
    # invariant anyway rather than trusting the argument.
    for n in nodes:
        for dep in n.depends_on:
            if theory.nodes[dep].chapter > n.chapter:
                raise RuntimeError(
                    f"{n.node_id} in chapter {n.chapter} cites {dep} in "
                    f"chapter {theory.nodes[dep].chapter}")


def chapter_nodes(theory: Theory) -> dict:
    out: dict = {}
    for nid in theory.order:
        out.setdefault(theory.nodes[nid].chapter, []).append(theory.nodes[nid])
    for c in out:
        out[c].sort(key=lambda n: (n.layer, n.node_id))
    return out


def build(seed: int) -> Theory:
    """Convenience: sample a structure for the seed and derive its theory."""
    from src.mathgen.algebra import sample_structure
    return build_theory(sample_structure(seed))
