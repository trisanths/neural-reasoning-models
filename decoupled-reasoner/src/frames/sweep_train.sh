#!/bin/bash
# Train sweep arms one after another on one card.
#
#   bash src/frames/sweep_train.sh GPU 1 3 10 30 72
#
# Run from the repo root. Every arm gets the same data size, the same order,
# the same steps and the same hyperparameters; only the frame count differs,
# and that is already baked into the per-arm data file.
set -u
GPU=$1; shift
O=${SWEEP:-/home/ec2-user/sweep}
CK=${BASE_CK:-/home/ec2-user/rlckpt/rlsimple-503-921-final.pt}
mkdir -p "$O/ckpt" "$O/logs"
for A in "$@"; do
  P=$(printf "arm%03d" "$A")
  echo "=== $P start $(date -u +%FT%TZ)"
  CUDA_VISIBLE_DEVICES=$GPU PYTHONPATH=. .venv/bin/python -m src.frames.sweep train \
    --checkpoint "$CK" --data "$O/data/$P.jsonl" --out "$O/ckpt/$P.pt" \
    --log "$O/logs/$P.jsonl" --epochs 3 --batch 16 \
    > "$O/logs/$P.log" 2>&1 || { echo "TRAIN_FAIL $P"; exit 1; }
  echo "=== $P done $(date -u +%FT%TZ)"
done
echo "TRAIN_ALL_DONE $(date -u +%FT%TZ)"
