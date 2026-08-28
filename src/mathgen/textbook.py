"""Render a theory as a textbook, chunked so a retriever can serve a section.

A chapter is not a dump of its nodes. It runs through ten slots, the ones a real
chapter has: why the chapter exists, what it defines, what shape the thing has,
where the results come from, a worked example, a case that breaks, the limits of
what was proved, the neighbouring results, the proofs, and exercises.

Five registers rotate across chapters, so a universe does not read as one voice
repeated. The register changes which phrasings a slot draws from, not what the
slot says: content comes from the theory graph and from the reference
implementation, never from a template's imagination. Every number, element name,
extension and worked step in the prose was computed.

Chunking is by section, split at a word budget, and each chunk carries its
chapter, section kind and the node ids it covers, so a retriever that serves one
chunk serves a coherent unit of the argument rather than a fragment.
"""

from __future__ import annotations

import random
import textwrap
from dataclasses import dataclass, field

from src.mathgen.algebra import Structure
from src.mathgen.theory import (THEME_TITLES, Theory, chapter_nodes, ext_core,
                                ext_steady, names, reach_of, shadow_of, span_of)

WORDS_PER_PAGE = 400

REGISTERS = ["lecture", "treatise", "workbook", "chronicle", "applied"]

SECTION_ORDER = ["motivation", "definitions", "intuition", "derivation",
                 "example", "counterexample", "scope", "related", "proof",
                 "exercises"]

SECTION_TITLES = {
    "motivation": "Why this chapter",
    "definitions": "What is defined here",
    "intuition": "The shape of it",
    "derivation": "Where these results come from",
    "example": "A worked case",
    "counterexample": "A case that breaks",
    "scope": "Reach and limits",
    "related": "Neighbouring results",
    "proof": "Proofs",
    "exercises": "Exercises",
}


@dataclass
class Section:
    chapter: int
    chapter_title: str
    index: int
    kind: str
    title: str
    text: str
    node_ids: list = field(default_factory=list)
    register: str = "lecture"

    def word_count(self) -> int:
        return len(self.text.split())


@dataclass
class Chapter:
    number: int
    title: str
    register: str
    sections: list
    node_ids: list
    worked_examples: list = field(default_factory=list)

    def word_count(self) -> int:
        return sum(s.word_count() for s in self.sections)

    def to_markdown(self) -> str:
        out = [f"# Chapter {self.number + 1}. {self.title}", ""]
        for s in self.sections:
            out.append(f"## {s.title}")
            out.append("")
            out.append(s.text)
            out.append("")
        return "\n".join(out)


@dataclass
class Textbook:
    theory: Theory
    chapters: list
    front_matter: str

    def word_count(self) -> int:
        return len(self.front_matter.split()) + sum(c.word_count()
                                                    for c in self.chapters)

    def pages(self) -> float:
        return round(self.word_count() / WORDS_PER_PAGE, 1)


# ---------------------------------------------------------------------------
# Phrasing
# ---------------------------------------------------------------------------


def _pick(rng: random.Random, options: list) -> str:
    return rng.choice(options)


def _join(items: list) -> str:
    items = [str(i) for i in items]
    if not items:
        return "nothing"
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _wrap(text: str) -> str:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "\n\n".join(textwrap.fill(p, width=88) for p in paragraphs)


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


def render_table(s: Structure, k: int) -> str:
    width = max(len(e) for e in s.elements) + 2
    head = " " * width + "|" + "".join(e.rjust(width) for e in s.elements)
    rule = "-" * len(head)
    rows = [head, rule]
    for i, name in enumerate(s.elements):
        cells = "".join(s.name(s.op(k, i, j)).rjust(width) for j in range(s.size))
        rows.append(name.rjust(width - 1) + " |" + cells)
    return (f"The table for {s.op_glyphs[k]}. Read the left argument down the "
            f"side and the right argument across the top.\n\n"
            + "\n".join(rows))


def render_relation(s: Structure) -> str:
    lines = []
    for i in range(s.size):
        sh = names(s, shadow_of(s, i))
        lines.append(f"  {s.name(i)} {s.rel_glyph} " + (_join(sh) if sh else "nothing"))
    return (f"Every pair standing in the {s.rel_glyph} relation, grouped by left "
            f"argument.\n\n" + "\n".join(lines))


# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------


def build_front_matter(theory: Theory, rng: random.Random) -> str:
    s = theory.structure
    obj, objs = s.object_name, s.object_plural
    g0 = s.op_glyphs[0]
    opening = _pick(rng, [
        (f"This book is about {objs}. A {obj} is not a number and not a set; it "
         f"is one of exactly {s.size} objects, and everything said here is said "
         f"about how those {s.size} objects combine."),
        (f"What follows is a complete account of the {s.system_name} system. It "
         f"is complete in a strong sense: the system has {s.size} {objs} and "
         f"finitely many facts, and every one of those facts is settled here by "
         f"inspection rather than left to argument."),
        (f"The {s.system_name} system is small enough to hold in the hand and "
         f"strange enough to be worth the trouble. It has {s.size} {objs}, "
         + (f"two operations" if s.has_two_ops else "one operation")
         + f", and one relation, and nothing else."),
    ])
    naming = (f"The {objs} are written {_join(s.elements)}. The first operation "
              f"is written {g0}. ")
    if s.has_two_ops:
        naming += (f"The second is written {s.op_glyphs[1]} and binds more "
                   f"tightly, so x {g0} y {s.op_glyphs[1]} z means "
                   f"x {g0} (y {s.op_glyphs[1]} z). ")
    naming += (f"The relation is written {s.rel_glyph}; where it holds between "
               f"two {objs} we say the left one {s.rel_name} the right one. "
               f"Both operations associate to the left when written without "
               f"brackets, and brackets override that. Repeated combination is "
               f"abbreviated: x^3 means x {g0} x {g0} x.")
    if s.has_inverses:
        naming += (f" A trailing mark reverses: x' is the {obj} that combines "
                   f"with x to give the neutral one.")
    caution = _pick(rng, [
        ("A warning that will be repeated because it is the one readers ignore: "
         "nothing here is inherited from arithmetic. Familiar names have been "
         "avoided on purpose. Where a law of arithmetic happens to hold it is "
         "stated and checked, and where it fails a counterexample is given."),
        ("Readers arriving from arithmetic should put it down at the door. The "
         "operations below are defined by their tables and by nothing else. "
         "Several arithmetic habits survive the crossing and several do not, and "
         "the text is careful to say which is which."),
    ])
    return _wrap("\n\n".join([opening, naming, caution]))


# ---------------------------------------------------------------------------
# Section writers
# ---------------------------------------------------------------------------


def _sec_motivation(theory, chapter, nodes, rng, register) -> str:
    s = theory.structure
    kinds = {n.kind for n in nodes}
    incoming = sorted({theory.nodes[d].chapter for n in nodes
                       for d in n.depends_on if theory.nodes[d].chapter < chapter})
    what = _join([n.title for n in nodes[:3]])
    lines = []
    if register == "lecture":
        lines.append(_pick(rng, [
            f"So far the {s.object_plural} have been objects to be pushed around. "
            f"This chapter starts asking what they are like. We take up {what}.",
            f"Here is the question this chapter answers: once the combining is "
            f"settled, what can be said about the objects themselves? The route "
            f"runs through {what}."]))
    elif register == "treatise":
        lines.append(_pick(rng, [
            f"The present chapter develops {what}.",
            f"We turn to {what}. The treatment is self contained given the "
            f"material already established."]))
    elif register == "workbook":
        lines.append(_pick(rng, [
            f"Work through this chapter with the tables in front of you. It "
            f"covers {what}, and each claim can be checked by hand.",
            f"Everything in this chapter is checkable by inspection. The subject "
            f"is {what}."]))
    elif register == "chronicle":
        lines.append(_pick(rng, [
            f"The results collected here were not found in this order. {what} "
            f"came first, and the rest was assembled around it once the pattern "
            f"was visible.",
            f"What follows was pieced together backwards. The last item, {what}, "
            f"was noticed before anyone had a reason to expect it."]))
    else:
        lines.append(_pick(rng, [
            f"Anyone using this system to keep track of something will meet "
            f"{what} early, whether or not they go looking.",
            f"The practical content of this chapter is {what}. It is the part "
            f"that shows up in use."]))
    if incoming:
        lines.append(_pick(rng, [
            f"Nothing here stands on its own. The arguments lean on "
            f"{'chapter' if len(incoming) == 1 else 'chapters'} "
            f"{_join([c + 1 for c in incoming])}, and a reader who has skipped "
            f"{'it' if len(incoming) == 1 else 'them'} will find the derivations "
            f"opaque rather than difficult.",
            f"Prerequisites are real here: "
            f"{'chapter' if len(incoming) == 1 else 'chapters'} "
            f"{_join([c + 1 for c in incoming])} supply the notions the "
            f"statements below are phrased in."]))
    if "refutation" in kinds:
        lines.append(_pick(rng, [
            "Some of what follows is negative. A claim that fails is set out "
            "with the case that breaks it, because knowing which habits do not "
            "carry over is worth as much as knowing which do.",
            "Not every claim in this chapter survives. The ones that do not are "
            "kept, with their counterexamples, rather than quietly dropped."]))
    return _wrap("\n\n".join(lines))


def _sec_definitions(theory, chapter, nodes, rng, register) -> str:
    s = theory.structure
    defs = [n for n in nodes if n.kind == "definition"]
    axioms = [n for n in nodes if n.kind == "axiom"]
    parts = []
    if axioms:
        head = _pick(rng, [
            "These are the laws this system obeys. Each was checked against "
            "every case before it was written down.",
            "The following hold in this system, without exception, and each was "
            "verified by running through the tables in full."])
        body = "\n\n".join(f"{n.node_id}. {n.title.capitalize()}. {n.statement}"
                           for n in axioms)
        parts.append(head + "\n\n" + body)
    for n in defs:
        block = [f"{n.node_id}. {n.title.capitalize()}. {n.statement}"]
        p = n.payload
        if "extension" in p:
            ext = p["extension"]
            if ext:
                block.append(_pick(rng, [
                    f"In this system that picks out {_join(ext)}"
                    + (f", which is {len(ext)} of the {s.size} {s.object_plural}."
                       if len(ext) < s.size else ", that is, all of them."),
                    f"Running the definition over every {s.object_name} leaves "
                    f"{_join(ext)}."]))
            else:
                block.append("In this system nothing satisfies it, which is "
                             "itself a fact worth carrying forward.")
        if "element" in p:
            block.append(f"Here that is {p['element']}.")
        if "map" in p:
            items = list(p["map"].items())[:s.size]
            rendered = "; ".join(
                f"{k} to " + (_join(v) if isinstance(v, list) else str(v))
                for k, v in items)
            block.append(f"Worked out for each {s.object_name}: {rendered}.")
        parts.append("\n\n".join(block))
    if not parts:
        parts.append(_pick(rng, [
            "This chapter introduces no new vocabulary. It works entirely with "
            "what has already been defined.",
            "Nothing new is named here. The chapter is about consequences of "
            "definitions already given."]))
    return _wrap("\n\n".join(parts))


def _sec_intuition(theory, chapter, nodes, rng, register) -> str:
    s = theory.structure
    nm = theory.notion_names
    lines = []
    themes = {n.theme for n in nodes}
    if "collections" in themes:
        sizes = sorted({reach_of(s, i) for i in range(s.size)})
        lines.append(_pick(rng, [
            f"Picture the {nm['span']} as what happens when you start with one "
            f"{s.object_name} and keep folding it against itself and against "
            f"whatever appears, until nothing new appears. Because there are "
            f"only {s.size} {s.object_plural}, that stops. In this system the "
            f"sizes it stops at are {_join(sizes)}.",
            f"The right picture for {nm['span']} is a spreading stain rather "
            f"than a list. Drop one {s.object_name} in, apply the operation to "
            f"whatever is wet, repeat. The stain here reaches {_join(sizes)} "
            f"{s.object_plural} depending on where it started."]))
    if "relation" in themes:
        widths = sorted({len(shadow_of(s, i)) for i in range(s.size)})
        chain = len(set(len(shadow_of(s, i)) for i in range(s.size))) == s.size
        lines.append(_pick(rng, [
            f"The relation is easiest to see as a height. Each {s.object_name} "
            f"casts a {nm['shadow']} over what it {s.rel_name}, and the sizes of "
            f"those shadows here are {_join(widths)}."
            + (" No two are the same size, so the objects line up in a single "
               "file." if chain else " Sizes repeat, so the objects do not line "
               "up in single file."),
            f"Think of {s.rel_glyph} as pointing downhill. The {nm['shadow']} of "
            f"a {s.object_name} is everything downhill of it, and those shadows "
            f"here have sizes {_join(widths)}."]))
    if "operations" in themes:
        core = names(s, ext_core(s))
        steady = names(s, ext_steady(s))
        lines.append(_pick(rng, [
            f"A useful mental split: some {s.object_plural} are inert under the "
            f"operation and some are not. {_join(steady) if steady else 'None of them'} "
            f"come back unchanged when combined with themselves, and "
            f"{_join(core) if core else 'none'} "
            f"{'commute' if core else 'commutes'} with everything.",
            f"Two questions sort the {s.object_plural} quickly. Does combining a "
            f"{s.object_name} with itself change it? "
            f"{'For ' + _join(steady) + ' it does not' if steady else 'It always does'}. "
            f"Does it matter which side it goes on? "
            f"{'For ' + _join(core) + ' it does not' if core else 'It always does'}."]))
    if "neutral" in themes:
        e = s.identity_of(0)
        lines.append(_pick(rng, [
            f"The neutral {s.object_name} {s.name(e) if e is not None else ''} "
            f"is the one that does nothing. That sounds trivial and is not: "
            f"almost every result in this chapter is an argument about what "
            f"doing nothing forces.".replace("  ", " "),
            f"Neutrality is a strong condition disguised as a weak one. It fixes "
            f"a single {s.object_name} and, through that, constrains everything "
            f"that can combine with it."]))
    if "second_operation" in themes and s.has_two_ops:
        lines.append(_pick(rng, [
            f"With two operations the question stops being what each does and "
            f"becomes how they interfere. {s.op_glyphs[1]} binds tighter, so the "
            f"interference shows up whenever a bracket is left off.",
            f"The interesting content of a two operation system sits in the gap "
            f"between them: which one distributes over which, and which "
            f"{s.object_plural} are fixed by both."]))
    if not lines:
        lines.append(_pick(rng, [
            "The picture here is arithmetic in miniature, with the arithmetic "
            "removed. What is left is the bookkeeping, and the bookkeeping is "
            "the point.",
            "There is no geometry to lean on in a system this small. The "
            "intuition has to come from the tables, read as a whole rather than "
            "cell by cell."]))
    return _wrap("\n\n".join(lines))


def _sec_derivation(theory, chapter, nodes, rng, register) -> str:
    results = [n for n in nodes if n.kind in ("theorem", "refutation")]
    if not results:
        return _wrap(_pick(rng, [
            "Nothing is derived in this chapter. It lays down material that "
            "later chapters draw on.",
            "This chapter is groundwork. The derivations that use it start in "
            "the next one."]))
    lines = [_pick(rng, [
        "Each result below is reached from earlier material, and the route is "
        "worth reading before the statement.",
        "The order matters. Each of these leans on what came before it, and the "
        "chain is short enough to hold in mind."])]
    for n in results:
        cited = [theory.nodes[d] for d in n.depends_on]
        if cited:
            lines.append(
                f"{n.node_id} rests on " + _join([f"{c.node_id} ({c.title})"
                                                  for c in cited])
                + _pick(rng, [
                    ". Remove any one of them and the statement stops making "
                    "sense, not merely stops being provable.",
                    ". The dependence is on the content of those results, not "
                    "only on their vocabulary."]))
        else:
            lines.append(f"{n.node_id} stands on the tables alone.")
    return _wrap("\n\n".join(lines))


def _sec_example(theory, chapter, nodes, rng, register) -> tuple:
    """Returns (text, worked_records) so verification can recompute each one."""
    s = theory.structure
    nm = theory.notion_names
    records = []
    lines = []
    depth = 2 if chapter % 2 == 0 else 3
    picks = [rng.choice(s.elements) for _ in range(4)]
    g0 = s.op_glyphs[0]
    if depth == 2 and s.has_two_ops:
        expr = f"{picks[0]} {g0} {picks[1]} {s.op_glyphs[1]} {picks[2]}"
    elif depth == 2:
        expr = f"({picks[0]} {g0} {picks[1]}) {g0} {picks[2]}"
    else:
        expr = f"({picks[0]} {g0} {picks[1]}) {g0} ({picks[2]} {g0} {picks[3]})"
    trace = s.eval_trace(expr)
    value = s.evaluate(expr)
    records.append({"kind": "evaluate", "expression": expr, "value": value,
                    "steps": trace})
    body = [_pick(rng, [
        f"Take {expr} and work it out one step at a time.",
        f"Here is {expr}, reduced without skipping anything.",
        f"Evaluate {expr}. Each line below is one lookup in a table."])]
    for step in trace:
        body.append(f"    {step['expression']} = {step['value']}   ({step['reason']})")
    body.append(_pick(rng, [
        f"So {expr} is {value}.",
        f"The expression comes to {value}.",
        f"That leaves {value}, and no other reading of the notation gives "
        f"anything else."]))
    lines.append("\n".join(body))

    span_nodes = [n for n in nodes if n.key in ("def:span", "def:reach")]
    if span_nodes:
        x = rng.choice(s.elements)
        sp = names(s, span_of(s, s.index[x]))
        records.append({"kind": "span", "element": x, "value": ", ".join(sp)})
        lines.append(_pick(rng, [
            f"A second case, this time a {nm['span']}. Start from {x}. Combine "
            f"it with itself, add whatever is new, and repeat until nothing is "
            f"added. What survives is {_join(sp)}, so the {nm['reach']} of {x} "
            f"is {len(sp)}.",
            f"Now compute [{x}]. Fold {x} against itself, then fold whatever "
            f"appeared against everything present, and stop when a round adds "
            f"nothing. The result is {_join(sp)}, of size {len(sp)}."]))
    return _wrap("\n\n".join(lines)), records


def _sec_counterexample(theory, chapter, nodes, rng, register) -> str:
    s = theory.structure
    refs = [n for n in nodes if n.kind == "refutation"]
    lines = []
    if refs:
        for n in refs[:3]:
            w = n.payload.get("witness") or {}
            detail = ", ".join(f"{k} = {v}" for k, v in w.items()) or "see below"
            lines.append(_pick(rng, [
                f"{n.node_id}. {n.statement} The case that settles it: {detail}. "
                f"Anyone carrying this claim over from a more familiar system "
                f"will be wrong here, and wrong in a way that propagates.",
                f"{n.node_id}. {n.statement} It fails at {detail}. One case is "
                f"enough, and this is the earliest one."]))
    else:
        a, b = rng.choice(s.elements), rng.choice(s.elements)
        g0 = s.op_glyphs[0]
        left, right = s.evaluate(f"{a} {g0} {b}"), s.evaluate(f"{b} {g0} {a}")
        if left != right:
            lines.append(f"A quick guard against a common slip: {a} {g0} {b} is "
                         f"{left} while {b} {g0} {a} is {right}. Order is not "
                         f"decoration in this system.")
        else:
            steady = names(s, ext_steady(s))
            lines.append(_pick(rng, [
                f"Every claim in this chapter survives every case, which is "
                f"unusual enough to be worth saying plainly. The nearest thing "
                f"to a trap is the set of {s.object_plural} that come back "
                f"unchanged from themselves: {_join(steady) if steady else 'none'}. "
                f"Assuming more of them than that is the mistake to avoid.",
                f"No counterexample exists to anything asserted here. That is a "
                f"fact about this system and not a general one, and the next "
                f"chapter is where it stops being true."]))
    return _wrap("\n\n".join(lines))


def _sec_scope(theory, chapter, nodes, rng, register, sibling_report) -> str:
    lines = [_pick(rng, [
        "It is worth being exact about what has been shown and what has not.",
        "The limits of these results are sharper than they look."])]
    axioms_used = sorted({theory.nodes[d].title for n in nodes
                         for d in theory.prerequisites(n.node_id)
                         if theory.nodes[d].kind == "axiom"})
    if axioms_used:
        lines.append(_pick(rng, [
            f"Every result in this chapter is downstream of "
            f"{_join(axioms_used[:4])}. Those are properties of this system, not "
            f"of systems in general.",
            f"The load is carried by {_join(axioms_used[:4])}. A system without "
            f"them is not a system where these results are harder to prove; it "
            f"is a system where they are false."]))
    if sibling_report["broken"]:
        lines.append(_pick(rng, [
            f"That is not a rhetorical caution. Take the same {theory.structure.size} "
            f"objects, the same symbols, and a different table, and "
            f"{_join(sibling_report['broken'][:4])} stop holding. The notation "
            f"survives the substitution and the mathematics does not.",
            f"To see how little the notation guarantees: rebuild the system with "
            f"the same names over different tables and "
            f"{_join(sibling_report['broken'][:4])} fail outright."]))
    else:
        lines.append(_pick(rng, [
            "These particular results happen to survive rebuilding the system "
            "over different tables with the same names, which makes them weaker "
            "tests of understanding than the chapters around them.",
            "Unusually, nothing in this chapter distinguishes this system from "
            "its near neighbours. Take that as a warning about how much a "
            "familiar looking statement can be worth."]))
    return _wrap("\n\n".join(lines))


def _sec_related(theory, chapter, nodes, rng, register) -> str:
    ids = {n.node_id for n in nodes}
    downstream = []
    for nid in theory.order:
        n = theory.nodes[nid]
        if n.node_id in ids:
            continue
        if ids & set(n.depends_on):
            downstream.append(n)
    upstream = sorted({theory.nodes[d] for n in nodes for d in n.depends_on
                       if theory.nodes[d].node_id not in ids},
                      key=lambda n: n.node_id)
    lines = []
    if upstream:
        lines.append(_pick(rng, [
            "Read alongside " + _join([f"{n.node_id} ({n.title})"
                                       for n in upstream[:4]]) + ".",
            "The material this chapter borrows from: "
            + _join([f"{n.node_id} ({n.title})" for n in upstream[:4]]) + "."]))
    if downstream:
        lines.append(_pick(rng, [
            "What is built on it later: "
            + _join([f"{n.node_id} ({n.title})" for n in downstream[:4]]) + ".",
            "These results are used again in "
            + _join([f"{n.node_id} ({n.title})" for n in downstream[:4]]) + "."]))
    if not lines:
        lines.append("This chapter neither borrows from nor feeds another, "
                     "which is rare here and worth noticing.")
    return _wrap("\n\n".join(lines))


def _sec_proof(theory, chapter, nodes, rng, register) -> str:
    results = [n for n in nodes if n.kind in ("theorem", "refutation")]
    if not results:
        return _wrap("No proofs are needed here. Everything asserted is a "
                     "definition or a table entry.")
    blocks = []
    for n in results:
        v = n.payload["verification"]
        head = (f"{n.node_id}. {n.statement}")
        steps = []
        for i, step in enumerate(n.payload.get("proof", []), start=1):
            cite = step["cites"]
            tag = f" [{cite}]" if cite else ""
            steps.append(f"  ({i}){tag} {step['text']}")
        tail = (f"Checked over {v['cases_enumerated']} cases: "
                f"{v['domain']}. The check is exhaustive, so the statement is "
                f"settled rather than supported.")
        blocks.append(head + "\n\n" + "\n".join(steps) + "\n\n" + tail)
    return "\n\n".join(blocks)


def _sec_exercises(theory, chapter, exercises, rng, register) -> str:
    if not exercises:
        return _wrap(_pick(rng, [
            "This chapter carries no exercises. Nothing in it can be asked "
            "about in a way that could not be answered without reading it, and "
            "an exercise like that is worse than none.",
            "No exercises here. Every question this chapter suggested turned "
            "out to be answerable from the question itself, so all of them were "
            "discarded."]))
    by_level: dict = {}
    for ex in exercises:
        by_level.setdefault(ex.level, []).append(ex)
    lines = [_pick(rng, [
        "Exercises, easiest first. Answers are in the key at the back.",
        "The exercises below are graded. Each one needs something from this "
        "chapter that cannot be guessed from the question."])]
    for level in sorted(by_level):
        lines.append(f"Level {level}.")
        for ex in by_level[level]:
            lines.append(f"  {ex.exercise_id}. {ex.prompt}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def _sibling_report(theory: Theory, nodes) -> dict:
    """Which of this chapter's results fail in a rival system with the same names.

    This is what makes the "reach and limits" section a claim rather than a
    posture: the alternative system is built and the same checks are run on it.
    """
    from src.mathgen.theory import THEOREM_CHECKERS
    s = theory.structure
    try:
        sib = s.sibling(1)
    except RuntimeError:
        return {"broken": [], "tested": 0}
    broken = []
    tested = 0
    for n in nodes:
        if n.kind != "theorem" or n.key not in THEOREM_CHECKERS:
            continue
        tested += 1
        try:
            if not THEOREM_CHECKERS[n.key](sib)[0]:
                broken.append(n.node_id)
        except Exception:
            broken.append(n.node_id)
    return {"broken": broken, "tested": tested}


def build_textbook(theory: Theory, exercises: list | None = None) -> Textbook:
    """Render the whole theory. Worked examples are recorded for verification."""
    s = theory.structure
    rng = random.Random(s.seed ^ 0xB00C)
    chapters_map = chapter_nodes(theory)
    by_chapter_ex: dict = {}
    for ex in (exercises or []):
        by_chapter_ex.setdefault(ex.chapter, []).append(ex)

    chapters = []
    for number in sorted(chapters_map):
        nodes = chapters_map[number]
        register = REGISTERS[(s.seed + number) % len(REGISTERS)]
        themes = [n.theme for n in nodes]
        theme = max(set(themes), key=themes.count)
        title = THEME_TITLES.get(theme, "Further results")
        seen_before = sum(1 for c in chapters if c.title.split(" (")[0] == title)
        if seen_before:
            title = f"{title} ({seen_before + 1})"
        sib = _sibling_report(theory, nodes)
        sections = []
        example_text, worked = _sec_example(theory, number, nodes, rng, register)
        writers = {
            "motivation": lambda: _sec_motivation(theory, number, nodes, rng, register),
            "definitions": lambda: _sec_definitions(theory, number, nodes, rng, register),
            "intuition": lambda: _sec_intuition(theory, number, nodes, rng, register),
            "derivation": lambda: _sec_derivation(theory, number, nodes, rng, register),
            "example": lambda: example_text,
            "counterexample": lambda: _sec_counterexample(theory, number, nodes, rng, register),
            "scope": lambda: _sec_scope(theory, number, nodes, rng, register, sib),
            "related": lambda: _sec_related(theory, number, nodes, rng, register),
            "proof": lambda: _sec_proof(theory, number, nodes, rng, register),
            "exercises": lambda: _sec_exercises(theory, number,
                                                by_chapter_ex.get(number, []),
                                                rng, register),
        }
        for i, kind in enumerate(SECTION_ORDER):
            text = writers[kind]()
            sections.append(Section(
                chapter=number, chapter_title=title, index=i, kind=kind,
                title=SECTION_TITLES[kind], text=text,
                node_ids=[n.node_id for n in nodes], register=register))
        if number == 0:
            tables = [render_table(s, k) for k in range(len(s.tables))]
            tables.append(render_relation(s))
            sections.insert(1, Section(
                chapter=0, chapter_title=title, index=1, kind="tables",
                title="The tables in full", text="\n\n".join(tables),
                node_ids=["S2"], register=register))
        chapters.append(Chapter(
            number=number, title=title, register=register, sections=sections,
            node_ids=[n.node_id for n in nodes], worked_examples=worked))

    return Textbook(theory=theory, chapters=chapters,
                    front_matter=build_front_matter(theory, rng))


# ---------------------------------------------------------------------------
# Retrieval chunks
# ---------------------------------------------------------------------------


def chunks(book: Textbook, max_words: int = 220) -> list:
    """Sections, split at a word budget, each carrying where it came from."""
    out = []
    s = book.theory.structure
    out.append({
        "chunk_id": "front-0", "chapter": -1, "chapter_title": "Front matter",
        "section_kind": "front_matter", "section_title": "Front matter",
        "part": 0, "node_ids": ["S1"], "register": "front",
        "system": s.system_name, "text": book.front_matter,
        "words": len(book.front_matter.split()),
    })
    for chapter in book.chapters:
        for section in chapter.sections:
            words = section.text.split()
            n_parts = max(1, (len(words) + max_words - 1) // max_words)
            per = (len(words) + n_parts - 1) // n_parts
            for part in range(n_parts):
                piece = " ".join(words[part * per:(part + 1) * per])
                if not piece:
                    continue
                out.append({
                    "chunk_id": f"c{chapter.number}-{section.kind}-{part}",
                    "chapter": chapter.number,
                    "chapter_title": chapter.title,
                    "section_kind": section.kind,
                    "section_title": section.title,
                    "part": part,
                    "node_ids": section.node_ids,
                    "register": section.register,
                    "system": s.system_name,
                    "text": piece,
                    "words": len(piece.split()),
                })
    return out


def to_markdown(book: Textbook) -> str:
    parts = [f"# The {book.theory.structure.system_name} system", "",
             book.front_matter, ""]
    for chapter in book.chapters:
        parts.append(chapter.to_markdown())
    return "\n".join(parts)
