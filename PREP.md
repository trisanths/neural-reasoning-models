# Kill-test prep status

State of data assets, benchmarks, and open work before the Phase 1 kill test
(SPEC.md section 7). All numbers were measured on the project instance; paths
are on that machine.

## Data assets

| Asset | Location | Size | Notes |
| --- | --- | --- | --- |
| Regime A shards | ~/data/regime_a/shards | 7,500,274,047 tokens, 56 uint16 shards | Rendered from 14 FineWeb-style parquet files (27GB) with tokenizer v2. Two render passes merged into one indexed directory. |
| Regime A source | ~/data/regime_a/parquet | 27GB, 14 parquet files | Kept for re-renders. |
| Tokenizer v2 | ~/runs/tokenizer_v2/tokenizer_v2.json | 32,768 vocab | Used by both regimes and all shard tooling. |
| Regime C held-out episodes | ~/data/regime_c/heldout.jsonl | 5,000 episodes | Seed 20260824, episode indices from 1,000,000,000 up, disjoint from any training chunk by construction. Regenerated under the v1 corpus (restated templates). |
| Regime C training shards | ~/data/regime_c/shards | target ~7.5B tokens, ~15GB | Render running; see the regime C render section. |
| Naturalized reading suite | src/evals/data/naturalized/ | 250 items, version DRAFT-1 | 50 items in each of 5 registers (news, filing, manual, letter, transcript), all fictional content. |
| Knowledge probes | src/evals/probes.py | 244 four-way probes | Chance rate 0.25, leakage threshold derived from per-probe chance. |

## Benchmarks

Training throughput, 350M config (375,440,384 params total, 308,331,520
non-embedding), seq 4096, NVIDIA L40S, torch 2.13.0+cu130, from
~/logs/bench_phase1.log:

| Setup | tok/s | Peak reserved |
| --- | --- | --- |
| eager, micro batch 2, grad accum 32 | 31,084 | 21.7 GiB |
| compiled, micro batch 4, grad accum 16 | 48,079 | 24.8 GiB |
| compiled, micro batch 8, grad accum 8 | 49,003 | 43.3 GiB |

At the compiled micro batch 8 rate, one 7B-token run is about 40 hours on this
card. The PLAN.md estimate of roughly 10 effective H100-hours per model still
holds for the rented Phase 1 hardware.

Regime C generation throughput, measured on this instance (4 vCPUs, full
generate plus render path, seed 20260824): 545,983 tok/s with 4 processes
(811.6 episodes/s), 376,955 tok/s single process, 672.6 tokens per episode.
A 7.5B-token render is about 3.8 hours here, or minutes on a large CPU box.

## What is verified

- Full test suite passes on the instance: 141 tests under src and
  scripts/tests, via uv run pytest, including the no-clairvoyance check on
  generated episodes.
- Regime A shards: index totals 7,500,274,047 tokens across 56 shards, every
  file size matches the index, and two random windows from different shards
  decode with tokenizer v2 to readable English.
- Regime C renderer: oracle round-trip on real bench data regenerates stored
  episodes byte for byte from their seeds (ORACLE_VERIFY_OK), 200 traces pass
  the structural scan, and a wiped chunk re-renders byte-identically.
- Naturalized suite: every answer and every distractor is verified present in
  its passage under the suite normalization; passage lengths are within the
  150 to 400 word spec.

## Retrieval protocol v1: final gate metrics

The v0 protocol (single-shot BM25 over full-question terms, 38.9 percent
top-1 support) is replaced by the v1 multi-hop trace protocol in
src/train/retrieval.py: one verified retrieve-result round per derivation
hop, queries built from question terms plus earlier chunks only, with a
greedy margin builder and a minimax term-weighting fallback. Worldgen
document templates now restate the question-anchored entity of each
relation, which puts the argument role into term frequency where
bag-of-words retrieval can see it; this changed the rendered corpus
distribution, and every number below was measured after that change.

Gate at 2000 held-out episodes (seed 20260824, start index 1,000,000,000,
contradiction 0.15, filler 0.25): all_hops_top1 0.9803 (bar 0.85),
drop_rate 0.0187 (cap 0.10), mean hops 1.233.

| Domain | Questions | all_hops_top1 | drop_rate |
| --- | --- | --- | --- |
| corporate | 2818 | 0.9915 | 0.0085 |
| kinship_temporal | 2243 | 0.9996 | 0.0004 |
| logistics | 1997 | 0.9254 | 0.0746 |
| regulatory | 2256 | 1.0000 | 0.0000 |

The eval-time decode loop (src/evals/interactive.py) serves retrieval with
the training oracle's exact contracts: reliability-weighted BM25 ranking
and without-replacement serving across one question's rounds.

## Regime C render (running)

Launched detached on this instance, log ~/logs/regime_c_full.log:

- command: .venv/bin/python3 -m scripts.render_regime_c
- out ~/data/regime_c/shards, target 7,500,000,000 tokens, 4 processes,
  1000 episodes per chunk, resumable by chunk
- seed 20260824, contradiction 0.15, filler 0.25, all four domains
- tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json (32,768 vocab)
- held-out JSONL regenerated under the new corpus at
  ~/data/regime_c/heldout.jsonl (5000 episodes, indices from
  1,000,000,000); the pre-v1 heldout.jsonl at that path is superseded
- about 858 tokens per episode under the restated templates

Oracle spot-check on a fresh 3-chunk render: byte round-trip from seeds and
per-hop top-1 support both pass (ORACLE_VERIFY_OK, 3 samples).

## Open items before the kill test

1. Regime C render completion, then the shard checks from scripts/decode_trace
   (--shards scan plus --manifest oracle mode) on the full output.
2. Kill-test launch on two p5.4xlarge: train the 350M model under regime A
   and regime C, about 7B tokens each.
3. Score both models on the naturalized reading suite, the knowledge probes,
   and the retrieval-noise axis, then apply the pre-registered decision rule
   in SPEC.md section 7.
