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
| Regime C held-out episodes | ~/data/regime_c/heldout.jsonl | 5,000 episodes | Seed 20260824, episode indices from 1,000,000,000 up, disjoint from any training chunk by construction. |
| Regime C training shards | not rendered yet | target ~7.5B tokens, ~15GB | Pipeline is ready (scripts/render_regime_c.py); see open items. |
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

- Full test suite passes on the instance: 116 tests under src and 5 under
  scripts/tests, via uv run pytest.
- Regime A shards: index totals 7,500,274,047 tokens across 56 shards, every
  file size matches the index, and two random windows from different shards
  decode with tokenizer v2 to readable English.
- Regime C renderer: oracle round-trip on real bench data regenerates stored
  episodes byte for byte from their seeds (ORACLE_VERIFY_OK), 200 traces pass
  the structural scan, and a wiped chunk re-renders byte-identically.
- Naturalized suite: every answer and every distractor is verified present in
  its passage under the suite normalization; passage lengths are within the
  150 to 400 word spec.

## Open items before the kill test

1. Retrieval protocol decision. Under the current v0 protocol (single-shot
   BM25 over full-question terms), the top-1 document supports a fact in the
   question's derivation for only 38.9 percent of questions over 300 held-out
   episodes. Decide whether to keep v0 or revise before spending the regime C
   render, since traces bake the protocol into the training data.
2. Regime C full render, about 7.5B tokens, roughly 3.8 hours on this
   instance once item 1 is settled.
3. Train the 350M model under regime A and regime C, about 7B tokens each.
4. Score both models on the naturalized reading suite, the knowledge probes,
   and the retrieval-noise axis, then apply the pre-registered decision rule
   in SPEC.md section 7.
