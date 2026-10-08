"""Analytic inference FLOPs.

Counts multiply-accumulates and doubles them. Attention is counted with causal
masking, so a prefill of L tokens pays L(L+1)/2 score computations per layer
rather than L^2.

Only inference is counted -- training cost is a one-off, while the claim under
test is about per-query serving cost.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Arch:
    d_model: int
    n_layers: int
    vocab_size: int
    d_ff_mult: int = 4

    @property
    def proj_macs_per_token(self) -> int:
        d = self.d_model
        # q,k,v,out = 4d^2; MLP up+down = 2 * d * (mult*d)
        return 4 * d * d + 2 * self.d_ff_mult * d * d


def prefill_flops(a: Arch, n_tokens: int) -> int:
    """Cost of encoding a fresh sequence of ``n_tokens``."""
    proj = a.n_layers * n_tokens * a.proj_macs_per_token
    # QK^T and attn@V, causal.
    pairs = n_tokens * (n_tokens + 1) // 2
    attn = a.n_layers * 2 * pairs * a.d_model
    return 2 * (proj + attn)


def step_flops(a: Arch, ctx_len: int) -> int:
    """Cost of one incremental position attending to ``ctx_len`` cached keys."""
    proj = a.n_layers * a.proj_macs_per_token
    attn = a.n_layers * 2 * ctx_len * a.d_model
    return 2 * (proj + attn)


def lm_head_flops(a: Arch, n_tokens: int) -> int:
    return 2 * n_tokens * a.d_model * a.vocab_size


def coconut_flops(a: Arch, n_question: int, k_latent: int, n_decode: int) -> int:
    """Single-model Coconut: prefill, k latent steps, then decode."""
    total = prefill_flops(a, n_question)
    ctx = n_question
    for _ in range(k_latent):
        total += step_flops(a, ctx)
        ctx += 1
    total += step_flops(a, ctx)  # <eot>
    ctx += 1
    for _ in range(n_decode):
        total += step_flops(a, ctx)
        ctx += 1
    total += lm_head_flops(a, n_decode + 1)
    return total


def cot_flops(a: Arch, n_question: int, n_cot: int, n_decode: int) -> int:
    """Explicit chain of thought: every reasoning token is generated."""
    total = prefill_flops(a, n_question)
    ctx = n_question
    for _ in range(n_cot + n_decode):
        total += step_flops(a, ctx)
        ctx += 1
    total += lm_head_flops(a, n_cot + n_decode)
    return total


def pipeline_flops(
    small: Arch,
    big: Arch,
    n_question: int,
    k_latent: int,
    n_decode: int,
    d_small: int | None = None,
    d_big: int | None = None,
    n_message: int | None = None,
) -> dict:
    """Cross-model pipeline.

    The small model prefills the question; the big model prefills the projected
    states and runs the latent steps but never decodes; the small model consumes
    the returned thoughts from its existing cache and decodes the answer.

    With ``n_message`` set, only that many compressed states cross to the big
    model, so the big model's cost stops scaling with question length -- this is
    where the pipeline's savings actually come from.
    """
    d_s = d_small or small.d_model
    d_b = d_big or big.d_model
    n_up = n_question if n_message is None else n_message

    small_cost = prefill_flops(small, n_question)
    big_cost = prefill_flops(big, n_up)

    ctx = n_up
    for _ in range(k_latent):
        big_cost += step_flops(big, ctx)
        ctx += 1

    ctx = n_question
    for _ in range(k_latent):
        small_cost += step_flops(small, ctx)
        ctx += 1
    small_cost += step_flops(small, ctx)  # <eot>
    ctx += 1
    for _ in range(n_decode):
        small_cost += step_flops(small, ctx)
        ctx += 1
    small_cost += lm_head_flops(small, n_decode + 1)

    # Projections: up over the transmitted states, down over the k thoughts.
    proj_cost = 2 * (n_up * d_s * d_b + k_latent * d_b * d_s)

    return {
        "small": small_cost,
        "big": big_cost,
        "proj": proj_cost,
        "total": small_cost + big_cost + proj_cost,
    }


def fmt(x: float) -> str:
    for unit, scale in [("T", 1e12), ("G", 1e9), ("M", 1e6), ("K", 1e3)]:
        if abs(x) >= scale:
            return f"{x / scale:.2f}{unit}"
    return f"{x:.0f}"
