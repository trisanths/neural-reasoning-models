"""Correctness tests for the backbone.

The latent pipeline runs the model incrementally with a reused KV cache, so a
subtle cache or masking bug would silently corrupt every downstream result
rather than crash. These tests pin that behaviour down.
"""

import sys

import torch

sys.path.insert(0, ".")
from src.model import ModelConfig, TinyLM  # noqa: E402


def _model(seed: int = 0) -> TinyLM:
    torch.manual_seed(seed)
    m = TinyLM(ModelConfig(vocab_size=50, d_model=64, n_layers=3, n_heads=4))
    m.eval()
    return m


def test_kv_cache_matches_full_forward():
    """Incremental decoding with a cache must equal a single full forward."""
    m = _model()
    ids = torch.randint(0, 50, (2, 12))
    with torch.no_grad():
        full = m(input_ids=ids).logits
        # Prefill 8 tokens, then feed the remaining 4 one at a time.
        out = m(input_ids=ids[:, :8])
        cache = out.past_key_values
        pieces = [out.logits]
        for t in range(8, 12):
            out = m(input_ids=ids[:, t : t + 1], past_key_values=cache)
            cache = out.past_key_values
            pieces.append(out.logits)
        inc = torch.cat(pieces, dim=1)
    assert torch.allclose(full, inc, atol=1e-4), (full - inc).abs().max()


def test_causality():
    """Changing token t must not alter logits at positions < t."""
    m = _model()
    ids = torch.randint(0, 50, (1, 10))
    alt = ids.clone()
    alt[0, 7] = (alt[0, 7] + 1) % 50
    with torch.no_grad():
        a = m(input_ids=ids).logits
        b = m(input_ids=alt).logits
    assert torch.allclose(a[:, :7], b[:, :7], atol=1e-5)
    assert not torch.allclose(a[:, 7:], b[:, 7:], atol=1e-5)


def test_inputs_embeds_matches_ids():
    m = _model()
    ids = torch.randint(0, 50, (2, 6))
    with torch.no_grad():
        a = m(input_ids=ids).logits
        b = m(inputs_embeds=m.wte(ids)).logits
    assert torch.allclose(a, b, atol=1e-6)


def test_padding_mask_isolates_batch_rows():
    """A padded row must produce the same logits as the unpadded sequence."""
    m = _model()
    short = torch.randint(1, 50, (1, 5))
    padded = torch.cat([short, torch.zeros(1, 3, dtype=torch.long)], dim=1)
    mask = torch.tensor([[1, 1, 1, 1, 1, 0, 0, 0]])
    with torch.no_grad():
        a = m(input_ids=short).logits
        b = m(input_ids=padded, attention_mask=mask).logits
    assert torch.allclose(a, b[:, :5], atol=1e-5), (a - b[:, :5]).abs().max()


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
