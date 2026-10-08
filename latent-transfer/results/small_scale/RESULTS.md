# Cross-model latent reasoning handoff: small-scale result

A small model reads the question, its hidden states are projected into a larger
model's residual space, the larger model reasons there in continuous thoughts,
those thoughts are projected back, and the small model decodes the answer. The
big model never emits a token and the small model never re-reads the question:
everything crossing between them is a vector.

## Setup

Sequential composition: three chained updates in Z_10. Chance is 0.112.
Small model 0.12M parameters, big model 8.0M, both trained from scratch, both
taught to reason with Coconut (Hao et al. 2024) before any handoff is trained.

## Result

| configuration | accuracy | FLOPs/query | vs small |
|---|---|---|---|
| small, no reasoning | 0.112 | 3.23M | 0.8x |
| small, explicit chain of thought | 1.000 | 5.75M | 1.4x |
| **small, Coconut — FLOOR** | **0.684** | 4.05M | 1.0x |
| **big, Coconut — CEILING** | **0.997** | 316.70M | 78.2x |
| pipeline, frozen receiver | 0.7485 | 241.67M | 59.7x |
| control: random frozen receiver | 0.7415 | 241.67M | 59.7x |
| **pipeline, adapted receiver** | **0.9995** | 241.67M | 59.7x |
| control: random adapted receiver | 0.7430 | 241.67M | 59.7x |
| pipeline, compressed to m=4 | 0.8230 | ~120M | ~30x |

## What the controls establish

**A frozen receiver transfers nothing.** At 0.7485 it is statistically
indistinguishable from its own random-network control at 0.7415. Whatever the
pipeline gained over the 0.684 floor came from the projectors and the small
model's adapter, not from the big model's reasoning.

**An adapted receiver transfers almost everything.** At 0.9995 it clears its
random control by 0.2565 and lands slightly above the big model's own 0.997
ceiling. Both controls pass: it beats the random receiver decisively, and it
beats the small model's own latent reasoning by 0.3155.

## The mechanism

Stage 1 measures whether the big model can answer at all when driven from
projected states instead of its own embeddings.

| receiver | native accuracy | from projected states |
|---|---|---|
| frozen | 1.000 | **0.268** |
| adapted | 0.918 | **0.994** |

A frozen model reads foreign states at 0.268 and is useless downstream. Given a
low-rank adapter it reads them at 0.994. The receiver's own accuracy drops from
1.000 to 0.918 as it specialises, which is the price of adaptation.

This matches the published literature. Interlat (ACL 2026) reports that removing
their communication adapter drops task success from 70.48 to 4.05.
Cache-to-Cache (arXiv 2510.03215) reports 20.70% for replacing receiver states
with projected ones, recovered to 44.88% only by adding a residual path.

## Compression

Sending only the last 4 projected states rather than all of them costs accuracy:
0.9995 to 0.8230, for roughly half the compute. That is the tradeoff curve the
architecture lives on, since sending everything is barely cheaper than running
the big model directly.

## Honest limitations

Both models are tiny and trained from scratch on a synthetic task, so this shows
the mechanism works, not that it scales. The compute figures are analytic FLOPs
at the measured sequence shape, not wall-clock. The uncompressed pipeline costs
0.76x the big model, which is not a useful saving on its own; the saving depends
entirely on compression, and compression costs accuracy.

Files: `c3_results.json` (numbers), `c3_manifest.json` (checkpoint map),
`c3_report.txt` (generated verdicts), per-run `metrics.json`.
