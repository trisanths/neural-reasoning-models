#!/bin/bash
# Continue corpus-v1-8k on the real-document mixture at the project's
# standard budget: 8000 optimizer steps, batch 32, AdamW at 2e-5, 200 warmup,
# cosine to a tenth, bfloat16 autocast, one L40S. Matching the budget the
# checkpoint being compared against was trained under is the point, so the
# data is the only thing that differs.
set -eu
REPO=/home/ec2-user/decoupled-reasoner
R=/mnt/nvme/realret
cd $REPO
nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv
FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
MICRO=${MICRO:-8}
# batch 32 must be a whole number of micro-batches
case "$MICRO" in 32|16|8|4|2|1) ;; *) MICRO=8 ;; esac
[ "$FREE" -lt 34000 ] && [ "$MICRO" -gt 8 ] && MICRO=8
[ "$FREE" -lt 20000 ] && MICRO=4
echo "free_mib=$FREE micro_batch=$MICRO"
.venv/bin/python -m src.corpus.sft train \
  --checkpoint /home/ec2-user/ckpt/corpus-v1-8k-final.pt \
  --pack $R/pack/mix_real1 \
  --out $R/real-v1-8k.pt \
  --log $R/logs/train.jsonl \
  --steps 8000 --batch 32 --micro-batch "$MICRO" \
  --lr 2e-5 --warmup 200 --min-lr-ratio 0.1 \
  --weight-decay 0.0 --grad-clip 1.0 --log-every 25 --ckpt-every 4000 \
  --seed 7701 --shuffle-seed 4113
echo TRAIN_DONE
