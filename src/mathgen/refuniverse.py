"""A reference universe: one invented calculus, six chapters, a real theory graph.

The eight levels need a body of theory with structure a benchmark can check:
notation that has to be parsed, definitions built out of that notation, a
theorem that follows from the definitions, a procedure taught in one setting
and needed in another, a late chapter whose words are empty without an early
one, and questions whose answers the text never states. This module invents
such a body per seed and carries a reference implementation for every claim,
so an answer is right or wrong mechanically.

The mathematics. Readings are the whole numbers below a prime modulus M. The
calculus has one product, written with an invented glyph:

    x (x) y = (a*x*y + b*(x + y) + c) mod M

Everything else in the universe is that product seen from a different angle.
The pivot of x is x (x) x. A reading is stable when its pivot is itself. The
translate law rewrites the product as a*(x+t)*(y+t) + d with t = b/a and
d = c - b^2/a, which introduces the offset t. The reciprocal march is the
Fermat inverse, taught in chapter four for undoing a scaling and nowhere
applied to the product itself. The conductor of a reading is the number of
distinct readings its pivot orbit visits, and chapter five states it in terms
of the pivot without restating what a pivot is, so its words are empty
without chapter two. A census is a sorted list of the readings holding a
property, defined in chapter six against a property that is not stability.

What the corpus never contains: the offset's annihilating partner, the way to
undo the product, the census of the stable readings, and the reading of
greatest conductor. Those are levels three, four, seven and eight.

Naming reuses src/skillacq/systems, so invented words here look like the
invented words the RL environment already trains against.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.mathgen.interface import Chapter, Item, Problem, closure
from src.skillacq.systems import GLYPHS, _word

PRIMES = [97, 101, 103, 107, 109, 113, 127, 131]


def _cap(rng: random.Random, n: int = 2) -> str:
    return _word(rng, n).capitalize()


@dataclass
class Params:
    modulus: int
    a: int
    b: int
    c: int
    g_core: str
    g_join: str
    g_scale: str
    name: str
    w_reading: str
    w_reduce: str
    w_pivot: str
    w_stable: str
    w_offset: str
    w_residue: str
    w_march: str
    w_orbit: str
    w_conductor: str
    w_census: str


def _draw(rng: random.Random) -> Params:
    m = rng.choice(PRIMES)
    glyphs = rng.sample(GLYPHS, 3)
    words = [_word(rng) for _ in range(10)]
    return Params(
        modulus=m,
        a=rng.randrange(2, m),
        b=rng.randrange(1, m),
        c=rng.randrange(0, m),
        g_core=glyphs[0],
        g_join=glyphs[1],
        g_scale=glyphs[2],
        name=_cap(rng),
        w_reading=words[0],
        w_reduce=words[1],
        w_pivot=words[2],
        w_stable=words[3],
        w_offset=words[4],
        w_residue=words[5],
        w_march=words[6],
        w_orbit=words[7],
        w_conductor=words[8],
        w_census=words[9],
    )


class RefCalculus:
    """The reference implementation. Every benchmark answer comes from here."""

    def __init__(self, p: Params):
        self.p = p

    @property
    def M(self) -> int:
        return self.p.modulus

    def inv(self, k: int) -> int:
        return pow(k % self.M, self.M - 2, self.M)

    def join(self, x: int, y: int) -> int:
        return (x + y) % self.M

    def scale(self, k: int, x: int) -> int:
        return (k * x) % self.M

    def core(self, x: int, y: int) -> int:
        p = self.p
        return (p.a * x * y + p.b * (x + y) + p.c) % self.M

    def pivot(self, x: int) -> int:
        return self.core(x, x)

    def stable(self, x: int) -> bool:
        return self.pivot(x) == x

    def offset(self) -> int:
        return (self.p.b * self.inv(self.p.a)) % self.M

    def residue(self) -> int:
        p = self.p
        return (p.c - p.b * p.b * self.inv(p.a)) % self.M

    def annihilator(self) -> int:
        """The reading u with a*u + b == 0, so u (x) y does not depend on y."""
        return (-self.p.b * self.inv(self.p.a)) % self.M

    def annihilator_value(self) -> int:
        u = self.annihilator()
        return (self.p.b * u + self.p.c) % self.M

    def unwind(self, x: int, z: int) -> int | None:
        """The y with x (x) y == z, when one exists."""
        k = (self.p.a * x + self.p.b) % self.M
        if k == 0:
            return None
        return ((z - self.p.b * x - self.p.c) * self.inv(k)) % self.M

    def orbit(self, x: int) -> list[int]:
        """Distinct readings the repeated pivot visits, starting at x."""
        seen: list[int] = []
        cur = x
        while cur not in seen:
            seen.append(cur)
            cur = self.pivot(cur)
        return seen

    def conductor(self, x: int) -> int:
        return len(self.orbit(x))

    def census_stable(self) -> list[int]:
        return [x for x in range(self.M) if self.stable(x)]

    def max_conductor(self) -> tuple[int, int]:
        best_x, best_n = 0, -1
        for x in range(self.M):
            n = self.conductor(x)
            if n > best_n:
                best_x, best_n = x, n
        return best_x, best_n

    def check_translate_law(self) -> bool:
        t, d = self.offset(), self.residue()
        return all(
            self.core(x, y) == (self.p.a * (x + t) * (y + t) + d) % self.M
            for x in range(0, self.M, 7)
            for y in range(0, self.M, 5)
        )


def _chapters(p: Params, calc: RefCalculus) -> tuple[list[Chapter], dict[str, Item]]:
    items: dict[str, Item] = {}

    def add(item: Item) -> Item:
        items[item.item_id] = item
        return item

    # Chapter one: notation.
    add(Item("i_carrier", "notation", p.w_reading,
             f"A {p.w_reading} of the {p.name} calculus is a whole number below "
             f"{p.modulus}. To {p.w_reduce} a whole number is to divide it by "
             f"{p.modulus} and keep the remainder, which is again a {p.w_reading}.",
             "ch1"))
    add(Item("i_join", "notation", f"the {p.g_join} mark",
             f"For {p.w_reading}s x and y, the mark x {p.g_join} y denotes the sum "
             f"of x and y, {p.w_reduce}d.", "ch1", ("i_carrier",)))
    add(Item("i_scale", "notation", f"the {p.g_scale} mark",
             f"For a whole number k and a {p.w_reading} x, the mark k {p.g_scale} x "
             f"denotes k copies of x added together, {p.w_reduce}d.", "ch1",
             ("i_carrier",)))

    ch1 = Chapter(
        "ch1", 1, f"Marks and {p.w_reading}s of the {p.name} calculus",
        (
            f"Marks and {p.w_reading}s.\n\n{items['i_carrier'].statement}\n\n"
            f"Every quantity in this book is a {p.w_reading}. No {p.w_reading} is "
            f"negative and none reaches {p.modulus}.",
            f"The two plain marks.\n\n{items['i_join'].statement}\n\n"
            f"{items['i_scale'].statement}\n\n"
            f"Worked reading: 3 {p.g_scale} (4 {p.g_join} 5) is "
            f"{calc.scale(3, calc.join(4, 5))}, because 4 {p.g_join} 5 is "
            f"{calc.join(4, 5)} and three copies of that, {p.w_reduce}d, give "
            f"{calc.scale(3, calc.join(4, 5))}.",
            f"On grouping.\n\nWhere a mark stands inside parentheses, the "
            f"parenthesised part is read first. Where no parentheses are written, "
            f"marks are read from left to right.",
        ),
        ("i_carrier", "i_join", "i_scale"),
    )

    # Chapter two: the product and what is built from it.
    add(Item("i_core", "definition", f"the {p.g_core} product",
             f"For {p.w_reading}s x and y, x {p.g_core} y is formed as follows. "
             f"Multiply x by y and take {p.a} copies of that. Add {p.b} copies of "
             f"x {p.g_join} y. Add {p.c}. {p.w_reduce.capitalize()} the result.",
             "ch2", ("i_carrier", "i_join", "i_scale")))
    add(Item("i_pivot", "definition", p.w_pivot,
             f"The {p.w_pivot} of a {p.w_reading} x is x {p.g_core} x.",
             "ch2", ("i_core",)))
    add(Item("i_stable", "definition", p.w_stable,
             f"A {p.w_reading} is {p.w_stable} when its {p.w_pivot} is itself.",
             "ch2", ("i_pivot",)))

    ch2 = Chapter(
        "ch2", 2, f"The {p.g_core} product",
        (
            f"The {p.g_core} product.\n\n{items['i_core'].statement}\n\n"
            f"Worked reading: 2 {p.g_core} 3 is {calc.core(2, 3)}.",
            f"The {p.w_pivot}.\n\n{items['i_pivot'].statement} "
            f"Worked reading: the {p.w_pivot} of 4 is {calc.pivot(4)}.",
            f"{p.w_stable.capitalize()} {p.w_reading}s.\n\n"
            f"{items['i_stable'].statement} Whether any given {p.w_reading} is "
            f"{p.w_stable} is settled by forming its {p.w_pivot} and comparing.",
        ),
        ("i_core", "i_pivot", "i_stable"),
        ("ch1",),
    )

    # Chapter three: laws.
    t, d = calc.offset(), calc.residue()
    add(Item("i_comm", "theorem", "the exchange law",
             f"For all {p.w_reading}s x and y, x {p.g_core} y equals "
             f"y {p.g_core} x.", "ch3", ("i_core",)))
    add(Item("i_translate", "theorem", "the translate law",
             f"Write {p.w_offset} for the {p.w_reading} {t} and {p.w_residue} for "
             f"the {p.w_reading} {d}. Then for all x and y, x {p.g_core} y equals "
             f"{p.a} copies of (x {p.g_join} {p.w_offset}) times "
             f"(y {p.g_join} {p.w_offset}), plus {p.w_residue}, {p.w_reduce}d.",
             "ch3", ("i_core", "i_join")))

    ch3 = Chapter(
        "ch3", 3, f"Laws of the {p.g_core} product",
        (
            f"The exchange law.\n\n{items['i_comm'].statement}\n\n"
            f"The two sides expand to the same expression, since x*y equals y*x "
            f"and x {p.g_join} y equals y {p.g_join} x.",
            f"The translate law.\n\n{items['i_translate'].statement}\n\n"
            f"The {p.w_reading} named {p.w_offset} is called the {p.w_offset} of "
            f"the {p.name} calculus, and {p.w_residue} its {p.w_residue}. "
            f"Worked reading: with x equal to 5 and y equal to 6, both sides give "
            f"{calc.core(5, 6)}.",
        ),
        ("i_comm", "i_translate"),
        ("ch2",),
    )

    # Chapter four: one procedure, taught only against the scaling mark.
    add(Item("i_march", "procedure", f"the {p.w_march}",
             f"To undo a scaling, that is to recover x from k {p.g_scale} x, "
             f"perform the {p.w_march}: raise k to the power {p.modulus - 2}, "
             f"{p.w_reduce} it, and scale the known value by the result. The "
             f"{p.w_march} succeeds for every k that is not zero.",
             "ch4", ("i_scale", "i_carrier")))

    kk = 5 if p.modulus > 7 else 3
    known = calc.scale(kk, 11)
    ch4 = Chapter(
        "ch4", 4, f"The {p.w_march}",
        (
            f"Undoing a scaling.\n\n{items['i_march'].statement}",
            f"A worked {p.w_march}.\n\nSuppose {kk} {p.g_scale} x is known to be "
            f"{known} and x is wanted. Raise {kk} to the power {p.modulus - 2} and "
            f"{p.w_reduce} it, which gives {calc.inv(kk)}. Then "
            f"{calc.inv(kk)} {p.g_scale} {known} is {calc.scale(calc.inv(kk), known)}, "
            f"and that is x.",
            f"Scope.\n\nThis chapter treats the {p.g_scale} mark and nothing else. "
            f"What the {p.w_march} does for other marks is not taken up here.",
        ),
        ("i_march",),
        ("ch1",),
    )

    # Chapter five: late, and empty without chapter two.
    add(Item("i_orbit", "definition", p.w_orbit,
             f"The {p.w_orbit} of a {p.w_reading} x is the list that begins with x "
             f"and continues by replacing each entry with its {p.w_pivot}, stopping "
             f"as soon as an entry already listed would be written again.",
             "ch5", ("i_pivot",)))
    add(Item("i_conductor", "definition", p.w_conductor,
             f"The {p.w_conductor} of a {p.w_reading} is the count of entries in "
             f"its {p.w_orbit}.", "ch5", ("i_orbit",)))

    ch5 = Chapter(
        "ch5", 5, f"{p.w_orbit.capitalize()}s and {p.w_conductor}s",
        (
            f"{p.w_orbit.capitalize()}s.\n\n{items['i_orbit'].statement}\n\n"
            f"An {p.w_orbit} is finite, since there are only {p.modulus} "
            f"{p.w_reading}s and a repeat must arrive.",
            f"{p.w_conductor.capitalize()}s.\n\n{items['i_conductor'].statement} "
            f"A {p.w_reading} whose {p.w_conductor} is one is one that the step "
            f"leaves where it was.",
        ),
        ("i_orbit", "i_conductor"),
        ("ch2",),
    )

    # Chapter six: what a census is, taught against a property that is not stability.
    add(Item("i_census", "definition", p.w_census,
             f"The {p.w_census} of a property is the list of every {p.w_reading} "
             f"holding that property, written in increasing order and separated by "
             f"commas. Where no {p.w_reading} holds the property the "
             f"{p.w_census} is written none.", "ch6", ("i_carrier",)))

    doubling_fixed = [x for x in range(p.modulus) if (2 * x) % p.modulus == x]
    ch6 = Chapter(
        "ch6", 6, f"{p.w_census.capitalize()}s",
        (
            f"{p.w_census.capitalize()}s.\n\n{items['i_census'].statement}",
            f"A worked {p.w_census}.\n\nTake the property of being unchanged by "
            f"2 {p.g_scale} x. Its {p.w_census} is "
            f"{','.join(str(v) for v in doubling_fixed) or 'none'}.",
            f"Scope.\n\nThis chapter says what a {p.w_census} is. Which "
            f"{p.w_census}s are worth taking is a matter for the chapters that "
            f"introduce the properties.",
        ),
        ("i_census",),
        ("ch1",),
    )

    return [ch1, ch2, ch3, ch4, ch5, ch6], items


class ReferenceUniverse:
    """One invented calculus, its corpus, its theory graph, its problems."""

    def __init__(self, seed: int):
        self.seed = seed
        rng = random.Random(seed * 1_000_003 + 17)
        for _ in range(64):
            p = _draw(rng)
            calc = RefCalculus(p)
            if len(calc.census_stable()) == 2 and calc.check_translate_law():
                break
        else:
            raise RuntimeError("no admissible parameters for seed %d" % seed)
        self.p = p
        self.calc = calc
        self.universe_id = f"ref-{seed:07d}-M{p.modulus}"
        self.chapters, self.items = _chapters(p, calc)
        self.by_id = {c.chapter_id: c for c in self.chapters}

    # -- corpus -----------------------------------------------------------
    def library(self) -> list[dict]:
        """Every retrievable chunk. One chunk is one page."""
        out = []
        for ch in self.chapters:
            for j, page in enumerate(ch.pages):
                out.append({
                    "chunk_id": f"{ch.chapter_id}-p{j}",
                    "chapter_id": ch.chapter_id,
                    "title": ch.title,
                    "text": page,
                })
        return out

    def chapter_text(self, chapter_ids) -> str:
        wanted = [c for c in self.chapters if c.chapter_id in set(chapter_ids)]
        return "\n\n".join(f"Chapter {c.index}. {c.title}\n\n{c.text}" for c in wanted)

    def theory_graph(self) -> dict:
        return {
            "chapters": {
                c.chapter_id: {"index": c.index, "title": c.title,
                               "prereqs": list(c.prereqs),
                               "items": list(c.item_ids)}
                for c in self.chapters
            },
            "items": {
                i.item_id: {"kind": i.kind, "chapter": i.chapter_id,
                            "deps": list(i.deps)}
                for i in self.items.values()
            },
        }

    # -- reference solving ------------------------------------------------
    def reference_solve(self, problem: Problem, allowed_chapter_ids) -> str | None:
        """The answer, but only when the derivation's chapters are all allowed."""
        allowed = set(allowed_chapter_ids)
        need = {self.items[i].chapter_id for i in closure(problem.required_items,
                                                          self.items)}
        if not need <= allowed:
            return None
        return problem.answer

    # -- problems ---------------------------------------------------------
    def problems(self, level: int, n: int, rng: random.Random) -> list[Problem]:
        maker = getattr(self, f"_level{level}")
        return [maker(rng, i) for i in range(n)]

    def _mk(self, level: int, idx: int, text: str, answer: str,
            required, targets, search=False, meta=None) -> Problem:
        return Problem(
            problem_id=f"{self.universe_id}-L{level}-{idx:04d}",
            level=level,
            text=text,
            answer=answer,
            required_items=closure(required, self.items),
            target_chapters=tuple(targets),
            universe_id=self.universe_id,
            search_required=search,
            meta=meta or {},
        )

    def _level1(self, rng, idx) -> Problem:
        p, c = self.p, self.calc
        k = rng.randrange(2, 9)
        x = rng.randrange(2, p.modulus)
        y = rng.randrange(2, p.modulus)
        shape = rng.choice(["scale_join", "join_scale"])
        if shape == "scale_join":
            text = (f"In the {p.name} calculus, evaluate "
                    f"{k} {p.g_scale} ({x} {p.g_join} {y}).")
            ans = c.scale(k, c.join(x, y))
        else:
            z = rng.randrange(2, p.modulus)
            text = (f"In the {p.name} calculus, evaluate "
                    f"({x} {p.g_join} {y}) {p.g_join} ({k} {p.g_scale} {z}).")
            ans = c.join(c.join(x, y), c.scale(k, z))
        return self._mk(1, idx, text, str(ans),
                        ["i_carrier", "i_join", "i_scale"], ["ch1"],
                        meta={"shape": shape})

    def _level2(self, rng, idx) -> Problem:
        p, c = self.p, self.calc
        kind = rng.choice(["pivot", "product", "pivot_twice"])
        if kind == "pivot":
            x = rng.randrange(2, p.modulus)
            text = (f"In the {p.name} calculus, what is the {p.w_pivot} of "
                    f"the {p.w_reading} {x}?")
            ans = c.pivot(x)
        elif kind == "product":
            x, y = rng.randrange(2, p.modulus), rng.randrange(2, p.modulus)
            text = f"In the {p.name} calculus, evaluate {x} {p.g_core} {y}."
            ans = c.core(x, y)
        else:
            x = rng.randrange(2, p.modulus)
            text = (f"In the {p.name} calculus, take the {p.w_pivot} of the "
                    f"{p.w_reading} {x}, then take the {p.w_pivot} of that. "
                    f"What is the result?")
            ans = c.pivot(c.pivot(x))
        return self._mk(2, idx, text, str(ans),
                        ["i_core", "i_pivot"], ["ch2"], meta={"kind": kind})

    def _level3(self, rng, idx) -> Problem:
        """Derivable from chapter two, stated nowhere in the corpus."""
        p, c = self.p, self.calc
        u, v = c.annihilator(), c.annihilator_value()
        phrasing = rng.choice(["pair", "value_only"])
        if phrasing == "pair":
            text = (f"In the {p.name} calculus there is exactly one {p.w_reading} u "
                    f"for which u {p.g_core} y is the same {p.w_reading} for every "
                    f"choice of y. Give u and that shared value, separated by a "
                    f"comma, u first.")
            ans = f"{u},{v}"
        else:
            text = (f"In the {p.name} calculus, one {p.w_reading} u has the "
                    f"property that u {p.g_core} y does not depend on y. What is "
                    f"the value of u {p.g_core} y for that u?")
            ans = str(v)
        return self._mk(3, idx, text, ans, ["i_core"], ["ch2"],
                        meta={"phrasing": phrasing, "u": u, "value": v})

    def _level4(self, rng, idx) -> Problem:
        """The march is taught for scaling only; here it is needed in the product."""
        p, c = self.p, self.calc
        for _ in range(200):
            x = rng.randrange(2, p.modulus)
            y = rng.randrange(2, p.modulus)
            if (p.a * x + p.b) % p.modulus != 0:
                break
        z = c.core(x, y)
        text = (f"In the {p.name} calculus, the {p.w_reading} y satisfies "
                f"{x} {p.g_core} y = {z}. What is y?")
        return self._mk(4, idx, text, str(y), ["i_core", "i_march"], ["ch4"],
                        meta={"x": x, "z": z})

    def _level5(self, rng, idx) -> Problem:
        """Chapter five's words are empty without chapter two, never mentioned."""
        p, c = self.p, self.calc
        x = rng.randrange(2, p.modulus)
        text = (f"In the {p.name} calculus, what is the {p.w_conductor} of the "
                f"{p.w_reading} {x}?")
        return self._mk(5, idx, text, str(c.conductor(x)),
                        ["i_conductor"], ["ch5"], meta={"x": x})

    def _level6(self, rng, idx) -> Problem:
        """The offset comes from chapter three, undoing it from chapter four."""
        p, c = self.p, self.calc
        t = c.offset()
        y = rng.randrange(2, p.modulus)
        z = c.core(t, y)
        text = (f"Let {p.w_offset} be the {p.w_reading} the laws of the {p.name} "
                f"calculus give that name. Report the {p.w_reading} y for which "
                f"{p.w_offset} {p.g_core} y equals {z}.")
        return self._mk(6, idx, text, str(y),
                        ["i_translate", "i_march", "i_core"], ["ch3", "ch4"],
                        meta={"offset": t, "z": z})

    def _level7(self, rng, idx) -> Problem:
        """Every ingredient is in the corpus; the statement is not."""
        p, c = self.p, self.calc
        cens = c.census_stable()
        ans = ",".join(str(v) for v in cens) if cens else "none"
        text = (f"Report the {p.w_census} of the {p.w_stable} {p.w_reading}s of "
                f"the {p.name} calculus.")
        return self._mk(7, idx, text, ans, ["i_stable", "i_census"],
                        ["ch2", "ch6"], meta={"size": len(cens)})

    def _level8(self, rng, idx) -> Problem:
        """The field is established; the answer is nowhere and needs a scan."""
        p, c = self.p, self.calc
        x, n = c.max_conductor()
        text = (f"Across all {p.w_reading}s of the {p.name} calculus, which has "
                f"the greatest {p.w_conductor}? Where several tie, take the "
                f"smallest such {p.w_reading}. Answer in the form "
                f"{p.w_reading}:{p.w_conductor}.")
        return self._mk(8, idx, text, f"{x}:{n}",
                        ["i_conductor"], ["ch5"], search=True,
                        meta={"reading": x, "conductor": n})


def build_universe(seed: int, **kwargs) -> ReferenceUniverse:
    return ReferenceUniverse(seed)
