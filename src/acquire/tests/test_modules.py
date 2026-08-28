"""The five modules, checked without a GPU against the reference reasoners."""

import pytest

from src.acquire import curriculum as curriculum_mod
from src.acquire import selftest
from src.acquire.gap import detect, evaluate_with_memory, _case_from_question
from src.acquire.lesson import LessonIndex
from src.acquire.loop import ABSTAIN, LoopConfig, run_problem, report
from src.acquire.reasoner import (AnswerRequest, ConstantReasoner,
                                  SymbolicReasoner)
from src.acquire.skill import SkillMemory, compile_section, concept_terms
from src.acquire.universe import build_universe


@pytest.fixture(scope="module")
def uni():
    return build_universe(seed=31, n_chapters=3, n_per_level=3)


@pytest.fixture(scope="module")
def docs(uni):
    return uni.documents()


# ------------------------------------------------------------------- skill.py


def test_compile_reads_the_rule_and_the_dependencies(uni, docs):
    ch = uni.chapters[0]
    top = ch.notions[ch.top]
    page = next(d for d in docs
                if d["page_id"] == ch.definition_page(ch.top).page_id)
    sec = compile_section(page)
    assert sec.term == ch.top
    assert sec.kind == "definition"
    assert set(sec.depends_on) == set(top.deps)
    assert set(sec.outputs) <= set(top.outputs)
    assert sec.rules


def test_a_bare_fragment_teaches_nothing(uni, docs):
    ch = uni.chapters[0]
    note = next(d for d in docs
                if d["page_id"] == f"{ch.chapter_id}/{ch.top}/note")
    skill = SkillMemory()
    skill.absorb(note)
    assert not skill.covers(ch.top)


def test_card_round_trips_and_compresses(uni, docs):
    ch = uni.chapters[0]
    skill = SkillMemory()
    for d in docs:
        if d.get("chapter") == ch.chapter_id:
            skill.absorb(d)
    card = skill.render()
    back = SkillMemory.load_card(card)
    assert set(back.concepts) == set(skill.concepts)
    assert back.top_term == skill.top_term
    for term in skill.concepts:
        assert back.concepts[term].depends_on == skill.concepts[term].depends_on
    assert skill.compression()["ratio"] < 0.5


def test_the_card_preserves_the_ability_to_execute(uni, docs):
    ch = uni.chapters[0]
    skill = SkillMemory()
    for d in docs:
        if d.get("chapter") == ch.chapter_id:
            skill.absorb(d)
    back = SkillMemory.load_card(skill.render())
    for prob in ch.problems:
        case = _case_from_question(prob.text)
        assert evaluate_with_memory(back, prob.notion, case) == prob.answer


def test_concept_terms_finds_the_notions_and_not_the_attributes(uni, docs):
    ch = uni.chapters[0]
    page = next(d for d in docs
                if d["page_id"] == ch.definition_page(ch.top).page_id)
    terms = concept_terms(page["text"])
    assert ch.top in terms
    assert set(ch.notions[ch.top].deps) <= terms
    assert not (terms & set(ch.attr_words.values()))


# --------------------------------------------------------------------- gap.py


def test_gap_fires_on_an_empty_memory(uni):
    ch = uni.chapters[0]
    for prob in ch.problems:
        g = detect(prob.text, SkillMemory())
        assert g.fired
        assert g.blockage in ("missing_definition", "missing_prerequisite")
        assert g.transformation
        assert g.query


def test_gap_falls_silent_once_everything_is_held(uni, docs):
    ch = uni.chapters[0]
    skill = SkillMemory()
    for d in docs:
        if d.get("chapter") == ch.chapter_id:
            skill.absorb(d)
    for prob in ch.problems:
        g = detect(prob.text, skill)
        assert not g.fired
        assert g.blockage == "known_computation"


def test_the_unnamed_question_gets_a_structural_description(uni):
    ch = uni.chapters[0]
    unnamed = [p for p in ch.problems if p.phrasing == "unnamed"]
    assert unnamed
    for prob in unnamed:
        g = detect(prob.text, SkillMemory())
        assert g.fired
        assert g.objects
        assert "final classification" in g.transformation
        # The missing notion is not named anywhere in the query, because the
        # agent has no way to name it yet.
        assert ch.top not in g.query


def test_structural_query_climbs_once_intermediates_are_held(uni, docs):
    """The point of the structural description: with level-1 values in hand,
    the query carries terms the level-2 page cites and the raw question does
    not."""
    ch = uni.chapters[0]
    # The unnamed phrasing is the case this exists for: with no name to search
    # on, the query has to be built out of what the agent is holding.
    prob = [p for p in ch.problems
            if p.level == 2 and p.phrasing == "unnamed"][0]
    skill = SkillMemory()
    for d in docs:
        if d.get("chapter") != ch.chapter_id:
            continue
        if d.get("notion") and ch.notions[d["notion"]].level < 2:
            skill.absorb(d)
    g = detect(prob.text, skill)
    assert g.fired
    assert g.known_properties
    holds = {t for t in skill.concepts if skill.resolvable(t)}
    assert any(t in g.query for t in holds)


def test_missing_prerequisite_is_distinguished_from_missing_definition(uni, docs):
    ch = uni.chapters[0]
    top = ch.top
    skill = SkillMemory()
    skill.absorb(next(d for d in docs
                      if d["page_id"] == ch.definition_page(top).page_id))
    prob = [p for p in ch.problems if p.level == 2 and p.phrasing == "named"][0]
    g = detect(prob.text, skill)
    assert g.blockage == "missing_prerequisite"
    assert set(g.missing_terms) <= set(ch.notions)


# ------------------------------------------------------------------ lesson.py


def test_definitions_outrank_bare_fragments(uni, docs):
    ch = uni.chapters[0]
    index = LessonIndex(docs)
    for name in ch.notions:
        sec = index.section_for_term(name, ch.name)
        assert sec is not None
        assert sec.kind == "definition", (name, sec.kind, sec.page_id)
        assert sec.notion == name


def test_turning_off_the_kind_prior_costs_definitions(uni, docs):
    ch = uni.chapters[0]
    plain = LessonIndex(docs, use_kind_prior=False)
    ranked = LessonIndex(docs)
    q = f"the {ch.top} value {ch.name} chapter"
    a = plain.retrieve(q, k=3)
    b = ranked.retrieve(q, k=3)
    assert sum(s.kind == "definition" for s in b) >= \
        sum(s.kind == "definition" for s in a)


def test_a_section_carries_its_worked_examples(uni, docs):
    ch = uni.chapters[0]
    index = LessonIndex(docs)
    sec = index.section_for_term(ch.top, ch.name)
    kinds = {c["kind"] for c in sec.companions}
    assert "worked_example" in kinds


# ---------------------------------------------------------------- selftest.py


def test_probes_come_out_of_the_page_not_the_generator(uni, docs):
    ch = uni.chapters[0]
    probes = selftest.probes_from_pages(docs, ch.top)
    assert len(probes) >= 3
    for p in probes:
        assert p.expected in ch.notions[ch.top].outputs
        assert p.expected not in p.question


def test_the_battery_hides_the_source(uni, docs):
    ch = uni.chapters[0]
    probes = selftest.probes_from_pages(docs, ch.top)
    skill = SkillMemory()
    for d in docs:
        if d.get("chapter") == ch.chapter_id:
            skill.absorb(d)
    card = skill.render()
    res = selftest.run_battery(SymbolicReasoner(), probes, card, docs, ch.top,
                               hide_terms=tuple(ch.notions))
    assert res.passed
    assert all(pid for pid in res.hidden_pages)
    # With the card empty and every page of the chapter withheld, a perfect
    # reader cannot answer, which is what makes the gate informative.
    empty = selftest.run_battery(SymbolicReasoner(), probes, "", docs, ch.top,
                                 hide_terms=tuple(ch.notions))
    assert empty.score == 0.0
    assert not empty.passed


def test_progress_controller_ignores_confidence_and_stops_on_a_stall():
    c = selftest.ProgressController(min_gain=0.1, patience=2, max_rounds=5)
    assert c.observe(0.3) == "continue"
    assert c.observe(0.3) == "continue"      # first stall
    assert c.observe(0.3) == "stop_stalled"  # second stall
    d = selftest.ProgressController(min_gain=0.1, patience=2, max_rounds=5)
    assert d.observe(0.4) == "continue"
    assert d.observe(0.9) == "continue"
    assert d.observe(1.0) == "stop_passed"


def test_diagnosis_routes_to_a_search_not_an_answer(uni, docs):
    ch = uni.chapters[0]
    skill = SkillMemory()
    skill.absorb(next(d for d in docs
                      if d["page_id"] == ch.definition_page(ch.top).page_id))
    probes = selftest.probes_from_pages(docs, ch.top)
    res = selftest.run_battery(ConstantReasoner(), probes, skill.render(),
                               docs, ch.top)
    assert not res.passed
    diag = selftest.diagnose(res, skill, ch.name)
    assert diag.query
    assert diag.missing_terms


# -------------------------------------------------------------- curriculum.py


def test_curriculum_reconstructs_the_required_subgraph(uni, docs):
    ch = uni.chapters[0]
    index = LessonIndex(docs)
    for prob in ch.problems:
        skill = SkillMemory()
        g = detect(prob.text, skill)
        curr = curriculum_mod.build(g.query, index, skill, chapter=ch.name)
        score = curriculum_mod.score_against(curr, ch.theory_graph(),
                                             prob.required_notions)
        assert score["node_recall"] == 1.0, (prob.qid, score)
        assert score["edge_recall"] == 1.0, (prob.qid, score)
        assert score["order_valid"] == 1.0, (prob.qid, score)


def test_curriculum_does_not_read_the_generators_cites_field(uni):
    """Strip the true edges out of the corpus. Nothing may change."""
    ch = uni.chapters[0]
    full = uni.documents()
    stripped = [{k: v for k, v in d.items() if k != "cites"} for d in full]
    prob = [p for p in ch.problems if p.level == 2][0]
    out = []
    for corpus in (full, stripped):
        skill = SkillMemory()
        g = detect(prob.text, skill)
        curr = curriculum_mod.build(g.query, LessonIndex(corpus), skill,
                                    chapter=ch.name)
        out.append(curriculum_mod.score_against(
            curr, ch.theory_graph(), prob.required_notions))
    assert out[0] == out[1]


def test_a_known_frontier_is_not_reopened(uni, docs):
    ch = uni.chapters[0]
    index = LessonIndex(docs)
    prob = [p for p in ch.problems if p.level == 2][0]
    skill = SkillMemory()
    for d in docs:
        if d.get("notion") and d["notion"] in ch.notions \
                and ch.notions[d["notion"]].level == 0:
            skill.absorb(d)
    g = detect(prob.text, skill)
    curr = curriculum_mod.build(g.query, index, skill, chapter=ch.name)
    known = [n for n in curr.nodes if n.status == "already_known"]
    assert known
    assert all(ch.notions[n.term].level == 0 for n in known)


# --------------------------------------------------------------------- loop.py


def test_loop_runs_end_to_end_with_a_perfect_reader(uni, docs):
    ch = uni.chapters[0]
    r = SymbolicReasoner()
    traces = [run_problem(p, ch, docs, r) for p in ch.problems]
    rep = report(traces)
    assert set(rep["by_level"]) == {"0", "1", "2"}
    for level, cell in rep["by_level"].items():
        assert cell["gated_accuracy"] == 1.0, (level, cell)
        assert cell["curriculum"]["node_recall"] == 1.0


def test_the_gate_withholds_every_answer_from_a_hopeless_model(uni, docs):
    ch = uni.chapters[0]
    traces = [run_problem(p, ch, docs, ConstantReasoner("nonsense"))
              for p in ch.problems]
    assert all(t.final_answer == ABSTAIN for t in traces)
    rep = report(traces)
    for cell in rep["by_level"].values():
        assert cell["gate_saved_a_wrong_answer"] == 1.0
        assert cell["gate_withheld_a_right_answer"] == 0.0


def test_ungating_shows_what_the_gate_prevented(uni, docs):
    ch = uni.chapters[0]
    cfg = LoopConfig(gate=False)
    traces = [run_problem(p, ch, docs, ConstantReasoner("nonsense"), cfg)
              for p in ch.problems]
    assert all(t.final_answer != ABSTAIN for t in traces)
    assert all(not t.final_correct for t in traces)


def test_report_never_pools_levels(uni, docs):
    ch = uni.chapters[0]
    traces = [run_problem(p, ch, docs, SymbolicReasoner()) for p in ch.problems]
    rep = report(traces)
    assert "accuracy" not in rep
    assert all("n" in cell for cell in rep["by_level"].values())
