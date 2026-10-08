#!/bin/bash
# Tiny end to end run of all five plan heads: does each one train, does each one
# emit a plan the executor accepts, is oracle_both 1.000 under each, and does the
# reported forward count match what the model was actually asked to do.
#
#   bash scripts/planheads_smoke.sh 7          run every head on gpu 7
#   bash scripts/planheads_smoke.sh 7 p3       run one head
#
# This is a smoke, not a measurement. The world count, the step count and the
# eval denominators are all far too small for an accuracy number to mean
# anything, and the summary says so.
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
export PYTHONPATH=$ROOT
GPU=${1:-7}
HEADS=${2:-"p1 p2 p2s p3 p4"}
TOK=/home/ec2-user/data/tokenizer_v2.json
mkdir -p runs/smoke results/smoke logs/smoke

TRAIN="--base ckpt/base350.pt --tokenizer $TOK --steps 240 --batch-size 8 \
--max-len 640 --worlds 600 --log-every 40 --lr 2e-5 --head-lr 2e-4 --warmup 20"
EVAL="--tokenizer $TOK --n 8 --batch-size 8 --styles 0 \
--kinds sequential,breadth,novel --temperatures 0.0,0.8 --verify-counter"

for H in $HEADS; do
  echo "=== $H train $(date -Is) ==="
  CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/planheads_train.py $TRAIN \
    --head "$H" --out "runs/smoke/$H.pt" > "logs/smoke/$H.train.log" 2>&1
  echo "train status=$?"
  tail -4 "logs/smoke/$H.train.log"
  echo "=== $H eval $(date -Is) ==="
  CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/planheads_eval.py $EVAL \
    --ckpt "runs/smoke/$H.pt" --out "results/smoke/$H.json" \
    --iters 1,4 > "logs/smoke/$H.eval.log" 2>&1
  echo "eval status=$?"
  tail -4 "logs/smoke/$H.eval.log"
done
echo "=== report $(date -Is) ==="
uv run python scripts/planheads_smoke_report.py results/smoke > results/smoke/REPORT.txt 2>&1
cat results/smoke/REPORT.txt
