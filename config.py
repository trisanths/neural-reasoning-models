"""Configuration dataclasses for the latent-space translation pipeline."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelConfig:
    """Abstracts model internals so the pipeline is not hardcoded to Qwen2.5.

    To support a new model family, create a new ModelConfig with the correct
    module paths.  The pipeline code never accesses model internals directly —
    it resolves layers through these paths.
    """

    name: str = "Qwen/Qwen2.5-0.5B-Instruct"
    hidden_dim: int = 896
    num_layers: int = 24  # transformer block count (not counting embedding)

    # --- Module path templates (Python attribute access from the model root) ---
    # {i} is replaced with the layer index at runtime.
    layers_path: str = "model.layers"          # nn.ModuleList of transformer blocks
    layer_template: str = "model.layers[{i}]"  # single block
    norm_path: str = "model.norm"              # final RMSNorm / LayerNorm
    embed_path: str = "model.embed_tokens"     # input embedding table
    rotary_path: str = "model.rotary_emb"      # rotary embedding module
    lm_head_path: str = "lm_head"              # language model head


# ── Pre-built configs for the two Qwen models ──────────────────────────────

QWEN_05B_CONFIG = ModelConfig(
    name="Qwen/Qwen2.5-0.5B-Instruct",
    hidden_dim=896,
    num_layers=24,
    layers_path="model.layers",
    layer_template="model.layers[{i}]",
    norm_path="model.norm",
    embed_path="model.embed_tokens",
    rotary_path="model.rotary_emb",
    lm_head_path="lm_head",
)

QWEN_3B_CONFIG = ModelConfig(
    name="Qwen/Qwen2.5-3B-Instruct",
    hidden_dim=2048,
    num_layers=36,
    layers_path="model.layers",
    layer_template="model.layers[{i}]",
    norm_path="model.norm",
    embed_path="model.embed_tokens",
    rotary_path="model.rotary_emb",
    lm_head_path="lm_head",
)


@dataclass
class PipelineConfig:
    """All pipeline hyperparameters and flags."""

    # ── Model selection ──────────────────────────────────────────────────────
    small_model: ModelConfig = field(default_factory=lambda: QWEN_05B_CONFIG)
    large_model: ModelConfig = field(default_factory=lambda: QWEN_3B_CONFIG)

    # ── Splice points (layer indices where we extract / inject) ──────────────
    small_extract_layer: int = 24   # extract from small model after this layer
    large_inject_layer: int = 33    # inject into large model before this layer

    # DESIGN DECISION: small_extract_layer=24 means we extract the output of
    # the *last* transformer block (index 23, 0-based) since HuggingFace
    # hidden_states[i] is the output of block i-1 (hidden_states[0] = embedding).
    # In hook terms, we hook the module at layers_path index 23 (0-based) and
    # capture its output.  The config value 24 matches the CKA analysis which
    # uses the HuggingFace convention (layer count including embedding offset).
    # We convert to 0-based indexing in the hook registration code.

    # ── Injection strategy ───────────────────────────────────────────────────
    injection_mode: str = "add"  # "add" or "replace"

    # ── Coconut loop ─────────────────────────────────────────────────────────
    coconut_num_iters: int = 6       # N iterations of the tail loop
    coconut_full_loop: bool = False  # True = loop over full large model (ablation)

    # ── Quantization ─────────────────────────────────────────────────────────
    use_8bit: bool = False  # bitsandbytes 8-bit quantization fallback
    dtype: str = "float16"  # "float16" or "bfloat16"

    # ── Misc ─────────────────────────────────────────────────────────────────
    device: str = "cuda"
    seed: int = 42


@dataclass
class TrainingConfig:
    """Training loop hyperparameters."""

    # ── Optimizer ─────────────────────────────────────────────────────────────
    lr: float = 1e-4
    weight_decay: float = 0.01
    grad_clip: float = 1.0

    # ── Schedule ──────────────────────────────────────────────────────────────
    warmup_steps: int = 100
    num_epochs: int = 10
    batch_size: int = 4
    gradient_accumulation_steps: int = 4

    # ── Loss weights ──────────────────────────────────────────────────────────
    lambda_answer: float = 1.0
    lambda_cycle: float = 0.5
    lambda_align: float = 0.3

    # ── Checkpointing & evaluation ────────────────────────────────────────────
    save_every_steps: int = 500
    eval_every_steps: int = 1000
    checkpoint_dir: str = "checkpoints"

    # ── Logging ───────────────────────────────────────────────────────────────
    use_wandb: bool = True
    wandb_project: str = "latent-space-translation"
    wandb_run_name: Optional[str] = None

    # ── Data ──────────────────────────────────────────────────────────────────
    max_seq_len: int = 512
    num_workers: int = 2

    # ── Procrustes init ───────────────────────────────────────────────────────
    procrustes_num_samples: int = 200  # number of samples for Procrustes alignment


def resolve_module(model, path: str):
    """Resolve a dotted path (with optional [i] indexing) to a module.

    Examples:
        resolve_module(model, "model.layers")       -> model.model.layers
        resolve_module(model, "model.layers[0]")    -> model.model.layers[0]
        resolve_module(model, "lm_head")            -> model.lm_head
    """
    obj = model
    for part in path.split("."):
        if "[" in part:
            attr, idx = part.rstrip("]").split("[")
            obj = getattr(obj, attr)[int(idx)]
        else:
            obj = getattr(obj, part)
    return obj
