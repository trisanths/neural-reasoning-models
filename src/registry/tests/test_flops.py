import pytest

from src.registry import flops

# The 350M config: configs/350m.yaml and every curve-350* run's config.yaml.
CFG_350M = {"d_model": 1024, "n_layers": 24, "d_ff": 2816, "n_heads": 16,
            "vocab_size": 32768, "max_seq_len": 4096}

# scripts/bench_evidence.py printed these on the L40S for the same shape, from
# an independent count over the built module's parameters.
BENCH_TOTAL = 375_440_384
BENCH_NON_EMBEDDING = 308_331_520


def test_param_count_matches_the_benchmarked_model():
    counts = flops.param_counts_from_config(CFG_350M)
    assert counts["params_total"] == BENCH_TOTAL
    assert counts["params_non_embedding"] == BENCH_NON_EMBEDDING


def test_embedding_share_is_two_untied_matrices():
    counts = flops.param_counts_from_config(CFG_350M)
    assert counts["params_embedding"] == 2 * 32768 * 1024
    assert (counts["params_total"]
            == counts["params_non_embedding"] + counts["params_embedding"])


def test_tying_embeddings_drops_exactly_one_matrix():
    tied = flops.param_counts(d_model=1024, n_layers=24, d_ff=2816,
                              vocab_size=32768, tie_embeddings=True)
    assert BENCH_TOTAL - tied["params_total"] == 32768 * 1024


def test_grouped_query_attention_shrinks_the_attention_block():
    full = flops.param_counts(d_model=1024, n_layers=1, d_ff=2816,
                              vocab_size=32768, n_heads=16)
    gqa = flops.param_counts(d_model=1024, n_layers=1, d_ff=2816,
                             vocab_size=32768, n_heads=16, n_kv_heads=4)
    assert gqa["params_non_embedding"] < full["params_non_embedding"]


def test_curve_runs_consumed_seven_billion_tokens():
    # CURVE.md: 26700 steps x 262,144 tokens per step.
    tokens = flops.training_tokens(
        {"max_steps": 26700}, {"batch_size": 8, "grad_accum_steps": 8},
        CFG_350M)
    assert tokens == 26700 * 8 * 8 * 4096
    assert tokens == pytest.approx(7.0e9, rel=0.01)


def test_a_dense_stack_has_no_loop_multiplier():
    assert flops.effective_layer_passes(CFG_350M) == 1.0


def test_a_looped_core_costs_more_passes_at_the_same_parameters():
    # curve-350me3loop-711/config.yaml
    looped = {"d_model": 1280, "n_layers": 14, "d_ff": 3648, "n_heads": 20,
              "vocab_size": 32768, "max_seq_len": 4096,
              "recurrent": {"loops": 4, "core_layers": 11,
                            "prelude_layers": 1, "coda_layers": 2}}
    multiplier = flops.effective_layer_passes(looped)
    assert multiplier == pytest.approx((1 + 11 * 4 + 2) / 14)
    assert multiplier > 3.0
    # weights are shared, so the parameter count is unaffected
    dense = dict(looped)
    dense.pop("recurrent")
    assert (flops.param_counts_from_config(looped)
            == flops.param_counts_from_config(dense))


def test_training_flops_is_six_p_t():
    assert flops.training_flops(1e8, 1e9) == pytest.approx(6e17)


def test_decode_flops_is_two_p_g():
    assert flops.decode_flops_per_answer(1e8, 40) == pytest.approx(8e9)


def test_decode_flops_is_a_lower_bound_on_inference_flops():
    decode = flops.decode_flops_per_answer(1e8, 40)
    full = flops.inference_flops_per_answer(1e8, 200, 40)
    assert decode < full
