import torch

from src.evals.mc import load_checkpoint_model, option_nll, score_mc


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


def test_score_mc_deterministic(tok, tiny_model):
    context = tok.encode("Is barin restricted in Tolema?")
    options = ["yes", "no", "sometimes"]
    a = score_mc(tiny_model, tok, context, options, "cpu")
    b = score_mc(tiny_model, tok, context, options, "cpu")
    assert a[0] == b[0]
    assert a[1] == b[1]
    assert 0 <= a[0] < len(options)


def test_load_checkpoint_model(tiny_ckpt, tiny_model):
    model, state = load_checkpoint_model(tiny_ckpt, "cpu")
    assert state["step"] == 7
    x = torch.zeros(1, 4, dtype=torch.long)
    with torch.no_grad():
        got, _ = model(x)
        want, _ = tiny_model(x)
    assert torch.allclose(got, want)
