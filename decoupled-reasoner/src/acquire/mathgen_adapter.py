"""Run the loop against a universe built to src/mathgen/interface.py.

The loop was written against src/acquire/universe.py, whose prose it can
parse sentence by sentence. A different generator writes different sentences,
and the honest question is how much of the loop survives the change.

The answer, module by module:

  lesson.py     survives unchanged. It ranks on the page's kind and its
                lexical fit, and this adapter supplies the kind from the
                structured fields the mathgen textbook already emits.
  curriculum.py survives, on a different extraction. Its grammar-based
                dependency reader finds nothing in mathgen prose, so it falls
                back to mentions: a page depends on a term when it names it
                and does not introduce it. The lexicon of terms comes from
                the library's own index of item names, never from the deps
                field, which is the true edge set and is what the score is
                against.
  gap.py        partly survives. It classifies and it builds a query, but the
                structural description of the objects in hand is written
                against records with attributes, and a mathgen problem hands
                over an expression instead. What it produces there is the
                chapter and the transformation, without the properties.
  selftest.py   does not survive. Its probes come from worked-example pages
                that state a case and its value in a fixed sentence shape.
                mathgen's worked readings are prose inside a definition page.
                The battery reports no probes, and the gate then withholds
                every answer, which is the correct behaviour for a gate that
                cannot test anything but is not a measurement of acquisition.

That last one is a real limitation and not a configuration: a source-derived
battery needs the source to state checkable instances in a recoverable shape.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field


@dataclass
class AdaptedProblem:
    """A mathgen Problem in the shape src/acquire/loop.py drives."""

    qid: str
    chapter: str
    level: int
    notion: str
    phrasing: str
    text: str
    answer: str
    case: dict = field(default_factory=dict)
    required_notions: tuple[str, ...] = ()
    required_pages: tuple[str, ...] = ()
    n_choices: int = 0
    proof: dict = field(default_factory=dict)


class AdaptedChapter:
    """Enough of src/acquire/universe.Chapter for the loop and the score."""

    def __init__(self, name: str, chapter_id: str, edges, nodes, top: str,
                 pages_by_notion: dict):
        self.name = name
        self.chapter_id = chapter_id
        self._edges = edges
        self._nodes = nodes
        self.top = top
        self._pages = pages_by_notion
        self.notions = {n["notion"]: None for n in nodes}

    def theory_graph(self) -> dict:
        return {"chapter": self.chapter_id, "nodes": self._nodes,
                "edges": self._edges, "top": self.top}

    def definition_page(self, notion: str):
        class _P:
            page_id = self._pages.get(notion, "")
        return _P()


def _kind_for(title: str, item_kind: str) -> str:
    """Which learning object this page is, from what the textbook says it is."""
    low = title.lower()
    if low.startswith("a worked") or "worked" in low:
        return "worked_example"
    if low.startswith("scope") or low.startswith("on "):
        return "statement"
    if item_kind in ("notation", "definition", "theorem", "procedure"):
        return "definition"
    return "statement"


def _mentions(text: str, name: str) -> int:
    return len(re.findall(rf"(?<!\w){re.escape(name)}(?!\w)", text))


def adapt(universe, levels=(1, 2, 3, 5), n_per_level: int = 4,
          seed: int = 0) -> tuple[list[dict], list[AdaptedProblem], dict]:
    """Turn a mathgen universe into documents, problems and chapters.

    Every page keeps the item it introduces, which is what lesson.py's whole
    section grouping needs, and the item's kind, which is what its ranking
    needs. Nothing here reads Item.deps.
    """
    items = universe.items
    by_chapter = {ch.chapter_id: ch for ch in universe.chapters}
    documents: list[dict] = []
    pages_by_notion: dict = {}
    notion_of_page: dict = {}

    for ch in universe.chapters:
        chapter_items = [items[i] for i in ch.item_ids]
        for pi, page in enumerate(ch.pages):
            title = page.split("\n")[0].strip()
            best, best_n = None, 0
            for it in chapter_items:
                n = _mentions(page, it.name)
                if n > best_n:
                    best, best_n = it, n
            if best is None and pi < len(chapter_items):
                best = chapter_items[pi]
            notion = best.name if best is not None else None
            kind = _kind_for(title, best.kind if best is not None else "")
            page_id = f"{ch.chapter_id}/p{pi}"
            notion_of_page[page_id] = notion
            if notion and kind == "definition" and notion not in pages_by_notion:
                pages_by_notion[notion] = page_id
            documents.append({
                "text": page, "reliability": 1.0, "page_id": page_id,
                "kind": kind, "chapter": ch.chapter_id, "notion": notion,
                "level": ch.index, "title": title,
                "body": page.split("\n\n", 1)[-1],
            })

    name_of = {i.item_id: i.name for i in items.values()}
    chapters: dict = {}
    for ch in universe.chapters:
        nodes = [{"notion": name_of[i], "level": ch.index, "deps": []}
                 for i in ch.item_ids]
        chapters[ch.chapter_id] = AdaptedChapter(
            name=ch.title, chapter_id=ch.chapter_id, edges=[], nodes=nodes,
            top=name_of[ch.item_ids[-1]] if ch.item_ids else "",
            pages_by_notion=pages_by_notion)

    rng = random.Random(seed)
    problems: list[AdaptedProblem] = []
    for level in levels:
        try:
            batch = universe.problems(level, n_per_level, rng)
        except Exception:
            continue
        for p in batch:
            target_chapter = p.target_chapters[0]
            req_names = tuple(sorted(name_of[i] for i in p.required_items
                                     if i in name_of))
            req_pages = tuple(sorted(
                pages_by_notion[n] for n in req_names if n in pages_by_notion))
            top = chapters[target_chapter].top
            problems.append(AdaptedProblem(
                qid=p.problem_id, chapter=target_chapter, level=level,
                notion=top, phrasing="named", text=p.text,
                answer=str(p.answer), required_notions=req_names,
                required_pages=req_pages,
                n_choices=0,
                proof={"ok": True, "source": "mathgen guard",
                       "checks": {"ablation": True}}))

    # The true edges, for scoring only. The agent never sees this structure;
    # it is read here and handed to score_against after the search has run.
    # A problem at level 6 spans chapters, so every adapted chapter carries the
    # whole universe's graph and score_against restricts it to the subgraph the
    # problem needs. Restricting here instead would score a cross-chapter
    # problem against a fragment of its own prerequisites.
    all_edges = []
    all_nodes = []
    for iid, item in items.items():
        all_nodes.append({"notion": item.name, "level": 0,
                          "deps": [name_of[d] for d in item.deps
                                   if d in name_of]})
        for dep in item.deps:
            if dep in name_of:
                all_edges.append({"prerequisite": name_of[dep],
                                  "notion": item.name})
    for ch in universe.chapters:
        chapters[ch.chapter_id]._edges = all_edges
        chapters[ch.chapter_id]._nodes = all_nodes
        chapters[ch.chapter_id].notions = {n["notion"]: None for n in all_nodes}

    lexicon = sorted({i.name for i in items.values()}, key=len, reverse=True)
    return documents, problems, {"chapters": chapters, "lexicon": lexicon,
                                 "by_chapter": by_chapter}
