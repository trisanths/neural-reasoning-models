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
# This suite is calibrated against the RL base checkpoint, so it resolves that
# one or nothing. Grading some other model with it would produce a number that
# looks like a result and is not one.
if [ -z "${CKPT:-}" ]; then
  for c in "$HOME"/ckpt/*rlsimple*final.pt "$HOME"/ckpt/final.pt; do
    [ -s "$c" ] && { CKPT="$c"; break; }
  done
fi
if [ -z "${CKPT:-}" ]; then
  echo "no RL base checkpoint in ~/ckpt. Stage it first:"
  echo "  CKPTS=s3://decoupled-reasoner-009398924577/runs/final/rlsimple-503-921/final.pt"
  echo "and re-run the bootstrap, or pass CKPT=<path> to grade a specific file."
  exit 1
fi
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
