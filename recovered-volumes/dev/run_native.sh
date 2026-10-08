#!/bin/bash
set -u
cd /home/ec2-user/decoupled-reasoner
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
OUT=/home/ec2-user/results/primitives
CK=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
TOK=/home/ec2-user/data/tokenizer_v2.json
echo "=== native start $(date -Is) ==="
uv run python -m src.primitives.cli --ckpt "$CK" --tokenizer "$TOK" \
  --out "$OUT" --stem primitives-native --n 40 --seed 0 --ks 2 --native-frame \
  --temperature 0.7 --top-k 50 --max-new-tokens 48 --batch 12 --char-budget 9000 \
  > "$OUT/native.log" 2>&1
echo "=== native exit $? $(date -Is) ==="
echo "=== suite-refresh start $(date -Is) ==="
uv run python -m src.primitives.cli --ckpt "$CK" --tokenizer "$TOK" \
  --out "$OUT" --stem primitives-isolated --n 40 --seed 0 \
  --mode isolated --ks 1,2,3,4,5 --rescue-n 20 \
  --temperature 0.7 --top-k 50 --max-new-tokens 48 --batch 12 --char-budget 9000 \
  > "$OUT/isolated.log" 2>&1
echo "=== suite-refresh exit $? $(date -Is) ==="
echo NATIVEDONE
