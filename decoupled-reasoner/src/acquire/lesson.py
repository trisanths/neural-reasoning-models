"""The learning-object retriever.

BM25 over a corpus does not care what kind of thing a passage is. A fragment
that mentions a term ten times outranks the definition that states its rule
once, and a reasoner that reads the fragment learns the term exists and
nothing else. Our own corpus contains exactly that trap on purpose: every
notion has a bare note whose only content is that the notion is used a lot.

So retrieval here ranks on two things. The lexical score comes from the same
BM25 the training oracle and src/rl/env.py use, which keeps the serving
surface identical to the one the policy was trained against. A prior over the
page's kind then multiplies it, so a definition beats a worked example beats a
chapter preamble beats a bare statement at equal lexical fit.

Whole sections beat fragments in a second sense too. Returning a definition
returns its worked examples with it, as one section, because the examples are
what the acquisition gate in src/acquire/selftest.py tests against and a
definition without them cannot be self-tested at all.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.train.retrieval import BM25Index

# A definition states a rule. A worked example pins it down. A preamble says
# what the chapter is for. A bare statement says a term is used. The gaps are
# wide because the difference in value is wide.
KIND_PRIOR = {
    "definition": 1.00,
    "worked_example": 0.60,
    "preamble": 0.45,
    "statement": 0.12,
}
DEFAULT_PRIOR = 0.5


@dataclass
class LessonSection:
    """One structured learning object, with the companions that complete it."""

    page_id: str
    chapter: str
    notion: str | None
    level: int
    kind: str
    title: str
    body: str
    text: str
    lexical: float
    score: float
    companions: list[dict] = field(default_factory=list)

    def documents(self) -> list[dict]:
        """The section as pages, the head first."""
        head = {"text": self.text, "page_id": self.page_id, "kind": self.kind,
                "title": self.title, "body": self.body, "notion": self.notion,
                "chapter": self.chapter, "level": self.level,
                "reliability": 1.0}
        return [head] + list(self.companions)


class LessonIndex:
    """A ranked view of the corpus that prefers whole structured sections."""

    def __init__(self, documents: list[dict], use_kind_prior: bool = True):
        self.documents = list(documents)
        self.texts = [d["text"] for d in self.documents]
        self.index = BM25Index(
            self.texts,
            reliabilities=[float(d.get("reliability", 1.0))
                           for d in self.documents])
        self.use_kind_prior = use_kind_prior

    def _prior(self, doc: dict) -> float:
        if not self.use_kind_prior:
            return 1.0
        return KIND_PRIOR.get(doc.get("kind", ""), DEFAULT_PRIOR)

    def rank(self, query: str, exclude=()) -> list[tuple[int, float, float]]:
        excluded = set(exclude)
        out = []
        for i, doc in enumerate(self.documents):
            if doc.get("page_id") in excluded or i in excluded:
                continue
            lex = self.index.score(query, i)
            out.append((i, lex, lex * self._prior(doc)))
        out.sort(key=lambda t: (-t[2], t[0]))
        return out

    def retrieve(self, query: str, k: int = 1, exclude=(),
                 whole_section: bool = True) -> list[LessonSection]:
        """Top k sections for a query, each carrying its companion pages."""
        sections: list[LessonSection] = []
        for i, lex, score in self.rank(query, exclude=exclude):
            if len(sections) >= k:
                break
            if score <= 0.0:
                break
            doc = self.documents[i]
            companions = []
            if whole_section and doc.get("notion"):
                companions = [
                    d for j, d in enumerate(self.documents)
                    if j != i and d.get("notion") == doc["notion"]
                    and d.get("chapter") == doc.get("chapter")
                    and d.get("kind") in ("definition", "worked_example")
                    and d.get("page_id") not in set(exclude)
                ]
            sections.append(LessonSection(
                page_id=doc.get("page_id", str(i)),
                chapter=doc.get("chapter", ""), notion=doc.get("notion"),
                level=int(doc.get("level", 0)), kind=doc.get("kind", ""),
                title=doc.get("title", ""), body=doc.get("body", ""),
                text=doc["text"], lexical=float(lex), score=float(score),
                companions=companions))
        return sections

    def section_for_term(self, term: str, chapter: str = "") -> LessonSection | None:
        """The definition of a term, when the agent already has its name.
        Still goes through ranking, so a wrong name retrieves the wrong page
        the way it would in deployment."""
        q = f"Definition of the {term} value"
        if chapter:
            q += f" {chapter} chapter"
        hits = self.retrieve(q, k=1)
        return hits[0] if hits else None


def retrieval_report(sections: list[LessonSection]) -> dict:
    """What kinds of learning object the ranking actually served."""
    kinds: dict[str, int] = {}
    for s in sections:
        kinds[s.kind] = kinds.get(s.kind, 0) + 1
    n = len(sections) or 1
    return {
        "n": len(sections),
        "by_kind": kinds,
        "definition_rate": kinds.get("definition", 0) / n,
        "statement_rate": kinds.get("statement", 0) / n,
        "mean_companions": sum(len(s.companions) for s in sections) / n,
    }
