"""The dependency-aware searcher.

One retrieval is not a curriculum. A section that answers the question cites
notions the reasoner has never met, and each of those cites more. The search
therefore recurses, but only into what is actually unknown: a notion already
held, and confirmed held by the acquisition gate, is a leaf and its subtree is
never opened.

Dependencies are read out of the retrieved text, by the grammar of the
sentences that state them, and never out of the document record's cites field.
That field holds the generator's true edges. Reading it would turn the
reconstruction into a copy and the score below into a tautology.

The output is data. score_against() compares the constructed graph to the
chapter's true theory graph restricted to the notions the problem actually
needs, which is a direct measure of whether the agent rebuilt the real
prerequisite structure rather than merely fetching enough text to answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.acquire.lesson import LessonIndex
from src.acquire.skill import SkillMemory


@dataclass
class CurriculumNode:
    term: str
    depth: int
    page_id: str
    kind: str
    deps: tuple[str, ...]
    status: str  # acquired | already_known | not_found
    query: str = ""
    requested_by: str = ""

    def to_dict(self) -> dict:
        return {"term": self.term, "depth": self.depth, "page_id": self.page_id,
                "kind": self.kind, "deps": list(self.deps),
                "status": self.status, "requested_by": self.requested_by}


@dataclass
class Curriculum:
    """The constructed prerequisite structure, as data."""

    nodes: list[CurriculumNode] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)
    order: list[str] = field(default_factory=list)
    queries: list[dict] = field(default_factory=list)
    misses: list[str] = field(default_factory=list)

    def terms(self) -> list[str]:
        return [n.term for n in self.nodes]

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [{"prerequisite": a, "notion": b} for a, b in self.edges],
            "order": list(self.order),
            "queries": list(self.queries),
            "misses": list(self.misses),
        }


def build(seed_query: str, index: LessonIndex, skill: SkillMemory,
          known_test=None, max_nodes: int = 8, max_rounds: int = 12,
          chapter: str = "") -> Curriculum:
    """Search from a structural query and recurse into the unknown frontier.

    known_test(term) -> bool decides whether a cited notion needs opening.
    The default answers from the skill memory alone. The loop passes a test
    backed by the acquisition battery, which is the stricter reading of
    "already understood".
    """
    if known_test is None:
        def known_test(term: str) -> bool:
            return skill.covers(term)

    curriculum = Curriculum()
    queue: list[tuple[str, int, str, str]] = [(seed_query, 0, "", "")]
    used_pages: set[str] = set()
    opened: set[str] = set()
    rounds = 0

    while queue and rounds < max_rounds and len(curriculum.nodes) < max_nodes:
        query, depth, requester, wanted = queue.pop(0)
        rounds += 1
        hits = index.retrieve(query, k=1, exclude=used_pages)
        if not hits:
            curriculum.misses.append(query)
            curriculum.queries.append({"query": query, "depth": depth,
                                       "hit": None})
            continue
        section = hits[0]
        pages = section.documents()
        for page in pages:
            used_pages.add(page.get("page_id", ""))
        compiled = [skill.absorb(p) for p in pages]
        head = compiled[0]
        curriculum.queries.append({
            "query": query, "depth": depth, "hit": section.page_id,
            "kind": section.kind, "notion": section.notion,
            "wanted": wanted,
            "on_target": bool(wanted) and section.notion == wanted,
        })
        if head is None:
            curriculum.misses.append(query)
            continue

        if head.kind == "preamble":
            # The preamble is the hop from what a question can say in English
            # to what the chapter calls it. Follow it and keep going.
            if head.top_term and not known_test(head.top_term):
                queue.append((f"Definition of the {head.top_term} value "
                              f"{chapter}", depth + 1, "", head.top_term))
            continue

        term = head.term
        if term in opened:
            continue
        opened.add(term)
        deps = tuple(skill.concepts[term].depends_on) if term in skill.concepts \
            else head.depends_on
        curriculum.nodes.append(CurriculumNode(
            term=term, depth=depth, page_id=section.page_id,
            kind=section.kind, deps=deps, status="acquired", query=query,
            requested_by=requester))
        for d in deps:
            curriculum.edges.append((d, term))
            if known_test(d):
                if d not in opened:
                    opened.add(d)
                    curriculum.nodes.append(CurriculumNode(
                        term=d, depth=depth + 1, page_id="", kind="",
                        deps=tuple(skill.concepts[d].depends_on)
                        if d in skill.concepts else (),
                        status="already_known", requested_by=term))
                continue
            queue.append((f"Definition of the {d} value {chapter}",
                          depth + 1, term, d))

    curriculum.order = teaching_order(curriculum)
    return curriculum


def teaching_order(curriculum: Curriculum) -> list[str]:
    """Prerequisites before what needs them. A cycle, which a text-level
    extraction can produce, degrades to discovery order rather than raising."""
    terms = curriculum.terms()
    incoming = {t: set() for t in terms}
    for a, b in curriculum.edges:
        if a in incoming and b in incoming:
            incoming[b].add(a)
    order: list[str] = []
    remaining = list(terms)
    while remaining:
        ready = [t for t in remaining if not (incoming[t] - set(order))]
        if not ready:
            order.extend(remaining)
            break
        ready.sort(key=lambda t: terms.index(t))
        for t in ready:
            order.append(t)
        remaining = [t for t in remaining if t not in order]
    return order


def score_against(curriculum: Curriculum, theory_graph: dict,
                  required_notions: tuple[str, ...]) -> dict:
    """Compare the constructed structure to the chapter's true one.

    Scored on the subgraph the problem actually needs. Nodes outside it are
    counted as extra rather than as errors, because acquiring a neighbouring
    notion is wasteful but not wrong, and the two failures deserve separate
    numbers.
    """
    need = set(required_notions)
    found = set(curriculum.terms())
    true_edges = {(e["prerequisite"], e["notion"]) for e in theory_graph["edges"]}
    need_edges = {(a, b) for a, b in true_edges if a in need and b in need}
    found_edges = {(a, b) for a, b in curriculum.edges}

    node_hits = found & need
    edge_hits = found_edges & need_edges
    order_index = {t: i for i, t in enumerate(curriculum.order)}
    orderable = [(a, b) for a, b in edge_hits
                 if a in order_index and b in order_index]
    order_ok = sum(1 for a, b in orderable if order_index[a] < order_index[b])

    on_target = [q for q in curriculum.queries if q.get("wanted")]
    return {
        "n_required": len(need),
        "n_found": len(found),
        "node_recall": len(node_hits) / len(need) if need else 0.0,
        "node_precision": len(node_hits) / len(found) if found else 0.0,
        "extra_nodes": sorted(found - need),
        "missed_nodes": sorted(need - found),
        "n_required_edges": len(need_edges),
        "n_found_edges": len(found_edges),
        # A problem needing one notion has no required edges. Scoring that as
        # zero recall would report a failure where there was nothing to find,
        # so an empty requirement is met vacuously and n_required_edges is
        # printed beside it so the vacuous cells stay visible.
        "edge_recall": len(edge_hits) / len(need_edges) if need_edges else 1.0,
        "edge_precision": (len(edge_hits) / len(found_edges)
                           if found_edges else 1.0),
        "order_valid": order_ok / len(orderable) if orderable else 1.0,
        "n_queries": len(curriculum.queries),
        "n_misses": len(curriculum.misses),
        "targeted_query_hit_rate": (
            sum(1 for q in on_target if q["on_target"]) / len(on_target)
            if on_target else 0.0),
    }


def aggregate(scores: list[dict]) -> dict:
    """Means over per-problem scores. Callers report these per level and per
    chapter; nothing here pools across either."""
    if not scores:
        return {}
    keys = ("node_recall", "node_precision", "edge_recall", "edge_precision",
            "order_valid", "targeted_query_hit_rate", "n_found", "n_required",
            "n_queries", "n_misses")
    return {"n": len(scores),
            **{k: sum(float(s.get(k, 0.0)) for s in scores) / len(scores)
               for k in keys}}
