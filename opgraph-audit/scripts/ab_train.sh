#!/bin/bash
# Full-sweep training for ladder rungs A (english) and B (symbolic).
# One rung per GPU. Settings are the original arms settings so the numbers are
# directly comparable to the plan_execute and oracle_plan record.
set -eu
GPU="$1"; ARM="$2"
cd /home/ec2-user/opg
PYTHONPATH=$PWD CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/opgraph_train.py \
  --base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --arm ladder_$ARM --out runs/ladder_ab/ladder_$ARM.pt \
  --steps 8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000
echo "TRAIN_DONE $ARM"
