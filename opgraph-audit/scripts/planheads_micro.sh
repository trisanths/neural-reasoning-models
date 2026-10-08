#!/bin/bash
# Micro end to end check of all five plan heads. Not a measurement: four
# optimizer steps and two items a cell. It only answers "does the path run".
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
export PYTHONPATH=$ROOT
GPU=${1:-7}
TOK=/home/ec2-user/data/tokenizer_v2.json
mkdir -p runs/micro results/micro logs/micro

TRAIN="--base ckpt/base350.pt --tokenizer $TOK --steps 4 --batch-size 4 \
--max-len 640 --worlds 40 --log-every 1 --warmup 2"
EVAL="--tokenizer $TOK --n 2 --batch-size 4 --styles 0 \
--kinds sequential --temperatures 0.0,0.8 --verify-counter --iters 1,3"

for H in p1 p2 p2s p3 p4; do
  echo "=== $H train $(date -Is) ==="
  CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/planheads_train.py $TRAIN \
    --head "$H" --out "runs/micro/$H.pt" > "logs/micro/$H.train.log" 2>&1
  echo "train status=$?"
  tail -3 "logs/micro/$H.train.log"
  echo "=== $H eval $(date -Is) ==="
  CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/planheads_eval.py $EVAL \
    --ckpt "runs/micro/$H.pt" --out "results/micro/$H.json" \
    > "logs/micro/$H.eval.log" 2>&1
  echo "eval status=$?"
  grep -E "counter|oracle_both|Error|Traceback" "logs/micro/$H.eval.log" | head -8
  tail -3 "logs/micro/$H.eval.log"
  rm -f "runs/micro/$H.pt"
done
echo "=== micro done $(date -Is) ==="
