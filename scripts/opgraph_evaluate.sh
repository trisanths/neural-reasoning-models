#!/bin/bash
# Score every condition on both page wordings, then write the summary.
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
mkdir -p results
export PYTHONPATH=$ROOT
GPU=${1:-7}
CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/opgraph_eval.py \
  --direct-ckpt runs/direct.pt \
  --opgraph-ckpt runs/opgraph.pt \
  --trace-ckpt runs/trace.pt \
  --base-ckpt ckpt/base350.pt \
  --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --out results/opgraph.json --n 150 --batch-size 32
uv run python scripts/opgraph_report.py --results results/opgraph.json \
  --out results/opgraph_summary.json | tee results/opgraph_report.txt
