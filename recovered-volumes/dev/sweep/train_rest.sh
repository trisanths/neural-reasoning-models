#!/bin/bash
# Train the remaining arms, one after another on one card.
# usage: train_rest.sh GPU ARM [ARM ...]
set -u
GPU=$1; shift
cd /home/ec2-user/decoupled-reasoner || exit 1
O=/home/ec2-user/sweep
CK=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
for A in "$@"; do
  P=$(printf "arm%03d" "$A")
  echo "=== $P start $(date -u +%FT%TZ)"
  CUDA_VISIBLE_DEVICES=$GPU PYTHONPATH=. .venv/bin/python -m src.frames.sweep train \
    --checkpoint $CK --data $O/data/$P.jsonl --out $O/ckpt/$P.pt \
    --log $O/logs/$P.jsonl --epochs 3 --batch 16 \
    > $O/logs/$P.log 2>&1 || { echo "TRAIN_FAIL $P"; exit 1; }
  echo "=== $P done $(date -u +%FT%TZ)"
done
echo "TRAIN_ALL_DONE $(date -u +%FT%TZ)"
