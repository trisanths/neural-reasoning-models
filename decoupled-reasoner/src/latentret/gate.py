"""The gate read from the recurrent state: halt or continue, retrieve or not.

Two signals, not one. "I have what I need" and "I am missing something" are
different claims about the same state, and collapsing them into a single head
would make the halting decision and the retrieval decision inseparable, which
is exactly the thing this experiment wants to look at.

The retrieve probability multiplies the injection, so it sits on the gradient
path of the task loss as well as the retrieval loss. If pulling a document in
does not help the answer, the task loss can close the gate on its own.

Halting follows PonderNet: lambda_i is the probability of halting at iteration i
given that iteration i was reached, the halting distribution is the resulting
geometric-like product, and the task loss is the expectation of the per
iteration losses under it. The last iteration halts with probability one so the
distribution sums to one at any loop count.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from src.train.model import RMSNorm


class RetrievalGate(nn.Module):
    """A two logit head on the core's hidden state at one position.

    The output layer starts at zero with a halt bias below zero, so an untrained
    gate keeps running and retrieves with probability one half. Starting the
    retrieve logit at zero rather than negative matters for the same reason the
    RL configs use a retrieval bonus: a gate that starts shut sees no gradient
    from anything downstream of the injection.
    """

    def __init__(self, d_model: int, hidden: int | None = None,
                 norm_eps: float = 1e-5, halt_bias: float = -2.0,
                 retrieve_bias: float = 0.0):
        super().__init__()
        hidden = hidden or max(32, d_model // 2)
        self.norm = RMSNorm(d_model, norm_eps)
        self.fc1 = nn.Linear(d_model, hidden)
        self.fc2 = nn.Linear(hidden, 2)
        nn.init.zeros_(self.fc2.weight)
        with torch.no_grad():
            self.fc2.bias.copy_(torch.tensor([halt_bias, retrieve_bias]))

    def forward(self, state: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """(B, D) state to (halt_logit, retrieve_logit), each (B,)."""
        h = torch.nn.functional.silu(self.fc1(self.norm(state)))
        halt, retrieve = self.fc2(h).unbind(-1)
        return halt, retrieve


def halting_distribution(halt_logits: torch.Tensor, eps: float = 1e-4) -> torch.Tensor:
    """(B, L) halt logits to (B, L) probabilities of halting at each iteration.

    The last iteration takes whatever probability is left, so the rows sum to
    one whatever the loop count is.
    """
    lam = torch.sigmoid(halt_logits.float()).clamp(eps, 1.0 - eps)
    remain = torch.cumprod(1.0 - lam, dim=1)
    shifted = torch.cat([torch.ones_like(remain[:, :1]), remain[:, :-1]], dim=1)
    probs = lam * shifted
    probs = torch.cat([probs[:, :-1], shifted[:, -1:]], dim=1)
    return probs


def ponder_kl(probs: torch.Tensor, lam_prior: float = 0.4) -> torch.Tensor:
    """KL of the halting distribution from a truncated geometric prior.

    Keeps the model from halting at iteration one before the gate has learned
    anything, which would leave the later iterations untrained.
    """
    loops = probs.shape[1]
    idx = torch.arange(loops, device=probs.device, dtype=torch.float32)
    prior = lam_prior * (1.0 - lam_prior) ** idx
    prior = prior / prior.sum()
    p = probs.clamp_min(1e-8)
    return (p * (p.log() - prior.log().unsqueeze(0))).sum(-1).mean()
