"""One training step of the latent chain, and the counters it spends.

The chain is n_latent + 1 forward passes. Pass r carries r filled latent
positions and no placeholders, and it does two things: it produces the vector
that pass r + 1 will inject, and it gives the loss of answering after exactly r
latent steps. The last pass has every latent filled and is where the default
objective reads its loss.

Building each pass at its own length rather than masking a fixed length matters
for the same reason the eval must report a shape rather than a value. If the
unfilled slots stayed in the sequence, the answer positions would attend to
placeholder tokens, and the loss at pass r would not be the loss of answering
after r latent steps. It would be the loss of answering after r latent steps
with n_latent - r blanks in the way, which is not a quantity anything wants.

Because every pass already computes states at every position, the per step
losses that PonderNet needs cost one extra projection over the supervised span
and no extra forward pass.
"""

from __future__ import annotations

import time
from contextlib import nullcontext
from dataclasses import dataclass, field

import torch
import torch.nn.functional as F

from src.latent.core import (compress_index, gather_at, scatter_at,
                             trunk_from_embeds)
from src.opgraph.data import IGNORE


@dataclass
class ChainCost:
    """What one chain actually spent, in units nothing can hide behind."""

    passes: int = 0                 # trunk forward passes
    positions: int = 0              # token positions run through the trunk
    reason_passes: int = 0          # of those, the ones spent on latent steps
    reason_positions: int = 0
    layer_apps: int = 0             # positions times the layers each ran
    seconds: float = 0.0
    reason_seconds: float = 0.0

    def add(self, other: "ChainCost") -> None:
        for f in ("passes", "positions", "reason_passes", "reason_positions",
                  "layer_apps", "seconds", "reason_seconds"):
            setattr(self, f, getattr(self, f) + getattr(other, f))

    def as_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in
                self.__dataclass_fields__.values()}


@dataclass
class ChainOut:
    loss: torch.Tensor
    per_pass: list = field(default_factory=list)
    halt_probs: torch.Tensor | None = None
    ponder: torch.Tensor | None = None
    cost: ChainCost = field(default_factory=ChainCost)


def span_loss(model, h, sel, tgt, rows: bool = False):
    """Cross entropy over the supervised span only.

    The arms project the whole sequence to the vocabulary and let IGNORE do the
    masking. Only the target span is ever supervised here, and the chain runs
    the trunk n_latent + 1 times, so projecting every position that many times
    would spend most of the step on states nothing reads. Gathering first gives
    the same number.
    """
    d = h.shape[-1]
    idx = sel.clamp(min=0)[..., None].expand(-1, -1, d)
    logits = model.lm_head(h.gather(1, idx))
    v = logits.shape[-1]
    if not rows:
        return F.cross_entropy(logits.float().view(-1, v), tgt.reshape(-1))
    ce = F.cross_entropy(logits.float().view(-1, v), tgt.reshape(-1),
                         reduction="none").view(tgt.shape)
    keep = (tgt != IGNORE).float()
    return (ce * keep).sum(1) / keep.sum(1).clamp_min(1.0)


def run_chain(model, head, batch, *, loss_at: str = "last", gate=None,
              ponder_beta: float = 0.01, backprop_last_k: int | None = None,
              loops: int | None = None, layers_per_pass: int | None = None,
              time_it: bool = False) -> ChainOut:
    """Fill the latent chain and return the objective.

    loss_at "last" takes the loss from the pass with every latent filled, which
    is the fixed R objective. loss_at "all" computes it at every pass, which is
    what a halting gate weights. A gate turns the objective into PonderNet's:
    the expectation of the per pass losses under the halting distribution, plus
    a KL to a truncated geometric prior so the gate cannot halt at pass zero
    before anything downstream has been trained.
    """
    ids = batch["ids"]
    first = batch["first_latent"]
    n_latent = int(batch["n_latent"])
    sel, tgt = batch["sel"], batch["tgt"]
    width = ids.shape[1]
    n_pass = n_latent + 1
    depth = layers_per_pass if layers_per_pass is not None else \
        model.cfg.effective_depth(model.resolve_loops(loops))
    want_rows = gate is not None
    if gate is not None:
        loss_at = "all"

    zs: list[torch.Tensor] = []
    per_pass: list = []
    halts: list = []
    cost = ChainCost()
    for r in range(n_pass):
        if time_it and ids.is_cuda:
            torch.cuda.synchronize()
        t0 = time.perf_counter() if time_it else 0.0
        idx = compress_index(first, n_latent, r, width)
        ids_r = ids.gather(1, idx)
        emb = model.tok_emb(ids_r)
        for j in range(r):
            emb = scatter_at(emb, first + j, zs[j])
        detach = (backprop_last_k is not None
                  and r < n_pass - int(backprop_last_k))
        with (torch.no_grad() if detach else nullcontext()):
            h = trunk_from_embeds(model, emb, loops)
        if detach:
            h = h.detach()
        if loss_at == "all" or r == n_pass - 1:
            per_pass.append(span_loss(model, h, sel - (n_latent - r), tgt,
                                      rows=want_rows))
        else:
            per_pass.append(None)
        produce = gather_at(h, first + r - 1)
        if gate is not None:
            halts.append(gate(produce)[0])
        if r < n_latent:
            zs.append(head(produce, r))
        if time_it and ids.is_cuda:
            torch.cuda.synchronize()
        dt = (time.perf_counter() - t0) if time_it else 0.0
        cost.passes += 1
        cost.positions += int(ids_r.numel())
        cost.layer_apps += int(ids_r.numel()) * depth
        cost.seconds += dt
        if r < n_latent:
            cost.reason_passes += 1
            cost.reason_positions += int(ids_r.numel())
            cost.reason_seconds += dt

    out = ChainOut(loss=per_pass[-1], per_pass=per_pass, cost=cost)
    if gate is not None:
        from src.latentret.gate import halting_distribution, ponder_kl
        halt_logits = torch.stack(halts, dim=1)
        probs = halting_distribution(halt_logits)
        stacked = torch.stack(per_pass, dim=1)
        out.halt_probs = probs
        out.ponder = ponder_kl(probs)
        out.loss = (probs * stacked).sum(1).mean() + ponder_beta * out.ponder
    return out
