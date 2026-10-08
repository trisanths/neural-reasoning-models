#!/bin/bash
# Standard 350M micro batch sweep on one GPU. Every setting keeps the global
# batch at 64 sequences of 4096 tokens, the SPEC.md optimizer step of 262144
# tokens. Each setting runs in its own process, one json line per setting.
# Usage, from the repo root:
#   bash scripts/bench/sweep.sh [shard_dir] [results_jsonl]
set -euo pipefail
DATA="${1:-$HOME/data/bench/shards}"
OUT="${2:-$HOME/data/bench/results.jsonl}"
for setting in "4 16" "8 8" "16 4" "32 2"; do
  set -- $setting
  uv run python -m scripts.bench.profile --config configs/350m.yaml \
    --data "$DATA" --micro-batch "$1" --grad-accum "$2" \
    --tag "eager" --out "$OUT"
done
