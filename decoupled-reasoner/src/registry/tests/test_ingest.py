import json

import pytest

from src.registry import ingest


def write_jsonl(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


@pytest.fixture
def rl_dir(tmp_path):
    run = tmp_path / "rl-demo"
    run.mkdir()
    write_jsonl(run / "rl.jsonl", [
        {"step": 1, "elapsed_s": 4.2, "n_rollouts": 64, "train_tokens": 415.0,
         "accuracy": 0.42, "reward_std": 0.49},
        {"step": 2, "elapsed_s": 9.9, "n_rollouts": 64, "train_tokens": 585.0,
         "accuracy": 0.55, "reward_std": 0.40},
    ])
    write_jsonl(run / "eval.jsonl", [
        {"tag": "before", "step": 0, "accuracy": 0.4479, "n_rollouts": 96,
         "elapsed_s": 8.93, "mean_generated": 10.71875, "any_retrieval": 0.885},
        {"tag": "step000100", "step": 100, "accuracy": 0.99, "n_rollouts": 96,
         "elapsed_s": 6.41, "mean_generated": 13.0, "any_retrieval": 1.0},
        {"tag": "after", "step": 200, "accuracy": 0.8541, "n_rollouts": 96,
         "elapsed_s": 7.0, "mean_generated": 15.6667, "any_retrieval": 1.0},
    ])
    return run


def test_rl_run_prefers_the_after_tag_over_the_best_score(rl_dir):
    facts = ingest.rl_run_facts(rl_dir)
    assert facts["detail"]["final_tag"] == "after"
    assert facts["metrics"]["reasoning"] == pytest.approx(0.8541)
    assert facts["detail"]["accuracy_best"] == pytest.approx(0.99)
    assert facts["detail"]["accuracy_before"] == pytest.approx(0.4479)


def test_rl_run_without_an_after_tag_falls_back_to_the_highest_step(rl_dir):
    rows = [json.loads(line) for line in
            (rl_dir / "eval.jsonl").read_text().strip().split("\n")]
    write_jsonl(rl_dir / "eval.jsonl", [r for r in rows if r["tag"] != "after"])
    facts = ingest.rl_run_facts(rl_dir)
    assert facts["detail"]["final_tag"] == "step000100"


def test_rl_run_sums_train_tokens_and_takes_the_last_wall_clock(rl_dir):
    facts = ingest.rl_run_facts(rl_dir)
    assert facts["raw"]["train_tokens"] == pytest.approx(1000.0)
    assert facts["compute"]["wall_clock_s"] == pytest.approx(9.9)


def test_rl_latency_is_eval_wall_clock_over_rollouts(rl_dir):
    facts = ingest.rl_run_facts(rl_dir)
    assert facts["compute"]["latency_s_per_answer"] == pytest.approx(7.0 / 96)


def test_rl_decode_flops_needs_a_parameter_count(rl_dir):
    assert ingest.rl_run_facts(rl_dir)["compute"]["decode_flops_per_answer"] is None
    with_params = ingest.rl_run_facts(rl_dir, params_non_embedding=308_331_520)
    assert with_params["compute"]["decode_flops_per_answer"] == pytest.approx(
        2 * 308_331_520 * 15.6667)


def test_an_empty_run_directory_yields_nulls_not_zeros(tmp_path):
    facts = ingest.rl_run_facts(tmp_path)
    assert facts["metrics"]["reasoning"] is None
    assert facts["compute"]["wall_clock_s"] is None
    assert facts["sources"] == []


def test_ablation_reads_both_spellings_of_the_empty_condition(tmp_path):
    for empty_key in ("no_documents", "no_textbook"):
        path = tmp_path / f"{empty_key}.json"
        path.write_text(json.dumps({
            "checkpoint": "/x/rl-000250.pt",
            "conditions": {
                "textbook": {"accuracy": 0.68, "n_rollouts": 500,
                             "mean_generated": 25.36},
                "wrong_textbook": {"accuracy": 0.002},
                empty_key: {"accuracy": 0.0},
            }}))
        facts = ingest.read_ablation(path)
        assert facts["metrics"]["retrieval_dependency"] == pytest.approx(0.678)
        assert facts["metrics"]["acc_no_evidence"] == 0.0
        assert facts["metrics"]["novel_system_acquisition"] == 0.68


def test_ablation_without_a_wrong_condition_leaves_dependency_null(tmp_path):
    path = tmp_path / "a.json"
    path.write_text(json.dumps({"conditions": {
        "textbook": {"accuracy": 0.5}, "no_documents": {"accuracy": 0.1}}}))
    facts = ingest.read_ablation(path)
    assert facts["metrics"]["retrieval_dependency"] is None
    assert facts["metrics"]["acc_correct_evidence"] == 0.5


def test_ablation_without_a_correct_condition_is_an_error(tmp_path):
    path = tmp_path / "a.json"
    path.write_text(json.dumps({"conditions": {"wrong_textbook": {"accuracy": 0.1}}}))
    with pytest.raises(ValueError, match="no correct-evidence condition"):
        ingest.read_ablation(path)


def test_eval_battery_pairs_summary_with_checkpoint_detail(tmp_path):
    path = tmp_path / "results.json"
    path.write_text(json.dumps({
        "summary": [{"name": "killtest-c-201", "regime": "c", "train_seed": 201,
                     "step": 26700, "naturalized_contains": 0.0,
                     "heldout_accuracy": 0.7208, "probes_accuracy": 0.2377,
                     "noise_slope": -0.2713}],
        "checkpoints": [{"meta": {"model_config": {"d_model": 1024},
                                  "checkpoint": "/x/ckpt.pt"},
                         "heldout": {"n_questions": 2314, "chance": 0.31,
                                     "per_type": {"multi_hop": {"accuracy": 0.56}}},
                         "timings": {"total_s": 656.5}}],
    }))
    rows = ingest.read_eval_battery(path)
    assert len(rows) == 1
    row = rows[0]
    assert row["metrics"] == {"reading": 0.0, "reasoning": 0.7208,
                              "closed_book_probe": 0.2377}
    assert row["detail"]["heldout_multi_hop"] == 0.56
    assert row["model_config"] == {"d_model": 1024}


def test_train_config_gives_params_tokens_and_flops(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        "model:\n  d_model: 1024\n  n_layers: 24\n  d_ff: 2816\n"
        "  n_heads: 16\n  vocab_size: 32768\n  max_seq_len: 4096\n"
        "schedule:\n  max_steps: 26700\n"
        "train:\n  batch_size: 8\n  grad_accum_steps: 8\n  seed: 401\n")
    parsed = ingest.read_train_config(path)
    assert parsed["arch"]["params_total"] == 375_440_384
    assert parsed["arch"]["variant"] == "dense"
    assert parsed["compute"]["train_tokens"] == 26700 * 64 * 4096
    assert parsed["compute"]["train_flops"] == pytest.approx(
        6 * 308_331_520 * 26700 * 64 * 4096)
    assert parsed["seed"] == 401


def test_a_run_with_only_a_before_eval_has_no_result(tmp_path):
    run = tmp_path / "stopped"
    run.mkdir()
    write_jsonl(run / "eval.jsonl", [
        {"tag": "before", "step": 0, "accuracy": 0.0, "n_rollouts": 192,
         "elapsed_s": 77.36, "mean_generated": 95.5, "well_formed": 0.0},
    ])
    facts = ingest.rl_run_facts(run)
    assert facts["metrics"]["reasoning"] is None
    assert facts["detail"]["accuracy_before"] == 0.0
    assert facts["detail"]["accuracy_best"] is None
    assert facts["detail"]["final_tag"] is None


def test_generated_tokens_sum_over_rollouts(rl_dir):
    facts = ingest.rl_run_facts(rl_dir)
    # rl.jsonl has no mean_generated, so there is nothing to sum
    assert facts["raw"]["generated_tokens"] is None


def test_generated_tokens_when_the_step_log_has_them(tmp_path):
    run = tmp_path / "gen"
    run.mkdir()
    write_jsonl(run / "rl.jsonl", [
        {"step": 1, "n_rollouts": 64, "mean_generated": 10.0, "elapsed_s": 1.0},
        {"step": 2, "n_rollouts": 64, "mean_generated": 20.0, "elapsed_s": 2.0},
    ])
    assert ingest.rl_run_facts(run)["raw"]["generated_tokens"] == pytest.approx(1920.0)


def test_an_evidence_encoder_config_refuses_to_report_a_parameter_count(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        "model:\n  d_model: 1024\n  n_layers: 21\n  d_ff: 2944\n"
        "  n_heads: 16\n  vocab_size: 32768\n  max_seq_len: 2048\n"
        "  d_enc: 512\n  evidence_mode: pooled\n"
        "schedule:\n  max_steps: 100\n"
        "train:\n  batch_size: 8\n  grad_accum_steps: 8\n")
    parsed = ingest.read_train_config(path)
    assert parsed["params_countable"] is False
    assert parsed["arch"]["params_total"] is None
    assert parsed["compute"]["train_flops"] is None
    # tokens are still knowable, they come from the schedule alone
    assert parsed["compute"]["train_tokens"] == 100 * 64 * 2048


def test_battery_exposes_the_heldout_timing_separately(tmp_path):
    path = tmp_path / "results.json"
    path.write_text(json.dumps({
        "summary": [{"name": "x", "heldout_accuracy": 0.7}],
        "checkpoints": [{"heldout": {"n_questions": 100},
                         "timings": {"total_s": 656.5, "heldout_s": 176.5}}],
    }))
    row = ingest.read_eval_battery(path)[0]
    assert row["detail"]["eval_heldout_s"] == 176.5
    assert row["detail"]["eval_seconds_total"] == 656.5


def test_per_domain_splits_the_pooled_eval_accuracy(tmp_path):
    run = tmp_path / "split"
    run.mkdir()
    write_jsonl(run / "eval-samples-before.jsonl", [
        {"domain": "skill_units", "correct": True}])  # ignored: pre-training
    write_jsonl(run / "eval-samples-step000100.jsonl", [
        {"domain": "skill_binary_op", "correct": False},
        {"domain": "skill_binary_op", "correct": False},
        {"domain": "skill_procedure", "correct": True},
    ])
    write_jsonl(run / "eval-samples-step000200.jsonl", [
        {"domain": "skill_binary_op", "correct": False},
        {"domain": "skill_procedure", "correct": False},
    ])
    out = ingest.read_rl_eval_samples(run)
    assert out["n_files"] == 2
    assert out["per_domain"]["skill_binary_op"] == {
        "n": 3, "correct": 0, "accuracy": 0.0}
    assert out["per_domain"]["skill_procedure"] == {
        "n": 2, "correct": 1, "accuracy": 0.5}
    assert "skill_units" not in out["per_domain"]


def test_per_domain_is_empty_when_samples_carry_no_domain(tmp_path):
    run = tmp_path / "nodomain"
    run.mkdir()
    write_jsonl(run / "eval-samples-step000100.jsonl", [{"correct": True}])
    assert ingest.read_rl_eval_samples(run)["per_domain"] == {}
