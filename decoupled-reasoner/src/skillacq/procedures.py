"""Instruction following as a retrievable procedure, not a weight-baked habit.

Conventional models learn to obey formatting and constraint instructions by
absorbing millions of supervised examples into their parameters. If a model can
read the specification of a system it has never seen and apply it, which we
measured at 0.68 against 0.002 with the wrong specification, then an instruction
is just another specification and can be fetched at inference.

Each episode invents a format convention, writes its procedure card, and poses
tasks whose compliance is checked mechanically. The convention is regenerated
per episode, so obeying it can only come from reading the card.
"""

from __future__ import annotations

import random
import re

from src.skillacq.systems import _word

TOPICS = ["a shipment", "a reading", "a request", "a sample", "a filing",
          "an entry", "a batch", "a record"]


class DelimiterFormat:
    """Emit the given items joined by an invented delimiter, in a stated order."""

    family = "delimiter_format"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.delim = rng.choice(["::", "|", "~", ">>", "+-+", "##"])
        self.order = rng.choice(["as given", "reversed", "alphabetical"])
        self.prefix = _word(rng)[:4].upper()

    def apply(self, items: list[str]) -> str:
        seq = list(items)
        if self.order == "reversed":
            seq = seq[::-1]
        elif self.order == "alphabetical":
            seq = sorted(seq)
        return self.prefix + self.delim + self.delim.join(seq)

    def describe(self) -> list[str]:
        return [
            f"The {self.name} reporting convention.\n\n"
            f"Every {self.name} report is a single line. It opens with the tag "
            f"{self.prefix}, then the separator {self.delim}, then the items.",
            f"Item order and separation.\n\n"
            f"Items are listed {self.order} and separated by {self.delim}. "
            f"No spaces are placed around the separator.",
            f"Worked example.\n\n"
            f"For items alpha, beta and gamma the report is "
            f"{self.apply(['alpha', 'beta', 'gamma'])}.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            k = rng.randint(2, 4)
            items = [_word(rng) for _ in range(k)]
            out.append({
                "qid": f"p{i}",
                "kind": "delimiter",
                "text": (f"Report these items in the {self.name} convention: "
                         + ", ".join(items) + "."),
                "answer": self.apply(items),
            })
        return out


class FieldOrderFormat:
    """State given fields as key-value pairs under an invented schema."""

    family = "field_order"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.fields = rng.sample(["mass", "count", "grade", "origin", "code"], 3)
        self.sep = rng.choice(["=", ":", "->"])
        self.joiner = rng.choice(["; ", ", ", " / "])
        self.upper = rng.random() < 0.5

    def apply(self, values: dict) -> str:
        parts = []
        for f in self.fields:
            key = f.upper() if self.upper else f
            parts.append(f"{key}{self.sep}{values[f]}")
        return self.joiner.join(parts)

    def describe(self) -> list[str]:
        case = "upper case" if self.upper else "lower case"
        return [
            f"The {self.name} record schema.\n\n"
            f"A {self.name} record lists exactly three fields, always in this "
            f"order: {', '.join(self.fields)}.",
            f"Field syntax.\n\n"
            f"Each field is written as the field name in {case}, then {self.sep}, "
            f"then the value. Fields are joined by '{self.joiner.strip() or 'a space'}'"
            f" exactly as shown in the example.",
            f"Worked example.\n\n"
            f"A record with " + ", ".join(f"{f} {i + 1}" for i, f in enumerate(self.fields))
            + f" is written {self.apply({f: i + 1 for i, f in enumerate(self.fields)})}.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            vals = {f: rng.randint(10, 99) for f in self.fields}
            shown = ", ".join(f"{f} of {vals[f]}" for f in sorted(self.fields))
            out.append({
                "qid": f"p{i}",
                "kind": "field_order",
                "text": (f"Write a {self.name} record for {rng.choice(TOPICS)} with "
                         f"{shown}."),
                "answer": self.apply(vals),
            })
        return out


class ConstraintFormat:
    """Answer a trivial question under an invented output constraint."""

    family = "constraint_format"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.style = rng.choice(["suffix", "wrap", "repeat"])
        self.token = _word(rng)[:5]
        self.times = rng.choice([2, 3])

    def apply(self, core: str) -> str:
        if self.style == "suffix":
            return f"{core} {self.token}"
        if self.style == "wrap":
            return f"{self.token} {core} {self.token}"
        return " ".join([core] * self.times)

    def describe(self) -> list[str]:
        if self.style == "suffix":
            rule = f"append the word {self.token} after the answer, separated by a space"
        elif self.style == "wrap":
            rule = f"place the word {self.token} both before and after the answer"
        else:
            rule = f"repeat the answer {self.times} times, separated by single spaces"
        return [
            f"The {self.name} response constraint.\n\n"
            f"Answers given under the {self.name} constraint carry a fixed decoration "
            f"so that they can be recognised downstream.",
            f"The constraint.\n\n"
            f"When answering under {self.name}, {rule}. The answer itself is not "
            f"otherwise changed.",
            f"Worked example.\n\n"
            f"Under {self.name}, the answer seven is written {self.apply('seven')}.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        words = ["north", "amber", "iron", "quiet", "double", "narrow"]
        for i in range(n):
            core = rng.choice(words)
            out.append({
                "qid": f"p{i}",
                "kind": "constraint",
                "text": (f"Under the {self.name} constraint, state the word "
                         f"'{core}' as your answer."),
                "answer": self.apply(core),
            })
        return out


PROCEDURE_FAMILIES = {
    "delimiter_format": DelimiterFormat,
    "field_order": FieldOrderFormat,
    "constraint_format": ConstraintFormat,
}


def build_procedure_episode(seed: int, family: str | None = None,
                            n_problems: int = 6, n_distractors: int = 1) -> dict:
    """One invented format convention, its procedure card, and checkable tasks."""
    rng = random.Random(seed)
    fams = sorted(PROCEDURE_FAMILIES)
    fam = family or fams[seed % len(fams)]
    system = PROCEDURE_FAMILIES[fam](rng)
    docs = [{"text": page} for page in system.describe()]
    for d in range(n_distractors):
        other_fam = fams[(seed + d + 1) % len(fams)]
        other = PROCEDURE_FAMILIES[other_fam](random.Random(seed * 17 + d + 5))
        docs.extend({"text": p} for p in other.describe())
    rng.shuffle(docs)
    problems = system.problems(rng, n_problems)
    return {
        "episode_id": f"proc-{fam}-{seed:09d}",
        "seed": seed,
        "world": {"domain": f"format_{fam}"},
        "n_context": 0,
        "documents": docs,
        "questions": [
            {"qid": p["qid"], "text": p["text"], "answer": p["answer"],
             "plan": [p["qid"]], "type": p["kind"]}
            for p in problems
        ],
    }
