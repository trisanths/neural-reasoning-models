# Latent-Space Translation: Cross-Model Reasoning Outsourcing

## Overview

A system where a small language model (Qwen2.5-0.5B-Instruct) outsources reasoning to a large model (Qwen2.5-3B-Instruct) by translating hidden states between their latent spaces. The large model's tail layers act as a dedicated reasoning core that iterates on the injected representation via a Coconut-style continuous thought loop. Built on top of Facebook's Coconut repository.

## Architecture

### Data Flow

```
Input text
    |
[Small model layers 0-24] --> extract hidden state h_s
    |
[Adapter S->L: Linear(896, 2048)] --> h_translated = W_SL(h_s)
    |
[Large model full forward with injection at layer 33] --> establishes KV cache for layers 0-32
    |
[Coconut tail loop: layers 33-36 x N iterations] --> uses KV cache, feeds output back as input
    |
[Adapter L->S: Linear(2048, 896)] --> h_back = W_LS(h_final)
    |
[Small model layers 24-25] --> decode via LM head
    |
Output text
```

### Key Design Decisions

1. **Tail-layer loop (Option A)**: The Coconut loop runs only over layers 33-36, not the full model. The initial pass builds a KV cache for layers 0-32 that the loop iterations attend to. A `coconut_full_loop` flag enables full-model looping for ablation.

2. **Hybrid hooks + direct layer access**: Forward hooks handle extraction/injection at specific layers. Direct layer iteration handles the Coconut tail loop. Layer paths are abstracted behind a ModelConfig dataclass.

3. **Injection modes**: "replace" fully overwrites the residual stream; "add" adds the translated vector to it. Default is "add" for training stability.

4. **Both models frozen**: Only the two adapter nn.Linear modules are trained. Models loaded in float16 with 8-bit quantization fallback.

### Components

- `config.py` - ModelConfig (layer paths), PipelineConfig, TrainingConfig dataclasses
- `models/hooks.py` - Forward hooks for extraction and injection
- `models/adapters.py` - Linear adapters with Procrustes initialization
- `models/coconut_loop.py` - Tail-layer loop with KV cache
- `models/pipeline.py` - End-to-end pipeline
- `training/losses.py` - Answer, cycle consistency, hidden alignment losses
- `training/train.py` - Training loop
- `data/gsm8k.py` - GSM8K loading with Qwen chat template
- `eval/evaluate.py` - Evaluation with baselines

### Training Objective

L = lambda_answer * L_answer + lambda_cycle * L_cycle + lambda_align * L_align

- L_answer: Cross-entropy on final answer tokens
- L_cycle: MSE(h_s, W_LS(W_SL(h_s))) - adapter inverse consistency
- L_align: MSE between translated state and large model's native layer 33 state

### Baselines

1. Small model only (0.5B)
2. Large model only (3B)
3. Small model with Coconut loop (no cross-model transfer)
