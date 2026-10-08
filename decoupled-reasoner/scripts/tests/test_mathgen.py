"""Tests for the eight-level generator, its guard, and the battery.

The tests worth having here are the ones that would have caught the failures
this project already paid for: a problem whose answer sits in its own
question, a level that silently emits nothing, a reference implementation
that answers a question its target chapter was removed from, and a score that
looks alive because it pooled a live family with a dead one.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from src.mathgen.battery import (PROBES, battery_report, run_battery,
                                 scripted_learner)
from src.mathgen.bench import (BM25, Guard, build_problem_set, extract_answer,
                               is_correct, keyword_nearest_guess,
                               prompt_closed_book, prompt_oracle, score,
                               scripted_parrot, scripted_reader, to_rl_episodes)
from src.mathgen.interface import (LEVELS, closure, load_universe,
                                   validate_universe)

SEEDS = range(500, 504)


@pytest.fixture(scope="module")
def universe():
    return load_universe(500)


@pytest.fixture(scope="module")
def problem_set():
    return build_problem_set(SEEDS, per_level=2)


def test_reference_implementation_agrees_with_its_own_theorems(universe):
    c = universe.calc
    assert c.check_translate_law()
    for x in range(0, c.M, 3):
        for y in range(0, c.M, 5):
            assert c.core(x, y) == c.core(y, x)
    u = c.annihilator()
    values = {c.core(u, y) for y in range(c.M)}
    assert values == {c.annihilator_value()}


def test_unwind_inverts_the_product(universe):
    c = universe.calc
    for x in range(2, c.M, 7):
        if (universe.p.a * x + universe.p.b) % c.M == 0:
            continue
        for y in (1, 4, 30):
            assert c.unwind(x, c.core(x, y % c.M)) == y % c.M


def test_every_level_emits_problems(problem_set):
    by_level = problem_set.by_level()
    for lv in LEVELS:
        assert by_level.get(lv), f"level {lv} emitted nothing"


def test_required_items_are_closed_over_dependencies(problem_set):
    for p in problem_set.problems:
        u = problem_set.universes[p.universe_id]
        assert p.closed_over(u.items)
        assert set(p.required_items) == set(closure(p.required_items, u.items))


def test_ablating_a_target_chapter_makes_the_reference_refuse(problem_set):
    for p in problem_set.problems:
        u = problem_set.universes[p.universe_id]
        allowed = [c.chapter_id for c in u.chapters]
        assert u.reference_solve(p, allowed) == p.answer
        for target in p.target_chapters:
            rest = [c for c in allowed if c != target]
            assert u.reference_solve(p, rest) is None


def test_no_answer_is_copyable_from_its_question(problem_set):
    for p in problem_set.problems:
        u = problem_set.universes[p.universe_id]
        assert Guard(u).check(p).ok


def test_level5_never_names_the_chapter_it_depends_on(problem_set):
    """Prerequisite discovery only means something if the prerequisite is hidden."""
    for p in problem_set.by_level()[5]:
        u = problem_set.universes[p.universe_id]
        need = {u.items[i].chapter_id for i in p.required_items}
        assert "ch2" in need and "ch5" in need
        assert u.by_id["ch5"].prereqs == ("ch2",)
        for iid in u.by_id["ch2"].item_ids:
            assert u.items[iid].name.lower() not in p.text.lower()


def test_level6_needs_an_early_chapter_and_a_late_one(problem_set):
    for p in problem_set.by_level()[6]:
        u = problem_set.universes[p.universe_id]
        idx = sorted(u.by_id[c].index for c in p.target_chapters)
        assert len(idx) == 2 and idx[0] < idx[1]


def test_level8_answer_is_absent_from_the_whole_library(problem_set):
    for p in problem_set.by_level()[8]:
        u = problem_set.universes[p.universe_id]
        corpus = "\n".join(c["text"] for c in u.library())
        assert p.answer not in corpus


def test_guard_refuses_a_problem_whose_answer_is_in_its_question(universe):
    rng = random.Random(0)
    p = universe.problems(2, 1, rng)[0]
    p.text = p.text + f" The answer is {p.answer}."
    assert Guard(universe).check(p).failed == "answer_not_copyable"


def test_guard_refuses_a_problem_that_survives_its_own_ablation(universe):
    rng = random.Random(1)
    p = universe.problems(5, 1, rng)[0]
    # A conductor question needs chapters one, two and five. Claiming it
    # targets the chapter of laws is a claim the ablation refutes.
    p.target_chapters = ("ch3",)
    verdict = Guard(universe).check(p)
    assert verdict.failed == "ablation"
    assert verdict.detail["chapter"] == "ch3"


def test_parrot_scores_zero_at_every_level_and_condition(problem_set):
    result = score(scripted_parrot(problem_set), problem_set)
    for cond, levels in result["per_level"].items():
        for name, entry in levels.items():
            assert entry["accuracy"] == 0.0, (cond, name)


def test_reader_separates_oracle_from_closed_book(problem_set):
    model = scripted_reader(problem_set)
    result = score(model, problem_set, conditions=("closed_book", "oracle"))
    for name, entry in result["per_level"]["oracle"].items():
        assert entry["accuracy"] == 1.0, name
    for name, entry in result["per_level"]["closed_book"].items():
        assert entry["accuracy"] <= 0.25, name


def test_oracle_prompt_carries_every_required_chapter(problem_set):
    for p in problem_set.problems[:20]:
        u = problem_set.universes[p.universe_id]
        text = prompt_oracle(p, u)
        for iid in p.required_items:
            assert u.items[iid].statement.split(".")[0] in text
        assert p.text not in prompt_closed_book(p).split("Problem.")[0]


def test_report_is_not_pooled(problem_set):
    result = score(scripted_parrot(problem_set), problem_set)
    assert "accuracy" not in result
    assert set(result["per_level"]) == {"closed_book", "oracle", "rag",
                                        "acquisition", "sibling", "blank"}
    for cond in result["per_level"]:
        assert len(result["per_level"][cond]) == len(LEVELS)


def test_discards_are_counted_per_level(problem_set):
    for name, entry in problem_set.discards.items():
        assert entry["kept"] + entry["discarded"] == entry["distinct_emitted"]
        assert 0.0 <= entry["discard_rate"] <= 1.0


def test_extract_answer_handles_the_shapes_the_levels_use():
    assert extract_answer("Answer: 42\nmore", "int") == "42"
    assert extract_answer("the answer is 17, obviously", "int") == "17"
    assert extract_answer("Answer: 12,45", "list") == "12,45"
    assert extract_answer("Answer: 43:12", "list") == "43:12"
    assert extract_answer("Answer: 17, 44", "list") == "17,44"
    assert extract_answer("the census is 3, 91 and nothing else", "list") == "3,91"
    assert is_correct("Answer: 7", "7")
    assert not is_correct("Answer: 8", "7")


def test_bm25_prefers_the_chapter_that_names_the_term(universe):
    index = BM25(universe.library())
    top = index.top(universe.p.w_conductor, 1)[0]
    assert top["chapter_id"] == "ch5"


def test_battery_grades_a_learner_and_refuses_a_bluffer(universe):
    good = battery_report(run_battery(scripted_learner(universe), universe, seed=3))
    assert all(good["acquired"].values())
    for taker in (lambda prompt: "Answer: 0",
                  lambda prompt: prompt,
                  lambda prompt: "A"):
        bad = battery_report(run_battery(taker, universe, seed=3))
        assert not any(bad["acquired"].values())


def test_battery_reconstruction_is_semantic_where_it_can_be(universe):
    rows = run_battery(scripted_learner(universe), universe, seed=3)
    recon = {r.item_id: r for r in rows if r.test == "reconstruction"}
    assert recon["i_core"].semantic and recon["i_march"].semantic
    assert not recon["i_conductor"].semantic
    assert "fitted" in recon["i_core"].detail
    assert "token_f1" in recon["i_conductor"].detail


def test_battery_hides_the_source(universe):
    rng = random.Random(0)
    for iid in PROBES:
        probe = PROBES[iid](universe, rng)
        statement = universe.items[iid].statement
        head = " ".join(statement.split()[:8])
        for test, prompt in probe.prompts.items():
            if test == "recognition":
                continue      # the options are meant to contain a paraphrase
            assert head not in prompt, (iid, test)


def test_rl_export_carries_every_problem_and_its_level(problem_set):
    episodes = to_rl_episodes(problem_set)
    assert len(episodes) == len(problem_set.universes)
    seen = 0
    for ep in episodes:
        assert ep["documents"] and ep["n_context"] == 0
        for q in ep["questions"]:
            assert q["answer"] and q["level"] in LEVELS
            assert q["target_chapters"]
            seen += 1
    assert seen == len(problem_set.problems)


def test_guard_refuses_a_problem_the_corpus_prints(universe):
    """A library that carries the question hands retrieval the chapter."""
    rng = random.Random(2)
    p = universe.problems(2, 1, rng)[0]
    guard = Guard(universe)
    assert guard.check(p).ok
    guard.corpus_flat = guard.corpus_flat + " " + " ".join(p.text.split())
    assert guard.check(p).failed == "prompt_in_corpus"


def test_keyword_baseline_answers_when_the_corpus_repeats_the_answer():
    chunks = [{"text": "the value is 7 and again 7 and again 7, also 3"}]
    guess, _ = keyword_nearest_guess(chunks, "int")
    assert guess == "7"


# ---------------------------------------------------------------------------
# the mathgen agent's own universes, through the adapter
# ---------------------------------------------------------------------------
MATHGEN = "src.mathgen.adapter"


@pytest.fixture(scope="module")
def mathgen_universe():
    return load_universe(11, module=MATHGEN)


def test_adapter_meets_the_contract_on_the_levels_it_emits(mathgen_universe):
    report = validate_universe(mathgen_universe)
    live = [lv for lv, entry in report["levels"].items() if entry["ok"]]
    assert live, "the adapter emitted nothing at any level"
    for lv in live:
        assert report["levels"][lv]["ok"]


def test_adapter_keeps_the_textbook_from_printing_its_own_questions(mathgen_universe):
    corpus = " ".join(" ".join(c["text"] for c in mathgen_universe.library()).split())
    rng = random.Random(0)
    for lv in (2, 3, 4, 5):
        for p in mathgen_universe.problems(lv, 50, rng):
            assert " ".join(p.text.split()) not in corpus


def test_adapter_problems_survive_ablation_of_each_required_chapter(mathgen_universe):
    rng = random.Random(1)
    seen = 0
    for lv in (2, 3, 4, 5):
        for p in mathgen_universe.problems(lv, 10, rng):
            seen += 1
            allowed = [c.chapter_id for c in mathgen_universe.chapters]
            assert mathgen_universe.reference_solve(p, allowed) == p.answer
            for target in p.target_chapters:
                rest = [c for c in allowed if c != target]
                assert mathgen_universe.reference_solve(p, rest) is None
    assert seen


def test_controls_behave_on_the_mathgen_universes():
    ps = build_problem_set(range(11, 15), per_level=2, levels=(2, 3, 4, 5),
                           universe_module=MATHGEN)
    assert ps.problems
    reader = score(scripted_reader(ps), ps, conditions=("closed_book", "oracle"))
    for name, entry in reader["per_level"]["oracle"].items():
        assert entry["accuracy"] == 1.0, name
    parrot = score(scripted_parrot(ps), ps)
    for cond, levels in parrot["per_level"].items():
        for name, entry in levels.items():
            assert entry["accuracy"] == 0.0, (cond, name)


def test_battery_reports_no_probes_for_a_universe_without_any(mathgen_universe):
    assert run_battery(lambda prompt: "Answer: 0", mathgen_universe) == []


# --------------------------------------------------------------------------
# the sibling and blank controls
# --------------------------------------------------------------------------
from src.mathgen.bench import (CONTROL_CONDITIONS, prompt_blank, prompt_sibling,
                               served_blank, served_sibling, sibling_of)


@pytest.fixture(scope="module")
def controlled_set():
    return build_problem_set(range(600, 606), per_level=1,
                             controls=CONTROL_CONDITIONS,
                             universe_kwargs={"int_answers": True})


def test_sibling_wears_the_same_words_and_means_something_else(universe):
    sib = sibling_of(universe, 1)
    for field in ("name", "w_reading", "w_pivot", "w_stable", "w_conductor",
                  "w_census", "g_core", "g_join", "g_scale"):
        assert getattr(sib.p, field) == getattr(universe.p, field)
    assert sib.p.modulus != universe.p.modulus
    assert [c.chapter_id for c in sib.chapters] == \
        [c.chapter_id for c in universe.chapters]
    assert sib.chapter_text(["ch2"]) != universe.chapter_text(["ch2"])


def test_reference_answer_reproduces_every_stated_answer(problem_set):
    for p in problem_set.problems:
        u = problem_set.universes[p.universe_id]
        assert u.reference_answer(p) == p.answer, p.problem_id


def test_int_answers_gives_one_number_at_every_level():
    u = load_universe(601, int_answers=True)
    rng = random.Random(0)
    for lv in LEVELS:
        for p in u.problems(lv, 3, rng):
            assert p.answer.isdigit(), (lv, p.answer)
            assert 0 <= int(p.answer) < u.p.modulus
            assert u.reference_answer(p) == p.answer


def test_controls_keep_only_problems_the_sibling_answers_differently(controlled_set):
    assert controlled_set.problems
    for p in controlled_set.problems:
        sib = controlled_set.siblings[p.problem_id]
        assert sib.reference_answer(p) != p.answer


def test_sibling_and_blank_prompts_keep_the_oracle_layout(controlled_set):
    for p in controlled_set.problems:
        u = controlled_set.universes[p.universe_id]
        sib = controlled_set.siblings[p.problem_id]
        oracle, sibling, blank = (prompt_oracle(p, u), prompt_sibling(p, u, sib),
                                  prompt_blank(p, u))
        tail = oracle.split("Problem.\n", 1)[1]
        assert sibling.split("Problem.\n", 1)[1] == tail
        assert blank.split("Problem.\n", 1)[1] == tail
        labels = [c["chapter_id"] for c in served_blank(p, u)]
        assert labels == [c["chapter_id"] for c in served_sibling(p, u, sib)]
        for cid in labels:
            assert f"[{cid}]" in oracle and f"[{cid}]" in blank
        body = blank.split("Problem.\n", 1)[0]
        assert body == "Reference.\n" + "\n\n".join(f"[{c}]" for c in labels) + "\n\n"


def test_blank_pages_carry_no_answer_shaped_token(controlled_set):
    for p in controlled_set.problems:
        u = controlled_set.universes[p.universe_id]
        assert all(c["text"] == "" for c in served_blank(p, u))


def test_check_served_refuses_a_sibling_that_agrees_with_the_gold(universe):
    guard = Guard(universe)
    rng = random.Random(3)
    p = universe.problems(2, 1, rng)[0]
    sib = sibling_of(universe, 1)
    served = served_sibling(p, universe, sib)
    verdict = guard.check_served(p, "sibling", served, p.answer)
    assert not verdict.ok and verdict.failed == "ablation"


def test_check_served_refuses_blank_pages_that_print_the_answer(universe):
    guard = Guard(universe)
    p = universe.problems(5, 1, random.Random(4))[0]
    verdict = guard.check_served(
        p, "blank", [{"chapter_id": "ch5", "text": f"See {p.answer}."}], None)
    assert not verdict.ok


def test_reader_and_parrot_on_the_controls(controlled_set):
    reader = score(scripted_reader(controlled_set), controlled_set,
                   conditions=("closed_book", "oracle", "sibling", "blank"))
    for name, entry in reader["per_level"]["oracle"].items():
        assert entry["accuracy"] == 1.0, name
    # The scripted reader answers whenever the right chapter ids are on the
    # page, so it cannot tell a sibling from the real book. That is the
    # plumbing check: a reader that does not read scores the same on both.
    for name, entry in reader["per_level"]["sibling"].items():
        assert entry["accuracy"] == 1.0, name
    # Blank slots carry the labels and nothing else, and the reader treats
    # an empty slot as missing, so blank lands where closed book does.
    blank = sum(e["accuracy"] * e["n"] for e in reader["per_level"]["blank"].values())
    n = sum(e["n"] for e in reader["per_level"]["blank"].values())
    assert n and blank / n < 0.5
    parrot = score(scripted_parrot(controlled_set), controlled_set,
                   conditions=("closed_book", "oracle", "sibling", "blank"))
    for cond, levels in parrot["per_level"].items():
        for name, entry in levels.items():
            assert entry["accuracy"] == 0.0, (cond, name)


def test_mathgen_sibling_names_its_notions_with_the_same_words(mathgen_universe):
    sib = mathgen_universe.sibling(1)
    assert sib.theory.notion_names == mathgen_universe.theory.notion_names
    s, t = mathgen_universe.theory.structure, sib.theory.structure
    assert s.elements == t.elements and s.op_glyphs == t.op_glyphs
    assert s.tables[0] != t.tables[0]


def test_mathgen_controls_build_and_disagree():
    ps = build_problem_set(range(11, 14), per_level=1, levels=(2, 3, 4, 5),
                           universe_module=MATHGEN, controls=CONTROL_CONDITIONS)
    assert ps.problems
    for p in ps.problems:
        u = ps.universes[p.universe_id]
        sib = ps.siblings[p.problem_id]
        assert u.reference_answer(p) == p.answer
        assert sib.reference_answer(p) != p.answer
        assert served_sibling(p, u, sib)
