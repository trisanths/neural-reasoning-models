# Cross-model latent-space reasoning

Serve a large model's reasoning quality at close to a small model's cost, by
letting the two models exchange **continuous thoughts** instead of text.

```
user -> small model -> hidden states -> [projector up]
     -> big model's latent space -> continuous-thought reasoning (Coconut)
     -> [projector down] -> small model -> answer
```

The big model never decodes a token. The small model never re-reads the
question. Everything that crosses between them is a vector.

## Why

Reasoning models spend enormous compute emitting chain-of-thought tokens, and
latent reasoning ([Coconut](https://arxiv.org/abs/2412.06769)) is still
expensive when the model doing it is very large. If a reasoning trajectory can
be projected between two independently trained residual streams, the large model
can be used only for the steps that need its capacity.

## Result

**The handoff works — but only if the receiving model is allowed to adapt.**

Sequential-composition task, 3 chained updates in Z_10, chance = 0.112.
Small model 0.12M params (2 layers, d=64); big model 8.0M (10 layers, d=256).

| configuration | accuracy | FLOPs/query |
|---|---|---|
| small, no reasoning | 0.112 | 3.2M |
| small, explicit CoT | 1.000 | 5.8M |
| **small, Coconut — floor** | **0.684** | 4.1M |
| **big, Coconut — ceiling** | **0.997** | 316.7M |
| pipeline, *frozen* receiver | 0.749 | 241.7M |
| ↳ control: untrained big model | 0.745 | 241.7M |
| **cross-model pipeline (adapted receiver)** | **1.000** | 241.7M |
| ↳ control: random big model | 0.736 | 241.7M |

Both controls pass for the adapted pipeline: swapping the trained big model for
an untrained one of identical shape costs 0.264, so the big model's learned
computation — not the adapters — is doing the work; and the pipeline beats the
small model's own latent reasoning by 0.316, so it is not merely extra
sequential compute.

### The frozen-receiver result matters as much

With the big model **frozen**, the pipeline scores 0.749 and its control scores
0.745 — statistically the same. The gain there was entirely the LoRA adapter on
the small model; no reasoning crossed between the models at all. Only the
control revealed this.

The stage-1 gate localises the cause. Driving the big model from projected
small-model states gives:

| receiver | big-model accuracy from projected states |
|---|---|
| frozen | 0.268 |
| frozen, tapping an earlier layer | 0.096 |
| **rank-8 adapter** | **0.994** |

A frozen network cannot read another model's residual stream, because the small
model's states encode *its own* running computation rather than the token
identities the big model expects as input. A rank-8 adapter is enough to fix it.
This matches what Interlat and Cache-to-Cache actually do — both train the
receiver — and it costs nothing at inference.

The injection path itself was verified separately: feeding the big model its own
token embeddings through the same seam reproduces native accuracy exactly
(0.996 vs 0.996), so the failure was never plumbing.

See [the design doc](docs/superpowers/specs/2026-07-24-cross-model-latent-reasoning-design.md)
for scope, the deviation from the original GPT-2/ProsQA plan, and the five task
variants that had to be discarded first.

## Layout

| path | what |
|---|---|
| `src/data.py` | ProsQA-style generator (tunable hops, degree-matched distractors) |
| `src/model.py` | decoder backbone: `inputs_embeds`, KV cache, hidden states |
| `src/coconut.py` | continuous-thought loop with a `thought_hook` injection seam |
| `src/pipeline.py` | the cross-model handoff, full-context or compressed |
| `src/projectors.py` | affine/MLP maps with RMS matching; LoRA |
| `src/flops.py` | analytic per-query inference FLOPs |

## Run it

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv torch transformers
```

```bash
.venv/bin/python scripts/prepare_data.py --out data --n_hops 4
```

```bash
scripts/run_all.sh data runs/exp 16000 3
```

Tests (no GPU needed):

```bash
for f in tests/test_*.py; do .venv/bin/python "$f"; done
```

## Where the savings come from — and where they don't

The big model's cost is dominated by prefilling the question. Sending it every
projected question state costs *more* than just running the big model directly
(1.07x). Sending only `n_message` compressed states makes big-model cost scale
with `m + k` instead of question length. For a 174-token question with a
0.85M/8M model pair:

| handoff | FLOPs/query | vs big alone | vs small alone |
|---|---|---|---|
| full context | 3.44G | 1.07x | 10.1x |
| m = 32 | 932M | 0.29x | 2.7x |
| m = 16 | 674M | 0.21x | 2.0x |
| m = 8 | 546M | 0.17x | 1.6x |

Measured on the composition task, compression trades accuracy for compute:

| handoff | accuracy | FLOPs/query | vs big | vs small |
|---|---|---|---|---|
| all 13 states | 1.000 | 241.7M | 0.78x | 60.6x |
| m = 4 | 0.823 | 114.8M | 0.35x | 27.0x |

Both still beat the 0.684 floor, so the compressed variant is a usable operating
point rather than a collapse.

Be clear about what this experiment does and does not show. It demonstrates the
mechanism, that reasoning crosses between two independently trained latent
spaces. It does not demonstrate the efficiency goal. Its questions are 13 tokens
long, leaving almost nothing to compress, and the big model holds 66x the small
model's parameters, so any use of it is expensive in relative terms.

The compute case needs the regime the first table models: long contexts, where
compression removes real work, and a size ratio closer to the 1B/7B pair this
project was motivated by. The mechanism is unchanged. Only the arithmetic is.

## Controls

An accuracy number here is meaningless without these, both implemented:

1. **Random frozen big model** — if the pipeline scores the same, the projectors
   and small model learned the task themselves.
2. **Small model with matched latent steps** — separates *capacity* from merely
   spending more sequential compute.
