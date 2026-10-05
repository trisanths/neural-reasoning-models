"""The skillacq rule families wearing the src/mathgen/interface.py contract.

src/mathgen/bench.py guards and prompts anything that looks like a universe:
chapters, items, a library, reference_solve, and for the controls sibling()
and reference_answer(). One skillacq system becomes one universe with one
chapter (its own pages, no distractor system), one item (the rule), and one
problem per question. That puts the binary_op and the three simple rule
families through the same eight checks, the same prompts and the same
sibling and blank controls as the reference universes.

A sibling copies every surface word of the system (its name, glyph,
attribute, labels and keys) and changes what they mean:

  binary_op          same form, modulus and associativity, other constants
  threshold_rule     another limit
  substitution_rule  the five desks reassigned by a derangement, the
                     fallback desk included, so every request moves
  exception_rule     the general and the special treatment swapped

Each question also carries its candidate set and the size of its answer
space, which is where its chance floor comes from.
"""

from __future__ import annotations

import copy
import itertools
import random

from src.mathgen.interface import Chapter, Item, Problem
from src.skillacq.simple import SIMPLE_FAMILIES
from src.skillacq.systems import FAMILIES, _answer_is_copyable

PILOT_FAMILIES = ("binary_op", "threshold_rule", "substitution_rule",
                  "exception_rule")
_POOL = {"binary_op": FAMILIES["binary_op"], **SIMPLE_FAMILIES}


def candidates_of(system) -> list[str] | None:
    """The closed label set a rule family answers from, None for integers."""
    fam = system.family
    if fam == "threshold_rule":
        return [system.high, system.low]
    if fam == "substitution_rule":
        return list(dict.fromkeys(system.values + [system.rng_default]))
    if fam == "exception_rule":
        return [system.general, system.special]
    return None


def answer_support(system, kind: str) -> int:
    """How many distinct answers the question generator can produce.

    For binary_op this is enumerated over the generator's own input ranges
    (direct 1..20 squared, nested 1..12 cubed, solve_for y in 1..15), so the
    floor is the rate of a guesser who knows the answer distribution exactly,
    which is the most generous floor available for a free numeric answer.
    """
    if system.family != "binary_op":
        return len(candidates_of(system))
    if kind == "direct":
        vals = {system.apply(x, y) for x in range(1, 21) for y in range(1, 21)}
    elif kind == "nested":
        if system.right_assoc:
            vals = {system.apply(x, system.apply(y, z))
                    for x, y, z in itertools.product(range(1, 13), repeat=3)}
        else:
            vals = {system.apply(system.apply(x, y), z)
                    for x, y, z in itertools.product(range(1, 13), repeat=3)}
    else:
        vals = set(range(1, 16))
    return len(vals)


def _sibling_system(system, offset: int, seed: int):
    rng = random.Random(seed * 7919 + offset * 104_729 + 3)
    sib = copy.deepcopy(system)
    fam = system.family
    if fam == "binary_op":
        for _ in range(200):
            sib.a = rng.choice([2, 3, 4, 5])
            sib.b = rng.choice([1, 2, 3, 6, 7])
            sib.c = rng.choice([0, 1, 2, 5, 10])
            if (sib.a, sib.b, sib.c) != (system.a, system.b, system.c):
                break
    elif fam == "threshold_rule":
        sib.limit = rng.choice([v for v in (20, 35, 50, 65, 80)
                                if v != system.limit])
    elif fam == "substitution_rule":
        desks = system.values + [system.rng_default]
        for _ in range(200):
            perm = desks[:]
            rng.shuffle(perm)
            if all(a != b for a, b in zip(perm, desks)):
                break
        sib.values, sib.rng_default = perm[:-1], perm[-1]
    elif fam == "exception_rule":
        sib.general, sib.special = system.special, system.general
    else:
        raise ValueError(f"no sibling rule for {fam}")
    return sib


def _answer_under(system, q: dict) -> str | None:
    """Re-solve one question with another system's definitions."""
    fam = system.family
    m = q["meta"]
    if fam == "binary_op":
        if q["kind"] == "direct":
            return str(system.apply(m["x"], m["y"]))
        if q["kind"] == "nested":
            x, y, z = m["x"], m["y"], m["z"]
            v = (system.apply(x, system.apply(y, z)) if system.right_assoc
                 else system.apply(system.apply(x, y), z))
            return str(v)
        sols = [y for y in range(1, 16) if system.apply(m["x"], y) == m["target"]]
        return str(sols[0]) if len(sols) == 1 else None
    if fam == "threshold_rule":
        return system.high if m["v"] > system.limit else system.low
    if fam == "substitution_rule":
        k = m["key"]
        if k in system.keys:
            return system.values[system.keys.index(k)]
        return system.rng_default
    if fam == "exception_rule":
        return system.special if m["cat"] == system.special_key else system.general
    raise ValueError(fam)


def _with_inputs(system, q: dict) -> dict:
    """Recover the inputs a question was generated from, out of its text."""
    import re

    fam, text = system.family, q["text"]
    nums = [int(v) for v in re.findall(r"-?\d+", text)]
    if fam == "binary_op":
        if q["kind"] == "direct":
            meta = {"x": nums[0], "y": nums[1]}
        elif q["kind"] == "nested":
            meta = {"x": nums[0], "y": nums[1], "z": nums[2]}
        else:
            meta = {"x": nums[0], "target": nums[1]}
    elif fam == "threshold_rule":
        meta = {"v": nums[0]}
    elif fam == "substitution_rule":
        meta = {"key": text.split()[1]}
    else:
        meta = {"cat": text.split("category ")[1].split()[0]}
    return {**q, "meta": meta}


class SkillUniverse:
    """One skillacq system, one chapter, its questions as problems."""

    def __init__(self, seed: int, family: str, n_problems: int = 24,
                 system=None, universe_id: str | None = None):
        if family not in _POOL:
            raise ValueError(f"family {family!r} is not one of {sorted(_POOL)}")
        self.seed = seed
        self.family = family
        rng = random.Random(seed)
        self.system = system if system is not None else _POOL[family](rng)
        self.universe_id = universe_id or f"sk-{family}-{seed:09d}"
        pages = tuple(self.system.describe())
        self.items = {"rule": Item("rule", "procedure", f"the {family} rule",
                                   "\n\n".join(pages), "ch1")}
        self.chapters = [Chapter("ch1", 1, pages[0].split("\n")[0].rstrip("."),
                                 pages, ("rule",))]
        self.by_id = {"ch1": self.chapters[0]}
        self._questions: list[dict] = []
        if system is None:
            seen = set()
            for _ in range(12):
                for q in self.system.problems(rng, n_problems * 2):
                    if q["text"] in seen or _answer_is_copyable(q["answer"], q["text"]):
                        continue
                    q = _with_inputs(self.system, q)
                    # A solve_for question with two solutions in range has
                    # no single gold, so it is not asked.
                    if _answer_under(self.system, q) != q["answer"]:
                        continue
                    seen.add(q["text"])
                    self._questions.append(q)
                if len(self._questions) >= n_problems:
                    break

    def library(self) -> list[dict]:
        ch = self.chapters[0]
        return [{"chunk_id": f"ch1-p{j}", "chapter_id": "ch1",
                 "title": ch.title, "text": page}
                for j, page in enumerate(ch.pages)]

    def chapter_text(self, chapter_ids) -> str:
        if "ch1" not in set(chapter_ids):
            return ""
        return self.chapters[0].text

    def theory_graph(self) -> dict:
        return {"chapters": {"ch1": {"index": 1, "title": self.chapters[0].title,
                                     "prereqs": [], "items": ["rule"]}},
                "items": {"rule": {"kind": "procedure", "chapter": "ch1",
                                   "deps": []}}}

    def reference_solve(self, problem: Problem, allowed_chapter_ids) -> str | None:
        return problem.answer if "ch1" in set(allowed_chapter_ids) else None

    def problems(self, level: int, n: int, rng: random.Random) -> list[Problem]:
        """Up to n problems, interleaved across distinct answers.

        A rule family can pose its fallback case under any fresh word but its
        stated case only one way, so the pool is mostly fallback. Problems are
        dealt round-robin over the answers, in an order drawn from rng, so
        the first few cover every answer the pool has.
        """
        out = []
        for i, q in enumerate(self._questions):
            out.append(Problem(
                problem_id=f"{self.universe_id}-{i:03d}", level=level,
                text=q["text"], answer=q["answer"], required_items=("rule",),
                target_chapters=("ch1",), universe_id=self.universe_id,
                meta={"kind": q["kind"], "inputs": q["meta"],
                      "candidates": candidates_of(self.system),
                      "answer_space": answer_support(self.system, q["kind"])}))
        rng.shuffle(out)
        groups: dict = {}
        for p in out:
            groups.setdefault(p.answer, []).append(p)
        dealt = []
        queues = list(groups.values())
        while queues:
            for qd in queues:
                dealt.append(qd.pop(0))
            queues = [qd for qd in queues if qd]
        return dealt[:n]

    def sibling(self, offset: int = 1) -> "SkillUniverse":
        return SkillUniverse(self.seed, self.family,
                             system=_sibling_system(self.system, offset, self.seed),
                             universe_id=f"{self.universe_id}-sib{offset}")

    def reference_answer(self, problem: Problem) -> str | None:
        q = {"kind": problem.meta["kind"], "meta": problem.meta["inputs"]}
        return _answer_under(self.system, q)

    acquisition_probes: dict = {}


def build_universe(seed: int, family: str = "binary_op", **kwargs) -> SkillUniverse:
    return SkillUniverse(seed, family, **kwargs)
