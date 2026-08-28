import json

import pytest

from src.registry import backfill


def test_regime_mixtures_carry_their_source():
    mix = backfill.mixture_for("c", pytest.importorskip("pathlib").Path("/nope"))
    assert mix["natural"] == 0.0
    assert mix["source"]


def test_a_rendered_manifest_beats_the_static_table(tmp_path):
    manifest_dir = tmp_path / "runs" / "data-manifests"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "regime_e3.json").write_text(json.dumps(
        {"mix": {"natural": 0.45, "qa": 0.25, "webret": 0.2},
         "total_tokens": 13_354_983_633}))
    mix = backfill.mixture_for("E3", tmp_path)
    assert mix["natural"] == 0.45
    assert mix["webret"] == 0.2
    assert mix["total_tokens_rendered"] == 13_354_983_633


def test_an_unknown_regime_yields_no_shares_rather_than_zero(tmp_path):
    mix = backfill.mixture_for("z", tmp_path)
    assert "natural" not in mix
    assert mix["source"] is None


def test_regime_is_read_off_the_run_command():
    assert backfill._run_regime(
        "curve-350me3-701",
        "uv run python -m src.train.cli --data /home/x/data/regime_e3 --out y"
    ) == "E3"


def test_regime_falls_back_to_the_run_name():
    assert backfill._run_regime("killtest-c-201", None) == "C"
    assert backfill._run_regime("curve-1300m-a", None) == "A"
    assert backfill._run_regime("curve-350md-401", None) == "D"


def test_gpu_count_comes_from_the_visible_devices_list():
    assert backfill._gpu_count("CUDA_VISIBLE_DEVICES=5 uv run python") == 1
    assert backfill._gpu_count("CUDA_VISIBLE_DEVICES=0,1,2,3 torchrun") == 4
    assert backfill._gpu_count("uv run python") is None


def test_every_pretraining_run_names_a_belief_that_exists():
    for _, lane, _, belief_key in backfill.PRETRAIN_RUNS:
        assert lane in ("exploit", "explore", "falsify")
        assert backfill.BELIEF[belief_key].strip()


def test_every_rl_run_names_a_lane_and_a_belief():
    for _, lane, family, _, belief, novel in backfill.RL_RUNS:
        assert lane in ("exploit", "explore", "falsify")
        assert belief.strip()
        assert isinstance(novel, bool)
        assert family


def test_the_rl_policy_class_is_the_benchmarked_350m():
    from src.registry import flops
    counts = flops.param_counts_from_config(backfill.RL_POLICY_CONFIG)
    assert counts["params_total"] == 375_440_384


def test_battery_alias_tables_only_cover_batteries_without_their_own_map():
    # every alias key must be a battery this backfill actually reads
    for rel in backfill.BATTERY_ALIASES:
        assert rel in backfill.BATTERY_ORDER


def test_every_rl_family_names_the_suite_it_was_graded_on():
    families = {family for _, _, family, _, _, _ in backfill.RL_RUNS}
    assert families <= set(backfill.RL_FAMILY_SUITE)
    for family in families:
        assert backfill.RL_FAMILY_SUITE[family].strip()


def test_the_arithmetic_and_procedural_families_are_kept_apart():
    assert (backfill.RL_FAMILY_SUITE["rlarith"]
            != backfill.RL_FAMILY_SUITE["rlproc"])
    assert (backfill.RL_FAMILY_SUITE["rlsimple"]
            != backfill.RL_FAMILY_SUITE["rlskill"])
