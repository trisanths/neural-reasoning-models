"""Independent verification of a whole universe, plus the novelty audit.

Nothing here trusts a stored value. Each check recomputes from the reference
implementation and compares against what the universe wrote down, so a bug in
the generator shows up as a verification failure rather than as a plausible
looking textbook.

Six checks run:

* theorems, re-settled by exhaustive enumeration over the carrier;
* worked examples, re-derived step by step, including every intermediate value;
* exercise answers, recomputed from their recipes;
* the necessity witness on every exercise, recomputed against fresh siblings;
* consistency, which confirms the declared axioms all hold in the model, that
  none is also listed as refuted, and that the known implications between them
  are respected;
* the dependency and chapter invariants, which are what the benchmark's
  prerequisite levels rest on.

The novelty audit is separate. It measures how much two universes drawn from
different seeds share, in symbols and in phrasing, and reports the numbers
rather than asserting a threshold.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field

from src.mathgen import algebra, exercises as ex_mod, textbook as tb_mod, theory as th_mod


@dataclass
class Check:
    name: str
    passed: int = 0
    failed: int = 0
    failures: list = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.passed + self.failed

    @property
    def rate(self) -> float:
        return self.passed / self.total if self.total else 1.0

    def record(self, ok: bool, detail: str = ""):
        if ok:
            self.passed += 1
        else:
            self.failed += 1
            if len(self.failures) < 20:
                self.failures.append(detail)

    def to_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "failed": self.failed,
                "total": self.total, "pass_rate": round(self.rate, 6),
                "failures": self.failures}


def verify_theorems(theory) -> Check:
    """Re-settle every stated result by enumerating the carrier again."""
    check = Check("theorems_and_refutations")
    s = theory.structure
    menu = dict(algebra.AXIOM_MENU)
    for nid in theory.order:
        node = theory.nodes[nid]
        if node.kind not in ("theorem", "refutation"):
            continue
        expected = node.kind == "theorem"
        if node.key in th_mod.THEOREM_CHECKERS:
            got = th_mod.THEOREM_CHECKERS[node.key](s)[0]
        elif node.key.startswith("axiom_fails:"):
            got = menu[node.key.split(":", 1)[1]](s)[0]
        else:
            check.record(False, f"{nid} ({node.key}) has no checker")
            continue
        check.record(bool(got) == expected,
                     f"{nid} ({node.key}): stated {expected}, recomputed {got}")
        stored = node.payload["verification"]["result"]
        check.record(stored == expected,
                     f"{nid}: verification record says {stored}")
    return check


def verify_axioms(theory) -> Check:
    """Every declared axiom, re-run over the carrier."""
    check = Check("axioms")
    s = theory.structure
    menu = dict(algebra.AXIOM_MENU)
    for nid in theory.order:
        node = theory.nodes[nid]
        if node.kind != "axiom":
            continue
        name = node.payload["axiom"]
        check.record(menu[name](s)[0] is True, f"{nid}: {name} does not hold")
    return check


def verify_definitions(theory) -> Check:
    """Every definition's extension, recomputed from the tables."""
    check = Check("definition_extensions")
    s = theory.structure
    for nid in theory.order:
        node = theory.nodes[nid]
        if node.kind != "definition":
            continue
        recompute = th_mod.DEFINITION_EXTENSIONS.get(node.key)
        if recompute is None:
            continue
        fresh = recompute(s)
        for field_name, value in fresh.items():
            check.record(node.payload.get(field_name) == value,
                         f"{nid}.{field_name} disagrees with a fresh computation")
    return check


def verify_worked_examples(book) -> Check:
    """Every printed example re-derived, intermediate steps included."""
    check = Check("worked_examples")
    s = book.theory.structure
    for chapter in book.chapters:
        for record in chapter.worked_examples:
            if record["kind"] == "evaluate":
                expr = record["expression"]
                check.record(s.evaluate(expr) == record["value"],
                             f"chapter {chapter.number}: {expr} does not evaluate "
                             f"to {record['value']}")
                fresh = s.eval_trace(expr)
                check.record(fresh == record["steps"],
                             f"chapter {chapter.number}: the steps for {expr} "
                             f"do not reproduce")
            elif record["kind"] == "span":
                fresh = ", ".join(th_mod.names(
                    s, th_mod.span_of(s, s.index[record["element"]])))
                check.record(fresh == record["value"],
                             f"chapter {chapter.number}: span of "
                             f"{record['element']} does not reproduce")
            elif record["kind"] == "relation":
                holds = s.decide(s.index[record["left"]], s.index[record["right"]])
                check.record(("holds" if holds else "fails") == record["value"],
                             f"chapter {chapter.number}: relation case does not "
                             f"reproduce")
    return check


def verify_exercises(theory, exercises) -> Check:
    """Every answer recomputed from its recipe by the reference implementation."""
    check = Check("exercise_answers")
    s = theory.structure
    for ex in exercises:
        try:
            got = ex_mod.compute(s, ex.recipe)
        except ex_mod.Undefined as exc:
            check.record(False, f"{ex.exercise_id}: recipe is undefined ({exc})")
            continue
        check.record(got == ex.answer,
                     f"{ex.exercise_id}: stored {ex.answer!r}, recomputed {got!r}")
    return check


def verify_necessity(theory, exercises) -> Check:
    """Rebuild the sibling comparison for every exercise and re-apply the rules."""
    check = Check("exercise_necessity")
    s = theory.structure
    for ex in exercises:
        fresh = ex_mod.necessity_witness(s, ex)
        check.record(fresh["sibling_answers"] == ex.necessity["sibling_answers"],
                     f"{ex.exercise_id}: sibling answers do not reproduce")
        check.record(ex_mod.passes_necessity(fresh),
                     f"{ex.exercise_id}: no longer passes the necessity rules")
        check.record(not ex_mod._answer_is_copyable(ex.answer, ex.prompt),
                     f"{ex.exercise_id}: the answer is readable off the prompt")
    return check


def verify_consistency(theory) -> Check:
    """No two axioms conflict, and the declaration matches the model."""
    check = Check("axiom_consistency")
    s = theory.structure
    report = algebra.consistency_report(s, theory.profile)
    check.record(report["ok"], "; ".join(report["problems"]))
    declared = {theory.nodes[n].payload["axiom"] for n in theory.order
                if theory.nodes[n].kind == "axiom"}
    refuted = {theory.nodes[n].key.split(":", 1)[1] for n in theory.order
               if theory.nodes[n].kind == "refutation"
               and theory.nodes[n].key.startswith("axiom_fails:")}
    check.record(not (declared & refuted),
                 f"axioms both asserted and refuted: {sorted(declared & refuted)}")
    check.record(declared == set(theory.profile["holds"]),
                 "the chapters declare a different axiom set from the profile")
    return check


def verify_graph(theory) -> Check:
    """Acyclicity, layer arithmetic, and the no forward citation chapter rule."""
    check = Check("dependency_graph")
    for nid in theory.order:
        node = theory.nodes[nid]
        for dep in node.depends_on:
            check.record(dep in theory.nodes, f"{nid} cites unknown {dep}")
            if dep in theory.nodes:
                check.record(theory.nodes[dep].layer < node.layer,
                             f"{nid} cites {dep} at the same or a later layer")
                check.record(theory.nodes[dep].chapter <= node.chapter,
                             f"{nid} in chapter {node.chapter} cites {dep} in "
                             f"chapter {theory.nodes[dep].chapter}")
        for step in node.payload.get("proof", []):
            if step["cites"]:
                allowed = set(node.depends_on) | theory.prerequisites(nid)
                check.record(step["cites"] in allowed,
                             f"{nid} proof cites {step['cites']}, not a prerequisite")
    check.record(theory.depth() >= 4, f"depth is only {theory.depth()}")
    return check


def verify_universe(theory, exercises, book) -> dict:
    """Run every check and return a report with per check pass rates."""
    checks = [
        verify_consistency(theory),
        verify_axioms(theory),
        verify_definitions(theory),
        verify_theorems(theory),
        verify_graph(theory),
        verify_worked_examples(book),
        verify_exercises(theory, exercises),
        verify_necessity(theory, exercises),
    ]
    total_passed = sum(c.passed for c in checks)
    total = sum(c.total for c in checks)
    return {
        "system": theory.structure.system_name,
        "seed": theory.structure.seed,
        "checks": [c.to_dict() for c in checks],
        "all_passed": all(c.failed == 0 for c in checks),
        "assertions_checked": total,
        "assertions_passed": total_passed,
        "pass_rate": round(total_passed / total, 6) if total else 1.0,
    }


# ---------------------------------------------------------------------------
# Novelty audit
# ---------------------------------------------------------------------------

_WORD = re.compile(r"[a-z]+")


def _symbols(theory) -> set:
    s = theory.structure
    return (set(s.elements) | set(s.op_glyphs) | {s.rel_glyph, s.object_name,
                                                  s.system_name.lower()}
            | set(theory.notion_names.values()))


def _ngrams(text: str, n: int = 5) -> set:
    words = _WORD.findall(text.lower())
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def novelty_audit(seed_a: int, seed_b: int, ngram: int = 5) -> dict:
    """Symbol and phrasing overlap between two universes from different seeds.

    Symbol overlap should be near zero: the invented names are drawn per
    universe. Phrasing overlap will not be zero, because the section templates
    are shared on purpose, and hiding that would be worse than reporting it.
    The number to watch is whether phrasing overlap climbs high enough that a
    model could answer by recognising a sentence rather than reading a table.
    """
    ta, tb = th_mod.build(seed_a), th_mod.build(seed_b)
    ba = tb_mod.build_textbook(ta, ex_mod.build_exercises(ta))
    bb = tb_mod.build_textbook(tb, ex_mod.build_exercises(tb))
    text_a, text_b = tb_mod.to_markdown(ba), tb_mod.to_markdown(bb)
    sym_a, sym_b = _symbols(ta), _symbols(tb)
    ng_a, ng_b = _ngrams(text_a, ngram), _ngrams(text_b, ngram)
    words_a = set(_WORD.findall(text_a.lower()))
    words_b = set(_WORD.findall(text_b.lower()))
    return {
        "seed_a": seed_a, "seed_b": seed_b,
        "symbol_overlap": round(_jaccard(sym_a, sym_b), 6),
        "shared_symbols": sorted(sym_a & sym_b),
        "phrase_overlap": round(_jaccard(ng_a, ng_b), 6),
        "ngram_size": ngram,
        "vocabulary_overlap": round(_jaccard(words_a, words_b), 6),
        "answers_overlap": round(_answer_overlap(ta, tb), 6),
        "note": ("Symbol overlap is the number that must stay near zero. Phrase "
                 "overlap reflects shared section templates and is expected to "
                 "be substantial; it only matters if an answer could be "
                 "recovered from a recognised sentence, which the exercise "
                 "necessity check rules out separately."),
    }


def _answer_overlap(theory_a, theory_b) -> float:
    """How often the two universes give the same answer to the same recipe.

    This is the overlap that would actually let a model cheat across universes,
    and it is the one the exercise filter already drives toward zero.
    """
    exs = ex_mod.build_exercises(theory_a)
    if not exs:
        return 0.0
    same = 0
    for ex in exs:
        try:
            if ex_mod.compute(theory_b.structure, ex.recipe) == ex.answer:
                same += 1
        except (ex_mod.Undefined, KeyError):
            continue
    return same / len(exs)


def novelty_sweep(seeds: list, ngram: int = 5) -> dict:
    """Every unordered pair from a seed list, summarised."""
    pairs = [novelty_audit(a, b, ngram) for a, b in itertools.combinations(seeds, 2)]
    def stat(key):
        vals = [p[key] for p in pairs]
        return {"min": round(min(vals), 6), "mean": round(sum(vals) / len(vals), 6),
                "max": round(max(vals), 6)}
    return {
        "pairs": len(pairs),
        "seeds": list(seeds),
        "symbol_overlap": stat("symbol_overlap"),
        "phrase_overlap": stat("phrase_overlap"),
        "vocabulary_overlap": stat("vocabulary_overlap"),
        "answers_overlap": stat("answers_overlap"),
    }
