import pytest
import torch
import torch.nn.functional as F

from src.lossmask.loss import weighted_cross_entropy


def fixture(seed=0, batch=3, seq=7, vocab=11):
    generator = torch.Generator().manual_seed(seed)
    logits = torch.randn(batch, seq, vocab, generator=generator)
    targets = torch.randint(0, vocab, (batch, seq), generator=generator)
    return logits, targets


def test_all_ones_is_the_plain_mean():
    logits, targets = fixture()
    plain = F.cross_entropy(
        logits.float().view(-1, logits.shape[-1]), targets.reshape(-1))
    weighted = weighted_cross_entropy(
        logits, targets, torch.ones_like(targets, dtype=torch.float32))
    assert weighted.item() == pytest.approx(plain.item(), rel=1e-6)


def test_zeroing_tokens_normalizes_by_the_surviving_weight():
    """The masked arm's loss is the mean over the tokens it kept, not a
    shrunken mean over all of them. Without that, an arm masking a third of
    its tokens would train at two thirds of the control's gradient scale."""
    logits, targets = fixture(seed=1)
    weights = torch.ones_like(targets, dtype=torch.float32)
    weights[:, ::2] = 0.0
    kept = weighted_cross_entropy(logits, targets, weights)
    only_kept = F.cross_entropy(
        logits[:, 1::2].reshape(-1, logits.shape[-1]),
        targets[:, 1::2].reshape(-1))
    assert kept.item() == pytest.approx(only_kept.item(), rel=1e-6)


def test_a_fractional_weight_lands_between_the_two_extremes():
    logits, targets = fixture(seed=2)
    ones = torch.ones_like(targets, dtype=torch.float32)
    mask = torch.ones_like(ones)
    mask[:, :3] = 0.0
    soft = mask.clone()
    soft[:, :3] = 0.1
    full = weighted_cross_entropy(logits, targets, ones).item()
    zero = weighted_cross_entropy(logits, targets, mask).item()
    tenth = weighted_cross_entropy(logits, targets, soft).item()
    assert min(full, zero) <= tenth <= max(full, zero)


def test_masked_tokens_get_no_gradient():
    logits, targets = fixture(seed=3)
    logits.requires_grad_(True)
    weights = torch.ones_like(targets, dtype=torch.float32)
    weights[:, 2] = 0.0
    weighted_cross_entropy(logits, targets, weights).backward()
    assert torch.count_nonzero(logits.grad[:, 2]) == 0
    assert torch.count_nonzero(logits.grad[:, 3]) > 0


def test_an_all_zero_batch_returns_zero_rather_than_a_nan():
    logits, targets = fixture(seed=4)
    logits.requires_grad_(True)
    loss = weighted_cross_entropy(
        logits, targets, torch.zeros_like(targets, dtype=torch.float32))
    assert loss.item() == 0.0
    loss.backward()
    assert torch.count_nonzero(logits.grad) == 0


def test_scaling_every_weight_leaves_the_loss_alone():
    """A weighted mean is scale free, so an arm that halves every weight is
    the same run, and only the ratios between tags matter."""
    logits, targets = fixture(seed=5)
    weights = torch.rand(targets.shape) + 0.1
    a = weighted_cross_entropy(logits, targets, weights).item()
    b = weighted_cross_entropy(logits, targets, weights * 4.0).item()
    assert a == pytest.approx(b, rel=1e-6)
