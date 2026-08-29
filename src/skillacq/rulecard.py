"""One page that states everything needed to answer.

The arithmetic families spread their definition across several pages: the
operator formula, the reduction rule, the evaluation order, a worked example.
A model that retrieves one page per round can never assemble the whole rule,
which is a retrieval-coverage failure rather than an inability to compute.
This builds a single canonical card carrying the complete definition, so the
two failure modes can be told apart.
"""

from __future__ import annotations

import random

from src.skillacq.systems import (BinaryOpSystem, ProcedureSystem, UnitSystem,
                                  _answer_is_copyable)


def _card_binary_op(s: BinaryOpSystem) -> str:
    if s.form == "linear":
        rule = (f"multiply the left value by {s.a}, multiply the right value by {s.b}, "
                f"add those two products, then add {s.c}")
    elif s.form == "square_first":
        rule = (f"square the left value, add {s.b} times the right value, "
                f"then subtract {s.c}")
    else:
        rule = (f"subtract the right value from the left value, multiply that "
                f"difference by {s.a}, then add {s.c}")
    lines = [
        f"Rule card for the {s.name} system.",
        f"Operator: {s.glyph}",
        f"To evaluate x {s.glyph} y: {rule}.",
    ]
    if s.modulus:
        lines.append(f"Reduction: every result is reduced modulo {s.modulus}, "
                     f"so keep only the remainder after dividing by {s.modulus}.")
    else:
        lines.append("Reduction: none, report the value as computed.")
    lines.append(f"Evaluation order: {s.glyph} associates "
                 f"{'right to left' if s.right_assoc else 'left to right'}.")
    lines.append(f"Worked example: 7 {s.glyph} 4 = {s.apply(7, 4)}.")
    lines.append(f"Worked example: 12 {s.glyph} 5 = {s.apply(12, 5)}.")
    return "\n".join(lines)


def _card_units(s: UnitSystem) -> str:
    return "\n".join([
        f"Rule card for the {s.name} convention.",
        f"Units, smallest to largest: {s.base}, {s.mid}, {s.big}.",
        f"One {s.mid} equals {s.k1} {s.base}.",
        f"One {s.big} equals {s.k2} {s.mid}, which is {s.k1 * s.k2} {s.base}.",
        f"To convert to {s.base}: multiply a {s.mid} count by {s.k1}, "
        f"and a {s.big} count by {s.k1 * s.k2}.",
        f"Worked example: 3 {s.mid} = {3 * s.k1} {s.base}.",
        f"Worked example: 2 {s.big} = {2 * s.k1 * s.k2} {s.base}.",
    ])


def _card_procedure(s: ProcedureSystem) -> str:
    return "\n".join([
        f"Rule card for the {s.name} assessment.",
        f"Start from the application's {s.attr} value.",
        f"If it is marked {s.bonus_attr}, add {s.bonus}.",
        f"If it is flagged, subtract {s.penalty}.",
        f"Both adjustments apply when both conditions hold.",
        f"An application is accepted when the adjusted value is at least {s.cutoff}, "
        f"otherwise it is refused.",
        f"Worked example: a value of 50, marked {s.bonus_attr}, not flagged, "
        f"adjusts to {s.score(50, True, False)} and is "
        f"{'accepted' if s.eligible(50, True, False) else 'refused'}.",
    ])


BUILDERS = {
    BinaryOpSystem: _card_binary_op,
    UnitSystem: _card_units,
    ProcedureSystem: _card_procedure,
}

FAMILY_CLASSES = {
    "binary_op": BinaryOpSystem,
    "units": UnitSystem,
    "procedure": ProcedureSystem,
}


def build_card_episode(seed: int, family: str, n_problems: int = 6,
                       n_distractors: int = 0) -> dict:
    """An episode whose documents are complete rule cards, not scattered pages."""
    rng = random.Random(seed)
    cls = FAMILY_CLASSES[family]
    system = cls(rng)
    kept: list[dict] = []
    for _ in range(12):
        if len(kept) >= n_problems:
            break
        for p in system.problems(rng, n_problems * 4):
            if not _answer_is_copyable(p["answer"], p["text"]):
                kept.append(p)
    kept = kept[:n_problems]
    for i, p in enumerate(kept):
        p["qid"] = f"p{i}"

    docs = [{"text": BUILDERS[cls](system)}]
    for d in range(n_distractors):
        other_family = sorted(FAMILY_CLASSES)[(hash((seed, d)) % len(FAMILY_CLASSES))]
        other_cls = FAMILY_CLASSES[other_family]
        other = other_cls(random.Random(seed * 31 + d + 1))
        docs.append({"text": BUILDERS[other_cls](other)})
    rng.shuffle(docs)

    return {
        "episode_id": f"card-{family}-{seed:09d}",
        "seed": seed,
        "world": {"domain": f"skill_{family}"},
        "n_context": 0,
        "documents": docs,
        "questions": [
            {"qid": p["qid"], "text": p["text"], "answer": p["answer"],
             "plan": [p["qid"]], "type": p["kind"]}
            for p in kept
        ],
    }
