# Latent-Space Translation: Cross-Model Reasoning Outsourcing

A research system for outsourcing reasoning from a small language model to a large one via latent-space translation, built on top of [Facebook's Coconut](https://github.com/facebookresearch/coconut) (Chain of Continuous Thought).

## How This Extends Coconut

The original Coconut paper introduces continuous thought — replacing explicit chain-of-thought tokens with latent reasoning iterations inside a single model. This project extends that idea across model boundaries:

1. **Cross-model transfer**: Instead of iterating within one model, the small model (Qwen2.5-0.5B) hands off its internal representation to a large model (Qwen2.5-3B) for deep reasoning, then takes the result back for decoding.

2. **Tail-layer reasoning core**: The large model's last few transformer layers (33-36) act as a dedicated reasoning module. A single forward pass establishes context via KV cache for layers 0-32, then only the tail layers iterate — giving full-model context without full-model cost per iteration.

3. **Learned linear adapters**: Two bias-free linear projections translate between the 896-dim and 2048-dim latent spaces. They are initialized via Procrustes alignment on paired activations and trained with a three-component loss (answer, cycle consistency, hidden alignment).

4. **Frozen models**: Both language models remain completely frozen. Only the two adapter matrices (~3.7M parameters total) are ever updated.

## Architecture

```
Input text
    |
[Qwen2.5-0.5B layers 0-24] --> extract hidden state (896-dim)
    |
[Adapter S->L: Linear(896, 2048)] --> translated to large model space
    |
[Qwen2.5-3B full pass with injection at layer 33] --> builds KV cache
    |
[Coconut tail loop: layers 33-36 x N iterations] --> iterative reasoning
    |
[Adapter L->S: Linear(2048, 896)] --> back to small model space
    |
[Qwen2.5-0.5B final norm + LM head] --> decode to text
    |
Output text
```

## Splice Point Selection

CKA (Centered Kernel Alignment) analysis confirmed that Qwen2.5-0.5B layer 24 and Qwen2.5-3B layer 33 have near-perfect representational similarity (~1.0 CKA score), making them optimal points for cross-model transfer. The CKA analysis script is preserved in the repository history.

## Installation

```bash
pip install torch transformers datasets wandb tqdm bitsandbytes
```

## Usage

### Training
```bash
# Default settings
python main.py train

# With custom hyperparameters
python main.py train --lr 5e-5 --epochs 20 --batch-size 2 --coconut-iters 8

# Without wandb logging
python main.py train --no-wandb

# With 8-bit quantization (if VRAM is tight)
python main.py train --use-8bit

# Ablation: full Coconut loop (not just tail layers)
python main.py train --coconut-full-loop

# Custom loss weights
python main.py train --lambda-answer 1.0 --lambda-cycle 0.3 --lambda-align 0.5
```

### Evaluation
```bash
# Full evaluation (pipeline + all baselines)
python main.py eval --checkpoint checkpoints/adapter_final.pt

# Baselines only (no adapter checkpoint needed)
python main.py eval --baselines-only

# Quick eval on subset
python main.py eval --checkpoint checkpoints/adapter_final.pt --max-samples 100
```

### Debugging
```bash
# Test Procrustes initialization quality
python main.py probe
```

## Training Objective

**L = lambda_answer * L_answer + lambda_cycle * L_cycle + lambda_align * L_align**

| Loss | Default Weight | Description |
|------|---------------|-------------|
| Answer | 1.0 | Cross-entropy on GSM8K final answer tokens |
| Cycle | 0.5 | MSE(h, L2S(S2L(h))) — adapters should be approximate inverses |
| Align | 0.3 | MSE between translated state and large model's native representation |

## Baselines

The evaluation harness runs four configurations:

1. **Full pipeline** — small -> large -> small with Coconut loop
2. **Small model only** — Qwen2.5-0.5B direct generation
3. **Large model only** — Qwen2.5-3B direct generation
4. **Small + Coconut** — Qwen2.5-0.5B with Coconut loop (no cross-model transfer)

## Project Structure

```
latent-space-translation/
  config.py               # All configuration dataclasses
  main.py                 # CLI entry point
  models/
    hooks.py              # Forward hook logic (extraction + injection)
    adapters.py           # Linear adapters with Procrustes init
    coconut_loop.py       # Tail-layer Coconut loop with KV cache
    pipeline.py           # End-to-end pipeline
  training/
    losses.py             # Answer, cycle, alignment losses
    train.py              # Training loop
  data/
    gsm8k.py              # GSM8K dataset loading and formatting
  eval/
    evaluate.py           # Evaluation harness and baselines
  coconut/                # Original Coconut repo (reference)
  docs/
    superpowers/specs/    # Design documents
```

## Hardware Requirements

- **Target**: Single NVIDIA RTX 5070 Ti (16GB VRAM)
- Both models loaded in float16 with `device_map="cuda"`
- 8-bit quantization fallback via bitsandbytes (`--use-8bit`)
- Only ~3.7M adapter parameters are trained (tiny memory footprint for gradients)

## Key Design Decisions

Documented inline with `# DESIGN DECISION:` comments throughout the codebase. Major ones:

- **Tail-layer loop (default)**: Only layers 33-36 iterate, using KV cache from layers 0-32. A `--coconut-full-loop` flag enables full-model looping for ablation.
- **Injection mode "add" (default)**: Adds the translated vector to the residual stream rather than replacing it, for training stability. Configurable via `--injection-mode`.
- **Sequence-level alignment loss**: Mean-pools before MSE because the two models use different tokenizers, so token positions don't correspond 1:1.
- **Autoregressive decoding**: After the initial pipeline pass, subsequent tokens are decoded by the small model only (the large model's contribution is "baked in").

## Citation

If you use this code, please cite the original Coconut paper:

```bibtex
@article{hao2024training,
  title={Training Large Language Models to Reason in a Continuous Latent Space},
  author={Hao, Shibo and others},
  journal={arXiv preprint arXiv:2412.06769},
  year={2024}
}
```
