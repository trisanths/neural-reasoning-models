# Execution plan

## Phases and budgets

Prices verified 2026-08-23 against runpod.io directly: H100 SXM $2.69/hr and H100 PCIe $1.99/hr on community cloud, A100 80GB $1.19 to $1.39/hr, RTX 4090 $0.34/hr, network volume $0.07/GB/month, per-second billing, no egress fees, spot pods up to 60 percent cheaper. Lambda's H100 is $3.99 to $4.29/hr for comparison.

### Phase 0, cloud scaffolding. Tier 0, roughly $10 to $30

One RTX 4090 community pod plus a small network volume. Build and test worldgen, procgen, tokenizer, trainer, and the eval harness. Train the 8M smoke model end to end on a few hundred million tokens. Exit criterion: the full pipeline runs from seed to eval report with no manual steps.

### Phase 1, the kill test. Complete; the strict form is dead

Finished 2026-08-26. The 350M class trained under regimes A and C, three seeds each, about 7B tokens per run. On the pre-registered gate (naturalized reading, contains-answer, clean variant, 250 items) regime A scored a mean of 0.2053 across seeds (0.228, 0.196, 0.192) and regime C scored 0.0000 on every item on every seed. The C to A ratio is 0.0000, bootstrap 95 percent interval [0.0000, 0.0000], below the 0.6 kill threshold in SPEC.md section 7.

The C checkpoints are not broken models. Their knowledge-probe leakage flags are clear, they score 0.66 to 0.72 on their own-format held-out worlds, and they average under one retrieval round per question in the interactive loop. They learned the synthetic format and did not learn to read natural text at all. Pretraining purely on synthetic worlds is dead as a route to a natural-text reasoner at this scale.

Verdict artifacts: results/killtest-2026-08-26/ in this repo and s3://decoupled-reasoner-009398924577/runs/killtest/evals/.

### Phase 2, the matrix. Tier 2, roughly $3,000 to $5,000

Re-scoped by the Phase 1 gate: only the weakened form is tested, and the writeup says so plainly. The strict form is dropped as a candidate; regimes A, B, and C stay in the matrix as baselines and controls.

Running now: the knowledge-free reasoning scaling curve, eight single-GPU lanes at iso-data 7.0B tokens covering 150M, 700M, and 1.3B under regimes A and C plus 150M and 350M under regime B, with the six kill-test runs standing as the 350M A and C points (CURVE.md).

The weakened-form arm pretrains on regime D: natural text plus retrieval-trace worldgen episodes mixed (natural 0.80, worldgen with regime C trace conventions 0.15, procgen 0.05), rendered by scripts/render_regime_b.py --worldgen-retrieval. Still planned on top of that: the frequency-ordered resident knowledge diet, the teacher distillation arm (open R1-distill weights served on our own pods as teacher; no paid APIs), and the retrieval-noise axis at every size.

## Current blockers

1. RUNPOD_API_KEY from the owner (account, billing, and key creation are owner-side actions).
2. Budget tier authorization.
3. HF read token for FineWeb-Edu and Wikipedia (regime A), delivered as a RunPod secret.

## Risk register

Distilled from a nine-agent literature verification run on 2026-08-23.

1. No existence proof that reasoning grows from scratch at this scale. Every strong small reasoner is distilled from a knowledge-rich teacher, and RL from scratch on small models loses to distillation (DeepSeek-R1 ablations; sub-3B learnability gap, arXiv:2502.12143). Mitigation: the weakened form keeps distillation; the strict form is tested cheaply first.
2. Language competence is made of facts. A zero-fact model may fail to read real documents at all (TinyStories needed a 1,500-word world; comprehension is knowledge-limited). This is exactly what the kill test measures before real money is spent. Outcome: this risk was realized in full; see Phase 1.
3. Evidence compression and retrieval noise hit small readers hardest (RGB, arXiv:2309.01431; compression answer-evidence gap, arXiv:2608.01631). Mitigation: the noise axis is a first-class metric, and the reasoner always keeps an escape hatch to raw documents.
4. Capacity pressure may delete tail skills instead of compressing them into algorithms (the grokking transition's causal story is contested, arXiv:2412.00104; transformers under compositional pressure learn linearized subgraph matching, arXiv:2305.18654). Mitigation: pre-registered gates, no post-hoc rescue of a failed strict form.
5. Synthetic streams lose distributional tails (arXiv modeled in Nature 2024 collapse result), so held-out-world scores never headline; only naturalized reading does.

## Supporting evidence

Procedural warm-up works at small scale (ICML 2026, arXiv:2601.21725; ACL 2025, arXiv:2502.19249). Reasoning and factual recall draw on different pretraining data (arXiv:2411.12580). Retrieval closes about 90 percent of the knowledge gap when weights are knowledge-poor (SILO, arXiv:2308.04430). Fact-masked pretraining exists (LMLM, arXiv:2505.15962). Retrieval infrastructure at the needed latency is production-proven (SPANN, DiskANN). Iterative retrieval works with sub-1B readers (IRCoT, ACL 2023).
