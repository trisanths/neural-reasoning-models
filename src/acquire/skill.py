"""The compiled skill memory: what the agent carries instead of the pages.

A retrieved page is prose. Most of it is scaffolding: a title, a sentence
saying what an attribute is, a closing remark that no other rule applies. The
part that has to survive into the next reasoning step is small: the term being
defined, the rule that fixes it, the values it can take, the terms it consults,
and the examples that pin it down.

This module compiles pages into that object and renders it back as a compact
card. Two things are deliberate.

Compilation reads the page text, not the generator's metadata. The document
records carry a cites field holding the true prerequisite edges, and reading
it would make the curriculum's reconstruction of the dependency graph
meaningless. Nothing here touches it; dependencies come out of the sentences
by their grammar, from the positions a term can occupy around the word
"value". test_curriculum_does_not_read_the_generators_cites_field pins that: the
whole corpus is re-run with the field stripped and nothing may change.

The card is discarded when the request ends. It is a working memory for one
question, not a store that accumulates across a benchmark, so nothing learned
on one problem can leak into the next.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# A term earns concept status by the position it occupies, not by being on a
# list of words. These are the frames the textbook writes definitions in.
_CONCEPT_FRAMES = (
    re.compile(r"\bthe ([a-z]{3,}) value\b"),
    re.compile(r"\bwhose ([a-z]{3,}) value\b"),
    re.compile(r"\bits ([a-z]{3,}) value\b"),
    re.compile(r"\bhas ([a-z]{3,}) value\b"),
)
_TITLE_TERM = re.compile(r"Definition of the ([a-z]{3,}) value")
_EXAMPLE_TERM = re.compile(r"Worked examples for the ([a-z]{3,}) value")
_STATEMENT_TERM = re.compile(r"On the ([a-z]{3,}) value")
_PREAMBLE_TOP = re.compile(
    r"final classification of a record in this chapter is its ([a-z]{3,}) value")
_CHAPTER = re.compile(r"The ([A-Z][a-z]+) chapter")
_CONDITION = re.compile(r"whose ([a-z]{3,}) value is ([a-z]{3,})")
_DETERMINED_BY = re.compile(
    r"determined by its ([a-z]{3,}) value and its ([a-z]{3,}) value")
_EXAMPLE_LINE = re.compile(r"^(.*?)\s+Its ([a-z]{3,}) value is ([a-z]{3,})\.$")
# The card's own line format, so a card can be read back into a memory.
_CARD_CHAPTER = re.compile(r"^Notes on the ([A-Z][a-z]+) chapter\.$")
_CARD_TOP = re.compile(r"^the final classification is the ([a-z]{3,}) value$")
_CARD_CONCEPT = re.compile(r"^([a-z]{3,})(?: from (.+?))?: (.*)$")


def _split_rules(text: str) -> list[str]:
    """Rule sentences out of one card line, periods kept so the rule regexes
    in src/acquire/gap.py see the same strings the page carried."""
    out = []
    for piece in re.split(r"(?<=\.)\s+", text.strip()):
        piece = piece.strip()
        if piece:
            out.append(piece)
    return out


def concept_terms(text: str) -> set[str]:
    """Terms occupying a definitional position in this text."""
    out: set[str] = set()
    for frame in _CONCEPT_FRAMES:
        out.update(frame.findall(text))
    return out


@dataclass
class Concept:
    """One acquired notion, compressed to what the next step needs."""

    term: str
    chapter: str = ""
    rules: list[str] = field(default_factory=list)
    outputs: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    reads_attribute: str = ""
    examples: list[tuple[str, str]] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    failure_conditions: list[str] = field(default_factory=list)
    source_pages: tuple[str, ...] = ()
    verified: bool = False
    battery_score: float | None = None

    def render(self) -> str:
        deps = (f" from {' and '.join(self.depends_on)}"
                if self.depends_on else
                (f" from {self.reads_attribute}" if self.reads_attribute else ""))
        head = f"{self.term}{deps}:"
        return " ".join([head] + self.rules)


@dataclass
class CompiledSection:
    """What one retrieved learning object contributed."""

    term: str
    kind: str
    page_id: str
    rules: list[str]
    outputs: tuple[str, ...]
    depends_on: tuple[str, ...]
    reads_attribute: str
    examples: list[tuple[str, str]]
    chapter_name: str = ""
    top_term: str = ""


def compile_section(page: dict) -> CompiledSection | None:
    """Read one page's text into structured fields. Returns None when the page
    states nothing worth carrying, which is what a bare fragment does."""
    title = page.get("title") or page["text"].split("\n\n")[0]
    body = page.get("body") or page["text"].split("\n\n", 1)[-1]
    chapter_name = ""
    m = _CHAPTER.search(page["text"])
    if m:
        chapter_name = m.group(1)

    m = _PREAMBLE_TOP.search(body)
    if m:
        return CompiledSection(
            term=m.group(1), kind="preamble", page_id=page.get("page_id", ""),
            rules=[f"the final classification of a record in the "
                   f"{chapter_name} chapter is its {m.group(1)} value"],
            outputs=(), depends_on=(), reads_attribute="", examples=[],
            chapter_name=chapter_name, top_term=m.group(1))

    m = _TITLE_TERM.search(title)
    if m:
        term = m.group(1)
        rules = [ln.strip() for ln in body.split("\n")
                 if f"has {term} value" in ln]
        outputs = tuple(dict.fromkeys(
            re.findall(rf"has {re.escape(term)} value ([a-z]{{3,}})", body)))
        deps = tuple(dict.fromkeys(
            d for d, _ in _CONDITION.findall(body) if d != term))
        if not deps:
            dm = _DETERMINED_BY.search(body)
            if dm:
                deps = (dm.group(1), dm.group(2))
        attr = ""
        am = re.search(r"Every record carries a ([a-z]{3,})", body)
        if am:
            attr = am.group(1)
        return CompiledSection(
            term=term, kind="definition", page_id=page.get("page_id", ""),
            rules=rules, outputs=outputs, depends_on=deps,
            reads_attribute=attr, examples=[], chapter_name=chapter_name)

    m = _EXAMPLE_TERM.search(title)
    if m:
        term = m.group(1)
        examples = []
        for line in body.split("\n"):
            em = _EXAMPLE_LINE.match(line.strip())
            if em and em.group(2) == term:
                examples.append((em.group(1).strip(), em.group(3)))
        return CompiledSection(
            term=term, kind="worked_example", page_id=page.get("page_id", ""),
            rules=[], outputs=tuple(dict.fromkeys(v for _, v in examples)),
            depends_on=(), reads_attribute="", examples=examples,
            chapter_name=chapter_name)

    m = _STATEMENT_TERM.search(title)
    if m:
        return CompiledSection(
            term=m.group(1), kind="statement", page_id=page.get("page_id", ""),
            rules=[], outputs=(), depends_on=(), reads_attribute="",
            examples=[], chapter_name=chapter_name)
    return None


def compile_by_mention(page: dict, lexicon) -> CompiledSection | None:
    """Compile a page whose prose this module cannot parse sentence by sentence.

    A corpus written by a different generator states its rules in its own
    grammar, and a reader tuned to one grammar reads nothing in another. What
    survives the change is coarser and still useful: the page introduces one
    term, and it mentions others it does not introduce, and those mentions are
    the prerequisites. The term the page introduces comes from the structured
    field the textbook emits; the mentions come from the text. The generator's
    own dependency list is never read.
    """
    term = page.get("notion")
    if not term:
        return None
    text = page["text"]
    deps = tuple(name for name in lexicon
                 if name != term
                 and re.search(rf"(?<!\w){re.escape(name)}(?!\w)", text))
    body = page.get("body") or text.split("\n\n", 1)[-1]
    rules = [ln.strip() for ln in body.split("\n") if ln.strip()]
    return CompiledSection(
        term=term, kind=page.get("kind", "definition"),
        page_id=page.get("page_id", ""), rules=rules, outputs=(),
        depends_on=deps, reads_attribute="", examples=[],
        chapter_name=page.get("chapter", ""))


class SkillMemory:
    """The compact object carried forward, and thrown away at the end."""

    def __init__(self) -> None:
        self.concepts: dict[str, Concept] = {}
        self.chapter_name: str = ""
        self.top_term: str = ""
        # One corpus holds several chapters and each has its own final
        # classification, so "the final classification" is ambiguous until a
        # chapter is in focus. Keeping them all and resolving on focus is the
        # difference between answering the question asked and answering a
        # neighbouring chapter's question.
        self.tops: dict[str, str] = {}
        self.transformations: list[str] = []
        self.proof_patterns: list[str] = []
        self.raw_chars: int = 0
        self.absorbed_pages: list[str] = []

    # ------------------------------------------------------------- building

    def absorb(self, page: dict, lexicon=None) -> CompiledSection | None:
        """Fold one page into the memory. A fragment that states no rule and
        no example changes nothing, which is why lesson ranking matters.

        lexicon, when given, enables the coarse mention-based reader for a
        corpus this module's sentence grammar does not fit.
        """
        sec = compile_section(page)
        if lexicon is not None and (sec is None or not sec.rules):
            sec = compile_by_mention(page, lexicon) or sec
        self.raw_chars += len(page["text"])
        self.absorbed_pages.append(page.get("page_id", ""))
        if sec is None:
            return None
        if sec.chapter_name and not self.chapter_name:
            self.chapter_name = sec.chapter_name
        if sec.kind == "preamble":
            if sec.chapter_name:
                self.tops[sec.chapter_name] = sec.top_term
            if not self.top_term or sec.chapter_name == self.chapter_name:
                self.top_term = sec.top_term
            self.transformations.append(sec.rules[0])
            return sec
        if sec.kind == "statement":
            return sec
        c = self.concepts.get(sec.term)
        if c is None:
            c = Concept(term=sec.term, chapter=sec.chapter_name)
            self.concepts[sec.term] = c
        if sec.rules:
            c.rules = sec.rules
        if sec.outputs:
            c.outputs = tuple(dict.fromkeys(c.outputs + sec.outputs))
        if sec.depends_on:
            c.depends_on = sec.depends_on
        if sec.reads_attribute:
            c.reads_attribute = sec.reads_attribute
        if sec.examples:
            c.examples = sec.examples
        c.source_pages = tuple(dict.fromkeys(c.source_pages + (sec.page_id,)))
        if sec.kind == "definition":
            c.invariants = [
                "the rules are applied in the order written and the first that "
                "applies decides"] if len(sec.rules) > 1 else []
            c.failure_conditions = [
                f"a record whose {d} value is unknown has no determined "
                f"{sec.term} value" for d in sec.depends_on]
        return sec

    def focus(self, chapter_name: str) -> None:
        """Say which chapter the current question is about."""
        if not chapter_name:
            return
        self.chapter_name = chapter_name
        if chapter_name in self.tops:
            self.top_term = self.tops[chapter_name]

    # ------------------------------------------------------------- querying

    def covers(self, term: str) -> bool:
        """A term is covered when its rule is held, not merely its name."""
        c = self.concepts.get(term)
        return bool(c and c.rules)

    def verified_terms(self) -> set[str]:
        return {t for t, c in self.concepts.items() if c.verified}

    def frontier(self) -> list[str]:
        """Terms cited by something held, whose own rule is missing."""
        out = []
        for c in self.concepts.values():
            for d in c.depends_on:
                if not self.covers(d) and d not in out:
                    out.append(d)
        if self.top_term and not self.covers(self.top_term):
            out.append(self.top_term)
        return out

    def dependency_graph(self) -> dict:
        """The graph the agent believes in, for scoring against the true one."""
        nodes = sorted(self.concepts)
        edges = [{"prerequisite": d, "notion": c.term}
                 for c in self.concepts.values() for d in c.depends_on]
        return {"nodes": nodes, "edges": edges, "top": self.top_term}

    def resolvable(self, term: str) -> bool:
        """Whether the closure under the held rules reaches term.

        Two notions at the same level routinely share a prerequisite, so the
        recursion has to memoize rather than refuse a second visit; refusing
        would report a diamond as a cycle and every level-2 notion in this
        universe is a diamond.
        """
        state: dict[str, bool | None] = {}

        def go(t: str) -> bool:
            if t in state:
                # None means the walk is still inside t, which is a real cycle.
                return bool(state[t])
            state[t] = None
            c = self.concepts.get(t)
            ok = bool(c and c.rules) and all(go(d) for d in c.depends_on)
            state[t] = ok
            return ok

        return go(term)

    def unresolved(self, term: str) -> list[str]:
        """Which terms in term's closure are still missing their rule."""
        missing: list[str] = []
        seen: set[str] = set()

        def go(t: str) -> None:
            if t in seen:
                return
            seen.add(t)
            c = self.concepts.get(t)
            if c is None or not c.rules:
                missing.append(t)
                return
            for d in c.depends_on:
                go(d)

        go(term)
        return missing

    # ------------------------------------------------------------ rendering

    def render(self, only: list[str] | None = None,
               verified_only: bool = False) -> str:
        """The card. One line per concept, rules only, prose dropped."""
        terms = only if only is not None else sorted(self.concepts)
        lines = []
        if self.chapter_name:
            lines.append(f"Notes on the {self.chapter_name} chapter.")
        for t in terms:
            c = self.concepts.get(t)
            if c is None or not c.rules:
                continue
            if verified_only and not c.verified:
                continue
            lines.append(c.render())
        if self.top_term and self.top_term in (terms or ()):
            lines.append(f"the final classification is the {self.top_term} value")
        return "\n".join(lines)

    def compression(self, only: list[str] | None = None) -> dict:
        card = self.render(only=only)
        return {"raw_chars": self.raw_chars, "card_chars": len(card),
                "ratio": (len(card) / self.raw_chars) if self.raw_chars else 0.0,
                "n_concepts": len(self.concepts)}

    @classmethod
    def load_card(cls, card: str) -> "SkillMemory":
        """Read a rendered card back into a memory.

        The card is what actually reaches the model, so anything the card
        drops is genuinely lost. Parsing it back is how the compression is
        checked for lossiness rather than assumed harmless.
        """
        mem = cls()
        mem.raw_chars = len(card)
        for line in card.splitlines():
            line = line.strip()
            if not line:
                continue
            m = _CARD_CHAPTER.match(line)
            if m:
                mem.chapter_name = m.group(1)
                continue
            m = _CARD_TOP.match(line)
            if m:
                mem.top_term = m.group(1)
                if mem.chapter_name:
                    mem.tops[mem.chapter_name] = m.group(1)
                mem.transformations.append(line)
                continue
            m = _CARD_CONCEPT.match(line)
            if not m:
                continue
            term, source, rules = m.group(1), m.group(2) or "", m.group(3)
            deps = tuple(s.strip() for s in source.split(" and ")
                         if s.strip()) if " and " in source else ()
            attr = source.strip() if source and not deps else ""
            c = Concept(term=term, chapter=mem.chapter_name,
                        rules=_split_rules(rules), depends_on=deps,
                        reads_attribute=attr, source_pages=("card",))
            c.outputs = tuple(dict.fromkeys(
                re.findall(rf"has {re.escape(term)} value ([a-z]{{3,}})", rules)))
            mem.concepts[term] = c
        return mem

    def discard(self) -> None:
        """End of request. Nothing survives into the next question."""
        self.concepts.clear()
        self.tops.clear()
        self.transformations.clear()
        self.proof_patterns.clear()
        self.absorbed_pages.clear()
        self.chapter_name = ""
        self.top_term = ""
        self.raw_chars = 0
