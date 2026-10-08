"""Cost in evidence size is linear, checked analytically and by the clock.

The analytic check is exact and cannot flake: the FLOP model separates the
terms that scale with the bank from the terms that do not, and doubling the
bank must double the former exactly. The timing check is the one that would
catch an implementation that silently materializes an N by N tensor, so it
runs at N in {32, 128, 256, 512} and is asserted only through ratio bounds
loose enough to survive a noisy box but far tighter than quadratic growth.
"""

import time

import pytest
import torch

from src.train.evidence_model import (EvidenceModelConfig,
                                      EvidenceTransformerLM,
                                      cross_attention_flops)

SIZES = [32, 128, 256, 512]

COST_CFG = EvidenceModelConfig(
    vocab_size=512, d_model=64, n_layers=2, n_heads=4, d_ff=176,
    max_seq_len=64, d_enc=64, enc_layers=2, enc_heads=4, enc_d_ff=176,
    chunk_len=32, xattn_every=1, xattn_n_kv_heads=2, max_chunks=1024,
)


def test_flop_model_is_exactly_linear_in_bank_size():
    for mode in ("pooled", "tokens"):
        base = cross_attention_flops(COST_CFG, seq_len=32, n_chunks=32, mode=mode)
        for factor in (2, 4, 8, 16):
            grown = cross_attention_flops(COST_CFG, seq_len=32,
                                          n_chunks=32 * factor, mode=mode)
            assert grown["evidence_scaling"] == factor * base["evidence_scaling"]
            assert grown["decoder"] == base["decoder"]


def test_flop_model_beats_in_context_evidence_by_a_wide_margin():
    """The same evidence tokens in a context window cost quadratically."""
    cfg = COST_CFG
    for n_chunks in SIZES:
        evidence_tokens = n_chunks * cfg.chunk_len
        xattn = cross_attention_flops(cfg, seq_len=32, n_chunks=n_chunks,
                                      mode="tokens")["total"]
        # A plain decoder reading the same tokens in context: self-attention
        # over (evidence + working) tokens, all n_layers of it.
        t = evidence_tokens + 32
        d = cfg.d_model
        in_context = 2 * cfg.n_layers * (t * 4 * d * d + 2 * t * t * d
                                         + t * 3 * d * cfg.d_ff)
        assert xattn < in_context
    # And the advantage widens with the bank, which is the whole point.
    small = (cross_attention_flops(cfg, 32, 32, "tokens")["total"], 32)
    large = (cross_attention_flops(cfg, 32, 512, "tokens")["total"], 512)
    assert large[0] / small[0] < 512 / 32 * 1.2


def _median_time(model, ids, ev, mask, rel, mode, device, repeats=5):
    def once():
        if device == "cuda":
            torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.no_grad():
            model(ids, ev, mask, rel, mode=mode)
        if device == "cuda":
            torch.cuda.synchronize()
        return time.perf_counter() - start

    once()
    once()
    return sorted(once() for _ in range(repeats))[repeats // 2]


@pytest.mark.parametrize("mode", ["pooled", "tokens"])
def test_wall_clock_is_linear_in_evidence_size(mode):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(0)
    cfg = EvidenceModelConfig(**{**COST_CFG.__dict__, "evidence_mode": mode})
    model = EvidenceTransformerLM(cfg).to(device).eval()
    ids = torch.randint(0, cfg.vocab_size, (1, 32), device=device)

    times = {}
    for n in SIZES:
        ev = torch.randint(0, cfg.vocab_size, (1, n, cfg.chunk_len), device=device)
        mask = torch.ones_like(ev, dtype=torch.bool)
        rel = torch.ones((1, n), device=device)
        times[n] = _median_time(model, ids, ev, mask, rel, mode, device)

    # Doubling the bank may at most a little more than double the time.
    # Quadratic growth would show up here as a factor near four.
    for small, large in ((128, 256), (256, 512)):
        ratio = times[large] / times[small]
        assert ratio < 2.6, (mode, times, ratio)
    # And the whole sweep stays well under the quadratic envelope.
    assert times[512] / times[128] < 5.0, (mode, times)

    # Marginal cost per chunk stops falling once fixed overhead is amortized,
    # which is the signature of an affine cost curve.
    per_chunk = {n: times[n] / n for n in SIZES}
    assert per_chunk[512] < per_chunk[32]
    assert per_chunk[512] < 2.0 * per_chunk[256]


def test_pooled_mode_is_cheaper_than_token_mode_at_the_same_bank():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(0)
    model = EvidenceTransformerLM(COST_CFG).to(device).eval()
    ids = torch.randint(0, COST_CFG.vocab_size, (1, 32), device=device)
    ev = torch.randint(0, COST_CFG.vocab_size, (1, 256, COST_CFG.chunk_len),
                       device=device)
    mask = torch.ones_like(ev, dtype=torch.bool)
    rel = torch.ones((1, 256), device=device)
    pooled = _median_time(model, ids, ev, mask, rel, "pooled", device)
    tokens = _median_time(model, ids, ev, mask, rel, "tokens", device)
    assert pooled < tokens


def test_bank_can_hold_far_more_tokens_than_the_context_window():
    """A 512 chunk bank is 16384 evidence tokens against a 64 token context."""
    cfg = COST_CFG
    model = EvidenceTransformerLM(cfg).eval()
    ids = torch.randint(0, cfg.vocab_size, (1, 32))
    ev = torch.randint(0, cfg.vocab_size, (1, 512, cfg.chunk_len))
    mask = torch.ones_like(ev, dtype=torch.bool)
    with torch.no_grad():
        logits, _ = model(ids, ev, mask)
    assert logits.shape == (1, 32, cfg.vocab_size)
    assert ev.numel() > 200 * cfg.max_seq_len
