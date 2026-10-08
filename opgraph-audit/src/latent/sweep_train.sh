#!/bin/bash
# Train one latent condition for the depth by recurrence sweep.
# usage: sweep_train.sh GPU ARM OUT [extra args...]
#
# Matched to the token channel arms on base checkpoint, worlds, seeds,
# questions, optimizer, learning rate, warmup, batch size in sequences and
# number of optimizer steps. --micro-batch only splits a step's sequences
# across several forward and backward passes, so neither matched axis moves.
set -eu
GPU=$1; ARM=$2; OUT=$3; shift 3
cd /home/ec2-user/opg
mkdir -p logs runs/latent
export CUDA_VISIBLE_DEVICES=$GPU
export PYTHONPATH=$PWD
exec uv run python -m src.latent.train \
  --base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --arm "$ARM" --out "$OUT" \
  --steps 8000 --batch-size 32 --max-len 1024 --lr 2e-5 --warmup 200 \
  --worlds 40000 --seed 0 --log-every 50 --save-every 2000 \
  --r-choices 1,2,4,8,16,32 --backprop-last-k 2 "$@"
