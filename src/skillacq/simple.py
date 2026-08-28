"""Minimal rule application: does the model use a stated rule at all?

The invented-system families ask the model to read a rule and then compute
with it, which conflates two abilities. These families strip the computation
out. A single comparison, a single substitution, a single stated exception.
The answer is never copyable from the question and never derivable without
the page, but applying the rule takes no arithmetic beyond one comparison.

If a model fails here, the problem is reading the rule. If it succeeds here
and fails on the arithmetic families, the problem is computation, which tools
and greater test-time depth can supply.
"""

from __future__ import annotations

import random

from src.skillacq.systems import _word, GLYPHS


class ThresholdRule:
    """One stated threshold applied to a new case. Answer is a stated label."""

    family = "threshold_rule"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.attr = _word(rng)
        self.limit = rng.choice([20, 35, 50, 65, 80])
        self.high = _word(rng)
        self.low = _word(rng)

    def describe(self) -> list[str]:
        return [
            f"The {self.name} classification.\n\n"
            f"Every specimen in the {self.name} classification carries a {self.attr} "
            f"reading, which is a whole number.",
            f"The rule.\n\n"
            f"A specimen whose {self.attr} reading is greater than {self.limit} is "
            f"called {self.high}. A specimen whose {self.attr} reading is {self.limit} "
            f"or less is called {self.low}.",
            f"A worked example.\n\n"
            f"A specimen with a {self.attr} reading of {self.limit + 7} is {self.high}.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            v = rng.randint(1, 100)
            while abs(v - self.limit) < 3:
                v = rng.randint(1, 100)
            out.append({
                "qid": f"p{i}",
                "kind": "threshold",
                "text": (f"A specimen has a {self.attr} reading of {v}. "
                         f"In the {self.name} classification, what is it called?"),
                "answer": self.high if v > self.limit else self.low,
            })
        return out


class SubstitutionRule:
    """A stated mapping applied to a new item. No arithmetic at all."""

    family = "substitution_rule"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.keys = [_word(rng) for _ in range(4)]
        self.values = [_word(rng) for _ in range(4)]
        self.rng_default = _word(rng)

    def describe(self) -> list[str]:
        lines = "\n".join(f"A {k} is handled by the {v} desk."
                          for k, v in zip(self.keys, self.values))
        return [
            f"The {self.name} routing table.\n\n"
            f"Requests in the {self.name} office are routed by their type.",
            f"Routing.\n\n{lines}\n\n"
            f"Any request whose type is not listed goes to the {self.rng_default} desk.",
            f"A note on precedence.\n\n"
            f"The table above is complete. Do not infer a desk from the name of a "
            f"request type; use only the routing given here.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            if rng.random() < 0.8:
                idx = rng.randrange(len(self.keys))
                k, a = self.keys[idx], self.values[idx]
            else:
                k, a = _word(rng), self.rng_default
            out.append({
                "qid": f"p{i}",
                "kind": "substitution",
                "text": f"A {k} request arrives at the {self.name} office. Which desk handles it?",
                "answer": a,
            })
        return out


class ExceptionRule:
    """A general rule plus one stated exception, applied to new cases."""

    family = "exception_rule"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.glyph = rng.choice(GLYPHS)
        self.general = _word(rng)
        self.special_key = _word(rng)
        self.special = _word(rng)

    def describe(self) -> list[str]:
        return [
            f"The {self.name} protocol.\n\n"
            f"Items reaching the {self.name} protocol are marked with a category word.",
            f"The general rule.\n\n"
            f"Every item is given the {self.general} treatment.",
            f"The exception.\n\n"
            f"There is one exception. An item whose category is {self.special_key} "
            f"is given the {self.special} treatment instead.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            if rng.random() < 0.5:
                cat, ans = self.special_key, self.special
            else:
                cat, ans = _word(rng), self.general
            out.append({
                "qid": f"p{i}",
                "kind": "exception",
                "text": (f"An item of category {cat} reaches the {self.name} protocol. "
                         f"Which treatment does it receive?"),
                "answer": ans,
            })
        return out


SIMPLE_FAMILIES = {
    "threshold_rule": ThresholdRule,
    "substitution_rule": SubstitutionRule,
    "exception_rule": ExceptionRule,
}
