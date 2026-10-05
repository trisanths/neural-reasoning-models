"""Drive the harness on the mathgen agent's own universes.

src/mathgen/theory.py, textbook.py and exercises.py build a structure, derive
a numbered theory over it, lay that theory out in chapters, write the
textbook, and generate exercises whose answers come from compute(). That is
the same shape src/mathgen/interface.py asks for, under different names, so
this is a translation rather than a reimplementation:

  Node        -> Item, its depends_on becoming deps and its chapter number
                 becoming a chapter id
  Chapter     -> Chapter, its sections becoming the retrievable pages
  Exercise    -> Problem, its target node's dependency closure becoming
                 required_items
  compute()   -> the reference implementation behind reference_solve

Two things the translation does not invent. The levels their generator does
not emit come back empty rather than being filled with something weaker, so
validate_universe names them. And the acquisition battery has no probes for
these universes, because a probe has to know how to fit a reconstructed rule
back onto a reference implementation and that is written per family; the
battery reports no probes rather than scoring token overlap and calling it
acquisition.

  python scripts/run_math_bench.py --fake reader \\
      --universe-module src.mathgen.adapter --seeds 11:15 --out /tmp/b
"""

from __future__ import annotations

import random

from src.mathgen.interface import Chapter, Item, Problem, closure

KIND_MAP = {
    "signature": "notation",
    "axiom": "definition",
    "definition": "definition",
    "theorem": "theorem",
    "refutation": "theorem",
}


def _chapter_id(number: int) -> str:
    return f"ch{number}"


class MathgenUniverse:
    """One of the mathgen agent's universes, wearing the harness's contract."""

    def __init__(self, seed: int, n_siblings: int = 4, variants: int = 3,
                 exclude_section_kinds: tuple = ("exercises",),
                 theory=None, universe_id: str | None = None):
        from src.mathgen.exercises import build_exercises
        from src.mathgen.textbook import build_textbook
        from src.mathgen.theory import build

        self.seed = seed
        # The textbook prints its own exercise prompts, so leaving those
        # sections in the retrievable library would hand a term-overlap
        # retriever the target chapter for free on every problem. They are
        # dropped from what a model can read; nothing else changes.
        self.excluded = tuple(exclude_section_kinds)
        # A universe built around a given theory is a sibling control: it
        # serves pages and answers questions but poses none of its own.
        self.theory = theory if theory is not None else build(seed)
        self.exercises = ([] if theory is not None else
                          build_exercises(self.theory, n_siblings=n_siblings,
                                          variants=variants))
        self.textbook = build_textbook(self.theory, self.exercises)
        self.universe_id = universe_id or f"mathgen-{seed:07d}"

        self.items: dict[str, Item] = {}
        for nid in self.theory.order:
            node = self.theory.nodes[nid]
            self.items[nid] = Item(
                item_id=nid,
                kind=KIND_MAP.get(node.kind, "definition"),
                name=node.title,
                statement=node.statement,
                chapter_id=_chapter_id(node.chapter),
                deps=tuple(node.depends_on),
            )

        by_chapter: dict[int, list[str]] = {}
        for nid in self.theory.order:
            by_chapter.setdefault(self.theory.nodes[nid].chapter, []).append(nid)

        self.chapters: list[Chapter] = []
        for ch in self.textbook.chapters:
            deps = set()
            for nid in by_chapter.get(ch.number, []):
                for dep in self.theory.nodes[nid].depends_on:
                    other = self.theory.nodes[dep].chapter
                    if other != ch.number:
                        deps.add(_chapter_id(other))
            self.chapters.append(Chapter(
                chapter_id=_chapter_id(ch.number),
                index=ch.number + 1,
                title=ch.title,
                pages=tuple(s.text for _, s in self._sections(ch)),
                item_ids=tuple(by_chapter.get(ch.number, [])),
                prereqs=tuple(sorted(deps)),
            ))
        self.by_id = {c.chapter_id: c for c in self.chapters}

        self._problems: dict[int, list[Problem]] = {}
        for ex in self.exercises:
            self._problems.setdefault(ex.level, []).append(self._to_problem(ex))

    # -- contract ---------------------------------------------------------
    def _to_problem(self, ex) -> Problem:
        required = closure([ex.target_node], self.items)
        # Every chapter the derivation touches is a chapter whose removal
        # should stop the reference from answering, so each one is a target
        # the guard ablates on its own.
        targets = sorted({self.items[i].chapter_id for i in required},
                         key=lambda cid: self.by_id[cid].index)
        return Problem(
            problem_id=f"{self.universe_id}-{ex.exercise_id}",
            level=ex.level,
            text=ex.prompt,
            answer=ex.answer,
            required_items=required,
            target_chapters=tuple(targets),
            universe_id=self.universe_id,
            meta={"target_node": ex.target_node, "answer_kind": ex.answer_kind,
                  "recipe": ex.recipe, "necessity": ex.necessity},
        )

    def _sections(self, ch):
        return [(j, s) for j, s in enumerate(ch.sections)
                if s.kind not in self.excluded]

    def library(self) -> list[dict]:
        out = []
        for ch in self.textbook.chapters:
            for j, section in self._sections(ch):
                out.append({
                    "chunk_id": f"ch{ch.number}-s{j}",
                    "chapter_id": _chapter_id(ch.number),
                    "title": section.title,
                    "text": section.text,
                })
        return out

    def chapter_text(self, chapter_ids) -> str:
        wanted = set(chapter_ids)
        parts = []
        for ch in self.textbook.chapters:
            if _chapter_id(ch.number) not in wanted:
                continue
            body = [f"# Chapter {ch.number + 1}. {ch.title}", ""]
            for _, section in self._sections(ch):
                body += [f"## {section.title}", "", section.text, ""]
            parts.append("\n".join(body))
        return "\n\n".join(parts)

    def theory_graph(self) -> dict:
        return {
            "chapters": {c.chapter_id: {"index": c.index, "title": c.title,
                                        "prereqs": list(c.prereqs),
                                        "items": list(c.item_ids)}
                         for c in self.chapters},
            "items": {i.item_id: {"kind": i.kind, "chapter": i.chapter_id,
                                  "deps": list(i.deps)}
                      for i in self.items.values()},
        }

    def reference_solve(self, problem: Problem, allowed_chapter_ids) -> str | None:
        allowed = set(allowed_chapter_ids)
        need = {self.items[i].chapter_id
                for i in closure(problem.required_items, self.items)}
        if not need <= allowed:
            return None
        return problem.answer

    def problems(self, level: int, n: int, rng: random.Random) -> list[Problem]:
        pool = list(self._problems.get(level, []))
        rng.shuffle(pool)
        return pool[:n]

    # -- the sibling control ----------------------------------------------
    def sibling(self, offset: int = 1) -> "MathgenUniverse":
        """The rival system from Structure.sibling, written up as a textbook.

        Structure.sibling keeps the system name, object names, glyphs and
        relation symbol and swaps the tables. The sibling structure is given
        this structure's seed back, because the theory draws its invented
        notion words from the seed; with the seed kept, the sibling's book
        names its notions with the same words this one does, and only what
        the words mean changes.
        """
        import dataclasses

        from src.mathgen.theory import build_theory

        s = self.theory.structure
        sib = dataclasses.replace(s.sibling(offset), seed=s.seed)
        return MathgenUniverse(self.seed, theory=build_theory(sib),
                               exclude_section_kinds=self.excluded,
                               universe_id=f"{self.universe_id}-sib{offset}")

    def reference_answer(self, problem: Problem) -> str | None:
        """The problem's recipe run against this universe's structure."""
        from src.mathgen.exercises import Undefined, compute

        try:
            return compute(self.theory.structure, problem.meta["recipe"])
        except (Undefined, KeyError, IndexError):
            return None

    def matching_chapters(self, problem: Problem, origin, wanted) -> list[str]:
        """This book's chapters that hold the nodes the oracle's chapters hold.

        Two systems with different tables satisfy different axioms, so their
        theories are cut into chapters differently. A node is matched by its
        key (the same notion, axiom or theorem in both books); a chapter of
        the origin with no matched node falls back to the chapter with the
        same number when this book has one.
        """
        out: list[str] = []
        for cid in wanted:
            keys = [origin.theory.nodes[i].key
                    for i in origin.by_id[cid].item_ids]
            mine = []
            for key in keys:
                node = self.theory.by_key(key)
                if node is not None:
                    mine.append(_chapter_id(node.chapter))
            if not mine and cid in self.by_id:
                mine = [cid]
            for c in sorted(set(mine), key=lambda c: self.by_id[c].index):
                if c not in out:
                    out.append(c)
        return out

    # The battery's probes are written against a reference implementation's
    # parameters, and there are none for these families yet.
    acquisition_probes: dict = {}


def build_universe(seed: int, **kwargs) -> MathgenUniverse:
    return MathgenUniverse(seed, **kwargs)
