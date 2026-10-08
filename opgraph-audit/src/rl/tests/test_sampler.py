"""The cached sampler has to agree with the plain model forward."""

import pytest
import torch

from src.rl.sampler import CachedPolicy, sample_from_logits


def _reference_logits(model, ids):
    with torch.no_grad():
        logits, _ = model(torch.tensor([ids], dtype=torch.long))
    return logits[0, -1].float()


def test_cached_prefill_matches_the_plain_forward(tiny_model):
    prompts = [[5, 9, 13, 21, 34], [7, 7, 11], [3, 100, 200, 44, 66, 88]]
    policy = CachedPolicy(tiny_model, "cpu", max_len=64, temperature=0.0)
    policy.begin(prompts)
    for i, prompt in enumerate(prompts):
        want = _reference_logits(tiny_model, prompt)
        got = policy.last_logits[i].float()
        assert torch.allclose(got, want, atol=1e-4), f"lane {i}"


def test_cached_decode_matches_the_plain_forward(tiny_model):
    prompts = [[5, 9, 13, 21, 34], [7, 7, 11], [3, 100, 200, 44, 66, 88]]
    policy = CachedPolicy(tiny_model, "cpu", max_len=64, temperature=0.0)
    policy.begin(prompts)
    histories = [list(p) for p in prompts]
    for token_row in ([12, 13, 14], [200, 5, 9], [31, 41, 59]):
        policy.advance(token_row)
        for i, tok_id in enumerate(token_row):
            histories[i].append(tok_id)
        for i, hist in enumerate(histories):
            want = _reference_logits(tiny_model, hist)
            got = policy.last_logits[i].float()
            assert torch.allclose(got, want, atol=1e-4), f"lane {i}"


def test_left_padding_does_not_leak_between_lanes(tiny_model):
    """A short prompt must decode the same whether or not it shares a batch
    with a much longer one."""
    short = [7, 7, 11]
    alone = CachedPolicy(tiny_model, "cpu", max_len=64, temperature=0.0)
    alone.begin([short])
    solo = alone.last_logits[0].float().clone()

    shared = CachedPolicy(tiny_model, "cpu", max_len=64, temperature=0.0)
    shared.begin([[3, 4, 5, 6, 7, 8, 9, 10, 11, 12], short])
    assert torch.allclose(shared.last_logits[1].float(), solo, atol=1e-4)


def test_greedy_sampling_is_argmax():
    logits = torch.tensor([[0.1, 5.0, -2.0], [3.0, 0.0, 3.0]])
    picked = sample_from_logits(logits, 0.0, 0, None)
    assert picked.tolist() == [1, 0]


def test_temperature_sampling_is_seed_reproducible():
    logits = torch.randn(4, 32)
    out = []
    for _ in range(2):
        gen = torch.Generator(device="cpu")
        gen.manual_seed(99)
        out.append(sample_from_logits(logits, 1.0, 0, gen).tolist())
    assert out[0] == out[1]


def test_top_k_restricts_the_support():
    logits = torch.tensor([[10.0, 9.0, -50.0, -60.0]])
    gen = torch.Generator(device="cpu")
    gen.manual_seed(0)
    for _ in range(20):
        picked = int(sample_from_logits(logits, 1.0, 2, gen).item())
        assert picked in (0, 1)


def test_max_len_is_enforced(tiny_model):
    policy = CachedPolicy(tiny_model, "cpu", max_len=6, temperature=0.0)
    with pytest.raises(ValueError):
        policy.begin([[1] * 8])
