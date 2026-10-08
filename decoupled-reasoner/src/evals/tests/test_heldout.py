import numpy as np

from src.evals.heldout import (
    answer_pools,
    build_context_ids,
    build_options,
    run_heldout,
)


def test_build_context_fits_budget(episodes, tok, tiny_model):
    max_len = tiny_model.cfg.max_seq_len
    for ep in episodes:
        for q in ep["questions"]:
            ids = build_context_ids(ep, q, tok, max_len)
            assert len(ids) <= max_len
            assert ids[0] == tok.special_ids["<|world|>"]
            assert ids[-1] == tok.special_ids["<|a|>"]


def test_build_options_yes_no(episodes):
    rng = np.random.default_rng(0)
    q = {"answer": "no", "type": "yes_no"}
    options, idx = build_options(q, [], episodes[0], rng)
    assert options == ["yes", "no"]
    assert idx == 1


def test_build_options_contains_answer(episodes):
    rng = np.random.default_rng(0)
    pools = answer_pools(episodes)
    for ep in episodes:
        pool = pools.get(ep["world"]["domain"], [])
        for q in ep["questions"]:
            options, idx = build_options(q, pool, ep, rng)
            assert options[idx] == q["answer"]
            assert len(options) >= 2
            assert len(set(options)) == len(options)


def test_run_heldout_structure(episodes, tok, tiny_model):
    out = run_heldout(tiny_model, tok, episodes, "cpu", seed=1)
    assert out["n_episodes"] == len(episodes)
    assert out["n_questions"] == sum(len(e["questions"]) for e in episodes)
    assert 0.0 <= out["accuracy"] <= 1.0
    assert 0.0 < out["chance"] < 1.0
    assert set(out["per_domain"]) == {e["world"]["domain"] for e in episodes}


def test_run_heldout_deterministic(episodes, tok, tiny_model):
    a = run_heldout(tiny_model, tok, episodes, "cpu", seed=1)
    b = run_heldout(tiny_model, tok, episodes, "cpu", seed=1)
    assert a == b
