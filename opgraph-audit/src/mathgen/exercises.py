"""Graded exercises, each carrying a machine proof that it needs its chapter.

The rule this module exists to enforce: an exercise that can be answered without
the material it claims to test is worse than no exercise, because it inflates a
score and hides a whole family sitting at zero. So nothing is emitted until it
has passed three automatic checks.

1. The answer is not readable off the prompt. A question whose answer is one of
   the objects it names is a copy task wearing a reasoning costume.
2. The answer moves when the textbook moves. Every exercise carries a recipe
   that the reference implementation can run against any structure. We run it
   against sibling systems: same object names, same glyphs, same relation
   symbol, different content. If the answer survives that substitution the
   exercise is not testing anything this textbook says, and it is discarded.
   The surviving fraction is recorded, not just thresholded.
3. Guessing does not pay. Every answer is an object name, a list of object
   names, or a count. There are no yes or no answers anywhere in the benchmark,
   because a coin already scores 0.5 on those and that number would survive
   into a pooled average.

Levels run one to five and are reported separately, as is every chapter. There
is no pooled number in the output of this module by design.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.mathgen.algebra import ParseError, Structure
from src.mathgen.theory import (Theory, ext_core, ext_floor, ext_regular,
                                ext_steady, ext_tight, names, reach_of,
                                shadow_of, span_of)


class Undefined(Exception):
    """The recipe has no answer in the structure it was run against."""


# ---------------------------------------------------------------------------
# Recipes: a small language the reference implementation can execute
# ---------------------------------------------------------------------------


def _element(s: Structure, name: str) -> int:
    if name not in s.index:
        raise Undefined(f"{name} is not an object of this system")
    return s.index[name]


EXTENSIONS = {
    "steady": ext_steady,
    "core": ext_core,
    "ridge": ext_steady,
    "regular": ext_regular,
    "floor": ext_floor,
    "tight": ext_tight,
    "crest": lambda s: frozenset(
        i for i in range(s.size)
        if reach_of(s, i) == max(reach_of(s, j) for j in range(s.size))),
}


def compute(s: Structure, recipe: dict) -> str:
    """Run a recipe against a structure and return the canonical answer string.

    Raises Undefined when the structure cannot answer it, which is itself
    evidence that the question depends on structure specific content.
    """
    kind = recipe["kind"]
    if kind == "evaluate":
        try:
            return s.evaluate(recipe["expr"])
        except ParseError as exc:
            raise Undefined(str(exc)) from exc
    if kind == "op_second":
        if not s.has_two_ops:
            raise Undefined("this system has one operation")
        i, j = _element(s, recipe["left"]), _element(s, recipe["right"])
        return s.name(s.op(1, i, j))
    if kind == "solve_left":
        target = _element(s, recipe["target"])
        right = _element(s, recipe["right"])
        sols = [i for i in range(s.size) if s.op(0, i, right) == target]
        if not sols:
            raise Undefined("no solution in this system")
        return ", ".join(names(s, sols))
    if kind == "anchor":
        e = s.identity_of(0)
        if e is None:
            raise Undefined("this system has no neutral object")
        return s.name(e)
    if kind == "absorbing_both":
        z = None
        for i in range(s.size):
            if all(s.op(0, i, x) == i and s.op(0, x, i) == i for x in range(s.size)):
                z = i
        if z is None:
            raise Undefined("no absorbing object")
        return s.name(z)
    if kind == "extension":
        ext = EXTENSIONS[recipe["which"]](s)
        if not ext:
            raise Undefined(f"nothing is {recipe['which']} in this system")
        return ", ".join(names(s, ext))
    if kind == "span":
        return ", ".join(names(s, span_of(s, _element(s, recipe["element"]))))
    if kind == "span_of":
        try:
            value = s.eval_tree(s.parse(recipe["expr"]))
        except ParseError as exc:
            raise Undefined(str(exc)) from exc
        return ", ".join(names(s, span_of(s, value)))
    if kind == "shadow":
        sh = shadow_of(s, _element(s, recipe["element"]))
        if not sh:
            raise Undefined("the shadow is empty in this system")
        return ", ".join(names(s, sh))
    if kind == "reach":
        return str(reach_of(s, _element(s, recipe["element"])))
    if kind == "reach_of":
        try:
            value = s.eval_tree(s.parse(recipe["expr"]))
        except ParseError as exc:
            raise Undefined(str(exc)) from exc
        return str(reach_of(s, value))
    if kind == "max_reach":
        return str(max(reach_of(s, i) for i in range(s.size)))
    if kind == "partner":
        inv = s.inverse_of(_element(s, recipe["element"]), 0)
        if inv is None:
            raise Undefined("this object has no partner in this system")
        return s.name(inv)
    if kind == "partner_of":
        try:
            value = s.eval_tree(s.parse(recipe["expr"]))
        except ParseError as exc:
            raise Undefined(str(exc)) from exc
        inv = s.inverse_of(value, 0)
        if inv is None:
            raise Undefined("this object has no partner in this system")
        return s.name(inv)
    if kind == "generator":
        for i in range(s.size):
            if len(span_of(s, i)) == s.size:
                return s.name(i)
        raise Undefined("no object spans the whole system")
    if kind == "counterexample":
        i = first_failing_element(s, recipe["claim"])
        if i is None:
            raise Undefined("the claim holds here, so there is no counterexample")
        return s.name(i)
    raise ValueError(f"unknown recipe kind {kind!r}")


# ---------------------------------------------------------------------------
# Canonical counterexamples
# ---------------------------------------------------------------------------
#
# A counterexample question needs a single right answer, so we ask for the
# earliest object in the order the textbook introduces them that witnesses the
# failure. Each predicate below says what it means for one object to be that
# witness.

def _fails_commutativity(s, i, k=0):
    return any(s.op(k, i, j) != s.op(k, j, i) for j in range(s.size))


def _fails_associativity(s, i, k=0):
    return any(s.op(k, s.op(k, i, j), m) != s.op(k, i, s.op(k, j, m))
               for j in range(s.size) for m in range(s.size))


def _fails_idempotence(s, i, k=0):
    return s.op(k, i, i) != i


def _fails_cancellation(s, i):
    seen = {}
    for j in range(s.size):
        v = s.op(0, i, j)
        if v in seen:
            return True
        seen[v] = j
    return False


def _fails_inverses(s, i):
    return s.identity_of(0) is None or s.inverse_of(i, 0) is None


def _fails_reflexive(s, i):
    return not s.decide(i, i)


def _fails_antisymmetric(s, i):
    return any(i != j and s.decide(i, j) and s.decide(j, i) for j in range(s.size))


def _fails_transitive(s, i):
    return any(s.decide(i, j) and s.decide(j, m) and not s.decide(i, m)
               for j in range(s.size) for m in range(s.size))


def _fails_total(s, i):
    return any(not s.decide(i, j) and not s.decide(j, i) for j in range(s.size))


def _fails_compatible(s, i, k=0):
    for j in range(s.size):
        if not s.decide(i, j):
            continue
        for m in range(s.size):
            if not s.decide(s.op(k, m, i), s.op(k, m, j)):
                return True
            if not s.decide(s.op(k, i, m), s.op(k, j, m)):
                return True
    return False


def _fails_distributivity(s, i):
    if not s.has_two_ops:
        return False
    for j in range(s.size):
        for m in range(s.size):
            if s.op(1, i, s.op(0, j, m)) != s.op(0, s.op(1, i, j), s.op(1, i, m)):
                return True
            if s.op(1, s.op(0, j, m), i) != s.op(0, s.op(1, j, i), s.op(1, m, i)):
                return True
    return False


def _fails_absorption(s, i):
    if not s.has_two_ops:
        return False
    return any(s.op(0, i, s.op(1, i, j)) != i or s.op(1, i, s.op(0, i, j)) != i
               for j in range(s.size))


def _not_in_core(s, i):
    return i not in ext_core(s)


def _anchor_not_absorbing(s, i):
    e = s.identity_of(0)
    return e is not None and s.op(0, e, i) != e


def _breaks_relation_symmetry(s, i):
    return any(s.decide(i, j) and not s.decide(j, i) for j in range(s.size))


def _in_tight_pair(s, i):
    return i in ext_tight(s)


def _breaks_ridge_sealing(s, i):
    ridge = ext_steady(s)
    return i in ridge and any(s.op(0, i, j) not in ridge for j in ridge)


def _reach_does_not_divide(s, i):
    return s.size % reach_of(s, i) != 0


def _span_leaves_core(s, i):
    core = ext_core(s)
    return i in core and not span_of(s, i) <= core


FAILURE_WITNESSES = {
    "axiom_fails:commutativity_first": _fails_commutativity,
    "axiom_fails:associativity_first": _fails_associativity,
    "axiom_fails:idempotence_first": _fails_idempotence,
    "axiom_fails:cancellation_first": _fails_cancellation,
    "axiom_fails:inverses_first": _fails_inverses,
    "axiom_fails:relation_reflexive": _fails_reflexive,
    "axiom_fails:relation_antisymmetric": _fails_antisymmetric,
    "axiom_fails:relation_transitive": _fails_transitive,
    "axiom_fails:relation_total": _fails_total,
    "axiom_fails:relation_compatible_first": _fails_compatible,
    "axiom_fails:commutativity_second": lambda s, i: _fails_commutativity(s, i, 1),
    "axiom_fails:associativity_second": lambda s, i: _fails_associativity(s, i, 1),
    "axiom_fails:idempotence_second": lambda s, i: _fails_idempotence(s, i, 1),
    "axiom_fails:distributivity": _fails_distributivity,
    "axiom_fails:absorption": _fails_absorption,
    "thm:core_is_everything": _not_in_core,
    "thm:ridge_is_everything": lambda s, i: _fails_idempotence(s, i, 0),
    "thm:anchor_is_absorbing": _anchor_not_absorbing,
    "thm:relation_symmetric": _breaks_relation_symmetry,
    "thm:tight_empty": _in_tight_pair,
    "thm:ridge_sealed": _breaks_ridge_sealing,
    "thm:reach_divides_size": _reach_does_not_divide,
    "thm:span_inside_core": _span_leaves_core,
    "thm:core_sealed": lambda s, i: i in ext_core(s) and any(
        s.op(0, i, j) not in ext_core(s) for j in ext_core(s)),
}


def first_failing_element(s: Structure, claim: str):
    """Earliest object, in the order the textbook lists them, witnessing failure."""
    pred = FAILURE_WITNESSES.get(claim)
    if pred is None:
        return None
    for i in range(s.size):
        try:
            if pred(s, i):
                return i
        except Undefined:
            continue
    return None


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------


@dataclass
class Exercise:
    exercise_id: str
    level: int
    chapter: int
    target_node: str
    required_chapters: list
    prompt: str
    answer: str
    answer_kind: str        # object, object_list, count
    recipe: dict
    necessity: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "exercise_id": self.exercise_id, "level": self.level,
            "chapter": self.chapter, "target_node": self.target_node,
            "required_chapters": list(self.required_chapters),
            "prompt": self.prompt, "answer": self.answer,
            "answer_kind": self.answer_kind, "recipe": self.recipe,
            "necessity": self.necessity,
        }


GUESS_SPACE = {
    "object": lambda s: s.size,
    "object_list": lambda s: 2 ** s.size - 1,
    "count": lambda s: s.size,
}


def _answer_is_copyable(answer: str, prompt: str) -> bool:
    """True when the whole answer sits in the prompt as a standalone token."""
    import re
    return re.search(rf"(?<![\w]){re.escape(answer)}(?![\w])", prompt) is not None


def necessity_witness(structure: Structure, exercise: Exercise,
                      n_siblings: int = 4) -> dict:
    """Run the exercise's recipe against rival systems wearing the same notation."""
    sibling_answers = []
    available = min(n_siblings, structure.n_siblings())
    for k in range(available):
        sib = structure.sibling(k + 1)
        try:
            sibling_answers.append(compute(sib, exercise.recipe))
        except Undefined as exc:
            sibling_answers.append(f"undefined: {exc}")
    changed = sum(1 for a in sibling_answers if a != exercise.answer)
    space = GUESS_SPACE[exercise.answer_kind](structure)
    return {
        "answer_absent_from_prompt": not _answer_is_copyable(exercise.answer,
                                                             exercise.prompt),
        "siblings_tested": len(sibling_answers),
        "siblings_answering_differently": changed,
        "sibling_divergence": (changed / len(sibling_answers)
                               if sibling_answers else 0.0),
        "sibling_answers": sibling_answers,
        "guess_space": space,
        "blind_guess_rate": 1.0 / space,
    }


def passes_necessity(witness: dict, min_divergence: float = 0.5,
                     max_guess_rate: float = 0.34) -> bool:
    return (witness["answer_absent_from_prompt"]
            and witness["siblings_tested"] > 0
            and witness["sibling_divergence"] >= min_divergence
            and witness["blind_guess_rate"] <= max_guess_rate)


# ---------------------------------------------------------------------------
# Prompt phrasing
# ---------------------------------------------------------------------------

def _phrase(rng, options):
    return rng.choice(options)


def _build_expression(s: Structure, rng: random.Random, depth: int) -> str:
    """A written expression of the requested nesting depth."""
    g0 = s.op_glyphs[0]
    picks = [rng.choice(s.elements) for _ in range(depth + 1)]
    if depth == 1:
        return f"{picks[0]} {g0} {picks[1]}"
    if depth == 2:
        if s.has_two_ops and rng.random() < 0.5:
            return f"{picks[0]} {g0} {picks[1]} {s.op_glyphs[1]} {picks[2]}"
        return f"({picks[0]} {g0} {picks[1]}) {g0} {picks[2]}"
    inner = f"({picks[0]} {g0} {picks[1]})"
    tail = f"({picks[2]} {g0} {picks[3]})"
    return f"{inner} {g0} {tail}"


def _exercises_for_node(theory: Theory, node, rng: random.Random,
                        variants: int = 3) -> list:
    """Candidate exercises hosted by one node, before the necessity filter."""
    s = theory.structure
    nm = theory.notion_names
    obj, objs = s.object_name, s.object_plural
    g0 = s.op_glyphs[0]
    r = s.rel_glyph
    out = []

    def make(level, prompt, answer_kind, recipe):
        out.append((level, prompt, answer_kind, recipe))

    key = node.key

    if key == "tables":
        # Many candidates, because the filter is strict. In a system where the
        # operation projects onto one side almost every evaluation is copyable
        # and gets thrown out, and that is the right outcome; the answer is to
        # propose more, not to relax the check.
        plan = [(1, 1)] * (3 * variants) + [(2, 2)] * (2 * variants) \
            + [(3, 3)] * variants
        for depth, level in plan:
            expr = _build_expression(s, rng, depth)
            make(level,
                 _phrase(rng, [f"Evaluate {expr}.",
                               f"Work out the value of {expr}.",
                               f"What {obj} does {expr} name?",
                               f"Reduce {expr} to a single {obj}."]),
                 "object", {"kind": "evaluate", "expr": expr})
        for _ in range(variants):
            x = rng.choice(s.elements)
            k = rng.choice([2, 3])
            make(2, _phrase(rng, [f"Evaluate {x}^{k}.",
                                  f"What is {x} combined with itself {k} times "
                                  f"under {g0}?"]),
                 "object", {"kind": "evaluate", "expr": f"{x}^{k}"})
        if s.has_inverses:
            for _ in range(variants):
                x, y = rng.choice(s.elements), rng.choice(s.elements)
                make(2, f"Evaluate {x} {g0} {y}'.", "object",
                     {"kind": "evaluate", "expr": f"{x} {g0} {y}'"})
        for _ in range(2 * variants):
            a, bb = rng.choice(s.elements), rng.choice(s.elements)
            target = s.evaluate(f"{a} {g0} {bb}")
            make(2, _phrase(rng, [
                    f"Which {objs} x satisfy x {g0} {bb} = {target}? List them all.",
                    f"Solve x {g0} {bb} = {target} for x, naming every solution."]),
                 "object_list",
                 {"kind": "solve_left", "target": target, "right": bb})
        if s.has_two_ops:
            g1 = s.op_glyphs[1]
            for _ in range(2 * variants):
                a, bb = rng.choice(s.elements), rng.choice(s.elements)
                make(1, _phrase(rng, [f"Evaluate {a} {g1} {bb}.",
                                      f"What {obj} is {a} {g1} {bb}?"]),
                     "object", {"kind": "op_second", "left": a, "right": bb})
            for _ in range(variants):
                a, bb, c = (rng.choice(s.elements) for _ in range(3))
                expr = f"{a} {g0} {bb} {g1} {c}"
                make(3, (f"Evaluate {expr}, minding which operation binds "
                         f"tighter."), "object", {"kind": "evaluate", "expr": expr})

    if key == "def:anchor":
        make(2, _phrase(rng, [
                f"Name the {nm['anchor']} of the system.",
                f"Which {obj} leaves every {obj} unchanged under {g0}?"]),
             "object", {"kind": "anchor"})

    ext_map = {"def:steady": "steady", "def:core": "core", "def:ridge": "ridge",
               "def:regular": "regular", "def:floor": "floor",
               "def:tight": "tight", "def:crest": "crest"}
    if key in ext_map:
        which = ext_map[key]
        word = nm[which]
        level = 3 if which in ("steady", "core", "ridge", "regular") else 4
        make(level, _phrase(rng, [
                f"List every {obj} in the {word}.",
                f"Which {objs} make up the {word}? Name them all.",
                f"Write down the {word} in full."]),
             "object_list", {"kind": "extension", "which": which})

    if key == "def:span":
        for x in s.elements:
            make(3, _phrase(rng, [
                    f"List the {nm['span']} of {x}.",
                    f"Name every {obj} in [{x}]."]),
                 "object_list", {"kind": "span", "element": x})
        for _ in range(variants):
            expr = _build_expression(s, rng, 1)
            make(4, f"Let z be {expr}. List the {nm['span']} of z.",
                 "object_list", {"kind": "span_of", "expr": expr})

    if key == "def:reach":
        for x in s.elements:
            make(3, _phrase(rng, [
                    f"What is the {nm['reach']} of {x}?",
                    f"How many {objs} lie in [{x}]?"]),
                 "count", {"kind": "reach", "element": x})
        for _ in range(2 * variants):
            expr = _build_expression(s, rng, 2)
            make(5, f"Let z be {expr}. What is the {nm['reach']} of z?",
                 "count", {"kind": "reach_of", "expr": expr})

    if key == "def:shadow":
        for x in s.elements:
            make(3, _phrase(rng, [
                    f"List the {nm['shadow']} of {x}.",
                    f"Which {objs} y satisfy {x} {r} y? Name them all."]),
                 "object_list", {"kind": "shadow", "element": x})

    if key == "def:partner":
        for x in s.elements:
            make(3, _phrase(rng, [
                    f"Name the {nm['partner']} of {x}.",
                    f"Which {obj} reverses {x} under {g0}?"]),
                 "object", {"kind": "partner", "element": x})
        for _ in range(variants):
            expr = _build_expression(s, rng, 1)
            make(5, f"Let z be {expr}. Name the {nm['partner']} of z.",
                 "object", {"kind": "partner_of", "expr": expr})

    if key == "thm:some_object_spans_all":
        make(4, _phrase(rng, [
                f"Name a {obj} whose {nm['span']} is the whole system. Give the "
                f"earliest such {obj} in the order the {objs} were introduced.",
                f"Which {obj}, taken earliest in the listed order, has "
                f"{nm['reach']} equal to {s.size}?"]),
             "object", {"kind": "generator"})

    if key == "thm:reach_divides_size":
        make(4, f"What is the largest {nm['reach']} any {obj} has?", "count",
             {"kind": "max_reach"})

    if key == "thm:distributive_absorbing":
        make(4, f"Name the {obj} that absorbs every {obj} under {g0}.", "object",
             {"kind": "absorbing_both"})

    if key in ("thm:core_sealed", "thm:second_op_preserves_core",
               "thm:span_inside_core"):
        core = sorted(ext_core(s))
        if len(core) >= 2:
            a, bb = s.name(core[0]), s.name(core[1])
            glyph = (s.op_glyphs[1] if key == "thm:second_op_preserves_core"
                     and s.has_two_ops else g0)
            recipe = ({"kind": "op_second", "left": a, "right": bb}
                      if glyph != g0 else
                      {"kind": "evaluate", "expr": f"{a} {glyph} {bb}"})
            make(4, (f"{a} and {bb} both lie in the {nm['core']}. Name "
                     f"{a} {glyph} {bb}."), "object", recipe)

    if key == "thm:floor_exists":
        make(4, f"Name the {nm['floor']} of the system.", "object_list",
             {"kind": "extension", "which": "floor"})

    if node.kind == "refutation" and key in FAILURE_WITNESSES:
        if first_failing_element(s, key) is not None:
            claim_text = node.statement.replace("It is not the case that: ", "")
            make(5, (f"The following fails in this system: {claim_text} "
                     f"Name the earliest {obj}, in the order the {objs} were "
                     f"introduced, that witnesses the failure."),
                 "object", {"kind": "counterexample", "claim": key})

    return out


def build_exercises(theory: Theory, n_siblings: int = 4,
                    seed_offset: int = 0, variants: int = 3) -> list:
    """Every exercise the theory can host that survives the necessity checks."""
    s = theory.structure
    rng = random.Random(s.seed ^ 0xE1E1 ^ seed_offset)
    kept: list = []
    counter = 0
    for nid in theory.order:
        node = theory.nodes[nid]
        required = sorted({theory.nodes[p].chapter
                           for p in theory.prerequisites(nid)} | {node.chapter})
        for level, prompt, answer_kind, recipe in _exercises_for_node(
                theory, node, rng, variants=variants):
            try:
                answer = compute(s, recipe)
            except Undefined:
                continue
            counter += 1
            ex = Exercise(
                exercise_id=f"x{counter:03d}", level=level, chapter=node.chapter,
                target_node=nid, required_chapters=required, prompt=prompt,
                answer=answer, answer_kind=answer_kind, recipe=recipe)
            ex.necessity = necessity_witness(s, ex, n_siblings=n_siblings)
            if passes_necessity(ex.necessity):
                kept.append(ex)
    for i, ex in enumerate(kept):
        ex.exercise_id = f"x{i + 1:03d}"
    return kept


def rejected_report(theory: Theory, n_siblings: int = 4,
                    variants: int = 3) -> dict:
    """How many candidates the necessity filter threw out, and on which check.

    Kept as a first class output rather than a debug print. The size of this
    number is the honest measure of how much of a naive generator would have
    been answerable without reading anything.
    """
    s = theory.structure
    rng = random.Random(s.seed ^ 0xE1E1)
    reasons = {"undefined": 0, "copyable": 0, "invariant_under_siblings": 0,
               "guessable": 0, "kept": 0}
    for nid in theory.order:
        node = theory.nodes[nid]
        for level, prompt, answer_kind, recipe in _exercises_for_node(
                theory, node, rng, variants=variants):
            try:
                answer = compute(s, recipe)
            except Undefined:
                reasons["undefined"] += 1
                continue
            ex = Exercise("tmp", level, node.chapter, nid, [], prompt, answer,
                          answer_kind, recipe)
            w = necessity_witness(s, ex, n_siblings=n_siblings)
            if not w["answer_absent_from_prompt"]:
                reasons["copyable"] += 1
            elif w["sibling_divergence"] < 0.5:
                reasons["invariant_under_siblings"] += 1
            elif w["blind_guess_rate"] > 0.34:
                reasons["guessable"] += 1
            else:
                reasons["kept"] += 1
    return reasons


def breakdown(exercises: list) -> dict:
    """Counts by level and by chapter, never pooled into one number."""
    by_level: dict = {}
    by_chapter: dict = {}
    for ex in exercises:
        by_level.setdefault(ex.level, 0)
        by_level[ex.level] += 1
        by_chapter.setdefault(ex.chapter, 0)
        by_chapter[ex.chapter] += 1
    return {
        "by_level": {str(k): by_level[k] for k in sorted(by_level)},
        "by_chapter": {str(k): by_chapter[k] for k in sorted(by_chapter)},
        "by_answer_kind": {
            k: sum(1 for e in exercises if e.answer_kind == k)
            for k in sorted({e.answer_kind for e in exercises})},
        "total": len(exercises),
        "note": ("Report scores against by_level and by_chapter separately. A "
                 "single pooled number over these exercises hides a family at "
                 "zero, which is the failure this generator was built to avoid."),
    }
