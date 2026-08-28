"""Parameter counts and FLOPs, from the same formulas the trainer implies.

Every number here is derived from a config, never guessed. The parameter
count is exact for src/train's llama-style block and is checked in the tests
against the independent count that scripts/bench_evidence.py printed on the
L40S (375,440,384 total, 308,331,520 non-embedding for the 350M config).

The FLOPs figures are the standard dense-transformer estimates:

    training   6 * P * T      forward, backward, and weight gradients over
                              T tokens with P non-embedding parameters
    inference  2 * P * (C+G)  one forward pass over C context tokens and G
                              generated tokens

Both drop the attention term, which is under five percent of the total at
these widths and context lengths, and both drop the embedding and LM-head
matmuls. They are comparable across our runs, which is what the frontier
needs; they are not a substitute for a profiler.
"""

from __future__ import annotations

from typing import Any


def param_counts(
    *,
    d_model: int,
    n_layers: int,
    d_ff: int,
    vocab_size: int,
    n_heads: int | None = None,
    n_kv_heads: int | None = None,
    tie_embeddings: bool = False,
    loops: int | None = None,
    core_layers: int | None = None,
) -> dict[str, int]:
    """Exact parameter count for the project's llama-style decoder.

    Per layer: attention q/k/v/o projections plus a SwiGLU MLP with three
    d_model x d_ff matrices, plus two RMSNorm vectors. One final RMSNorm.
    Embeddings and LM head are separate d_model x vocab matrices unless
    ``tie_embeddings``.

    ``loops`` describes the weight-tied looped core: the weights are shared,
    so the parameter count does not change, but the compute does. Pass it to
    ``effective_layer_passes`` instead.
    """
    if n_kv_heads is None or n_heads is None or n_kv_heads == n_heads:
        attn = 4 * d_model * d_model
    else:
        head_dim = d_model // n_heads
        attn = (2 * d_model * d_model
                + 2 * d_model * n_kv_heads * head_dim)
    mlp = 3 * d_model * d_ff
    per_layer = attn + mlp + 2 * d_model
    decoder = n_layers * per_layer + d_model  # + final norm
    embedding = vocab_size * d_model
    lm_head = 0 if tie_embeddings else vocab_size * d_model
    total = decoder + embedding + lm_head
    return {
        "params_total": int(total),
        "params_non_embedding": int(decoder),
        "params_embedding": int(embedding + lm_head),
        "params_per_layer": int(per_layer),
    }


def param_counts_from_config(model_cfg: dict[str, Any]) -> dict[str, int]:
    """Parameter count straight off a run's ``config.yaml`` model block."""
    recurrent = model_cfg.get("recurrent") or {}
    return param_counts(
        d_model=int(model_cfg["d_model"]),
        n_layers=int(model_cfg["n_layers"]),
        d_ff=int(model_cfg["d_ff"]),
        vocab_size=int(model_cfg["vocab_size"]),
        n_heads=model_cfg.get("n_heads"),
        n_kv_heads=model_cfg.get("n_kv_heads"),
        tie_embeddings=bool(model_cfg.get("tie_embeddings", False)),
        loops=recurrent.get("loops"),
        core_layers=recurrent.get("core_layers"),
    )


def effective_layer_passes(model_cfg: dict[str, Any]) -> float:
    """Layer executions per token, which is what compute scales with.

    A dense stack runs each layer once. A weight-tied looped core runs its
    core layers ``loops`` times, so the same parameters cost more FLOPs.
    Returns a multiplier on ``n_layers``.
    """
    n_layers = int(model_cfg["n_layers"])
    rec = model_cfg.get("recurrent") or {}
    loops = rec.get("loops")
    core = rec.get("core_layers")
    if not loops or not core:
        return 1.0
    prelude = int(rec.get("prelude_layers", 0))
    coda = int(rec.get("coda_layers", 0))
    passes = prelude + int(core) * int(loops) + coda
    return passes / n_layers


def compute_params(non_embedding: int, model_cfg: dict[str, Any] | None = None) -> float:
    """Parameters as seen by the FLOPs formulas, after any loop multiplier."""
    if model_cfg is None:
        return float(non_embedding)
    return float(non_embedding) * effective_layer_passes(model_cfg)


def training_tokens(schedule: dict[str, Any], train: dict[str, Any],
                    model_cfg: dict[str, Any]) -> int:
    """Tokens consumed by a full run: steps x global batch x context."""
    steps = int(schedule["max_steps"])
    batch = int(train["batch_size"])
    accum = int(train.get("grad_accum_steps", 1))
    seq = int(model_cfg["max_seq_len"])
    return steps * batch * accum * seq


def training_flops(params_non_embedding: float, tokens: float) -> float:
    """6 * P * T."""
    return 6.0 * float(params_non_embedding) * float(tokens)


def decode_flops_per_answer(params_non_embedding: float,
                            generated_tokens: float) -> float:
    """2 * P * G: the decode half of one answer, ignoring the prompt."""
    return 2.0 * float(params_non_embedding) * float(generated_tokens)


def inference_flops_per_answer(params_non_embedding: float,
                               context_tokens: float,
                               generated_tokens: float) -> float:
    """2 * P * (C + G): the whole forward cost of one answer."""
    return 2.0 * float(params_non_embedding) * (
        float(context_tokens) + float(generated_tokens))
