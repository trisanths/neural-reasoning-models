"""The objective: answer the question, find the page, and do not over-retrieve.

    L = sum_i P(halt at i) * CE_i                       task, PonderNet weighted
      + beta  * KL(P || truncated geometric)            ponder cost
      + alpha * -log(1 - prod_i (1 - g_i * p_i(gold)))  find the page
      + gamma * mean_i g_i                              retrieval budget

The retrieval term is a noisy-or over iterations: retrieving the gold page at
any one iteration is enough, and the gate probability multiplies inside it, so a
confident retriever behind a shut gate earns nothing and an open gate over a
confused retriever earns nothing either. That is the term that makes the query
projection and the gate learn together rather than one at a time.

The two asymmetries that give the gate something to discriminate on:

  - the retrieval term is applied only to episodes where the gold page is NOT
    already in the prompt. An in-context episode gets no upward pressure.
  - the budget term is applied to every episode.

So the only force on the gate in the in-context condition is downward, and the
only force in the retrieval condition is the noisy-or pulling it up against that
same budget. Whether the model can then tell the two conditions apart from the
recurrent state alone is the thing being measured, not the thing being taught:
nothing in the loss sees the in_context flag except through which term applies.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F

from src.latentret.gate import ponder_kl


@dataclass
class LossWeights:
    alpha: float = 1.0     # noisy-or retrieval
    beta: float = 0.01     # ponder KL
    gamma: float = 0.02    # retrieval budget
    lam_prior: float = 0.4


def noisy_or_retrieval(doc_log_probs: torch.Tensor, gate_probs: torch.Tensor,
                       gold: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """-log P(the gold page is retrieved through an open gate at some iteration).

    doc_log_probs (B, L, N), gate_probs (B, L), gold (B,) -> (B,).
    """
    b = torch.arange(gold.shape[0], device=gold.device)
    p_gold = doc_log_probs.float().exp()[b, :, gold]      # (B, L)
    miss = (1.0 - gate_probs.float() * p_gold).clamp(eps, 1.0)
    hit = (1.0 - miss.prod(dim=1)).clamp_min(eps)
    return -hit.log()


def latentret_loss(out, batch, w: LossWeights) -> tuple[torch.Tensor, dict]:
    """Total loss and the scalars worth logging."""
    bsz, loops, _ = out.logits.shape
    target = batch.answer.unsqueeze(1).expand(bsz, loops).reshape(-1)
    ce = F.cross_entropy(out.logits.reshape(bsz * loops, -1).float(), target,
                         reduction="none").view(bsz, loops)
    halt = out.halt_probs.float()
    task = (halt * ce).sum(dim=1).mean()

    ponder = ponder_kl(halt, w.lam_prior)

    need = (~batch.in_context).float()
    retrieval_per = noisy_or_retrieval(out.doc_log_probs, out.gate_probs, batch.gold)
    retrieval = (retrieval_per * need).sum() / need.sum().clamp_min(1.0)

    budget = out.gate_probs.float().mean()

    total = task + w.beta * ponder + w.alpha * retrieval + w.gamma * budget
    stats = {
        "loss": float(total.detach()),
        "task": float(task.detach()),
        "ponder": float(ponder.detach()),
        "retrieval": float(retrieval.detach()),
        "budget": float(budget.detach()),
    }
    return total, stats
