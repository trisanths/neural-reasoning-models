"""The acquisition gate: has this actually been learned, with the page gone?

A model that has a definition in its context and answers correctly has shown
nothing except that it can read. The question the gate asks is narrower: with
the source page no longer retrievable and only the compiled card carried
forward, can the model still answer questions about that notion?

The probes come out of the section itself. Every worked-example page states
three records and the value each takes, so the battery is the page's own
examples with the page then withheld. Nothing here consults the generator's
reference solver, which matters: an oracle-graded gate would be measuring the
benchmark rather than the agent, and could not exist in deployment.

Failure does not route to an answer. It routes to diagnosis and another
search, and whether to search again is decided by learning progress -- did the
last round move the battery score -- and never by the model's confidence in
its own answer. Confidence is not an input to anything in this file, and there
is no parameter through which it could become one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.acquire.reasoner import AnswerRequest
from src.acquire.skill import SkillMemory, compile_section

_EXAMPLE_LINE = re.compile(r"^(.*?)\s+Its ([a-z]{3,}) value is ([a-z]{3,})\.$")


@dataclass
class Probe:
    """One battery item: a record the page stated, and the value it stated."""

    term: str
    question: str
    expected: str
    source_page: str


@dataclass
class BatteryResult:
    term: str
    n: int
    n_correct: int
    score: float
    passed: bool
    wrong: list[tuple[str, str, str]] = field(default_factory=list)
    hidden_pages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"term": self.term, "n": self.n, "n_correct": self.n_correct,
                "score": round(self.score, 4), "passed": self.passed,
                "n_wrong": len(self.wrong),
                "hidden_pages": list(self.hidden_pages)}


def probes_from_pages(pages: list[dict], term: str) -> list[Probe]:
    """Battery items read out of the section's own worked examples."""
    out: list[Probe] = []
    for page in pages:
        sec = compile_section(page)
        if sec is None or sec.kind != "worked_example" or sec.term != term:
            continue
        for case_text, value in sec.examples:
            out.append(Probe(
                term=term,
                question=f"{case_text} What is its {term} value?",
                expected=value, source_page=page.get("page_id", "")))
    return out


def run_battery(reasoner, probes: list[Probe], card: str,
                corpus: list[dict], term: str, threshold: float = 0.67,
                hide_terms: tuple[str, ...] = ()) -> BatteryResult:
    """Ask the battery with the term's own pages taken out of the corpus.

    hide_terms extends what is withheld, so a level-2 notion can be tested
    with every page it depends on withheld too and the card left to carry the
    whole chain.
    """
    hidden = set(hide_terms) | {term}
    visible = [d for d in corpus if d.get("notion") not in hidden]
    hidden_pages = [d.get("page_id", "") for d in corpus
                    if d.get("notion") in hidden]
    if not probes:
        return BatteryResult(term=term, n=0, n_correct=0, score=0.0,
                             passed=False, hidden_pages=hidden_pages)
    requests = [AnswerRequest(question=p.question, documents=visible,
                              card=card, tag=f"battery:{term}")
                for p in probes]
    answers = reasoner.answer_batch(requests)
    wrong = []
    n_correct = 0
    for p, a in zip(probes, answers):
        if _matches(a, p.expected):
            n_correct += 1
        else:
            wrong.append((p.question, p.expected, a))
    score = n_correct / len(probes)
    return BatteryResult(term=term, n=len(probes), n_correct=n_correct,
                         score=score, passed=score >= threshold, wrong=wrong,
                         hidden_pages=hidden_pages)


def _matches(answer: str, expected: str) -> bool:
    """The same normalized containment the RL environment's scorer uses,
    kept local so the gate does not depend on a tokenizer."""
    a = re.sub(r"[^a-z0-9 ]", " ", (answer or "").lower()).split()
    return expected.lower() in a


@dataclass
class Diagnosis:
    """Why the battery failed, and what to search for next."""

    term: str
    reason: str
    query: str
    missing_terms: list[str] = field(default_factory=list)


def diagnose(result: BatteryResult, skill: SkillMemory,
             chapter: str = "") -> Diagnosis:
    """Turn a failed battery into the next search, not into an answer."""
    term = result.term
    if result.n == 0:
        return Diagnosis(term, "no probes: the section carried no worked "
                                "examples to test against",
                         f"Worked examples for the {term} value {chapter}")
    missing = skill.unresolved(term)
    if missing:
        first = missing[0]
        return Diagnosis(term, f"the card cites {first} but holds no rule for it",
                         f"Definition of the {first} value {chapter}", missing)
    c = skill.concepts.get(term)
    if c is None or not c.rules:
        return Diagnosis(term, "the card holds no rule for the term at all",
                         f"Definition of the {term} value {chapter}", [term])
    given = {w for _, _, w in result.wrong if w}
    if given and all(w in c.outputs for w in given):
        return Diagnosis(term, "answers are drawn from the right value set but "
                                "the wrong rule branch is firing",
                         f"Worked examples for the {term} value {chapter}")
    return Diagnosis(term, "answers fall outside the term's stated value set",
                     f"Definition of the {term} value {chapter} {' '.join(c.outputs[:3])}")


class ProgressController:
    """Whether to keep searching, decided by learning progress.

    The only inputs are battery scores. A round that moves the score buys
    another round; a round that does not is a stall, and stalling twice ends
    the search whether or not the model would have felt sure.
    """

    def __init__(self, min_gain: float = 0.05, patience: int = 2,
                 max_rounds: int = 4):
        self.min_gain = min_gain
        self.patience = patience
        self.max_rounds = max_rounds
        self.history: list[float] = []
        self.stalls = 0

    def observe(self, score: float) -> str:
        """Returns continue, stop_passed, stop_stalled or stop_budget."""
        gain = score - (self.history[-1] if self.history else 0.0)
        self.history.append(score)
        if score >= 1.0:
            return "stop_passed"
        if len(self.history) >= self.max_rounds:
            return "stop_budget"
        if gain < self.min_gain:
            self.stalls += 1
            if self.stalls >= self.patience:
                return "stop_stalled"
        else:
            self.stalls = 0
        return "continue"

    def to_dict(self) -> dict:
        return {"history": [round(s, 4) for s in self.history],
                "stalls": self.stalls, "rounds": len(self.history)}


def battery_report(results: list[BatteryResult]) -> dict:
    """Per-term gate outcomes. Never pooled into one number on its own."""
    if not results:
        return {"n_terms": 0, "pass_rate": 0.0, "by_term": {}}
    return {
        "n_terms": len(results),
        "pass_rate": sum(1 for r in results if r.passed) / len(results),
        "mean_score": sum(r.score for r in results) / len(results),
        "by_term": {r.term: r.to_dict() for r in results},
    }
