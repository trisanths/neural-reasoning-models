"""Primitive 7: verification and action.

Every item hands the model a candidate answer that a plausible first
reading produces, and a manual against which that candidate can be checked
in one lookup. Half the candidates are wrong in exactly the way the
plausible first reading is wrong. The model reports whether the candidate
survives the check and then gives its own final answer.

Handing over the candidate is the whole design. A model that cannot solve
the problem at all can still check a candidate against a stated clause, so
the score does not require the faculty the check is about to protect.
Detection and correction are reported apart, as required: a model that
notices the trap and cannot fix it, and a model that fixes nothing because
it notices nothing, produce different profiles.

Two trap shapes, both pure lookup.

exception. A general rule assigns every case one treatment, and one stated
clause carves out a case that gets another. The candidate applies the
general rule. On trap items the case falls under the clause.

constraint. A selection is proposed from a roster, and a stated
requirement disqualifies entries with a particular marking. The candidate
is the first entry that satisfies the obvious part of the requirement. On
trap items it carries the disqualifying marking.

CONTAMINATION CONTROL, faculty by faculty.

Composition depth: the check is one clause read against one stated
property of the case. The correction is one further lookup, and it is
scored separately from detection so a model that can detect but not
correct is visible rather than scored as a total failure.

Abstraction construction: the rule, the exception and the requirement are
all stated in prose. Nothing is induced from examples.

Information acquisition: the manual is in the context and in the chunk
list. Nothing is retrieved.

Missing-capability recognition: nothing is missing. The clause that
settles every item is present in every item.

Intent understanding: the instruction is literal and the answer set is
enumerated.

Temporary knowledge: single turn, manual immediately above the question.

Arithmetic: none.

Chance control: traps and controls are balanced exactly, so detection
chance is one half and both degenerate strategies, always FAIL and always
PASS, land there and are visible as a false-alarm rate of one or a miss
rate of one. Correction chance is one over the size of the treatment set.
"""

from __future__ import annotations

import random

from src.primitives.common import (
    Item, field_or_whole, invented_words, parse_binary, parse_fields,
    parse_one_label, proportion,
)

CHECK_CUES = {
    "PASS": ["pass", "correct", "right", "yes", "valid", "accept", "accepted",
             "agree", "stands"],
    "FAIL": ["fail", "wrong", "incorrect", "no", "not", "invalid", "reject",
             "rejected", "disagree"],
}

PRIMITIVE = "verification"
SHAPES = ("exception", "constraint")

INSTRUCTIONS = """Below are a manual, a case, and a candidate answer someone
has already written down. The candidate may be wrong. Check it against the
manual, then give your own final answer.
Answer with exactly these two lines:
CHECK: PASS if the candidate is right, FAIL if it is not
ANSWER: your final answer, one of {labels}"""


def _exception(seed: int, trap: bool, mode: str) -> Item:
    rng = random.Random(seed * 2246822519 % (2 ** 31) + 5)
    w = invented_words(rng, 8, 2)
    sys, general, special, key = w[0].capitalize(), w[1], w[2], w[3]
    other_treatments = [w[4], w[5]]
    cats = [w[6], w[7], key]
    case_cat = key if trap else rng.choice([w[6], w[7]])

    manual = (
        f"The {sys} protocol.\n\n"
        f"Every item that reaches the {sys} protocol is given the {general} "
        f"treatment.\n\n"
        f"There is one exception. An item whose category is {key} is given "
        f"the {special} treatment instead, and never the {general} one.\n\n"
        f"No other category alters the treatment. The categories on file are "
        f"{', '.join(sorted(cats))}.")
    check_note = (f"\n\nThe check.\nRead the case's category. If it is {key}, "
                  f"the exception applies and the {general} treatment is "
                  f"wrong.") if mode == "isolated" else ""
    case = (f"An item of category {case_cat} reaches the {sys} protocol.")
    candidate = general
    gold = special if trap else general
    labels = sorted({general, special, *other_treatments})
    body = (INSTRUCTIONS.format(labels=" or ".join(labels))
            + "\n\nManual.\n" + manual + check_note
            + "\n\nCase.\n" + case
            + f"\n\nCandidate answer.\n  {candidate}")
    return Item(
        item_id=f"p7-exception-{'trap' if trap else 'control'}-{mode}-{seed:07d}",
        primitive=PRIMITIVE,
        variant=f"exception/{'trap' if trap else 'control'}",
        mode=mode, question=body, chunks=[{"text": manual}],
        gold={"check": "FAIL" if trap else "PASS", "answer": gold,
              "labels": labels, "candidate": candidate, "trap": trap},
        meta={"seed": seed, "shape": "exception", "n_labels": len(labels)},
    )


def _constraint(seed: int, trap: bool, mode: str) -> Item:
    rng = random.Random(seed * 3266489917 % (2 ** 31) + 9)
    w = invented_words(rng, 10, 2)
    sys, mark, band = w[0].capitalize(), w[1], w[2]
    names = w[3:9]
    rng.shuffle(names)
    first, second = names[0], names[1]
    rows = {n: {"band": rng.choice([band, w[9]]), "mark": False} for n in names}
    rows[first]["band"] = band
    rows[second]["band"] = band
    rows[first]["mark"] = trap
    rows[second]["mark"] = False
    for n in names[2:]:
        rows[n]["band"] = w[9]

    roster = "\n".join(
        f"  {n}: band {rows[n]['band']}, "
        f"{'marked ' + mark if rows[n]['mark'] else 'not marked ' + mark}."
        for n in names)
    manual = (
        f"The {sys} selection.\n\n"
        f"A selection is made from the roster. The entry chosen must be in "
        f"band {band}.\n\n"
        f"An entry that is marked {mark} may never be chosen, whatever its "
        f"band. Where more than one entry qualifies, the one listed first "
        f"is chosen.\n\nRoster.\n{roster}")
    check_note = (f"\n\nThe check.\nRead the candidate's row. If it is marked "
                  f"{mark}, it may not be chosen.") if mode == "isolated" else ""
    gold = second if trap else first
    labels = sorted(names)
    body = (INSTRUCTIONS.format(labels="the roster names")
            + "\n\nManual.\n" + manual + check_note
            + "\n\nCase.\nMake the selection.\n"
            + f"\n\nCandidate answer.\n  {first}")
    return Item(
        item_id=f"p7-constraint-{'trap' if trap else 'control'}-{mode}-{seed:07d}",
        primitive=PRIMITIVE,
        variant=f"constraint/{'trap' if trap else 'control'}",
        mode=mode, question=body, chunks=[{"text": manual}],
        gold={"check": "FAIL" if trap else "PASS", "answer": gold,
              "labels": labels, "candidate": first, "trap": trap},
        meta={"seed": seed, "shape": "constraint", "n_labels": len(labels)},
    )


_BUILDERS = {"exception": _exception, "constraint": _constraint}


def generate(seed: int, shape: str, trap: bool, mode: str = "isolated") -> Item:
    return _BUILDERS[shape](seed, trap, mode)


def generate_many(n: int, seed: int = 0, mode: str = "isolated") -> list[Item]:
    """n items per shape, traps and controls balanced exactly."""
    out: list[Item] = []
    for shape in SHAPES:
        for i in range(n):
            out.append(generate(seed + i, shape, i % 2 == 0, mode=mode))
    return out


def grade(item: Item, response: str) -> dict:
    """Detection read generously, correction read from the whole reply.

    The strict parse rate is reported separately, so a model that cannot
    write the two-line format is visible as a format failure and not as a
    faculty of zero.
    """
    f = parse_fields(response)
    check = parse_binary(field_or_whole(f, "CHECK", response), CHECK_CUES)
    ans = parse_one_label(field_or_whole(f, "ANSWER", response),
                          item.gold["labels"])
    g = item.gold
    detected = check == g["check"]
    return {
        "parsed": "CHECK" in f,
        "detected": float(detected),
        "false_alarm": float(not g["trap"] and check == "FAIL"),
        "miss": float(g["trap"] and check != "FAIL"),
        "corrected": float(ans == g["answer"]),
        "corrected_given_detection": (float(ans == g["answer"])
                                      if detected else None),
        "overcorrected": float(not g["trap"] and ans is not None
                               and ans != g["answer"]),
        "trap": g["trap"], "shape": item.meta["shape"],
        "n_labels": item.meta["n_labels"],
    }


CHECK_OPTIONS = ["the written candidate answer is correct",
                 "the written candidate answer is wrong"]


def choices(item: Item) -> list[dict]:
    labels = list(item.gold["labels"])
    stem = item.question.split("\n\nManual.")[0]
    body = "\n\nManual." + item.question.split("\n\nManual.")[1]
    return [
        {"field": "check", "question": stem + body +
         "\n\nHas the candidate survived the check?",
         "options": CHECK_OPTIONS, "gold": 1 if item.gold["trap"] else 0},
        {"field": "answer", "question": item.question,
         "options": labels, "gold": labels.index(item.gold["answer"])},
    ]


def aggregate(items: list[Item], grades: list[dict]) -> dict:
    if not items:
        return {"primitive": PRIMITIVE, "n": 0}
    n = len(grades)
    traps = [g for g in grades if g["trap"]]
    ctrls = [g for g in grades if not g["trap"]]
    nl = max(2, max(g["n_labels"] for g in grades))
    det = proportion(sum(int(g["detected"]) for g in grades), n, 0.5, "detection")
    cor = proportion(sum(int(g["corrected"]) for g in grades), n, 1.0 / nl,
                     "correction")
    seen = [g for g in grades if g["corrected_given_detection"] is not None]
    per_shape = {}
    for sh in sorted({g["shape"] for g in grades}):
        sel = [g for g in grades if g["shape"] == sh]
        per_shape[sh] = {
            "detection": proportion(sum(int(g["detected"]) for g in sel),
                                    len(sel), 0.5, f"{sh}/detection"),
            "correction": proportion(sum(int(g["corrected"]) for g in sel),
                                     len(sel), 1.0 / nl, f"{sh}/correction"),
        }
    return {
        "primitive": PRIMITIVE, "mode": items[0].mode, "n": n,
        "headline": det["adjusted"],
        "detection": det,
        "correction": cor,
        "correction_given_detection": proportion(
            sum(int(g["corrected_given_detection"]) for g in seen), len(seen),
            1.0 / nl, "correction|detection") if seen else None,
        "trap_recall": proportion(sum(int(1 - g["miss"]) for g in traps),
                                  len(traps), 0.5, "trap_recall"),
        "false_alarm": proportion(sum(int(g["false_alarm"]) for g in ctrls),
                                  len(ctrls), 0.5, "false_alarm"),
        "overcorrection": proportion(sum(int(g["overcorrected"]) for g in ctrls),
                                     len(ctrls), 0.0, "overcorrection"),
        "per_shape": per_shape,
        "parse_rate": proportion(sum(int(g["parsed"]) for g in grades), n, 0.0,
                                 "parse_rate"),
    }


CONTAMINATION = __doc__
