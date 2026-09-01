#!/usr/bin/env bash
# Prove a bootstrapped worker can do real work, not just import torch.
#
# Loads the base RL checkpoint onto the GPU and scores a small slice of the
# primitives suite. A worker that passes this has a working env, a working GPU,
# the tokenizer, and a checkpoint it can actually read.
#
# Run it on the worker:
#   bash scripts/worker_run.sh 1 'cd ~/decoupled-reasoner && bash scripts/worker_selftest.sh'
#
# usage: bash scripts/worker_selftest.sh [n]
set -euo pipefail

N="${1:-8}"
CKPT="${CKPT:-$HOME/ckpt/final.pt}"
TOK="${TOK:-$HOME/data/tokenizer_v2.json}"
OUT="${OUT:-$HOME/results/selftest}"
UV="$HOME/.local/bin/uv"
cd "$HOME/decoupled-reasoner"

[ -s "$CKPT" ] || { echo "no checkpoint at $CKPT"; exit 1; }
[ -s "$TOK" ]  || { echo "no tokenizer at $TOK"; exit 1; }
mkdir -p "$OUT"

export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
echo "checkpoint $(du -h "$CKPT" | cut -f1) on $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
START=$(date +%s)

"$UV" run python -m src.primitives.cli \
  --ckpt "$CKPT" --tokenizer "$TOK" \
  --out "$OUT" --stem selftest --n "$N" --seed 0 \
  --mode isolated --ks 1,2 --rescue-n 0 \
  --temperature 0.7 --top-k 50 --max-new-tokens 32 --batch 8 --char-budget 9000

echo "SELFTEST_OK in $(( $(date +%s) - START ))s, report under $OUT"
