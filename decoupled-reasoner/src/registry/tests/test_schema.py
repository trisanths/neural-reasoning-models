import pytest

from src.registry.schema import (Arch, Compute, Metrics, RunRecord,
                                 ValidationError, get_path)


def minimal(**kwargs) -> RunRecord:
    base = dict(run_id="r1", lane="explore", belief_changed="none")
    base.update(kwargs)
    return RunRecord(**base)


def test_minimal_record_validates():
    assert minimal().validate().run_id == "r1"


def test_lane_must_be_known():
    with pytest.raises(ValidationError, match="lane"):
        minimal(lane="wander").validate()


def test_belief_changed_is_required_but_none_is_allowed():
    assert minimal(belief_changed="none").validate()
    with pytest.raises(ValidationError, match="belief_changed"):
        minimal(belief_changed="   ").validate()


def test_run_id_shape():
    with pytest.raises(ValidationError, match="run_id"):
        minimal(run_id="has spaces").validate()


def test_metrics_are_bounded():
    with pytest.raises(ValidationError, match="metrics.reasoning"):
        minimal(metrics=Metrics(reasoning=1.4)).validate()
    with pytest.raises(ValidationError, match="metrics.retrieval_dependency"):
        minimal(metrics=Metrics(retrieval_dependency=-1.5)).validate()


def test_a_string_is_not_a_number():
    with pytest.raises(ValidationError, match="must be a number"):
        minimal(metrics=Metrics(reasoning="0.42")).validate()


def test_retrieval_dependency_is_derived_when_absent():
    record = minimal(metrics=Metrics(acc_correct_evidence=0.68,
                                     acc_wrong_evidence=0.002)).validate()
    assert record.metrics.retrieval_dependency == pytest.approx(0.678)


def test_evidence_lift_is_derived_when_absent():
    record = minimal(metrics=Metrics(acc_correct_evidence=0.68,
                                     acc_no_evidence=0.0)).validate()
    assert record.metrics.evidence_lift == pytest.approx(0.68)


def test_a_dependency_that_disagrees_with_its_parts_is_rejected():
    with pytest.raises(ValidationError, match="disagrees"):
        minimal(metrics=Metrics(acc_correct_evidence=0.68,
                                acc_wrong_evidence=0.002,
                                retrieval_dependency=0.9)).validate()


def test_non_embedding_cannot_exceed_total():
    with pytest.raises(ValidationError, match="params_non_embedding"):
        minimal(arch=Arch(params_total=10, params_non_embedding=11)).validate()


def test_decode_flops_cannot_exceed_full_inference_flops():
    with pytest.raises(ValidationError, match="decode_flops_per_answer"):
        minimal(compute=Compute(decode_flops_per_answer=10.0,
                                inference_flops_per_answer=5.0)).validate()


def test_gpu_utilization_is_a_fraction():
    with pytest.raises(ValidationError, match="gpu_utilization"):
        minimal(compute=Compute(gpu_utilization=97.0)).validate()


def test_round_trip_through_dict():
    record = minimal(
        family="curve",
        arch=Arch(description="24L x 1024d", params_total=375_440_384),
        metrics=Metrics(reading=0.2),
        compute=Compute(train_flops=1.2e19),
    ).validate()
    again = RunRecord.from_dict(record.to_dict())
    assert again.to_dict() == record.to_dict()


def test_unknown_field_is_rejected_on_load():
    blob = minimal().to_dict()
    blob["mystery"] = 1
    with pytest.raises(ValidationError, match="unknown fields"):
        RunRecord.from_dict(blob)


def test_get_path_reads_nested_and_missing():
    record = minimal(metrics=Metrics(reading=0.2))
    assert get_path(record, "metrics.reading") == 0.2
    assert get_path(record, "metrics.nope") is None
    assert get_path(record, "nope.nope") is None
