#!/bin/bash
# Full-sweep training for one ladder rung. Same settings for every arm, so a
# rung is comparable to the plan_execute and oracle_plan numbers on record.
set -eu
ARM="$1"; GPU="$2"
cd /home/ec2-user/opg
mkdir -p runs/ef logs/ef results/ef
PYTHONPATH=$PWD CUDA_VISIBLE_DEVICES="$GPU" uv run python scripts/opgraph_train.py \
  --base ckpt/base350.pt \
  --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --arm "$ARM" --out runs/ef/"$ARM".pt \
  --steps 8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000
echo "[trained] $ARM"
