# Cross-model latent reasoning handoff — design

**Date:** 2026-07-24
**Status:** implemented (proof of concept)

## Goal

Serve big-model reasoning quality at close to small-model cost, by keeping the
user-facing model small and delegating only the *reasoning* to a large model —
in latent space, without ever decoding tokens between them.

```
user -> small model -> hidden states -> [projector up]
     -> big model's latent space -> continuous-thought reasoning
     -> [projector down] -> small model -> answer
```

The motivation is that today's reasoning models emit enormous numbers of
chain-of-thought tokens, and even latent reasoning (Coconut) is expensive when
run on a very large model. If reasoning state can cross between two models'
residual streams, the large model can be used for the few steps that need its
capacity and nothing else.

## Scope of this proof of concept

The question under test is narrow and mechanistic:

> Can a reasoning trajectory produced in one model's latent space be projected
> into another independently trained model's latent space and still carry the
> reasoning?

To answer that cleanly the testbed must satisfy one property above all: **the
small model must fail the task and the big model must succeed**. Without that
gap there is nothing for the pipeline to close and the result is uninterpretable.

### Deviation from the original plan

The approved design specified GPT-2 small → GPT-2 medium on ProsQA. Measurement
on the target hardware (M2 Pro, 16 GB, already under memory pressure) showed the
reference recipe — GPT-2, ~360-token contexts, 50 epochs, 4 GPUs — is roughly
three orders of magnitude out of budget; a GPT-2-medium training step at seq 448
thrashed swap rather than computing.

The testbed was therefore rescaled while preserving the science:

| | original | implemented |
|---|---|---|
| task | ProsQA (fixed) | ProsQA-style generator, tunable hops/branching |
| context | ~360 tokens | ~174 tokens (~99 in the easy variant) |
| vocab | 50257 (GPT-2 BPE) | 111 (word-level, closed) |
| models | GPT-2 124M → 355M pretrained | from-scratch decoders, 0.85M → 8M |

A tunable generator is arguably *better* for a proof of concept, because the
capacity gap can be engineered rather than hoped for. The cost is that this
does not test whether *pretrained* representations transfer, which is where the
"platonic representation" similarity that makes model stitching work is thought
to come from. That is milestone 2, and the code is written backbone-agnostic
(`inputs_embeds`, `past_key_values`, `output_hidden_states`) so the same
pipeline runs on GPT-2 or Qwen on a real GPU.

## Task

Random layered DAG over fictional concepts. A person is asserted to belong to a
root concept; the question asks which of two candidates they belong to. Exactly
one is reachable.

Two shortcuts were found and closed during development:

* **Mention frequency** — the reachable target appeared in more statements than
  the unreachable distractor, giving a counting heuristic 69% accuracy. Fixed by
  degree-matching the distractor to the target; the heuristic now ties on 100%
  of examples.
* **Position** — verified balanced at 0.502.

Solving it requires multi-hop search, not lookup: several edges may leave the
current concept, so producing even the *explicit* reasoning chain requires
knowing which branch reaches the target.

## Architecture

The small model reads the question and keeps its KV cache. Its final-layer
states are projected into the big model's residual space, where the big model
runs `k` Coconut continuous-thought steps. Those thoughts are projected back
down and consumed by the small model at its latent positions; it then decodes
the answer from its existing cache.

The big model never decodes a token, and the small model never re-reads the
question.

Components:

* `src/model.py` — decoder backbone exposing the three seams the pipeline needs.
* `src/coconut.py` — continuous-thought loop with KV reuse; a `thought_hook`
  seam lets an externally produced thought be injected, which is how the
  cross-model pipeline reuses the same decode path.
* `src/projectors.py` — affine (or MLP) maps plus optional RMS rescaling,
  because two separately trained models share no activation scale; LoRA.
* `src/pipeline.py` — the handoff.
* `src/flops.py` — analytic per-query inference FLOPs.

## Training

Stage-wise, each with a gate, per the approved plan (A then C):

* **Stage 0** — train both backbones standalone with the Coconut curriculum.
  Gate: big model clears the small model's accuracy.
* **Stage 1** — freeze the big model; train the up-projector to match the big
  model's *own* continuous thoughts (MSE) and keep its answer correct through
  its own head (CE). This isolates "can the big model consume foreign states"
  from "can the small model decode foreign thoughts".
* **Stage 2** — freeze upstream; train the down-projector and a LoRA adapter on
  the small model with the answer loss.
* **Stage 3** — joint polish at low LR.

Cross-model CODI (approach C) is the follow-on once the mechanism is validated.

## Controls

The headline number is meaningless without these:

1. **Random frozen big model** — same shapes, untrained weights. If the pipeline
   scores the same, the projectors and small model learned the task themselves
   and the big model is decoration.
2. **Small model with matched latent steps** — the same `k` continuous thoughts,
   no big model. Distinguishes *capacity* from merely *more sequential compute*.

## Success criteria

The pipeline beats the small-model-Coconut floor and both controls, closing a
meaningful fraction of the gap to the big-model ceiling, at per-query FLOPs
well below the big model's.

## Efficiency: where the savings actually come from

The originally approved handoff — projecting *every* question state up to the
big model — does not save anything. The big model still prefills the whole
question, which dominates its cost:

| handoff | FLOPs/query | vs big alone | vs small alone |
|---|---|---|---|
| full context | 3.44G | **1.07x** | 10.1x |
| m = 32 | 932M | 0.29x | 2.7x |
| m = 16 | 674M | 0.21x | 2.0x |
| m = 8 | 546M | **0.17x** | 1.6x |

So the pipeline must transmit a *compressed* message: only the last `n_message`
small-model states, which are causally downstream of the whole question. That
makes big-model cost O(m + k) rather than O(question length). Both variants are
implemented; a test asserts structurally that the big model's context never
exceeds `m + k` positions under compression.

## Task calibration (empirical)

Four difficulty settings were trained. The consistent finding across all of
them is **low teacher-forced loss with chance accuracy**: from-scratch models
learn the surface form of the reasoning chain quickly and the multi-hop content
lookups slowly.

| variant | hops | concepts | ctx tokens | branching | big-model result |
|---|---|---|---|---|---|
| `data` | 4 | 90 | 174 | 1.34 | small: 0.485 (chance) |
| `data_med` | 4 | 24 | 145 | 1.11 | CoT 0.468 (chance) |
| `data_focus` | 4 | 15 | 105 | ~1.5 | CoT 0.422, latent-stage-1 0.468 |
| `data_h2` | 2 | 12 | 80 | ~1.4 | CoT 0.524 |

Two things this ruled out, and one it did not:

* **Not an implementation bug.** An 8-example overfit drives loss to 7e-4 with
  exact-match generation of the full chain, and 24 correctness tests pass.
* **Not a task shortcut.** Frequency, position and single-hop heuristics are all
  closed and enforced by tests.
* **It is training budget.** The reference recipe is 4 GPUs x 50 epochs from
  *pretrained* GPT-2, which already carries the induction heads this task needs;
  these models start from scratch at roughly a quarter of the per-stage steps.

A further consequence: the Coconut curriculum bootstraps from chain-of-thought
ability, so when explicit CoT never rises above chance the early stages are
wasted compute. `--final_only` trains directly at the full-latent configuration
instead.

## Result

The graph task was abandoned after five difficulty settings (see calibration
above). The reported experiment uses the sequential-composition task, where
depth is the only difficulty and explicit CoT reaches 1.000 — the prerequisite
the Coconut curriculum needs.

Small = 0.12M (2 layers, d=64), big = 8.0M (10 layers, d=256), chance = 0.112.

| configuration | accuracy |
|---|---|
| small, no reasoning | 0.112 |
| small, explicit CoT | 1.000 |
| small, Coconut (floor) | 0.684 |
| big, Coconut (ceiling) | 0.997 |
| pipeline, frozen receiver | 0.749 |
| ↳ control, untrained big | 0.745 |
| **pipeline, adapted receiver** | **1.000** |
| ↳ control, random big | 0.736 |

**The frozen-receiver configuration is a negative result that only the control
exposed.** At 0.749 against a 0.684 floor it looks like a partial success; the
random-big control at 0.745 shows the entire gain was the small model's LoRA
adapter, with nothing crossing between the models.

Giving the receiver a rank-8 adapter changes everything:

| receiver | big-model accuracy when driven from projected states |
|---|---|
| frozen | 0.268 |
| frozen, `tap_layer=1` | 0.096 |
| rank-8 adapter | 0.994 |

The interpretation is that a frozen model cannot read another model's residual
stream. The small model's states encode its own running computation, not the
token identities the big model expects at its input, and no affine or MLP map
recovers that. This is consistent with the stitching literature transferring
*static* objects (SAEs, probes, steering vectors) rather than a full contextual
encoding another model must compute over — and with Interlat and Cache-to-Cache
both training the receiver. Inference cost is unchanged by the adapter.

Ruled out as an explanation: the injection path itself. Feeding the big model
its own token embeddings through the same `prefix_embeds` seam reproduces native
accuracy exactly (0.996 vs 0.996).

### Efficiency caveat

This testbed validates the mechanism, not the cost claim. Its questions are 13
tokens, so compression has almost nothing to remove, and the big model holds 66x
the small model's parameters.

| handoff | accuracy | FLOPs/query | vs big | vs small |
|---|---|---|---|---|
| all 13 states | 1.000 | 241.7M | 0.78x | 60.6x |
| m = 4 | 0.823 | 114.8M | 0.35x | 27.0x |

Compression is a usable operating point, not a collapse: 0.823 still sits well
above the 0.684 floor for half the compute. But the compute case requires long
contexts and a realistic size ratio, which is what the analytic table models.

## Validation

Correctness is pinned by tests rather than assumed, because a silent cache or
alignment bug would corrupt every number without crashing:

* incremental KV-cached decoding equals a single full forward pass
* Coconut's multi-pass output equals one forward over the assembled embeddings
* causality, padding isolation, `inputs_embeds` ≡ `input_ids`
* gradients reach both projectors; perturbing the big model changes the output
* an 8-example overfit drives loss to ~0 with exact-match generation
