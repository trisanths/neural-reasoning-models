import random

import torch

from src.evals.mc import (choose, load_checkpoint_model, option_nll,
                          option_nll_stats, option_scores, score_mc,
                          shuffled_order)


class FixedLogitModel:
    """Assigns high probability to one favored token id everywhere."""

    class cfg:
        max_seq_len = 64

    def __init__(self, vocab_size=32, favored=5):
        self.vocab_size = vocab_size
        self.favored = favored

    def __call__(self, idx, targets=None):
        logits = torch.zeros(idx.shape[0], idx.shape[1], self.vocab_size)
        logits[..., self.favored] = 8.0
        return logits, None


class UniformModel:
    """Every token equally likely, so NLL is proportional to option length."""

    class cfg:
        max_seq_len = 64

    def __call__(self, idx, targets=None):
        return torch.zeros(idx.shape[0], idx.shape[1], 32), None


class ListTokenizer:
    """Encodes a space separated string of integers as those token ids."""

    def encode(self, text):
        return [int(t) for t in text.split()]


def test_option_nll_prefers_favored_token():
    model = FixedLogitModel(favored=5)
    good = option_nll(model, [1, 2, 3], [5, 5], "cpu")
    bad = option_nll(model, [1, 2, 3], [6, 6], "cpu")
    assert good < bad


def test_option_nll_truncates_long_context():
    model = FixedLogitModel(favored=5)
    ctx = [1] * 100
    val = option_nll(model, ctx, [5], "cpu")
    assert val >= 0.0


def test_option_nll_stats_counts_option_tokens():
    s, n = option_nll_stats(UniformModel(), [1, 2], [3, 4, 5], "cpu")
    assert n == 3
    assert abs(s - 3 * torch.log(torch.tensor(32.0)).item()) < 1e-4


def test_score_mc_deterministic(tok, tiny_model):
    context = tok.encode("Is barin restricted in Tolema?")
    options = ["yes", "no", "sometimes"]
    a = score_mc(tiny_model, tok, context, options, "cpu")
    b = score_mc(tiny_model, tok, context, options, "cpu")
    assert a[0] == b[0]
    assert a[1] == b[1]
    assert 0 <= a[0] < len(options)


def test_length_normalisation_removes_the_short_option_bias():
    # Under a uniform model every token costs the same, so the summed rule
    # always picks the shortest option while the mean rule sees a tie.
    model, tok = UniformModel(), ListTokenizer()
    options = ["7 7 7 7", "7", "7 7"]
    best_legacy, _ = score_mc(model, tok, [1], options, "cpu", legacy=True)
    assert best_legacy == 1
    picks = {score_mc(model, tok, [1], options, "cpu", seed=s)[0]
             for s in range(40)}
    assert picks == {0, 1, 2}


def test_mean_rule_prefers_the_likelier_option_whatever_its_length():
    model, tok = FixedLogitModel(favored=5), ListTokenizer()
    # Four favoured tokens against one unfavoured token: the summed NLL is
    # also lower here, so check a case where the sums disagree with the means.
    sums = [4 * 0.1, 1 * 0.3]
    counts = [4, 1]
    assert choose(sums, counts, rng=random.Random(0)) == 0
    assert choose(sums, counts, legacy=True) == 1
    best, _ = score_mc(model, tok, [1], ["5 5 5 5", "6"], "cpu", seed=3)
    assert best == 0


def test_ties_are_broken_by_the_seed_not_by_position():
    sums, counts = [1.0, 1.0, 1.0, 1.0], [1, 1, 1, 1]
    picks = [choose(sums, counts, rng=random.Random(s)) for s in range(200)]
    for i in range(4):
        assert 30 < picks.count(i) < 70
    assert [choose(sums, counts, rng=random.Random(9)) for _ in range(3)] == \
        [choose(sums, counts, rng=random.Random(9))] * 3
    assert choose(sums, counts, legacy=True) == 0


def test_a_strict_winner_is_never_overridden_by_the_shuffle():
    sums, counts = [2.0, 1.0, 3.0], [1, 1, 1]
    assert {choose(sums, counts, rng=random.Random(s)) for s in range(50)} == {1}


def test_shuffled_order_is_a_seeded_permutation():
    a = shuffled_order(6, random.Random(4))
    assert sorted(a) == list(range(6))
    assert a == shuffled_order(6, random.Random(4))
    assert len({tuple(shuffled_order(6, random.Random(s))) for s in range(20)}) > 1


def test_option_scores_refuses_an_empty_option():
    try:
        option_scores([1.0], [0])
    except ValueError:
        return
    raise AssertionError("an option with no tokens was scored")


def test_load_checkpoint_model(tiny_ckpt, tiny_model):
    model, state = load_checkpoint_model(tiny_ckpt, "cpu")
    assert state["step"] == 7
    x = torch.zeros(1, 4, dtype=torch.long)
    with torch.no_grad():
        got, _ = model(x)
        want, _ = tiny_model(x)
    assert torch.allclose(got, want)
