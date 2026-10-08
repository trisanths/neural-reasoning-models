#!/bin/bash
set -u
cd /home/ec2-user/decoupled-reasoner
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
CKPT=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
TOK=/home/ec2-user/data/tokenizer_v2.json
OUT=/home/ec2-user/results/primitives
for M in isolated integrated; do
  R=20; [ "$M" = integrated ] && R=0
  echo "=== $M start $(date -Is) ==="
  uv run python -m src.primitives.cli --ckpt "$CKPT" --tokenizer "$TOK" \
    --out "$OUT" --stem "primitives-$M" --n 40 --seed 0 \
    --mode "$M" --ks 1,2,3,4,5 --rescue-n $R \
    --temperature 0.7 --top-k 50 --max-new-tokens 48 --batch 12 --char-budget 9000 \
    > "$OUT/$M.log" 2>&1
  echo "=== $M exit $? $(date -Is) ==="
done
echo ALLDONE
