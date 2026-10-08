#!/bin/bash
set -u
cd /home/ec2-user/decoupled-reasoner
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
CKPT=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
TOK=/home/ec2-user/data/tokenizer_v2.json
OUT=/home/ec2-user/results/primitives
echo "=== integrated start $(date -Is) ==="
uv run python -m src.primitives.cli --ckpt "$CKPT" --tokenizer "$TOK" \
  --out "$OUT" --stem primitives-integrated --n 40 --seed 0 \
  --mode integrated --ks 1,2,3,4,5 --rescue-n 0 \
  --temperature 0.7 --top-k 50 --max-new-tokens 48 --batch 12 --char-budget 9000 \
  > "$OUT/integrated.log" 2>&1
echo "=== integrated exit $? $(date -Is) ==="
uv run python -m src.primitives.cli --calibrate --out "$OUT" --n 60 --ks 1,2,3 \
  > "$OUT/calibration.log" 2>&1
echo "=== calibration exit $? $(date -Is) ==="
echo ALLDONE
