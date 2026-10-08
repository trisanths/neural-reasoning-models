import pytest

from src.registry import pareto, theory
from src.registry.schema import Arch, Compute, Metrics, RunRecord


def row(run_id, **kwargs) -> dict:
    metrics = Metrics(**kwargs.pop("metrics", {}))
    compute = Compute(**kwargs.pop("compute", {}))
    arch = Arch(**kwargs.pop("arch", {}))
    base = dict(run_id=run_id, lane="explore", belief_changed="none")
    base.update(kwargs)
    return RunRecord(metrics=metrics, compute=compute, arch=arch,
                     **base).validate().to_dict()


def test_dominates_needs_at_least_as_good_everywhere():
    assert pareto.dominates((1.0, 1.0), (0.5, 0.5))
    assert pareto.dominates((1.0, 0.5), (0.5, 0.5))
    assert not pareto.dominates((1.0, 0.1), (0.5, 0.5))
    assert not pareto.dominates((0.5, 0.5), (0.5, 0.5))  # ties do not dominate


def test_minimised_objectives_are_flipped():
    cheap = row("cheap", compute={"decode_flops_per_answer": 1e9})
    dear = row("dear", compute={"decode_flops_per_answer": 1e12})
    objective = pareto.resolve("decode_flops")
    assert objective.score(cheap) > objective.score(dear)


def test_frontier_keeps_the_undominated_and_names_the_dominator():
    rows = [
        row("best", metrics={"reasoning": 0.9},
            compute={"decode_flops_per_answer": 1e9}),
        row("worse", metrics={"reasoning": 0.5},
            compute={"decode_flops_per_answer": 1e10}),
        row("cheaper-but-weaker", metrics={"reasoning": 0.2},
            compute={"decode_flops_per_answer": 1e8}),
    ]
    result = pareto.frontier(
        rows, [pareto.resolve("reasoning"), pareto.resolve("decode_flops")])
    assert {r["run_id"] for r in result["frontier"]} == {"best",
                                                         "cheaper-but-weaker"}
    assert result["dominated"] == [{"run_id": "worse", "dominated_by": "best"}]


def test_rows_missing_an_objective_are_skipped_not_zeroed():
    rows = [
        row("scored", metrics={"reasoning": 0.1},
            compute={"decode_flops_per_answer": 1e12}),
        row("unmeasured", metrics={"reasoning": 0.9}),
    ]
    result = pareto.frontier(
        rows, [pareto.resolve("reasoning"), pareto.resolve("decode_flops")])
    assert [r["run_id"] for r in result["frontier"]] == ["scored"]
    assert result["skipped"] == [{"run_id": "unmeasured",
                                  "missing": ["decode_flops"]}]


def test_ties_are_both_kept_on_the_frontier():
    rows = [row("a", metrics={"reasoning": 0.5}, arch={"params_total": 100}),
            row("b", metrics={"reasoning": 0.5}, arch={"params_total": 100})]
    result = pareto.frontier(
        rows, [pareto.resolve("reasoning"), pareto.resolve("params")])
    assert len(result["frontier"]) == 2


def test_frontier_is_sorted_along_the_first_objective():
    rows = [row("low", metrics={"reasoning": 0.2}, arch={"params_total": 10}),
            row("high", metrics={"reasoning": 0.9}, arch={"params_total": 900})]
    result = pareto.frontier(
        rows, [pareto.resolve("reasoning"), pareto.resolve("params")])
    assert [r["run_id"] for r in result["frontier"]] == ["high", "low"]


def test_unknown_objective_names_are_refused():
    with pytest.raises(KeyError, match="unknown objective"):
        pareto.resolve("vibes")


# -- theory flags ----------------------------------------------------------

def test_a_high_score_with_no_evidence_dependence_contradicts_t2():
    record = row("suspicious", metrics={"reasoning": 0.9,
                                        "acc_correct_evidence": 0.9,
                                        "acc_wrong_evidence": 0.89})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T2-evidence-dependence-is-real" in keys


def test_a_genuine_reader_does_not_contradict_t2():
    record = row("rule-test", metrics={"reasoning": 0.68,
                                       "acc_correct_evidence": 0.68,
                                       "acc_wrong_evidence": 0.002})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T2-evidence-dependence-is-real" not in keys


def test_an_execution_family_that_works_contradicts_t3():
    record = row("rlarith-x", family="rlarith", metrics={"reasoning": 0.4})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T3-execution-over-rules-is-unlearned" in keys


def test_an_execution_family_that_failed_is_consistent_with_t3():
    record = row("rlarith-y", family="rlarith", metrics={"reasoning": 0.0})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T3-execution-over-rules-is-unlearned" not in keys


def test_reading_without_natural_text_contradicts_t1():
    record = row("impossible", data_mixture={"natural": 0.0},
                 metrics={"reading": 0.4})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T1-reading-needs-natural-text" in keys


def test_a_high_score_without_rl_contradicts_t4():
    record = row("pretrain-only", objective="next-token language modelling",
                 metrics={"reasoning": 0.95})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T4-rl-against-verifiers-is-the-lever" in keys


def test_the_same_score_from_grpo_does_not_contradict_t4():
    record = row("rl", objective="GRPO against a programmatic verifier",
                 metrics={"reasoning": 0.95})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T4-rl-against-verifiers-is-the-lever" not in keys


def test_probe_leakage_contradicts_t6():
    record = row("leaky", metrics={"closed_book_probe": 0.48})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T6-knowledge-stays-outside-the-weights" in keys


def test_a_row_with_nothing_measured_contradicts_nothing():
    assert theory.contradictions(row("empty")) == []


def test_frontier_with_flags_marks_rows_to_promote():
    rows = [
        row("clean", objective="GRPO against a verifier",
            metrics={"reasoning": 0.9}, arch={"params_total": 375_440_384}),
        row("huge", objective="GRPO against a verifier",
            metrics={"reasoning": 0.95}, arch={"params_total": 1_300_000_000}),
    ]
    result = pareto.frontier_with_flags(
        rows, [pareto.resolve("reasoning"), pareto.resolve("params")])
    promote = {f["row"]["run_id"]: f["promote"] for f in result["frontier_flagged"]}
    assert promote == {"huge": True, "clean": False}
    assert result["n_promote"] == 1


def test_a_frontier_on_one_suite_is_not_flagged_as_mixed():
    rows = [row("a", reasoning_suite="heldout_worlds",
                metrics={"reasoning": 0.9}, arch={"params_total": 100}),
            row("b", reasoning_suite="heldout_worlds",
                metrics={"reasoning": 0.5}, arch={"params_total": 10})]
    result = pareto.frontier_with_flags(
        rows, [pareto.resolve("reasoning"), pareto.resolve("params")])
    assert result["suites_mixed"] is False
    assert result["frontier_suites"] == ["heldout_worlds"]


def test_a_frontier_mixing_suites_says_so():
    rows = [row("pretrain", reasoning_suite="heldout_worlds",
                metrics={"reasoning": 0.9}, arch={"params_total": 100}),
            row("rl", reasoning_suite="rl_episodes:skillacq",
                metrics={"reasoning": 0.5}, arch={"params_total": 10})]
    result = pareto.frontier_with_flags(
        rows, [pareto.resolve("reasoning"), pareto.resolve("params")])
    assert result["suites_mixed"] is True
    assert len(result["frontier_suites"]) == 2


def test_a_row_with_no_suite_reads_as_unrecorded_not_as_a_match():
    rows = [row("a", metrics={"reasoning": 0.9}, arch={"params_total": 100})]
    result = pareto.frontier_with_flags(
        rows, [pareto.resolve("reasoning"), pareto.resolve("params")])
    assert result["frontier_suites"] == ["unrecorded"]


def test_suites_are_not_reported_when_reasoning_is_not_on_an_axis():
    rows = [row("a", reasoning_suite="heldout_worlds",
                metrics={"reading": 0.2}, arch={"params_total": 100})]
    result = pareto.frontier_with_flags(
        rows, [pareto.resolve("reading"), pareto.resolve("params")])
    assert result["suites_mixed"] is False
    assert result["frontier_suites"] == []


def test_a_pooled_score_built_only_from_non_arithmetic_items_is_consistent_with_t3():
    record = row("rlarith-calc-931", family="rlarith",
                 metrics={"reasoning": 0.156},
                 detail={"per_domain": {
                     "skill_binary_op": {"n": 45, "correct": 0, "accuracy": 0.0},
                     "skill_units": {"n": 45, "correct": 0, "accuracy": 0.0},
                     "skill_procedure": {"n": 30, "correct": 14,
                                         "accuracy": 0.467}}})
    verdicts = {c["key"]: c for c in theory.evaluate(record)}
    claim = verdicts["T3-execution-over-rules-is-unlearned"]
    assert claim["verdict"] == theory.CONSISTENT
    assert "skill_binary_op 0.000" in claim["reason"]


def test_real_arithmetic_progress_still_contradicts_t3():
    record = row("rlarith-future", family="rlarith",
                 metrics={"reasoning": 0.4},
                 detail={"per_domain": {
                     "skill_binary_op": {"n": 45, "correct": 18,
                                         "accuracy": 0.4}}})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T3-execution-over-rules-is-unlearned" in keys


def test_without_a_per_domain_split_a_pooled_score_still_contradicts_t3():
    record = row("rlarith-nodetail", family="rlarith",
                 metrics={"reasoning": 0.4})
    keys = [c["key"] for c in theory.contradictions(record)]
    assert "T3-execution-over-rules-is-unlearned" in keys
