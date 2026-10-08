"""Pointer-generator output head: select a span from the evidence, or generate.

The measured failure this exists to fix is not retrieval. On the routing-table
family the model was handed the page that says a request is handled by the
tutez desk and answered "wrenbra desk": two real syllables from the family's
name pool, assembled by the vocabulary head, present nowhere in the page it had
just read. On the web questions the correct Britannica page reached the context
in 12 of 60 cases and the answer span was extracted in none of them. On the
arithmetic families the score with the right textbook and the wrong textbook
was 0.104 against 0.098, which is what "the evidence is not reaching the output
distribution" looks like when you measure it.

In every one of those cases the answer exists verbatim in the evidence. A
softmax over 32768 vocabulary entries has to rediscover that string through the
lm_head; a softmax over the few hundred positions of the evidence only has to
point at it. So selection is made the natural output space and generation the
fallback, which is the pointer-generator arrangement of See, Liu and Manning
(2017), itself the pointer network of Vinyals, Fortunato and Jaitly (2015) mixed
with an ordinary language-model head.

The head produces three things from the decoder state h_t and the evidence
states e_1..e_M with their token ids w_1..w_M:

    vocabulary       P_vocab(.)  = softmax(lm_head(h_t))
    copy             a_t(m)      = softmax_m(<W_q h_t, W_k e_m> / sqrt(d))
    gate             g_t         = sigmoid(W_g [h_t ; c_t] + b),  c_t = sum_m a_t(m) W_v e_m

and mixes them over the extended vocabulary:

    P(w) = g_t * P_vocab(w) + (1 - g_t) * sum_{m : w_m = w} a_t(m)

The extended vocabulary is the vocabulary plus the evidence positions mapped
back to their token ids. With a byte-level BPE there are no out-of-vocabulary
tokens, so that mapping is into the ordinary vocabulary and the extension is
the identity: every unit of copy mass lands on a real vocabulary id and the two
paths compete for the same softmax slots. That is the point. The copy path does
not add new symbols, it adds a second, much cheaper route to the symbols that
are already there.

Everything after the projections runs in float32 inside an autocast-disabled
region, so the head is exact under bf16 autocast rather than merely tolerable.
The mixture is assembled in log space: log g and log (1 - g) come from
logsigmoid, the copy mass is scattered into vocabulary slots as a shifted
log-sum-exp, and the two terms meet in logaddexp. A target token that the
vocabulary path has all but ruled out still gets a finite log probability from
the copy path, which is exactly the regime this head is meant to rescue and
exactly the regime a probability-space mixture would flush to zero.

Memory. The mixture is a (B, T, V) object, so at V = 32768 a full sequence of
768 positions costs about 1.6 GiB per tensor. Under the partitioned objective
only the authored positions are ever supervised, and there are a handful of
those per example, so pass `select` with the supervised positions and the head
works on (B, K, V) instead. src/train/pointer_data.py hands out exactly that
index tensor.
"""

from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

IGNORE_INDEX = -100

# A finite stand-in for log(0) in the final mixture. Minus infinity is the
# right answer in the forward pass and a NaN factory in the backward one:
# logaddexp differentiates to exp(term - result), and where both terms are
# minus infinity that is exp(nan), which then multiplies an upstream zero into
# a NaN. exp(-1e30) is zero in float32, so flooring here costs nothing that a
# float32 probability could represent and it keeps every gradient finite.
LOG_ZERO = -1e30
# Smallest positive float32 normal, used to keep log() off zero. The entries it
# rescues are masked out of the gradient path by the guard around it.
TINY = 1e-38


@dataclass
class PointerConfig:
    """The model.pointer block of a config.

    d_attn          width of the query and key projections, default d_model
    evidence_dim    width of the evidence states, default d_model. Set it when
                    the states come from a separate encoder rather than from
                    the decoder's own residual stream.
    gate_bias_init  bias of the gate before training. Zero puts the gate at
                    0.5, so both paths carry gradient from the first step.
                    Positive favours the vocabulary, negative favours copying.
    """

    d_attn: int | None = None
    evidence_dim: int | None = None
    gate_bias_init: float = 0.0

    def __post_init__(self):
        if self.d_attn is not None and self.d_attn < 1:
            raise ValueError("pointer.d_attn must be at least 1")
        if self.evidence_dim is not None and self.evidence_dim < 1:
            raise ValueError("pointer.evidence_dim must be at least 1")


@dataclass
class PointerOutput:
    """What the head produced, for the loss and for diagnostics.

    log_probs       (B, K, V) log of the mixture, the model's real output
    log_p_vocab     (B, K, V) log of the vocabulary path alone
    log_p_copy      (B, K, M) log of the copy distribution over evidence
                    positions, a proper distribution over the unmasked ones
    log_copy_vocab  (B, K, V) log of the copy path's mass after it has been
                    summed into vocabulary slots, before the gate
    gate            (B, K, 1) the mixing weight on the vocabulary path
    """

    log_probs: torch.Tensor
    log_p_vocab: torch.Tensor
    log_p_copy: torch.Tensor
    log_copy_vocab: torch.Tensor
    gate: torch.Tensor

    @property
    def copy_weight(self) -> torch.Tensor:
        """1 - gate: how much of the output distribution came from selection."""
        return 1.0 - self.gate

    def copy_mass_of(self, token_ids: torch.Tensor) -> torch.Tensor:
        """Gated copy probability of the given token ids, shape (B, K).

        token_ids broadcasts against (B, K); pass a target vector to see how
        much of a token's probability the head got by pointing rather than by
        generating.
        """
        ids = token_ids.expand(self.log_copy_vocab.shape[:2])
        picked = self.log_copy_vocab.gather(2, ids[..., None].long()).squeeze(2)
        return picked.exp()


class PointerHead(nn.Module):
    """Attention-scored copy distribution plus a scalar gate over the lm_head.

    The head owns no vocabulary matrix. It reads the vocabulary logits the
    model already computed, so turning it on adds
    2 * d_model * d_attn + d_evidence * d_attn + (d_model + d_attn) + 1
    parameters and nothing that scales with the vocabulary.
    """

    def __init__(self, d_model: int, vocab_size: int, cfg: PointerConfig | dict | None = None):
        super().__init__()
        if cfg is None:
            cfg = PointerConfig()
        elif isinstance(cfg, dict):
            cfg = PointerConfig(**cfg)
        self.cfg = cfg
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.d_attn = cfg.d_attn or d_model
        self.d_evidence = cfg.evidence_dim or d_model
        self.wq = nn.Linear(d_model, self.d_attn, bias=False)
        self.wk = nn.Linear(self.d_evidence, self.d_attn, bias=False)
        self.wv = nn.Linear(self.d_evidence, self.d_attn, bias=False)
        self.gate_proj = nn.Linear(d_model + self.d_attn, 1, bias=True)
        self.reset_parameters()

    def reset_parameters(self) -> None:
        for linear in (self.wq, self.wk, self.wv):
            nn.init.normal_(linear.weight, mean=0.0, std=0.02)
        # The gate projection starts small but not zero, so the gate begins at
        # roughly sigmoid(gate_bias_init) for every token. Zero would be tidier
        # and it is what the cross-attention gate does, but there the gate
        # multiplies the layer's whole output and zero is a deliberate exact
        # no-op. Here the gate is the only consumer of the value projection, so
        # a zero weight makes d(loss)/d(W_v) exactly zero and the value path
        # would stay frozen until the gate weight had moved on its own.
        nn.init.normal_(self.gate_proj.weight, mean=0.0, std=0.02)
        nn.init.constant_(self.gate_proj.bias, self.cfg.gate_bias_init)

    def num_params(self) -> int:
        return sum(p.numel() for p in self.parameters())

    # ---------------- the mixture ----------------

    def forward(self, hidden: torch.Tensor, evidence_states: torch.Tensor,
                evidence_ids: torch.Tensor, evidence_mask: torch.Tensor | None = None,
                vocab_logits: torch.Tensor | None = None,
                gate_override: float | None = None,
                select: torch.Tensor | None = None) -> PointerOutput:
        """Mix the vocabulary head with a copy distribution over the evidence.

        hidden          (B, T, d_model) decoder states, post final norm
        evidence_states (B, M, d_evidence) one state per evidence position
        evidence_ids    (B, M) the vocabulary id sitting at each position
        evidence_mask   (B, M) True where a position is real, None for all real
        vocab_logits    (B, T, V) the lm_head output for `hidden`; required
        gate_override   force the gate to this constant, for diagnostics. 1.0
                        recovers the vocabulary head exactly, 0.0 gives a pure
                        copy distribution that is zero off the evidence.
        select          (B, K) decoder positions to evaluate, which keeps the
                        (B, K, V) mixture off the full sequence length

        A row whose evidence is entirely masked falls back to the vocabulary
        path exactly, rather than producing a softmax over nothing.
        """
        if vocab_logits is None:
            raise ValueError("PointerHead needs the vocabulary logits it should mix with")
        if select is not None:
            width = hidden.shape[-1]
            index = select[..., None]
            hidden = hidden.gather(1, index.expand(-1, -1, width))
            if vocab_logits.shape[1] != select.shape[1]:
                vocab_logits = vocab_logits.gather(1, index.expand(-1, -1, vocab_logits.shape[-1]))
        if evidence_mask is None:
            evidence_mask = torch.ones(evidence_ids.shape, dtype=torch.bool,
                                       device=evidence_ids.device)
        evidence_mask = evidence_mask.bool()

        # Everything below is float32 whatever autocast is doing outside. The
        # projections are small and the mixture is a log-space object; running
        # it in bf16 would cost more accuracy than the compute is worth.
        with torch.autocast(device_type=hidden.device.type, enabled=False):
            h = hidden.float()
            e = evidence_states.float()
            q = F.linear(h, self.wq.weight.float())
            k = F.linear(e, self.wk.weight.float())
            v = F.linear(e, self.wv.weight.float())

            scores = torch.matmul(q, k.transpose(1, 2)) / (self.d_attn ** 0.5)
            live = evidence_mask[:, None, :]
            row_ok = evidence_mask.any(-1)[:, None, None]
            # A dead row would make the softmax below all -inf and produce NaN,
            # so it is scored flat here and then given zero weight through the
            # gate. Nothing downstream ever reads its copy distribution.
            scores = torch.where(live, scores, torch.full_like(scores, float("-inf")))
            scores = torch.where(row_ok, scores, torch.zeros_like(scores))
            log_p_copy = F.log_softmax(scores, dim=-1)

            context = torch.matmul(log_p_copy.exp(), v)
            gate_logit = F.linear(
                torch.cat([h, context], dim=-1),
                self.gate_proj.weight.float(), self.gate_proj.bias.float(),
            )
            if gate_override is None:
                log_g = F.logsigmoid(gate_logit)
                log_1mg = F.logsigmoid(-gate_logit)
                gate = gate_logit.sigmoid()
            else:
                g = float(gate_override)
                if not 0.0 <= g <= 1.0:
                    raise ValueError("gate_override must lie in [0, 1]")
                gate = torch.full_like(gate_logit, g)
                log_g = torch.log(gate)
                log_1mg = torch.log1p(-gate)
            # Dead rows are pure vocabulary: gate one, copy weight zero.
            log_g = torch.where(row_ok, log_g, torch.zeros_like(log_g))
            log_1mg = torch.where(row_ok, log_1mg,
                                  torch.full_like(log_1mg, float("-inf")))
            gate = torch.where(row_ok, gate, torch.ones_like(gate))

            log_p_vocab = F.log_softmax(vocab_logits.float(), dim=-1)
            log_copy_vocab = self._scatter_copy(log_1mg + log_p_copy, evidence_ids)
            log_copy_vocab = log_copy_vocab.clamp(min=LOG_ZERO)
            log_probs = torch.logaddexp(
                (log_g + log_p_vocab).clamp(min=LOG_ZERO), log_copy_vocab
            )

        return PointerOutput(
            log_probs=log_probs,
            log_p_vocab=log_p_vocab,
            log_p_copy=log_p_copy,
            log_copy_vocab=log_copy_vocab,
            gate=gate,
        )

    def _scatter_copy(self, log_mass: torch.Tensor, evidence_ids: torch.Tensor) -> torch.Tensor:
        """Sum the copy mass of every evidence position into its token's slot.

        log_mass is (B, K, M) and holds log((1 - g) * a(m)); the result is
        (B, K, V) and holds the log of the sum over the positions carrying each
        token, minus infinity for tokens the evidence does not contain. The sum
        is shifted by the row maximum before exponentiating, which is the
        ordinary log-sum-exp trick: terms more than about e^-87 below the
        largest one flush to zero, and a term that small cannot move a float32
        probability that already holds the largest one.
        """
        bsz, width, n_pos = log_mass.shape
        index = evidence_ids[:, None, :].expand(bsz, width, n_pos).long()
        shift = log_mass.amax(dim=-1, keepdim=True)
        # An all -inf row (a fully masked bank) would give -inf - -inf = NaN.
        shift = torch.where(torch.isneginf(shift), torch.zeros_like(shift), shift)
        acc = torch.zeros(bsz, width, self.vocab_size, dtype=log_mass.dtype,
                          device=log_mass.device)
        acc.scatter_add_(2, index, torch.exp(log_mass - shift))
        # Minus infinity is the right forward answer for a token the evidence
        # does not hold, but log() differentiates to 1/acc, so taking it at zero
        # would send an upstream zero through 0/0. The clamp keeps the log node
        # finite and the where keeps the clamped entries out of the result.
        log_acc = torch.where(acc > 0, torch.log(acc.clamp(min=TINY)),
                              torch.full_like(acc, float("-inf")))
        return shift + log_acc


def pointer_cross_entropy(log_probs: torch.Tensor, targets: torch.Tensor,
                          ignore_index: int = IGNORE_INDEX) -> torch.Tensor:
    """Mean negative log likelihood of the targets under the mixture.

    log_probs is already normalized, so this is nll_loss rather than
    cross_entropy. The reduction matches F.cross_entropy: a mean over the
    positions that are not ignore_index.
    """
    vocab = log_probs.shape[-1]
    return F.nll_loss(
        log_probs.reshape(-1, vocab).float(),
        targets.reshape(-1),
        ignore_index=ignore_index,
    )


def copy_fraction(out: PointerOutput, targets: torch.Tensor,
                  ignore_index: int = IGNORE_INDEX) -> float:
    """Share of the supervised targets' probability that came from copying.

    A diagnostic for training logs: it answers "is the head actually pointing",
    which is a different question from "is the loss going down".
    """
    keep = targets != ignore_index
    if not bool(keep.any()):
        return float("nan")
    safe = targets.clamp(min=0)[..., None]
    total = out.log_probs.gather(2, safe).squeeze(2).exp()
    copied = out.log_copy_vocab.gather(2, safe).squeeze(2).exp()
    denom = total[keep].sum()
    if float(denom) == 0.0:
        return float("nan")
    return float(copied[keep].sum() / denom)
