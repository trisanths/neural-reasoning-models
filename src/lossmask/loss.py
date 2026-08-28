"""Per token cross entropy weighted by a mask, and its normalization.

The normalization is the whole design decision here. Dividing the weighted
sum by the token count would make an arm that zeroes fifteen percent of its
tokens train at roughly eighty five percent of the control's loss and so at
eighty five percent of its gradient scale, and the four way table would then
be reading a learning rate difference as a masking effect. Dividing by the
sum of the weights instead keeps the mean surviving token contributing what
it contributes in the control, so the arms differ in which tokens are learned
and in nothing else.

With every weight at one the result is F.cross_entropy's default mean, to
floating point. src/lossmask/tests/test_loss.py pins that.
"""

import torch
import torch.nn.functional as F


def weighted_cross_entropy(logits: torch.Tensor, targets: torch.Tensor,
                           weights: torch.Tensor) -> torch.Tensor:
    """Mean cross entropy over the target tokens, weighted per token.

    logits is (B, T, V), targets and weights are (B, T). The return is a
    scalar: sum(w * ce) / sum(w). A batch whose weights are all zero has no
    gradient to give and returns zero rather than a division by zero.
    """
    vocab = logits.shape[-1]
    per_token = F.cross_entropy(
        logits.float().view(-1, vocab), targets.reshape(-1), reduction="none")
    w = weights.reshape(-1).to(per_token.dtype)
    total = w.sum()
    if float(total) == 0.0:
        return (per_token * w).sum()
    return (per_token * w).sum() / total
