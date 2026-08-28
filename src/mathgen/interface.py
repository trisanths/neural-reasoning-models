"""The contract a generated universe must satisfy to be benchmarked.

src/mathgen/bench.py never touches the mathematics of a universe. It asks a
universe for chapters, for a theory graph, for problems at a level, and for a
reference answer under an ablation. Any generator that answers those four
questions can be scored by the same harness.

The universe generator (src/mathgen/universe.py, owned by the mathgen agent)
was not on disk when this was written, so src/mathgen/refuniverse.py supplies
a reference universe implementing this contract and the harness is exercised
against it. When universe.py lands, point load_universe at it with
--universe-module and nothing else changes.

The contract, in one place:

  Item      an atom of theory. item_id, kind in {notation, definition,
            theorem, procedure}, name, statement (the prose the corpus
            carries), chapter_id, deps (item_ids it is stated in terms of).

  Chapter   chapter_id, index (reading order), title, pages (list of str),
            item_ids, prereqs (chapter_ids). The pages are the retrievable
            corpus; nothing outside pages is visible to a model.

  Universe  universe_id, chapters, items, theory_graph, and two methods:

              problems(level, n, rng) -> list[Problem]
              reference_solve(problem, allowed_chapter_ids) -> str | None

            reference_solve returns the answer only when every chapter the
            problem's derivation depends on is in allowed_chapter_ids, and
            None otherwise. That is what makes the ablation guard mean
            something: a problem that still answers with its target chapter
            removed is not testing that chapter.

  Problem   problem_id, level (1..8), text, answer, required_items,
            target_chapters (the chapters the level is about, each ablated
            separately by the guard), search_required (True when the
            reference solution scans the carrier rather than deriving), and
            meta.

A universe must also guarantee that required_items is closed under deps.
Problem.closed_over checks it, and the guard refuses a problem that fails.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

ITEM_KINDS = ("notation", "definition", "theorem", "procedure")
LEVELS = (1, 2, 3, 4, 5, 6, 7, 8)

LEVEL_NAMES = {
    1: "new_notation",
    2: "new_definitions",
    3: "new_theorem",
    4: "new_proof_technique",
    5: "prerequisite_discovery",
    6: "cross_chapter_composition",
    7: "not_explicitly_stated",
    8: "open",
}


@dataclass(frozen=True)
class Item:
    item_id: str
    kind: str
    name: str
    statement: str
    chapter_id: str
    deps: tuple[str, ...] = ()


@dataclass(frozen=True)
class Chapter:
    chapter_id: str
    index: int
    title: str
    pages: tuple[str, ...]
    item_ids: tuple[str, ...]
    prereqs: tuple[str, ...] = ()

    @property
    def text(self) -> str:
        return "\n\n".join(self.pages)


@dataclass
class Problem:
    problem_id: str
    level: int
    text: str
    answer: str
    required_items: tuple[str, ...]
    target_chapters: tuple[str, ...]
    universe_id: str
    search_required: bool = False
    meta: dict = field(default_factory=dict)

    def required_chapters(self, items: dict[str, Item]) -> set[str]:
        return {items[i].chapter_id for i in self.required_items}

    def closed_over(self, items: dict[str, Item]) -> bool:
        """True when required_items already contains every dependency."""
        have = set(self.required_items)
        for iid in self.required_items:
            for dep in items[iid].deps:
                if dep not in have:
                    return False
        return True


def closure(item_ids, items: dict[str, Item]) -> tuple[str, ...]:
    """Every item reachable from item_ids through deps, itself included."""
    seen: set[str] = set()
    stack = list(item_ids)
    while stack:
        iid = stack.pop()
        if iid in seen:
            continue
        seen.add(iid)
        stack.extend(items[iid].deps)
    return tuple(sorted(seen))


@runtime_checkable
class UniverseLike(Protocol):
    universe_id: str
    chapters: list
    items: dict

    def theory_graph(self) -> dict: ...

    def problems(self, level: int, n: int, rng) -> list: ...

    def reference_solve(self, problem, allowed_chapter_ids) -> str | None: ...


def load_universe(seed: int, module: str | None = None, **kwargs):
    """Build a universe from the mathgen generator, or from the reference one.

    module names an importable module exposing build_universe(seed, **kwargs).
    With module None the reference universe is used and the caller is told
    which one it got through Universe.universe_id.
    """
    if module:
        import importlib

        mod = importlib.import_module(module)
        return mod.build_universe(seed, **kwargs)
    from src.mathgen.refuniverse import build_universe

    return build_universe(seed, **kwargs)
