import pytest

from src.mathgen import exercises, theory

SEEDS = list(range(14))


def _pairs():
    for seed in SEEDS:
        th = theory.build(seed)
        yield th, exercises.build_exercises(th)


def test_determinism_by_seed():
    for seed in SEEDS[:5]:
        a = [e.to_dict() for e in exercises.build_exercises(theory.build(seed))]
        b = [e.to_dict() for e in exercises.build_exercises(theory.build(seed))]
        assert a == b


def test_every_answer_recomputes_from_the_reference_implementation():
    for th, exs in _pairs():
        assert exs
        for ex in exs:
            assert exercises.compute(th.structure, ex.recipe) == ex.answer


def test_no_answer_can_be_copied_out_of_its_prompt():
    """The registry lesson, enforced. A no-op item must never survive."""
    for _th, exs in _pairs():
        for ex in exs:
            assert ex.necessity["answer_absent_from_prompt"]
            assert not exercises._answer_is_copyable(ex.answer, ex.prompt)


def test_every_exercise_diverges_on_rival_systems():
    for _th, exs in _pairs():
        for ex in exs:
            n = ex.necessity
            assert n["siblings_tested"] >= 1
            assert n["siblings_answering_differently"] >= 1
            assert n["sibling_divergence"] >= 0.5


def test_the_divergence_claim_is_true_when_recomputed():
    """Re-run the sibling comparison rather than trusting the stored number."""
    for th, exs in _pairs():
        s = th.structure
        for ex in exs[:8]:
            fresh = exercises.necessity_witness(s, ex, n_siblings=4)
            assert fresh["sibling_answers"] == ex.necessity["sibling_answers"]
            assert fresh["sibling_divergence"] == ex.necessity["sibling_divergence"]


def test_no_yes_or_no_answers_anywhere():
    for _th, exs in _pairs():
        for ex in exs:
            assert ex.answer_kind in ("object", "object_list", "count")
            assert ex.answer.lower() not in ("yes", "no", "true", "false")
            assert ex.necessity["blind_guess_rate"] <= 0.34


def test_answers_are_well_formed_for_their_kind():
    for th, exs in _pairs():
        s = th.structure
        for ex in exs:
            if ex.answer_kind == "object":
                assert ex.answer in s.elements
            elif ex.answer_kind == "object_list":
                parts = [p.strip() for p in ex.answer.split(",")]
                assert parts and all(p in s.elements for p in parts)
                assert len(set(parts)) == len(parts)
            else:
                assert ex.answer.isdigit() and 1 <= int(ex.answer) <= s.size


def test_levels_are_graded_and_all_of_them_appear():
    seen = set()
    for _th, exs in _pairs():
        for ex in exs:
            assert 1 <= ex.level <= 5
            seen.add(ex.level)
    assert seen == {1, 2, 3, 4, 5}


def test_required_chapters_cover_the_target_and_its_prerequisites():
    for th, exs in _pairs():
        for ex in exs:
            expected = sorted({th.nodes[p].chapter
                               for p in th.prerequisites(ex.target_node)}
                              | {th.nodes[ex.target_node].chapter})
            assert ex.required_chapters == expected
            assert ex.chapter in ex.required_chapters
            assert max(ex.required_chapters) == ex.chapter


def test_counterexample_answers_really_witness_the_failure():
    checked = 0
    for th, exs in _pairs():
        s = th.structure
        for ex in exs:
            if ex.recipe["kind"] != "counterexample":
                continue
            claim = ex.recipe["claim"]
            pred = exercises.FAILURE_WITNESSES[claim]
            i = s.index[ex.answer]
            assert pred(s, i), f"{claim}: {ex.answer} is not a witness"
            for j in range(i):
                assert not pred(s, j), f"{claim}: {s.name(j)} comes earlier"
            checked += 1
    assert checked > 0


def test_solve_answers_are_complete_solution_sets():
    for th, exs in _pairs():
        s = th.structure
        for ex in exs:
            if ex.recipe["kind"] != "solve_left":
                continue
            target = s.index[ex.recipe["target"]]
            right = s.index[ex.recipe["right"]]
            expected = {s.name(i) for i in range(s.size)
                        if s.op(0, i, right) == target}
            assert {p.strip() for p in ex.answer.split(",")} == expected


def test_a_copyable_item_is_rejected():
    """Plant the exact failure the registry audit found, and check it dies."""
    th = theory.build(1)
    s = th.structure
    a = s.elements[0]
    ex = exercises.Exercise(
        exercise_id="planted", level=1, chapter=0, target_node="S2",
        required_chapters=[0],
        prompt=f"Among {a} and {s.elements[1]}, which one is {a}?",
        answer=a, answer_kind="object",
        recipe={"kind": "evaluate", "expr": a})
    witness = exercises.necessity_witness(s, ex)
    assert witness["answer_absent_from_prompt"] is False
    assert not exercises.passes_necessity(witness)


def test_an_item_invariant_across_rival_systems_is_rejected():
    """A question whose answer does not depend on the textbook must not survive."""
    th = theory.build(1)
    s = th.structure
    # The span of an object always contains that object, in every system, so
    # asking how many objects a one element collection has is textbook free.
    ex = exercises.Exercise(
        exercise_id="planted", level=3, chapter=0, target_node="S2",
        required_chapters=[0], prompt="How many objects are named in this system?",
        answer=str(s.size), answer_kind="count", recipe={"kind": "constant"})
    ex.necessity = {
        "answer_absent_from_prompt": True, "siblings_tested": 4,
        "siblings_answering_differently": 0, "sibling_divergence": 0.0,
        "sibling_answers": [str(s.size)] * 4, "guess_space": s.size,
        "blind_guess_rate": 1.0 / s.size,
    }
    assert not exercises.passes_necessity(ex.necessity)


def test_rejected_report_accounts_for_every_candidate():
    th = theory.build(2)
    report = exercises.rejected_report(th)
    assert report["kept"] == len(exercises.build_exercises(th))
    assert sum(report.values()) > report["kept"]
    assert report["copyable"] > 0, "the filter should be doing real work"


def test_breakdown_is_split_by_level_and_chapter_with_no_pooled_score():
    th = theory.build(4)
    exs = exercises.build_exercises(th)
    b = exercises.breakdown(exs)
    assert sum(b["by_level"].values()) == len(exs)
    assert sum(b["by_chapter"].values()) == len(exs)
    assert len(b["by_chapter"]) >= 3
    assert "pooled" in b["note"]


def test_every_universe_hosts_a_usable_number_of_exercises():
    for _th, exs in _pairs():
        assert len(exs) >= 15
        assert len({e.level for e in exs}) >= 3
        assert len({e.chapter for e in exs}) >= 3


def test_undefined_recipes_raise_rather_than_returning_a_wrong_answer():
    th = theory.build(3)
    s = th.structure
    with pytest.raises(exercises.Undefined):
        exercises.compute(s, {"kind": "partner", "element": "notanobject"})
    with pytest.raises(exercises.Undefined):
        exercises.compute(s, {"kind": "evaluate", "expr": "notanobject"})


def test_every_exercise_declares_where_its_answer_comes_from():
    from src.mathgen import textbook
    for th, exs in _pairs():
        prose = textbook.to_markdown(textbook.build_textbook(th))
        for ex in exs:
            assert ex.answer_source in (exercises.STATED, exercises.DERIVED)
            assert ex.answer_source == exercises.answer_source(ex, prose)


def test_the_stated_label_means_the_chapters_really_print_the_answer():
    from src.mathgen import textbook
    for th, exs in _pairs():
        prose = textbook.to_markdown(textbook.build_textbook(th))
        for ex in exs:
            printed = any(p in prose for p in exercises.statement_patterns(ex))
            assert printed == (ex.answer_source == exercises.STATED), \
                f"{ex.exercise_id} ({ex.recipe['kind']})"


def test_a_recipe_that_cannot_be_printed_is_never_labelled_stated():
    """Evaluating, solving and composing are not precomputed anywhere."""
    for _th, exs in _pairs():
        for ex in exs:
            if ex.recipe["kind"] not in exercises.LOOKUP_CANDIDATES:
                assert ex.answer_source == exercises.DERIVED


def test_both_answer_source_families_are_present_and_neither_is_marginal():
    """Pooling these two would reproduce the failure this project already hit."""
    counts = {exercises.STATED: 0, exercises.DERIVED: 0}
    for _th, exs in _pairs():
        for ex in exs:
            counts[ex.answer_source] += 1
    total = sum(counts.values())
    for name, n in counts.items():
        assert n / total >= 0.20, f"{name} is only {n / total:.2f} of the set"


def test_breakdown_crosses_answer_source_with_level():
    th = theory.build(4)
    exs = exercises.build_exercises(th)
    b = exercises.breakdown(exs)
    assert sum(b["by_answer_source"].values()) == len(exs)
    crossed = sum(v for row in b["by_answer_source_and_level"].values()
                  for v in row.values())
    assert crossed == len(exs)
    assert "answer_source" in b["note"]
