"""Novel formal systems with textbooks, for inference-time skill acquisition.

Each episode invents a system that has never existed: fresh operator glyphs,
fresh rules, fresh constants. The textbook states the rules in prose with
worked examples. The problems can only be solved by applying what the textbook
says. Because the system is regenerated per episode, memorizing any particular
rule has zero expected value across episodes; the only thing that transfers is
the ability to read a described system and execute it.

Every answer is produced by a reference implementation, so correctness is
mechanical and no model judgement is involved.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

GLYPHS = list("@#$%&*+~^<>?!|=/")
NAME_SYLLABLES = ["ka", "vor", "mi", "zel", "tu", "bra", "qen", "sol", "dri", "fex",
                  "lum", "nak", "pyr", "tez", "ovi", "wren", "xil", "yuk", "zam", "clo"]


def _word(rng: random.Random, n: int = 2) -> str:
    return "".join(rng.choice(NAME_SYLLABLES) for _ in range(n))


def _answer_is_copyable(answer: str, text: str) -> bool:
    """True when the answer stands alone in the question and could be echoed."""
    return re.search(rf"(?<![\w.]){re.escape(answer)}(?![\w.])", text) is not None


@dataclass
class Episode:
    """One invented system: its textbook pages, its problems, its answers."""

    episode_id: str
    seed: int
    family: str
    textbook: list[str]
    problems: list[dict]
    spec: dict = field(default_factory=dict)


class BinaryOpSystem:
    """An invented binary operator over integers, defined by a formula.

    The textbook states the formula in words and shows worked examples. The
    problems ask for evaluations, including nested applications that require
    respecting the stated evaluation order.
    """

    family = "binary_op"

    def __init__(self, rng: random.Random):
        self.glyph = rng.choice(GLYPHS)
        self.name = _word(rng).capitalize()
        self.a = rng.choice([2, 3, 4, 5])
        self.b = rng.choice([1, 2, 3, 6, 7])
        self.c = rng.choice([0, 1, 2, 5, 10])
        self.form = rng.choice(["linear", "square_first", "diff_scaled"])
        self.right_assoc = rng.random() < 0.5
        self.modulus = rng.choice([0, 0, 100, 1000])

    def apply(self, x: int, y: int) -> int:
        if self.form == "linear":
            v = self.a * x + self.b * y + self.c
        elif self.form == "square_first":
            v = x * x + self.b * y - self.c
        else:
            v = self.a * (x - y) + self.c
        if self.modulus:
            v %= self.modulus
        return v

    def describe(self) -> list[str]:
        if self.form == "linear":
            rule = (f"To evaluate x {self.glyph} y, multiply x by {self.a}, "
                    f"multiply y by {self.b}, add the two products, then add {self.c}.")
        elif self.form == "square_first":
            rule = (f"To evaluate x {self.glyph} y, square x, then add {self.b} times y, "
                    f"then subtract {self.c}.")
        else:
            rule = (f"To evaluate x {self.glyph} y, subtract y from x, multiply the "
                    f"difference by {self.a}, then add {self.c}.")
        pages = [
            f"The {self.name} System.\n\n"
            f"The {self.name} system introduces a single operator written {self.glyph}. "
            f"It combines two whole numbers and produces a whole number.\n\n{rule}"
        ]
        if self.modulus:
            pages.append(
                f"Reduction in the {self.name} system.\n\n"
                f"Every result in this system is reduced modulo {self.modulus}. "
                f"That is, after computing a value you divide it by {self.modulus} and "
                f"keep only the remainder. A result is therefore always between 0 and "
                f"{self.modulus - 1} inclusive."
            )
        assoc = "right to left" if self.right_assoc else "left to right"
        pages.append(
            f"Evaluation order in the {self.name} system.\n\n"
            f"When an expression contains more than one {self.glyph}, the operator "
            f"associates {assoc}. Parentheses, where written, are evaluated first."
        )
        ex_x, ex_y = 7, 4
        pages.append(
            f"A worked example.\n\n"
            f"Consider {ex_x} {self.glyph} {ex_y}. Applying the rule gives "
            f"{self.apply(ex_x, ex_y)}."
        )
        return pages

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            kind = rng.choice(["direct", "direct", "nested", "solve_for"])
            if kind == "direct":
                x, y = rng.randint(1, 20), rng.randint(1, 20)
                out.append({
                    "qid": f"p{i}",
                    "kind": kind,
                    "text": f"Evaluate {x} {self.glyph} {y}.",
                    "answer": str(self.apply(x, y)),
                })
            elif kind == "nested":
                x, y, z = (rng.randint(1, 12) for _ in range(3))
                if self.right_assoc:
                    val = self.apply(x, self.apply(y, z))
                else:
                    val = self.apply(self.apply(x, y), z)
                out.append({
                    "qid": f"p{i}",
                    "kind": kind,
                    "text": f"Evaluate {x} {self.glyph} {y} {self.glyph} {z}.",
                    "answer": str(val),
                })
            else:
                x, y = rng.randint(1, 15), rng.randint(1, 15)
                target = self.apply(x, y)
                out.append({
                    "qid": f"p{i}",
                    "kind": kind,
                    "text": (f"In the {self.name} system, {x} {self.glyph} y equals "
                             f"{target}. What is y?"),
                    "answer": str(y),
                })
        return out


class UnitSystem:
    """An invented system of units with stated conversion factors."""

    family = "units"

    def __init__(self, rng: random.Random):
        self.base = _word(rng)
        self.mid = _word(rng)
        self.big = _word(rng)
        self.k1 = rng.choice([4, 5, 8, 12, 16])
        self.k2 = rng.choice([3, 6, 10, 20])
        self.name = _word(rng).capitalize()

    def to_base(self, n: int, unit: str) -> int:
        if unit == self.base:
            return n
        if unit == self.mid:
            return n * self.k1
        return n * self.k1 * self.k2

    def describe(self) -> list[str]:
        return [
            f"Measures in the {self.name} convention.\n\n"
            f"The {self.name} convention measures length in three units. The smallest "
            f"is the {self.base}. Next is the {self.mid}. The largest is the {self.big}.",
            f"Conversions.\n\n"
            f"One {self.mid} equals {self.k1} {self.base}. "
            f"One {self.big} equals {self.k2} {self.mid}. "
            f"Conversions compose in the obvious way, so a quantity given in {self.big} "
            f"may be reduced to {self.base} by multiplying twice.",
            f"A worked example.\n\n"
            f"Two {self.mid} equal {2 * self.k1} {self.base}.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            kind = rng.choice(["convert", "convert", "sum"])
            if kind == "convert":
                unit = rng.choice([self.mid, self.big])
                q = rng.randint(2, 15)
                out.append({
                    "qid": f"p{i}",
                    "kind": kind,
                    "text": f"How many {self.base} are {q} {unit}?",
                    "answer": str(self.to_base(q, unit)),
                })
            else:
                q1, q2 = rng.randint(1, 9), rng.randint(1, 9)
                total = self.to_base(q1, self.mid) + self.to_base(q2, self.big)
                out.append({
                    "qid": f"p{i}",
                    "kind": kind,
                    "text": (f"A distance is {q1} {self.mid} plus {q2} {self.big}. "
                             f"Express the total in {self.base}."),
                    "answer": str(total),
                })
        return out


class ProcedureSystem:
    """An invented eligibility or scoring procedure with stated thresholds."""

    family = "procedure"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.attr = _word(rng)
        self.thresh = rng.choice([30, 40, 50, 60])
        self.bonus_attr = _word(rng)
        self.bonus = rng.choice([5, 10, 15])
        self.penalty = rng.choice([5, 10])
        self.cutoff = rng.choice([45, 55, 65])

    def score(self, base: int, bonus_flag: bool, flagged: bool) -> int:
        s = base
        if bonus_flag:
            s += self.bonus
        if flagged:
            s -= self.penalty
        return s

    def eligible(self, base: int, bonus_flag: bool, flagged: bool) -> bool:
        return self.score(base, bonus_flag, flagged) >= self.cutoff

    def describe(self) -> list[str]:
        return [
            f"The {self.name} assessment.\n\n"
            f"Each application carries a {self.attr} value, a whole number. "
            f"The assessment begins from that value and adjusts it.",
            f"Adjustments.\n\n"
            f"If the application is marked {self.bonus_attr}, add {self.bonus} to the "
            f"value. If the application is flagged, subtract {self.penalty}. "
            f"Both adjustments apply when both conditions hold.",
            f"Decision.\n\n"
            f"An application is accepted when its adjusted value is at least "
            f"{self.cutoff}. Otherwise it is refused.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            base = rng.randint(20, 80)
            bf = rng.random() < 0.5
            fl = rng.random() < 0.4
            kind = rng.choice(["score", "decide"])
            desc = (f"An application has a {self.attr} value of {base}. "
                    f"It is {'marked ' + self.bonus_attr if bf else 'not marked ' + self.bonus_attr}. "
                    f"It is {'flagged' if fl else 'not flagged'}.")
            if kind == "score":
                out.append({
                    "qid": f"p{i}",
                    "kind": kind,
                    "text": f"{desc} What is its adjusted value?",
                    "answer": str(self.score(base, bf, fl)),
                })
            else:
                out.append({
                    "qid": f"p{i}",
                    "kind": kind,
                    "text": f"{desc} Is it accepted or refused?",
                    "answer": "accepted" if self.eligible(base, bf, fl) else "refused",
                })
        return out


FAMILIES = {
    "binary_op": BinaryOpSystem,
    "units": UnitSystem,
    "procedure": ProcedureSystem,
}


def _all_families() -> dict:
    """Arithmetic families plus the computation-free rule families."""
    from src.skillacq.simple import SIMPLE_FAMILIES
    merged = dict(FAMILIES)
    merged.update(SIMPLE_FAMILIES)
    return merged


def generate_episode(seed: int, family: str | None = None,
                     n_problems: int = 8, distractor: bool = True) -> Episode:
    """Build one episode: a novel system, its textbook, and verified problems."""
    rng = random.Random(seed)
    pool = _all_families()
    fam = family or rng.choice(sorted(pool))
    system = pool[fam](rng)
    pages = system.describe()
    # Reject problems whose answer is copyable straight out of the question,
    # so a model cannot score by echoing a number it was handed.
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
    if distractor:
        other_fam = rng.choice([f for f in sorted(pool) if f != fam])
        other = pool[other_fam](random.Random(seed ^ 0x5EED))
        pages = pages + other.describe()
        rng.shuffle(pages)
    return Episode(
        episode_id=f"sk-{seed:09d}",
        seed=seed,
        family=fam,
        textbook=pages,
        problems=kept,
        spec={"family": fam},
    )


def verify_episode(ep: Episode) -> bool:
    """Regenerate from the seed and confirm every answer reproduces."""
    again = generate_episode(ep.seed, family=ep.family,
                             n_problems=len(ep.problems),
                             distractor=len(ep.textbook) > 4)
    if len(again.problems) != len(ep.problems):
        return False
    return all(a["answer"] == b["answer"] and a["text"] == b["text"]
               for a, b in zip(again.problems, ep.problems))


def system_overlap(seed_a: int, seed_b: int) -> float:
    """Fraction of shared textbook lines between two episodes, a novelty check."""
    a = set(generate_episode(seed_a).textbook)
    b = set(generate_episode(seed_b).textbook)
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a), len(b))
