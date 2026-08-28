"""The knowledge-gap detector.

Two jobs, and the second matters more than the first.

The first is classification: given a stalled reasoning state, say what kind of
blockage it is. The categories are the ones a reasoner can actually act on
differently -- a known computation is finished by computing, a missing
definition is finished by finding a page, a missing prerequisite is finished
by recursing.

The second is the structural description. A reasoner that is blocked because
it lacks a concept usually cannot name that concept: naming it is what it
lacks. So the description that leaves this module never assumes the missing
result has a name. It states the objects in hand and the properties they are
known to have, the transformation that has to be produced, and the property
that must be preserved on the way. Those three fields are what the search
query is built from, and that is what lets the agent find a section whose
title it could not have written.

The difference is measurable. A naive query is the question's own words, which
mention only the record's primitive attributes and so retrieve the level-0
pages over and over. A structural query carries the intermediate values the
agent now holds, which are exactly the terms a higher-level page cites, so it
retrieves the page above. run_report in src/acquire/loop.py measures both.

Categories that this universe cannot produce are still implemented and still
checked; they report as never firing rather than being quietly absent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.acquire.skill import SkillMemory, concept_terms

BLOCKAGES = (
    "known_computation",
    "known_concept",
    "missing_fact",
    "missing_definition",
    "missing_transformation",
    "missing_theorem",
    "missing_proof_technique",
    "missing_language",
    "missing_prerequisite",
)

_NUMERIC_ATTR = re.compile(r"\ba ([a-z]{3,}) (reading|count) of (\d+)\b")
_WORD_ATTR = re.compile(r"\ba ([a-z]{3,}) of ([a-z]{3,})\b")
_CHAPTER = re.compile(r"\bthe ([A-Z][a-z]+) chapter\b")
_ASK_NAMED = re.compile(r"What is its ([a-z]{3,}) value\?")
_ASK_UNNAMED = re.compile(r"What is its (final classification)\?")
# A symbol the textbook never introduced is a language gap, not a concept gap.
# Only a free-standing glyph counts: the question mark ending a question is
# punctuation, and reading it as undefined notation would fire on everything.
_GLYPH = re.compile(r"(?:(?<=\s)|^)([@#$&*+~^<>|=/])(?=\s|$)")


@dataclass
class StructuralGap:
    """What is missing, said without needing the missing thing's name."""

    fired: bool
    blockage: str
    objects: list[str] = field(default_factory=list)
    known_properties: list[str] = field(default_factory=list)
    transformation: str = ""
    preserve: str = ""
    named_targets: list[str] = field(default_factory=list)
    query: str = ""
    naive_query: str = ""
    rationale: str = ""
    missing_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "fired": self.fired, "blockage": self.blockage,
            "objects": list(self.objects),
            "known_properties": list(self.known_properties),
            "transformation": self.transformation, "preserve": self.preserve,
            "named_targets": list(self.named_targets),
            "query": self.query, "naive_query": self.naive_query,
            "rationale": self.rationale,
            "missing_terms": list(self.missing_terms),
        }


def parse_state(question: str) -> dict:
    """The objects in hand and the property asked for, read off the question."""
    objects = [f"a {w} {noun} of {v}"
               for w, noun, v in _NUMERIC_ATTR.findall(question)]
    numeric_words = {w for w, _, _ in _NUMERIC_ATTR.findall(question)}
    for w, v in _WORD_ATTR.findall(question):
        if w in numeric_words or w == "record":
            continue
        objects.append(f"a {w} of {v}")
    ch = _CHAPTER.search(question)
    named = _ASK_NAMED.search(question)
    unnamed = _ASK_UNNAMED.search(question)
    return {
        "objects": objects,
        "chapter": ch.group(1) if ch else "",
        "target": named.group(1) if named else "",
        "asked_for": (named.group(1) + " value") if named else
                     (unnamed.group(1) if unnamed else "an answer"),
        "glyphs": sorted(set(_GLYPH.findall(question))),
    }


def detect(question: str, skill: SkillMemory,
           attempted_answer: str | None = None) -> StructuralGap:
    """Classify the blockage and describe it structurally.

    The stalled state is the question together with everything the skill
    memory currently holds. attempted_answer, when supplied, is what the model
    said from that state; it is recorded but is never what decides whether the
    gap fires, because an answer that sounds fluent is exactly the state this
    module has to fire on.
    """
    st = parse_state(question)
    chapter = st["chapter"] or skill.chapter_name
    target = st["target"]
    in_hand = _properties_in_hand(question, skill)

    base = dict(objects=st["objects"], known_properties=in_hand,
                naive_query=question.strip())

    if st["glyphs"]:
        undefined = [g for g in st["glyphs"]
                     if not any(g in c.render() for c in skill.concepts.values())]
        if undefined:
            return StructuralGap(
                fired=True, blockage="missing_language",
                transformation=f"read the notation {' '.join(undefined)}",
                preserve="the notation's stated meaning",
                query=f"notation {' '.join(undefined)} {chapter} chapter meaning",
                rationale="a symbol appears that no held page introduces",
                missing_terms=undefined, **base)

    if target:
        if skill.resolvable(target):
            return StructuralGap(
                fired=False, blockage="known_computation",
                transformation=f"apply the held {target} rule to this record",
                preserve="the rule order stated in the definition",
                named_targets=[target], query="",
                rationale="every rule in the target's closure is held",
                **base)
        missing = skill.unresolved(target)
        if skill.covers(target):
            first = missing[0]
            return StructuralGap(
                fired=True, blockage="missing_prerequisite",
                transformation=(f"determine the {first} value of this record, "
                                f"which the held {target} rule consults"),
                preserve=f"the {target} rule already held",
                named_targets=[target], missing_terms=missing,
                query=_named_query(first, chapter, in_hand),
                rationale=(f"the {target} rule is held but cites {first}, "
                           f"whose rule is not"), **base)
        return StructuralGap(
            fired=True, blockage="missing_definition",
            transformation=f"determine the {target} value of this record",
            preserve="whatever the chapter states, applied in its stated order",
            named_targets=[target], missing_terms=missing or [target],
            query=_named_query(target, chapter, in_hand),
            rationale=f"the question names {target} and no held page defines it",
            **base)

    # Nothing is named. This is the case the structural description exists for.
    asked = st["asked_for"]
    if skill.top_term and skill.resolvable(skill.top_term):
        return StructuralGap(
            fired=False, blockage="known_computation",
            transformation=f"apply the held {skill.top_term} rule",
            preserve="the rule order stated in the definition",
            named_targets=[skill.top_term], query="",
            rationale="the chapter's final value is fully resolvable",
            **base)
    if skill.top_term:
        missing = skill.unresolved(skill.top_term)
        return StructuralGap(
            fired=True, blockage="missing_prerequisite",
            transformation=(f"produce {asked}, which is the "
                            f"{skill.top_term} value"),
            preserve="the chapter's own vocabulary and its stated rule order",
            named_targets=[skill.top_term], missing_terms=missing,
            query=_structural_query(chapter, asked, in_hand, missing),
            rationale=(f"the target has a name ({skill.top_term}) but its "
                       f"closure is incomplete"), **base)
    if not skill.concepts:
        return StructuralGap(
            fired=True, blockage="missing_definition",
            transformation=f"produce {asked} for a record of this chapter",
            preserve="the chapter's own vocabulary",
            query=(_structural_query(chapter, asked, in_hand, [])
                   or question.strip()),
            rationale="nothing about this chapter is held and the target is "
                      "not named in the question",
            **base)
    return StructuralGap(
        fired=True, blockage="missing_transformation",
        transformation=(f"turn the values now in hand into {asked}"),
        preserve="the chapter's own vocabulary and its stated rule order",
        missing_terms=[],
        query=(_structural_query(chapter, asked, in_hand, [])
               or question.strip()),
        rationale="values are held but nothing held maps them to what is asked",
        **base)


def _properties_in_hand(question: str, skill: SkillMemory) -> list[str]:
    """Values the memory can already derive for this record, stated as
    property phrases. These are the terms a higher page cites, so they are
    what makes a structural query reach upward."""
    case = _case_from_question(question)
    out = []
    for term in sorted(skill.concepts):
        if not skill.resolvable(term):
            continue
        value = evaluate_with_memory(skill, term, case)
        if value is None:
            continue
        out.append(f"its {term} value is {value}")
    return out


def _case_from_question(question: str) -> dict:
    case: dict = {}
    for w, noun, v in _NUMERIC_ATTR.findall(question):
        case[w] = int(v)
        case[noun] = int(v)
    numeric_words = {w for w, _, _ in _NUMERIC_ATTR.findall(question)}
    for w, v in _WORD_ATTR.findall(question):
        if w in numeric_words or w == "record":
            continue
        case[w] = v
        case.setdefault("type", v)
    return case


_RULE_THRESHOLD = re.compile(
    r"A record whose ([a-z]{3,}) (?:reading|count) is greater than (\d+)"
    r"(?: but not greater than (\d+))? has [a-z]{3,} value ([a-z]{3,})")
_RULE_TABLE = re.compile(
    r"A record of ([a-z]{3,}) ([a-z]{3,}) has [a-z]{3,} value ([a-z]{3,})")
_RULE_DEFAULT_TABLE = re.compile(
    r"A record whose ([a-z]{3,}) is not one of those listed has [a-z]{3,} "
    r"value ([a-z]{3,})")
_RULE_COMPOSED = re.compile(
    r"A record whose (.+?) has [a-z]{3,} value ([a-z]{3,})\.")
_RULE_ANY = re.compile(r"Any other record has [a-z]{3,} value ([a-z]{3,})")
_COND = re.compile(r"([a-z]{3,}) value is ([a-z]{3,})")


def evaluate_with_memory(skill: SkillMemory, term: str, case: dict,
                         _seen: set | None = None):
    """Run the rules the memory holds, the way the memory recorded them.

    This is the agent's own execution of what it learned, not the generator's
    reference solver. It is what makes "the values in hand" real rather than
    borrowed, and it returns None whenever a rule it needs is missing.
    """
    _seen = _seen or set()
    if term in _seen:
        return None
    _seen = _seen | {term}
    c = skill.concepts.get(term)
    if c is None or not c.rules:
        return None
    for line in c.rules:
        m = _RULE_THRESHOLD.search(line)
        if m:
            attr, low, high, out = m.groups()
            v = case.get(attr)
            if v is None:
                continue
            if high is None:
                if int(v) > int(low):
                    return out
            elif int(low) < int(v) <= int(high):
                return out
            continue
        m = _RULE_TABLE.search(line)
        if m:
            attr, key, out = m.groups()
            if case.get(attr) == key:
                return out
            continue
        m = _RULE_DEFAULT_TABLE.search(line)
        if m:
            attr, out = m.groups()
            if case.get(attr) is not None:
                return out
            continue
        m = _RULE_COMPOSED.search(line)
        if m:
            conds = _COND.findall(m.group(1))
            if conds and all(
                    evaluate_with_memory(skill, d, case, _seen) == v
                    for d, v in conds):
                return m.group(2)
            continue
    # The catch-all only fires once every input the rule list could have
    # consulted is actually in hand. Falling through because an attribute is
    # absent from the record is not the same as falling through because no
    # rule applied, and conflating them would invent an answer.
    if c.reads_attribute and case.get(c.reads_attribute) is None:
        return None
    for line in c.rules:
        m = _RULE_ANY.search(line)
        if m:
            for d in c.depends_on:
                if evaluate_with_memory(skill, d, case, _seen) is None:
                    return None
            return m.group(1)
    return None


def _named_query(term: str, chapter: str, in_hand: list[str]) -> str:
    parts = [f"Definition of the {term} value"]
    if chapter:
        parts.append(f"{chapter} chapter")
    return " ".join(parts)


def _structural_query(chapter: str, asked: str, in_hand: list[str],
                      missing: list[str]) -> str:
    """The query that does not need the missing thing's name.

    Objects in hand plus the transformation. When the agent already holds
    intermediate values, their terms go in: a page that consumes them cites
    them, so this is the query that climbs a level.
    """
    parts = []
    if chapter:
        parts.append(f"{chapter} chapter")
    parts.append(asked)
    for term in missing[:3]:
        parts.append(f"Definition of the {term} value")
    for prop in in_hand[:4]:
        parts.append(prop.replace("its ", "whose "))
    parts.append("determined by")
    query = " ".join(parts)
    if not chapter and not in_hand and not missing:
        # Nothing structural was recoverable from this question, which happens
        # when the corpus is not the one this module's patterns were written
        # for. Saying so and falling back to the question's own words is
        # better than emitting a two word query and calling it a search.
        return ""
    return query


def summarize(gaps: list[StructuralGap]) -> dict:
    """Per-category firing counts, including the categories that never fire."""
    counts = {b: 0 for b in BLOCKAGES}
    for g in gaps:
        counts[g.blockage] = counts.get(g.blockage, 0) + 1
    return {
        "n": len(gaps),
        "fired": sum(1 for g in gaps if g.fired),
        "by_blockage": counts,
        "never_fired": [b for b, c in counts.items() if c == 0],
    }
