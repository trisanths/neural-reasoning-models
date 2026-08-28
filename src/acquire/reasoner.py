"""The narrow interface the loop drives, and two reference implementations.

Everything in src/acquire talks to the model through answer_batch, which takes
a question, the documents that are retrievable for it, and the compiled card
that sits in context. Keeping it batch-first matters: the acquisition gate
asks a whole battery at once, and a per-probe call would spend the run's time
in prompt encoding.

Two reference implementations bracket whatever the real policy does.
SymbolicReasoner reads the pages and the card the way the compiler does and
executes the rules exactly; it is the ceiling a perfect reader would reach,
and it is what the tests use so the loop's logic can be checked without a GPU.
ConstantReasoner always says the same word; it is the floor, and it is how the
gate's behaviour on a hopeless model gets measured. The GPU-backed
implementation lives in scripts/acquire_loop.py, because it drags in torch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from src.acquire.gap import evaluate_with_memory, _case_from_question
from src.acquire.skill import SkillMemory


@dataclass
class AnswerRequest:
    """One question, what it can retrieve, and what is already in context."""

    question: str
    documents: list[dict] = field(default_factory=list)
    card: str = ""
    tag: str = ""


class Reasoner(Protocol):
    def answer_batch(self, requests: list[AnswerRequest]) -> list[str]:
        ...


class _Base:
    def answer(self, request: AnswerRequest) -> str:
        return self.answer_batch([request])[0]


class SymbolicReasoner(_Base):
    """A perfect reader. Compiles everything available and runs the rules.

    Reads only page text and the card, exactly as the model would, so it is
    subject to the same necessity: withhold a required definition and it
    returns nothing rather than guessing.
    """

    def __init__(self, target_from_question=None):
        self.target_from_question = target_from_question
        self.calls = 0

    def answer_batch(self, requests: list[AnswerRequest]) -> list[str]:
        out = []
        for req in requests:
            self.calls += 1
            skill = (SkillMemory.load_card(req.card) if req.card
                     else SkillMemory())
            for doc in req.documents:
                skill.absorb(doc)
            skill.focus(_chapter_of(req.question))
            case = _case_from_question(req.question)
            target = _target(req.question, skill)
            value = (evaluate_with_memory(skill, target, case)
                     if target else None)
            out.append(value or "")
        return out


class ConstantReasoner(_Base):
    """Always the same word. The floor, and a way to see what the gate does
    when the model cannot possibly be right."""

    def __init__(self, word: str = "unknown"):
        self.word = word
        self.calls = 0

    def answer_batch(self, requests: list[AnswerRequest]) -> list[str]:
        self.calls += len(requests)
        return [self.word] * len(requests)


class ScriptedReasoner(_Base):
    """Answers from a lookup, falling back to a fixed word. For tests that
    need a model which is right about some things and wrong about others."""

    def __init__(self, answers: dict, fallback: str = "unknown"):
        self.answers = dict(answers)
        self.fallback = fallback
        self.calls = 0
        self.seen: list[str] = []

    def answer_batch(self, requests: list[AnswerRequest]) -> list[str]:
        out = []
        for req in requests:
            self.calls += 1
            self.seen.append(req.question)
            out.append(self.answers.get(req.question, self.fallback))
        return out


def _chapter_of(question: str) -> str:
    import re
    m = re.search(r"\bthe ([A-Z][a-z]+) chapter\b", question)
    return m.group(1) if m else ""


def _target(question: str, skill: SkillMemory) -> str:
    import re
    m = re.search(r"What is its ([a-z]{3,}) value\?", question)
    if m:
        return m.group(1)
    if "final classification" in question and skill.top_term:
        return skill.top_term
    return ""
