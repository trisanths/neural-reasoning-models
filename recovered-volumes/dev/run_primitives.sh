#!/bin/bash
set -u
cd /home/ec2-user/decoupled-reasoner
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
CKPT=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
TOK=/home/ec2-user/data/tokenizer_v2.json
OUT=/home/ec2-user/results/primitives
mkdir -p "$OUT"
for MODE in isolated integrated; do
  RES=0
  if [ "$MODE" = "isolated" ]; then RES=20; fi
  echo "=== $MODE start $(date -Is) ==="
  uv run python -m src.primitives.cli \
    --ckpt "$CKPT" --tokenizer "$TOK" --out "$OUT" --stem "primitives-$MODE" \
    --n 40 --seed 0 --mode "$MODE" --ks 1,2,3,4,5 --rescue-n $RES \
    --temperature 0.7 --top-k 50 --max-new-tokens 48 \
    --batch 12 --char-budget 9000 \
    > "$OUT/$MODE.log" 2>&1
  echo "=== $MODE exit $? $(date -Is) ==="
done
echo "=== calibration $(date -Is) ==="
uv run python -m src.primitives.cli --calibrate --out "$OUT" --n 60 --ks 1,2,3 \
  > "$OUT/calibration.log" 2>&1
echo "=== calibration exit $? $(date -Is) ==="
echo ALLDONE
