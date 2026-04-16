"""Loss functions for training the latent-space translation adapters.

Three loss components:
  1. Answer loss: cross-entropy on final answer tokens decoded by the small model
  2. Cycle consistency loss: MSE(h_s, W_LS(W_SL(h_s)))
  3. Hidden alignment loss: MSE between translated state and large model's native
     hidden state at the injection layer
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional
from models.adapters import AdapterPair


def answer_loss(
    logits: torch.Tensor,
    labels: torch.Tensor,
) -> torch.Tensor:
    """Cross-entropy loss on the answer portion of the sequence.

    Args:
        logits: (batch, seq, vocab) model output logits
        labels: (batch, seq) token IDs with -100 for non-answer positions

    Returns:
        Scalar loss tensor.
    """
    # Standard shifted cross-entropy (predict next token). If the two streams
    # are not perfectly aligned, score only the shared prefix rather than
    # failing with a shape mismatch.
    shared_seq_len = min(logits.shape[1], labels.shape[1])
    if shared_seq_len < 2:
        return logits.new_zeros(())

    shift_logits = logits[..., : shared_seq_len - 1, :].contiguous()
    shift_labels = labels[..., 1:shared_seq_len].contiguous()

    if not torch.any(shift_labels != -100):
        return logits.new_zeros(())

    loss = F.cross_entropy(
        shift_logits.view(-1, shift_logits.size(-1)),
        shift_labels.view(-1),
        ignore_index=-100,
    )
    return loss


def cycle_consistency_loss(
    h_small: torch.Tensor,
    adapter_pair: AdapterPair,
) -> torch.Tensor:
    """MSE between the original small hidden state and its round-trip translation.

    Computes: MSE(h_small, W_LS(W_SL(h_small)))

    This forces the two adapters to be approximate inverses of each other,
    ensuring information is preserved through the translation round-trip.

    Args:
        h_small: (batch, seq, small_dim) hidden state from the small model
        adapter_pair: the adapter pair (S->L and L->S)

    Returns:
        Scalar MSE loss.
    """
    h_roundtrip = adapter_pair.forward_l2s(adapter_pair.forward_s2l(h_small))
    return F.mse_loss(h_roundtrip, h_small.detach())

    # DESIGN DECISION: We detach h_small as the target to prevent gradients
    # flowing back through the (frozen) small model.  The loss only trains
    # the adapter weights to make the round-trip reconstruction accurate.


def hidden_alignment_loss(
    h_translated: torch.Tensor,
    h_native_large: torch.Tensor,
) -> torch.Tensor:
    """MSE between the S->L translated hidden state and the large model's own
    hidden state at the injection layer for the same input.

    This acts as a regularizer ensuring the translated representation lives
    in a region of the large model's latent space that it can meaningfully
    process.

    Args:
        h_translated: (batch, seq, large_dim) output of the S->L adapter
        h_native_large: (batch, seq, large_dim) large model's own hidden state
                        at the injection layer (computed on a probe pass)

    Returns:
        Scalar MSE loss.
    """
    # DESIGN DECISION: We mean-pool over the sequence dimension before computing
    # MSE.  Token-level alignment is too strict — the models use different
    # tokenizers so token positions don't correspond 1:1.  Sequence-level
    # alignment captures the overall representation geometry.
    h_trans_pooled = h_translated.mean(dim=1)      # (batch, large_dim)
    h_native_pooled = h_native_large.mean(dim=1)   # (batch, large_dim)

    return F.mse_loss(h_trans_pooled, h_native_pooled.detach())


class CombinedLoss(nn.Module):
    """Weighted combination of all three loss components."""

    def __init__(
        self,
        lambda_answer: float = 1.0,
        lambda_cycle: float = 0.5,
        lambda_align: float = 0.3,
    ):
        super().__init__()
        self.lambda_answer = lambda_answer
        self.lambda_cycle = lambda_cycle
        self.lambda_align = lambda_align

    def forward(
        self,
        logits: torch.Tensor,
        labels: torch.Tensor,
        h_small: torch.Tensor,
        adapter_pair: AdapterPair,
        h_translated: torch.Tensor,
        h_native_large: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """Compute the combined loss.

        Args:
            logits: pipeline output logits
            labels: answer labels (-100 for masked positions)
            h_small: small model hidden state (for cycle loss)
            adapter_pair: adapter pair (for cycle loss)
            h_translated: S->L translated state (for alignment loss)
            h_native_large: large model's native state at inject layer
                           (None to skip alignment loss)

        Returns:
            Dict with 'total', 'answer', 'cycle', and optionally 'align' losses.
        """
        l_answer = answer_loss(logits, labels)
        l_cycle = cycle_consistency_loss(h_small, adapter_pair)

        total = self.lambda_answer * l_answer + self.lambda_cycle * l_cycle

        result = {
            "total": total,
            "answer": l_answer,
            "cycle": l_cycle,
        }

        if h_native_large is not None:
            l_align = hidden_alignment_loss(h_translated, h_native_large)
            total = total + self.lambda_align * l_align
            result["align"] = l_align
            result["total"] = total

        return result
