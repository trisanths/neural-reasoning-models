"""Item-level guarantees: reproducibility, balance, and no shortcuts.

Every claim a generator's docstring makes about why its items cannot be
solved without the faculty they test is checked here against real
generated items, so the contamination argument is executable rather than
prose.
"""

from __future__ import annotations

import pytest

from src.primitives import episode as ep
from src.primitives import (
    common, p1_intent, p2_gap, p3_acquisition, p4_abstraction, p5_composition,
    p6_memory, p7_verification,
)
from src.train.retrieval import BM25Index


# ------------------------------------------------------------------ common

def test_parse_fields_is_lenient_about_shape():
    text = ("  1. goal : G3\n"
            "* CONSTRAINTS = C1, C4\n"
            "- Uncertain -> U2\n"
            "CONFLICT: XNONE\n"
            "success: S1\n"
            "GOAL: G9 (a restatement that must not win)\n")
    f = common.parse_fields(text)
    assert f["GOAL"] == "G3"
    assert f["CONSTRAINTS"] == "C1, C4"
    assert f["CONFLICT"] == "XNONE"
    assert f["SUCCESS"] == "S1"


def test_parse_labels_respects_boundaries_and_ambiguity():
    assert common.parse_labels("C1 and C10", ["C1", "C10"]) == ["C1", "C10"]
    assert common.parse_one_label("G1 or maybe G2", ["G1", "G2"]) is None
    assert common.parse_one_label("g3", ["G1", "G3"]) == "G3"


def test_wilson_brackets_the_point_estimate():
    lo, hi = common.wilson(5, 20)
    assert lo < 0.25 < hi
    assert (0.0, 1.0) == common.wilson(0, 0)
    assert common.wilson(20, 20)[1] == 1.0


def test_proportion_adjusts_for_chance():
    s = common.proportion(10, 20, chance=0.5)
    assert s["acc"] == 0.5
    assert abs(s["adjusted"]) < 1e-9
    assert not s["above_chance"]


# ------------------------------------------------------- reproducibility

@pytest.mark.parametrize("build", [
    lambda: p1_intent.generate(41),
    lambda: p2_gap.generate(41),
    lambda: p3_acquisition.generate(41),
    lambda: p4_abstraction.generate(41),
    lambda: p5_composition.generate(41, "sequential", 3),
    lambda: p5_composition.generate(41, "relational", 3),
    lambda: p5_composition.generate(41, "novel", 3),
    lambda: p6_memory.generate(41, "interfere"),
    lambda: p7_verification.generate(41, "exception", True),
])
def test_generation_is_reproducible(build):
    a, b = build(), build()
    assert a.question == b.question
    assert a.gold == b.gold


def test_episode_is_reproducible():
    a, b = ep.build(41), ep.build(41)
    assert a["archive"] == b["archive"] and a["final"] == b["final"]


# ------------------------------------------------------------ P1 intent

def test_intent_items_survive_every_shortcut_heuristic():
    items = p1_intent.generate_many(30, seed=100)
    for item in items:
        for guard in item.meta["guards"].values():
            assert not guard["any"], item.item_id


def test_intent_conflict_arm_is_balanced():
    items = p1_intent.generate_many(40, seed=200)
    n_conflict = sum(1 for i in items if i.meta["has_conflict"])
    assert 12 <= n_conflict <= 28


def test_intent_gold_is_recovered_by_a_perfect_answer():
    from src.primitives.fakes import _gold_intent
    for mode in ("isolated", "integrated"):
        for item in p1_intent.generate_many(12, seed=300, mode=mode):
            g = p1_intent.grade(item, _gold_intent(item))
            assert g["parsed"]
            assert g["goal"] == 1.0 and g["conflict"] == 1.0
            assert g["success"] == 1.0 and g["constraints"] == 1.0


def test_intent_canonical_options_are_not_lifted_from_the_request():
    for item in p1_intent.generate_many(20, seed=400):
        stem = item.question.split("Goal menu.")[0]
        gold = item.gold
        for lab in gold["constraints"]:
            idx = gold["constraint_labels"].index(lab)
            text = item.question.split("Constraint menu.\n")[1].splitlines()[idx]
            body = text.split(". ", 1)[1].rstrip(".")
            assert body.lower() not in stem.lower()


# --------------------------------------------------------------- P2 gap

def test_gap_page_count_and_stem_do_not_leak_the_arm():
    for seed in range(20):
        a = p2_gap.generate(seed, blocked=True)
        b = p2_gap.generate(seed, blocked=False)
        assert a.meta["n_pages"] == b.meta["n_pages"] == 6
        stem = lambda it: it.question.split("Problem.\n")[1]
        assert stem(a) == stem(b)


def test_gap_arms_and_types_are_balanced():
    items = p2_gap.generate_many(100, seed=0)
    assert sum(1 for i in items if i.meta["blocked"]) == 50
    types = [i.gold["gap"] for i in items if i.meta["blocked"]]
    for label, _ in p2_gap.GAP_MENU:
        assert types.count(label) == 10


def test_gap_ablated_value_is_absent_from_the_manual():
    for item in p2_gap.generate_many(40, seed=7):
        hv = item.gold["hidden_value"]
        if not hv or not item.meta["blocked"]:
            continue
        assert all(hv not in c["text"] for c in item.chunks)


def test_gap_gold_answer_scores_one():
    from src.primitives.fakes import _gold_gap
    for item in p2_gap.generate_many(20, seed=11):
        g = p2_gap.grade(item, _gold_gap(item))
        assert g["detected"] == 1.0 and g["gap"] == 1.0 and g["step"] == 1.0
        assert g["leak_named"] == 0.0


# ------------------------------------------------------- P3 acquisition

def test_acquisition_copy_fails_and_the_oracle_query_wins():
    for variant in ("direct", "recursive"):
        items = p3_acquisition.generate_many(25, seed=5, variant=variant)
        for item in items:
            assert not item.meta["copy_hits"], item.item_id
            assert item.meta["oracle_hits"], item.item_id


def test_acquisition_gold_query_is_scored_correct():
    from src.primitives.fakes import _gold_acq
    for variant in ("direct", "recursive"):
        for item in p3_acquisition.generate_many(15, seed=9, variant=variant):
            follow = (_gold_acq(item, "hop") if variant == "recursive"
                      else None)
            g = p3_acquisition.grade(item, _gold_acq(item, "main"),
                                     followup=follow)
            assert g["hit1"] == 1.0 and g["source"] == 1.0
            if variant == "recursive":
                assert g["hop_hit1"] == 1.0


def test_acquisition_gold_page_is_reached_by_a_key_only_the_note_gives():
    for item in p3_acquisition.generate_many(15, seed=13):
        page = item.meta["docs"][item.gold["first_doc"]]
        assert item.gold["first_query"] in page
        need = item.question.split("What is needed.\n")[-1]
        assert item.gold["first_query"] not in need


def test_acquisition_gold_tier_rotates():
    """A constant gold tier would make source selection meaningless."""
    tiers = {i.meta["target_tier"]
             for i in p3_acquisition.generate_many(30, seed=21)}
    assert len(tiers) >= 3, tiers


def test_intent_conflict_arms_are_balanced_exactly():
    items = p1_intent.generate_many(40, seed=500)
    assert sum(1 for i in items if i.meta["has_conflict"]) == 20


def test_acquisition_echoing_the_request_scores_at_or_below_copy():
    items = p3_acquisition.generate_many(25, seed=17)
    grades = []
    for item in items:
        need = item.question.split("What is needed.\n")[-1]
        grades.append(p3_acquisition.grade(
            item, f"SOURCE: LEDGER\nQUERY: {need}"))
    assert sum(g["hit1"] for g in grades) == 0.0


# ------------------------------------------------------- P4 abstraction

def test_abstraction_labels_are_balanced_and_baselines_sit_at_chance():
    for condition in ("same_surface", "transfer"):
        items = p4_abstraction.generate_many(300, seed=0, condition=condition)
        gold0 = sum(1 for i in items if i.gold["index"] == 0) / len(items)
        copy = sum(i.meta["copy_correct"] for i in items) / len(items)
        maj = sum(i.meta["majority_correct"] for i in items) / len(items)
        assert 0.45 <= gold0 <= 0.55
        assert 0.40 <= copy <= 0.65, (condition, copy)
        assert 0.40 <= maj <= 0.60, (condition, maj)


def test_abstraction_transfer_case_shares_no_label_word_with_the_lesson():
    for item in p4_abstraction.generate_many(20, seed=3, condition="transfer"):
        lesson = item.question.split("Lesson.\n")[1].split("\n\nLegend.")[0]
        for label in item.gold["labels"]:
            assert label not in lesson


def test_abstraction_test_readings_sit_outside_the_taught_range():
    for item in p4_abstraction.generate_many(20, seed=4):
        case = item.question.split("New case.\n")[1]
        nums = [int(x) for x in case.split() if x.isdigit()]
        assert nums and min(nums) > 60


# ------------------------------------------------------- P5 composition

def test_sequential_chain_never_revisits_a_name():
    for k in (1, 2, 3, 4, 5):
        for item in p5_composition.generate_curve(6, "sequential", [k], seed=2):
            seen = [item.meta["start"]] + [s["answer"] for s in item.meta["steps"]]
            assert len(set(seen)) == len(seen)
            assert item.gold["answer"] == seen[-1]


def test_relational_needs_every_clue():
    """All k clues single out one entry; dropping any one leaves at least two."""
    for k in (2, 3, 4):
        for item in p5_composition.generate_curve(4, "relational", [k], seed=2):
            rows = item.meta["rows"]
            clues = item.meta["clues"]
            assert len(clues) == k

            def hits(cs):
                return [n for n, a in rows.items()
                        if all(a[i] == val for i, val in cs)]

            assert hits(clues) == [item.gold["answer"]]
            for drop in range(k):
                rest = [c for i, c in enumerate(clues) if i != drop]
                assert len(hits(rest)) >= 2, (k, drop)


def test_novel_composition_never_shows_two_procedures_together():
    for k in (2, 3, 4):
        for item in p5_composition.generate_curve(4, "novel", [k], seed=2):
            procs = item.meta["proc_names"]
            for lesson in item.meta["lessons"]:
                named = [p for p in procs if p in lesson]
                assert len(named) == 1, named
            assert item.meta["n_unused_procs"] == 2
            assert len(item.meta["lessons"]) == k + 2


def test_novel_chain_never_revisits_a_name():
    for k in (2, 3, 4, 5):
        for item in p5_composition.generate_curve(4, "novel", [k], seed=3):
            seen = [item.meta["start"]] + [s["answer"] for s in item.meta["steps"]]
            assert len(set(seen)) == len(seen)


def test_composition_probes_cover_every_step():
    items = p5_composition.generate_curve(3, "sequential", [4], seed=6)
    probes = p5_composition.probe_items(items)
    assert len(probes) == 12
    assert {p.meta["parent"] for p in probes} == {i.item_id for i in items}


def test_composition_answer_is_one_of_eight_named_candidates():
    for kind in p5_composition.KINDS:
        for item in p5_composition.generate_curve(3, kind, [3], seed=8):
            assert len(item.gold["labels"]) == p5_composition.N_NAMES
            assert item.gold["answer"] in item.gold["labels"]


# ------------------------------------------------------------ P6 memory

def test_memory_every_numeric_option_appears_in_the_transcript():
    for item in p6_memory.generate_many(8, seed=0):
        body = item.chunks[0]["text"]
        for opt in item.gold["labels"]:
            if opt == p6_memory.NOT_STATED:
                continue
            assert opt in body, (item.item_id, opt)


def test_memory_answer_occurs_exactly_once_in_the_transcript():
    for item in p6_memory.generate_many(8, seed=1):
        g = item.gold["answer"]
        if g == p6_memory.NOT_STATED:
            continue
        assert item.chunks[0]["text"].count(g) == 1


def test_memory_far_arm_really_is_farther():
    near = [i for i in p6_memory.generate_many(6, seed=2)
            if i.variant == "retain_near"]
    far = [i for i in p6_memory.generate_many(6, seed=2)
           if i.variant == "retain_far"]
    assert (min(i.meta["n_segments"] for i in far)
            > max(i.meta["n_segments"] for i in near))


def test_memory_voided_episode_answer_is_not_stated():
    for item in p6_memory.generate_many(6, seed=3,
                                        variants=("absent",)):
        assert item.gold["answer"] == p6_memory.NOT_STATED
        assert item.gold["leak"] in item.gold["labels"]


# ------------------------------------------------------ P7 verification

def test_verification_traps_and_controls_are_balanced():
    items = p7_verification.generate_many(20, seed=0)
    traps = sum(1 for i in items if i.gold["trap"])
    assert traps == len(items) // 2


def test_verification_candidate_is_wrong_exactly_on_traps():
    for item in p7_verification.generate_many(20, seed=4):
        wrong = item.gold["candidate"] != item.gold["answer"]
        assert wrong == item.gold["trap"]


def test_verification_always_fail_and_always_pass_both_score_half():
    items = p7_verification.generate_many(40, seed=6)
    for reply in ("CHECK: FAIL\nANSWER: none", "CHECK: PASS\nANSWER: none"):
        grades = [p7_verification.grade(i, reply) for i in items]
        acc = sum(g["detected"] for g in grades) / len(grades)
        assert abs(acc - 0.5) < 1e-9, reply


# ------------------------------------------------------------- episode

def test_no_oracle_block_contains_the_final_answer():
    for seed in range(12):
        spec = ep.build(seed)
        for cond in ep.CONDITIONS:
            item = ep.render(spec, cond)  # raises if a block leaks
            assert item.gold["answer"] == spec["final"]


def test_composition_oracle_supplies_intermediates_only():
    spec = ep.build(3)
    item = ep.render(spec, "oracle_composition")
    block = item.question.split("Intermediate results, supplied.")[1]
    assert spec["m1"] in block
    assert spec["final"] not in block.split("Question.")[0]


def test_acquisition_oracle_reduces_the_archive_to_one_chapter():
    spec = ep.build(3)
    assert ep.render(spec, "none").meta["n_chapters"] == 9
    assert ep.render(spec, "oracle_acquisition").meta["n_chapters"] == 1


def test_episode_candidate_is_always_wrong():
    for seed in range(15):
        spec = ep.build(seed)
        assert spec["candidate"] != spec["final"]


def test_second_table_is_silent_on_the_name_the_chain_reaches():
    for seed in range(10):
        spec = ep.build(seed)
        table = spec["gold_chapter"].split(f"The {spec['step_b']} operation:")[1]
        table = table.split("Two runs")[0]
        assert f"  {spec['m1']} goes to" not in table


# ------------------------------------------------------- the oracle path

def test_bm25_oracle_is_the_training_retriever():
    idx = BM25Index(["alpha beta", "gamma delta"])
    assert idx.top("gamma") == 1
