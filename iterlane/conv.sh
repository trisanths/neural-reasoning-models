#!/bin/bash
# Per head convergence check: the same small sequential grid at every saved step.
# Comparing two heads at a matched step count only means something once each has
# stopped moving, and the smoke showed the slot heads are the slow ones.
set -u
cd /home/ec2-user/opg
export PYTHONPATH=/home/ec2-user/opg
GPU=$1; HEAD=$2
for CK in runs/iter/${HEAD}_s*.pt runs/iter/${HEAD}.pt; do
  [ -f "$CK" ] || continue
  TAG=$(basename $CK .pt)
  OUT=results/iter/conv_${TAG}.json
  [ -f "$OUT" ] && continue
  echo "=== $CK ==="
  CUDA_VISIBLE_DEVICES=$GPU uv run python iterlane/eval_iter.py     --ckpt $CK --tokenizer /home/ec2-user/data/tokenizer_v2.json     --out $OUT --n 48 --batch-size 24 --gen-batch-size 96     --kinds sequential --depths 1,2,3,4,6,8,12 --styles 0 --iters 8     --temperatures 0.0,0.8 --conditions plan_execute --skip-gold 2>&1 | grep -E "^\[plan_execute|^\[induction"
done
echo CONV_DONE_$HEAD
