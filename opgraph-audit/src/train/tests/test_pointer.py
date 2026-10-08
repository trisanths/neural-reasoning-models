"""The pointer head's arithmetic: normalization, masking, the gate, gradients.

These tests do not care whether copying helps. They care that the object the
head returns is a probability distribution, that it is the mixture the
docstring claims, and that both routes into it carry gradient.
"""

import math

import pytest
import torch

from src.train.pointer import (PointerConfig, PointerHead, copy_fraction,
                               pointer_cross_entropy)

VOCAB = 64
D_MODEL = 32
TOL = 1e-5


def head(seed: int = 0, **cfg_kwargs) -> PointerHead:
    torch.manual_seed(seed)
    return PointerHead(D_MODEL, VOCAB, PointerConfig(**cfg_kwargs))


def inputs(bsz=2, seq=5, n_pos=7, seed=0, mask_tail=0, device="cpu", dtype=torch.float32):
    gen = torch.Generator().manual_seed(seed)
    hidden = torch.randn(bsz, seq, D_MODEL, generator=gen).to(device=device, dtype=dtype)
    evidence = torch.randn(bsz, n_pos, D_MODEL, generator=gen).to(device=device, dtype=dtype)
    ids = torch.randint(0, VOCAB, (bsz, n_pos), generator=gen).to(device)
    logits = torch.randn(bsz, seq, VOCAB, generator=gen).to(device=device, dtype=dtype)
    mask = torch.ones(bsz, n_pos, dtype=torch.bool, device=device)
    if mask_tail:
        mask[:, -mask_tail:] = False
    return hidden, evidence, ids, mask, logits


# ---------------- normalization ----------------


def test_copy_distribution_sums_to_one():
    h, e, ids, mask, logits = inputs(mask_tail=2)
    out = head()(h, e, ids, mask, vocab_logits=logits)
    total = out.log_p_copy.exp().sum(-1)
    assert torch.allclose(total, torch.ones_like(total), atol=TOL)


def test_final_distribution_sums_to_one():
    h, e, ids, mask, logits = inputs(mask_tail=2)
    out = head()(h, e, ids, mask, vocab_logits=logits)
    total = out.log_probs.exp().sum(-1)
    assert torch.allclose(total, torch.ones_like(total), atol=1e-4), total


@pytest.mark.parametrize("gate", [0.0, 0.25, 0.5, 0.9, 1.0])
def test_mixture_matches_the_written_formula(gate):
    """P(w) = g P_vocab(w) + (1 - g) sum over the positions holding w."""
    h, e, ids, mask, logits = inputs(mask_tail=1)
    out = head()(h, e, ids, mask, vocab_logits=logits, gate_override=gate)
    copy = torch.zeros_like(out.log_p_vocab)
    copy.scatter_add_(2, ids[:, None, :].expand(copy.shape[0], copy.shape[1], ids.shape[1]),
                      out.log_p_copy.exp())
    expected = gate * out.log_p_vocab.exp() + (1.0 - gate) * copy
    assert torch.allclose(out.log_probs.exp(), expected, atol=1e-5)


def test_gate_one_is_exactly_the_vocabulary_head():
    h, e, ids, mask, logits = inputs()
    out = head()(h, e, ids, mask, vocab_logits=logits, gate_override=1.0)
    assert torch.allclose(out.log_probs, out.log_p_vocab, atol=0.0, rtol=0.0)


def test_gate_zero_puts_no_mass_off_the_evidence():
    h, e, ids, mask, logits = inputs()
    with torch.no_grad():
        out = head()(h, e, ids, mask, vocab_logits=logits, gate_override=0.0)
    present = torch.zeros(out.log_probs.shape, dtype=torch.bool)
    present.scatter_(2, ids[:, None, :].expand(present.shape[0], present.shape[1], ids.shape[1]),
                     True)
    assert float(out.log_probs.exp()[~present].max()) == 0.0
    total = out.log_probs.exp().sum(-1)
    assert torch.allclose(total, torch.ones_like(total), atol=1e-4)


# ---------------- masking and degenerate banks ----------------


def test_masked_positions_get_no_copy_mass():
    h, e, ids, mask, logits = inputs(mask_tail=3)
    with torch.no_grad():
        out = head()(h, e, ids, mask, vocab_logits=logits)
    dead = out.log_p_copy.exp()[:, :, -3:]
    assert float(dead.abs().max()) == 0.0


@pytest.mark.parametrize("gate", [0.0, 1.0])
def test_a_pinned_gate_still_backpropagates_without_nan(gate):
    """Pinning the gate sends one whole term to log zero. Minus infinity is
    the right forward answer and a NaN in the backward of logaddexp and log,
    so both are floored; this is the regression test for that."""
    h, e, ids, mask, logits = inputs()
    h = h.clone().requires_grad_(True)
    e = e.clone().requires_grad_(True)
    logits = logits.clone().requires_grad_(True)
    module = head()
    out = module(h, e, ids, mask, vocab_logits=logits, gate_override=gate)
    targets = ids[:, :1].expand(-1, h.shape[1]).contiguous()
    loss = pointer_cross_entropy(out.log_probs, targets)
    assert torch.isfinite(loss), loss
    loss.backward()
    for name, tensor in (("hidden", h), ("evidence", e), ("logits", logits)):
        assert torch.isfinite(tensor.grad).all(), name
    for name, param in module.named_parameters():
        if param.grad is not None:
            assert torch.isfinite(param.grad).all(), name
    # The pinned path is the only one that moves anything.
    assert (float(logits.grad.abs().sum()) == 0.0) == (gate == 0.0)


def test_empty_evidence_row_falls_back_to_the_vocabulary_head():
    h, e, ids, mask, logits = inputs()
    mask[0] = False
    with torch.no_grad():
        out = head()(h, e, ids, mask, vocab_logits=logits)
    assert torch.isfinite(out.log_probs).all()
    assert torch.allclose(out.log_probs[0], out.log_p_vocab[0], atol=0.0, rtol=0.0)
    assert float(out.gate[0].min()) == 1.0
    # The other row is untouched by its neighbour's empty bank.
    assert not torch.allclose(out.log_probs[1], out.log_p_vocab[1])


def test_a_token_in_the_evidence_gains_probability():
    """The headline property: mass moves onto tokens the evidence holds."""
    h, e, ids, mask, logits = inputs()
    with torch.no_grad():
        out = head()(h, e, ids, mask, vocab_logits=logits, gate_override=0.5)
    gained = out.log_probs.exp() - 0.5 * out.log_p_vocab.exp()
    present = torch.zeros(gained.shape, dtype=torch.bool)
    present.scatter_(2, ids[:, None, :].expand(gained.shape[0], gained.shape[1], ids.shape[1]),
                     True)
    assert float(gained[present].min()) > 0.0
    # Off the evidence the copy term is exactly -inf, so all that is left here
    # is the float32 round trip through exp and log.
    assert float(gained[~present].abs().max()) < 1e-7


def test_repeated_evidence_token_sums_its_positions():
    """Two positions holding the same id contribute the sum, not the max."""
    torch.manual_seed(0)
    h = torch.randn(1, 1, D_MODEL)
    e = torch.randn(1, 4, D_MODEL)
    ids = torch.tensor([[5, 5, 9, 11]])
    logits = torch.randn(1, 1, VOCAB)
    out = head()(h, e, ids, vocab_logits=logits, gate_override=0.0)
    both = out.log_p_copy.exp()[0, 0, 0] + out.log_p_copy.exp()[0, 0, 1]
    assert torch.allclose(out.log_probs.exp()[0, 0, 5], both, atol=1e-6)


# ---------------- gradients ----------------


def test_gradient_flows_to_both_paths():
    h, e, ids, mask, logits = inputs()
    h = h.clone().requires_grad_(True)
    e = e.clone().requires_grad_(True)
    logits = logits.clone().requires_grad_(True)
    module = head()
    out = module(h, e, ids, mask, vocab_logits=logits)
    targets = ids[:, :1].expand(-1, h.shape[1]).contiguous()
    loss = pointer_cross_entropy(out.log_probs, targets)
    loss.backward()
    assert float(logits.grad.abs().sum()) > 0.0, "vocabulary path is dead"
    assert float(e.grad.abs().sum()) > 0.0, "copy path is dead"
    assert float(h.grad.abs().sum()) > 0.0
    for name, param in module.named_parameters():
        assert param.grad is not None, name
        assert float(param.grad.abs().sum()) > 0.0, name


def test_gate_moves_toward_copying_when_the_answer_is_only_in_the_evidence():
    """One step of descent on a target the vocabulary head dislikes should
    lower the gate, which is the mechanism the whole head rests on."""
    torch.manual_seed(0)
    module = head()
    h = torch.randn(4, 3, D_MODEL)
    e = torch.randn(4, 6, D_MODEL)
    ids = torch.randint(0, VOCAB, (4, 6))
    logits = torch.full((4, 3, VOCAB), -1.0)
    logits.scatter_(2, ids[:, :1, None].expand(4, 3, 1), -9.0)  # vocab hates the answer
    targets = ids[:, :1].expand(-1, 3).contiguous()
    out = module(h, e, ids, vocab_logits=logits)
    before = float(out.gate.mean())
    loss = pointer_cross_entropy(out.log_probs, targets)
    loss.backward()
    with torch.no_grad():
        for param in module.gate_proj.parameters():
            param -= 0.5 * param.grad
    after = float(module(h, e, ids, vocab_logits=logits).gate.mean())
    assert after < before, f"gate did not fall: {before} -> {after}"


# ---------------- numerics ----------------


def test_stable_when_the_vocabulary_path_has_ruled_the_answer_out():
    """A probability space mixture would flush this to zero and return inf."""
    torch.manual_seed(0)
    h = torch.randn(1, 1, D_MODEL)
    e = torch.randn(1, 3, D_MODEL)
    ids = torch.tensor([[7, 8, 9]])
    logits = torch.full((1, 1, VOCAB), 60.0)
    logits[0, 0, 7] = -60.0
    out = head()(h, e, ids, vocab_logits=logits, gate_override=0.9)
    target = torch.tensor([[7]])
    loss = pointer_cross_entropy(out.log_probs, target)
    vocab_only = pointer_cross_entropy(out.log_p_vocab, target)
    assert float(out.log_p_vocab[0, 0, 7]) < -100.0
    assert float(vocab_only) > 100.0
    assert torch.isfinite(loss) and float(loss) < 10.0, loss


@pytest.mark.parametrize("dtype", [torch.bfloat16, torch.float16])
def test_low_precision_inputs_stay_normalized(dtype):
    h, e, ids, mask, logits = inputs(mask_tail=2, dtype=dtype)
    out = head()(h, e, ids, mask, vocab_logits=logits)
    assert out.log_probs.dtype == torch.float32
    assert torch.isfinite(out.log_probs).all()
    total = out.log_probs.exp().sum(-1)
    assert torch.allclose(total, torch.ones_like(total), atol=1e-3), total


def test_autocast_region_does_not_change_the_result():
    h, e, ids, mask, logits = inputs()
    module = head()
    plain = module(h, e, ids, mask, vocab_logits=logits).log_probs
    with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
        under = module(h, e, ids, mask, vocab_logits=logits).log_probs
    assert under.dtype == torch.float32
    assert torch.allclose(plain, under, atol=0.0, rtol=0.0)


# ---------------- plumbing ----------------


def test_select_matches_slicing_by_hand():
    h, e, ids, mask, logits = inputs(seq=6)
    module = head()
    picked = torch.tensor([[1, 4], [0, 5]])
    selected = module(h, e, ids, mask, vocab_logits=logits, select=picked)
    full = module(h, e, ids, mask, vocab_logits=logits)
    for b in range(2):
        for k, t in enumerate(picked[b].tolist()):
            assert torch.allclose(selected.log_probs[b, k], full.log_probs[b, t], atol=0.0)


def test_head_adds_no_vocabulary_sized_parameters():
    """The head reads the lm_head's output, it does not own a second one."""
    small = PointerHead(D_MODEL, VOCAB, PointerConfig())
    large = PointerHead(D_MODEL, VOCAB * 100, PointerConfig())
    assert small.num_params() == large.num_params()
    assert small.num_params() == 3 * D_MODEL * D_MODEL + 2 * D_MODEL + 1


def test_copy_fraction_reports_the_share_that_came_from_pointing():
    h, e, ids, mask, logits = inputs()
    module = head()
    targets = ids[:, :1].expand(-1, h.shape[1]).contiguous()
    assert copy_fraction(module(h, e, ids, mask, vocab_logits=logits,
                                gate_override=1.0), targets) == 0.0
    assert math.isclose(
        copy_fraction(module(h, e, ids, mask, vocab_logits=logits,
                             gate_override=0.0), targets), 1.0, rel_tol=1e-5)


def test_rejects_a_gate_override_outside_the_unit_interval():
    h, e, ids, mask, logits = inputs()
    with pytest.raises(ValueError):
        head()(h, e, ids, mask, vocab_logits=logits, gate_override=1.5)


def test_rejects_missing_vocabulary_logits():
    h, e, ids, mask, _ = inputs()
    with pytest.raises(ValueError):
        head()(h, e, ids, mask)


def test_evidence_dim_may_differ_from_the_model_width():
    module = PointerHead(D_MODEL, VOCAB, PointerConfig(evidence_dim=8, d_attn=16))
    h, _, ids, mask, logits = inputs()
    e = torch.randn(2, 7, 8)
    out = module(h, e, ids, mask, vocab_logits=logits)
    total = out.log_probs.exp().sum(-1)
    assert torch.allclose(total, torch.ones_like(total), atol=1e-4)
