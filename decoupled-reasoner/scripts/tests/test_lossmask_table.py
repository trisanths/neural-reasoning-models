"""The reporting arithmetic, which is where a four way table goes wrong."""

import pytest

from scripts.lossmask_table import (build_table, factual_loss, probe_answer_tags,
                                    verdict, wilson)


def arm(name, probe, contains, plain, entity, weights):
    return {
        "run": f"/runs/{name}",
        "checkpoint": f"/runs/{name}/ckpt.pt",
        "step": 5000,
        "lossmask": {"weights": weights},
        "train_tokens": 655360000,
        "probe_accuracy": probe,
        "probe_chance": 0.25,
        "probe_n": 244,
        "naturalized_em": 0.01,
        "naturalized_contains": contains,
        "naturalized_n": 250,
        "heldout": {
            "loss": 3.9,
            "per_tag": {
                "plain": {"loss": plain, "tokens": 800},
                "entity": {"loss": entity, "tokens": 100},
                "number": {"loss": entity, "tokens": 100},
            },
        },
    }


RESULTS = [
    arm("lm-a", 0.30, 0.18, 3.86, 13.4, {"entity": 0.0, "number": 0.0}),
    arm("lm-b", 0.40, 0.20, 3.85, 6.2, {"number": 0.0}),
    arm("lm-c", 0.34, 0.19, 3.86, 8.1, {"entity": 0.1, "number": 0.1}),
    arm("lm-d", 0.45, 0.20, 3.84, 5.9, {}),
]


def test_wilson_brackets_the_point_estimate():
    lo, hi = wilson(50, 100)
    assert lo < 0.5 < hi
    # Wilson at p = 0.5 is symmetric and lands at the textbook 0.404, 0.596.
    assert lo == pytest.approx(0.4038, abs=1e-3)
    assert hi == pytest.approx(0.5962, abs=1e-3)
    assert wilson(0, 0) == (0.0, 1.0)


def test_wilson_narrows_as_the_sample_grows():
    small = wilson(25, 50)
    large = wilson(250, 500)
    assert (large[1] - large[0]) < (small[1] - small[0])


def test_probe_suppression_is_the_fraction_of_the_way_to_chance():
    summary = verdict(RESULTS)
    # control 0.45, masked 0.30, chance 0.25: three quarters of the way down.
    assert summary["probe_suppression"] == pytest.approx(0.75)


def test_reading_retained_is_measured_against_the_control_not_against_one():
    summary = verdict(RESULTS)
    assert summary["reading_retained"] == pytest.approx(0.9)
    assert summary["beats_regime_e_reading"] is True
    assert summary["regime_e_reading_bar"] == 0.83


def test_the_verdict_names_the_two_loss_gaps_separately():
    summary = verdict(RESULTS)
    assert summary["heldout_plain_loss_gap"] == pytest.approx(0.02)
    assert summary["heldout_factual_loss_gap"] == pytest.approx(13.4 - 5.9)


def test_an_incomplete_table_says_so_rather_than_guessing():
    assert verdict(RESULTS[:2])["verdict"] == "incomplete"


def test_factual_loss_weights_by_token_count():
    per_tag = {"entity": {"loss": 10.0, "tokens": 300},
               "number": {"loss": 2.0, "tokens": 100}}
    assert factual_loss(per_tag) == pytest.approx(8.0)
    assert factual_loss({}) is None


def test_the_table_has_a_row_per_arm_and_marks_the_control():
    table = build_table(RESULTS)
    lines = table.splitlines()
    assert len(lines) == 6, "header, rule, four arms"
    assert lines[-1].count("reference") == 2, "the control is its own baseline"
    assert "0.300 [" in table and "0.450 [" in table


def test_most_probes_are_reachable_by_masking_but_not_all():
    """The ceiling on what this method can suppress. If this ever reads 244
    the split has stopped meaning anything."""
    flags = probe_answer_tags()
    assert len(flags) == 244
    assert 150 < sum(flags) < 200
