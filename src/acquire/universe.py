"""A layered invented universe with a true dependency graph.

src/skillacq invents flat systems: three or four pages, no page depending on
another. That is enough to ask whether a model applies a rule it has just
read, and the answer there was yes. It cannot ask whether a model finds a
prerequisite it was never told about, because there are no prerequisites.

This module invents chapters instead. A chapter is a small theory whose
notions sit in levels. A level-0 notion reads a primitive attribute of a
record and returns an invented word. A level-1 notion reads the values of two
level-0 notions and returns a different invented word. A level-2 notion, the
chapter's final classification, reads two level-1 notions. Every notion has
its own definition page, its own worked example, and a bare statement
fragment that names it without stating its rule. The edges between notions
are recorded as the chapter's theory graph, which is what a constructed
curriculum is scored against.

Two properties are enforced mechanically on every problem, because our own
earlier reported successes were partly artefacts of items that were secretly
no-ops:

  copyability   the answer word does not stand alone anywhere in the
                question, so echoing the prompt cannot score.
  necessity     the answer is derived by a reference solver that records
                exactly which notions it consulted. For each consulted
                notion the solver is re-run with that notion's definition
                withheld and must fail to determine an answer. The answer
                word is then checked against every page in the store and must
                appear only on pages belonging to the consulted notions.

Problems carry their level, their chapter, and the proof record, so scores
are always reported per level and per chapter and never pooled.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

from src.skillacq.systems import _answer_is_copyable, _word

# A record is described by three primitive attributes. The attribute names
# themselves are invented per chapter, so a query that mentions them is a
# query about this chapter and not about any other.
PRIMITIVES = ("reading", "type", "count")


def _fresh(rng: random.Random, used: set[str], syllables: int = 3) -> str:
    """An invented word that has not been used anywhere in this corpus."""
    for _ in range(500):
        w = _word(rng, syllables)
        if w not in used:
            used.add(w)
            return w
    raise RuntimeError("invented word pool exhausted")


@dataclass
class Page:
    """One learning object. kind is what lesson.py ranks on."""

    page_id: str
    chapter: str
    notion: str | None
    level: int
    kind: str  # preamble | definition | worked_example | statement
    title: str
    body: str
    cites: tuple[str, ...] = ()
    defines: tuple[str, ...] = ()

    @property
    def text(self) -> str:
        return f"{self.title}\n\n{self.body}"

    def to_document(self) -> dict:
        """The shape src/rl/env.py and src/train/retrieval.py index."""
        return {
            "text": self.text,
            "reliability": 1.0,
            "page_id": self.page_id,
            "kind": self.kind,
            "chapter": self.chapter,
            "notion": self.notion,
            "level": self.level,
            "title": self.title,
            "body": self.body,
            "cites": list(self.cites),
        }


class _Notion:
    """Common surface: a name, a level, the notions it consults, its outputs."""

    def __init__(self, name: str, level: int, deps: tuple[str, ...],
                 outputs: tuple[str, ...]):
        self.name = name
        self.level = level
        self.deps = deps
        self.outputs = outputs


class ThresholdNotion(_Notion):
    """Level 0. Bands one integer attribute into three invented words."""

    def __init__(self, name, attribute, attr_word, noun, low, high, outputs):
        super().__init__(name, 0, (), outputs)
        self.attribute = attribute
        self.attr_word = attr_word
        self.noun = noun
        self.low = low
        self.high = high

    def evaluate(self, case, resolve, consulted):
        v = int(case[self.attribute])
        if v > self.high:
            return self.outputs[0]
        if v > self.low:
            return self.outputs[1]
        return self.outputs[2]

    def definition_body(self) -> str:
        return (
            f"Every record carries a {self.attr_word} {self.noun}, which is a "
            f"whole number. The {self.name} value of a record is read off that "
            f"number.\n"
            f"A record whose {self.attr_word} {self.noun} is greater than "
            f"{self.high} has {self.name} value {self.outputs[0]}.\n"
            f"A record whose {self.attr_word} {self.noun} is greater than "
            f"{self.low} but not greater than {self.high} has {self.name} value "
            f"{self.outputs[1]}.\n"
            f"Any other record has {self.name} value {self.outputs[2]}."
        )

    def example_case(self, rng):
        return {self.attribute: self.high + rng.randint(3, 20)}


class TableNotion(_Notion):
    """Level 0. A stated lookup over a categorical attribute, with a default."""

    def __init__(self, name, attribute, attr_word, table, default):
        super().__init__(name, 0, (), tuple(list(table.values()) + [default]))
        self.attribute = attribute
        self.attr_word = attr_word
        self.table = dict(table)
        self.default = default

    def evaluate(self, case, resolve, consulted):
        return self.table.get(case[self.attribute], self.default)

    def definition_body(self) -> str:
        lines = "\n".join(
            f"A record of {self.attr_word} {k} has {self.name} value {v}."
            for k, v in self.table.items())
        return (
            f"Every record carries a {self.attr_word}, which is a word.\n{lines}\n"
            f"A record whose {self.attr_word} is not one of those listed has "
            f"{self.name} value {self.default}.\n"
            f"The listing above is complete. Do not infer a {self.name} value "
            f"from the {self.attr_word} itself; use only what is written here."
        )

    def example_case(self, rng):
        return {self.attribute: rng.choice(sorted(self.table))}


@dataclass
class _Rule:
    """One line of an ordered rule list. conditions maps dep name to value."""

    conditions: dict
    output: str


class RuleListNotion(_Notion):
    """Level 1 or 2. An ordered rule list over the values of other notions.

    The first rule whose conditions hold decides. Deciding therefore requires
    the value of every dependency mentioned by a rule up to and including the
    one that fired, and the solver records exactly that set.
    """

    def __init__(self, name, level, deps, rules: list[_Rule], default: str):
        outputs = tuple([r.output for r in rules] + [default])
        super().__init__(name, level, tuple(deps), outputs)
        self.rules = rules
        self.default = default

    def evaluate(self, case, resolve, consulted):
        for rule in self.rules:
            ok = True
            for dep, want in rule.conditions.items():
                if resolve(dep) != want:
                    ok = False
                    break
            if ok:
                return rule.output
        return self.default

    def definition_body(self) -> str:
        deps = " value and its ".join(self.deps)
        lines = []
        for rule in self.rules:
            cond = " and whose ".join(
                f"{dep} value is {val}" for dep, val in rule.conditions.items())
            lines.append(f"A record whose {cond} has {self.name} value {rule.output}.")
        lines.append(f"Any other record has {self.name} value {self.default}.")
        return (
            f"The {self.name} value of a record is determined by its {deps} value.\n"
            + "\n".join(lines)
            + "\nThe rules above are applied in the order written, and the first "
              "one that applies decides. No other rule bears on the "
              f"{self.name} value."
        )

    def example_case(self, rng):
        return {}


@dataclass
class Problem:
    """One question, its answer, and the proof that the answer needs the pages."""

    qid: str
    chapter: str
    level: int
    notion: str
    phrasing: str  # named | unnamed
    text: str
    answer: str
    case: dict
    required_notions: tuple[str, ...]
    required_pages: tuple[str, ...]
    n_choices: int
    proof: dict = field(default_factory=dict)


@dataclass
class Chapter:
    """One invented theory: its notions, its pages, its true dependency graph."""

    chapter_id: str
    name: str
    seed: int
    notions: dict
    pages: list[Page]
    top: str  # the level-2 notion, the chapter's final classification
    attr_words: dict
    type_words: list[str]
    problems: list[Problem] = field(default_factory=list)

    # ------------------------------------------------------------ evaluation

    def evaluate(self, notion: str, case: dict, known: set | None = None):
        """Return (value, consulted). value is None when a needed definition
        is withheld, which is what makes the necessity proof mechanical.

        known, when given, is the set of notion names whose definitions are
        available. Anything outside it is undetermined and poisons every
        notion that consults it.
        """
        consulted: set[str] = set()
        memo: dict = {}
        failed = {"hit": False}

        def resolve(name: str):
            if name in memo:
                return memo[name]
            consulted.add(name)
            if known is not None and name not in known:
                failed["hit"] = True
                memo[name] = _UNKNOWN
                return _UNKNOWN
            value = self.notions[name].evaluate(case, resolve, consulted)
            if value is _UNKNOWN or failed["hit"]:
                memo[name] = _UNKNOWN
                return _UNKNOWN
            memo[name] = value
            return value

        value = resolve(notion)
        if value is _UNKNOWN or failed["hit"]:
            return None, consulted
        return value, consulted

    # ------------------------------------------------------------- accessors

    def definition_page(self, notion: str) -> Page:
        for p in self.pages:
            if p.notion == notion and p.kind == "definition":
                return p
        raise KeyError(notion)

    def preamble_page(self) -> Page:
        for p in self.pages:
            if p.kind == "preamble":
                return p
        raise KeyError("preamble")

    def theory_graph(self) -> dict:
        """Nodes and edges of the true dependency structure."""
        return {
            "chapter": self.chapter_id,
            "nodes": [
                {"notion": n.name, "level": n.level, "deps": list(n.deps)}
                for n in self.notions.values()
            ],
            "edges": [
                {"prerequisite": d, "notion": n.name}
                for n in self.notions.values() for d in n.deps
            ],
            "top": self.top,
        }


class _Unknown:
    def __repr__(self):
        return "<undetermined>"


_UNKNOWN = _Unknown()


# --------------------------------------------------------------- generation


def build_chapter(seed: int, used: set[str] | None = None) -> Chapter:
    """Invent one chapter: six notions across three levels, and their pages."""
    rng = random.Random(seed)
    used = used if used is not None else set()
    name = _word(rng, 2).capitalize()
    chapter_id = f"ch-{seed:07d}"

    attr_words = {p: _fresh(rng, used) for p in PRIMITIVES}
    type_words = [_fresh(rng, used) for _ in range(3)]

    low = rng.choice([20, 25, 30, 35])
    high = low + rng.choice([25, 30, 40])
    grade = ThresholdNotion(
        _fresh(rng, used), "reading", attr_words["reading"], "reading",
        low, high, tuple(_fresh(rng, used) for _ in range(3)))

    clow = rng.choice([3, 4, 6])
    chigh = clow + rng.choice([5, 7, 9])
    phase = ThresholdNotion(
        _fresh(rng, used), "count", attr_words["count"], "count",
        clow, chigh, tuple(_fresh(rng, used) for _ in range(3)))

    route = TableNotion(
        _fresh(rng, used), "type", attr_words["type"],
        {t: _fresh(rng, used) for t in type_words}, _fresh(rng, used))

    join = RuleListNotion(
        _fresh(rng, used), 1, (grade.name, route.name),
        [
            _Rule({grade.name: grade.outputs[0], route.name: route.outputs[0]},
                  _fresh(rng, used)),
            _Rule({grade.name: grade.outputs[0]}, _fresh(rng, used)),
            _Rule({route.name: route.outputs[1]}, _fresh(rng, used)),
        ],
        _fresh(rng, used))

    merge = RuleListNotion(
        _fresh(rng, used), 1, (phase.name, route.name),
        [
            _Rule({phase.name: phase.outputs[2]}, _fresh(rng, used)),
            _Rule({route.name: route.outputs[2], phase.name: phase.outputs[1]},
                  _fresh(rng, used)),
        ],
        _fresh(rng, used))

    top = RuleListNotion(
        _fresh(rng, used), 2, (join.name, merge.name),
        [
            _Rule({join.name: join.outputs[0]}, _fresh(rng, used)),
            _Rule({merge.name: merge.outputs[0], join.name: join.outputs[1]},
                  _fresh(rng, used)),
            _Rule({merge.name: merge.outputs[1]}, _fresh(rng, used)),
        ],
        _fresh(rng, used))

    notions = {n.name: n for n in (grade, phase, route, join, merge, top)}
    chapter = Chapter(chapter_id=chapter_id, name=name, seed=seed,
                      notions=notions, pages=[], top=top.name,
                      attr_words=attr_words, type_words=type_words)
    chapter.pages = _build_pages(chapter, rng)
    return chapter


def _build_pages(ch: Chapter, rng: random.Random) -> list[Page]:
    """Preamble, then a definition, a worked example and a bare fragment each.

    The preamble is the only page that connects the English phrase a question
    can use ("final classification") to the chapter's own word for it, so an
    unnamed question has to pass through the preamble to learn what to look
    for. That hop is a real prerequisite edge and not a formatting detail.
    """
    pages: list[Page] = []
    top = ch.notions[ch.top]
    pages.append(Page(
        page_id=f"{ch.chapter_id}/preamble", chapter=ch.chapter_id, notion=None,
        level=-1, kind="preamble",
        title=f"The {ch.name} chapter.",
        body=(f"Records filed under the {ch.name} chapter carry three "
              f"attributes: a {ch.attr_words['reading']} reading, a "
              f"{ch.attr_words['type']}, and a {ch.attr_words['count']} count.\n"
              f"The final classification of a record in this chapter is its "
              f"{ch.top} value. Every other value defined in this chapter "
              f"exists in order to determine it."),
        cites=(ch.top,)))

    for notion in ch.notions.values():
        pages.append(Page(
            page_id=f"{ch.chapter_id}/{notion.name}/def", chapter=ch.chapter_id,
            notion=notion.name, level=notion.level, kind="definition",
            title=f"Definition of the {notion.name} value.",
            body=notion.definition_body(),
            cites=notion.deps, defines=notion.outputs))

        case = _sample_case(ch, rng)
        case.update(notion.example_case(rng))
        value, _ = ch.evaluate(notion.name, case)
        pages.append(Page(
            page_id=f"{ch.chapter_id}/{notion.name}/ex", chapter=ch.chapter_id,
            notion=notion.name, level=notion.level, kind="worked_example",
            title=f"A worked example for the {notion.name} value.",
            body=(f"Consider a record with a {ch.attr_words['reading']} reading "
                  f"of {case['reading']}, a {ch.attr_words['type']} of "
                  f"{case['type']}, and a {ch.attr_words['count']} count of "
                  f"{case['count']}. Working through the definition, its "
                  f"{notion.name} value is {value}."),
            cites=(notion.name,)))

        pages.append(Page(
            page_id=f"{ch.chapter_id}/{notion.name}/note", chapter=ch.chapter_id,
            notion=notion.name, level=notion.level, kind="statement",
            title=f"On the {notion.name} value.",
            body=(f"Archivists working in the {ch.name} chapter refer to the "
                  f"{notion.name} value constantly, and it is the first thing "
                  f"recorded on a filing slip. The rule that fixes it is given "
                  f"elsewhere; this note only records that it is used."),
            cites=(notion.name,)))
    return pages


def _sample_case(ch: Chapter, rng: random.Random) -> dict:
    """A record. Types are drawn off the listed set sometimes, to exercise
    the default branch of the table notion."""
    if rng.random() < 0.75:
        t = rng.choice(ch.type_words)
    else:
        t = _word(rng, 3)
    return {"reading": rng.randint(1, 110), "type": t,
            "count": rng.randint(1, 20)}


def _describe_case(ch: Chapter, case: dict) -> str:
    return (f"A record in the {ch.name} chapter has a "
            f"{ch.attr_words['reading']} reading of {case['reading']}, a "
            f"{ch.attr_words['type']} of {case['type']}, and a "
            f"{ch.attr_words['count']} count of {case['count']}.")


def make_problems(ch: Chapter, n_per_level: int = 4, seed: int = 0,
                  store_pages: list[Page] | None = None) -> list[Problem]:
    """Problems at each level, every one carrying its necessity proof.

    store_pages, when given, is the full corpus the problem will be posed
    against, including other chapters. The answer word is checked against all
    of it, so a problem is only kept if no page outside the consulted notions
    hands the answer over.
    """
    rng = random.Random(seed ^ ch.seed)
    pages = store_pages if store_pages is not None else ch.pages
    by_level: dict[int, list[str]] = {}
    for n in ch.notions.values():
        by_level.setdefault(n.level, []).append(n.name)

    out: list[Problem] = []
    for level in sorted(by_level):
        kept = 0
        for _ in range(n_per_level * 60):
            if kept >= n_per_level:
                break
            notion = rng.choice(sorted(by_level[level]))
            case = _sample_case(ch, rng)
            answer, consulted = ch.evaluate(notion, case)
            if answer is None:
                continue
            # Phrasings alternate rather than coin-flip, so a small problem
            # set always carries both and the named/unnamed split is never an
            # accident of the seed.
            unnamed = level == 2 and kept % 2 == 1
            if unnamed:
                text = (f"{_describe_case(ch, case)} "
                        f"What is its final classification?")
            else:
                text = f"{_describe_case(ch, case)} What is its {notion} value?"
            required_notions = tuple(sorted(consulted))
            required_pages = [ch.definition_page(n).page_id
                              for n in required_notions]
            if unnamed:
                required_pages.append(ch.preamble_page().page_id)
            prob = Problem(
                qid=f"{ch.chapter_id}-l{level}-{kept}", chapter=ch.chapter_id,
                level=level, notion=notion,
                phrasing="unnamed" if unnamed else "named",
                text=text, answer=answer, case=case,
                required_notions=required_notions,
                required_pages=tuple(sorted(required_pages)),
                n_choices=len(set(ch.notions[notion].outputs)))
            proof = prove(ch, prob, pages)
            if not proof["ok"]:
                continue
            prob.proof = proof
            out.append(prob)
            kept += 1
    for i, p in enumerate(out):
        p.qid = f"{ch.chapter_id}-l{p.level}-{i}"
    return out


def prove(ch: Chapter, prob: Problem, pages: list[Page]) -> dict:
    """The automatic proof that this problem needs the pages it names.

    Three checks, all mechanical:

      not_copyable   the answer does not stand alone in the question.
      ablation       for every consulted notion, withholding its definition
                     leaves the reference solver unable to determine an
                     answer. This is run, not asserted.
      isolation      the answer word appears on no page of any other chapter,
                     and inside this chapter only on the consulted notions'
                     own pages or on the definition of a notion that consults
                     the target. The second kind of mention is a stated
                     condition ("a record whose G value is A ..."), which
                     names the word without saying that this record has it,
                     and those mentions are listed in the proof record rather
                     than hidden.
      choices        the target notion has at least three possible values, so
                     a blind guess is worth at most a third.
    """
    checks = {}
    checks["not_copyable"] = not _answer_is_copyable(prob.answer, prob.text)

    all_notions = set(ch.notions)
    ablation = {}
    for withheld in prob.required_notions:
        value, _ = ch.evaluate(prob.notion, prob.case,
                               known=all_notions - {withheld})
        ablation[withheld] = value is None
    checks["ablation"] = all(ablation.values()) and bool(ablation)

    consumers = {n.name for n in ch.notions.values()
                 if prob.notion in n.deps}
    allowed = {p.page_id for p in ch.pages
               if p.notion in prob.required_notions
               or (p.notion in consumers and p.kind == "definition")}
    conditional = {p.page_id for p in ch.pages
                   if p.notion in consumers and p.kind == "definition"}
    leaks = []
    mentions = []
    pattern = re.compile(rf"(?<![\w]){re.escape(prob.answer)}(?![\w])")
    for p in pages:
        if not pattern.search(p.text):
            continue
        if p.page_id in allowed:
            if p.page_id in conditional:
                mentions.append(p.page_id)
            continue
        leaks.append(p.page_id)
    checks["isolation"] = not leaks

    checks["choices"] = prob.n_choices >= 3

    return {
        "ok": all(checks.values()),
        "checks": checks,
        "ablation": ablation,
        "leaks": leaks,
        "conditional_mentions": mentions,
        "n_choices": prob.n_choices,
        "n_required_notions": len(prob.required_notions),
    }


@dataclass
class Universe:
    """A corpus of chapters, the pages they contribute, and their problems."""

    chapters: list[Chapter]
    pages: list[Page]

    def documents(self) -> list[dict]:
        return [p.to_document() for p in self.pages]

    def problems(self) -> list[Problem]:
        return [p for ch in self.chapters for p in ch.problems]

    def page_by_id(self, page_id: str) -> Page:
        for p in self.pages:
            if p.page_id == page_id:
                return p
        raise KeyError(page_id)

    def theory_graphs(self) -> list[dict]:
        return [ch.theory_graph() for ch in self.chapters]


def build_universe(seed: int, n_chapters: int = 3, n_per_level: int = 4,
                   problem_chapters: int | None = None) -> Universe:
    """Build a small universe. Chapters beyond problem_chapters are pure
    distractors, which is what forces retrieval to discriminate."""
    used: set[str] = set()
    chapters = [build_chapter(seed * 1000 + i, used) for i in range(n_chapters)]
    pages = [p for ch in chapters for p in ch.pages]
    n_with_problems = n_chapters if problem_chapters is None else problem_chapters
    for ch in chapters[:n_with_problems]:
        ch.problems = make_problems(ch, n_per_level=n_per_level, seed=seed,
                                    store_pages=pages)
    return Universe(chapters=chapters, pages=pages)
