#!/bin/bash
set -u
cd /home/ec2-user/opg
export PYTHONPATH=/home/ec2-user/opg
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
GPU=$1; SCRIPT=$2; HEAD=$3; OUT=$4; STEPS=$5
CUDA_VISIBLE_DEVICES=$GPU uv run python $SCRIPT   --base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json   --head $HEAD --out $OUT --steps $STEPS --batch-size 32 --worlds 40000   --ckpt-every 2000 --log-every 250
