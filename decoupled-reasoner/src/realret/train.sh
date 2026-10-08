#!/bin/bash
# Continue the corpus-retrained checkpoint on the real-document mixture.
#
# The budget is the project's standard, the same one `src/corpus/RETRAIN.md`
# records for corpus-v1-8k and the same one the eight opgraph arms in
# PREREGISTERED.md use: 8000 optimizer steps, batch 32 as micro-batch 8 with
# four accumulations, AdamW at 2e-5, 200 warmup steps, cosine to a tenth,
# bfloat16 autocast, one L40S. Matching it exactly is the point: the data is
# then the only thing that differs from the checkpoint being compared against.
#
# The training pass is `src/corpus/sft.py train`, unchanged. Only the pack
# it reads is new.
set -eu
cd /home/ec2-user/decoupled-reasoner
R=/home/ec2-user/realret
# Two other lanes share this card. The corpus run peaked at 20.9 GB with
# micro-batch 8; if that much is not free the micro-batch halves and the
# accumulation doubles, which leaves the optimizer step identical.
nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv
FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
MICRO=${MICRO:-8}
if [ "$FREE" -lt 26000 ]; then MICRO=4; fi
if [ "$FREE" -lt 14000 ]; then MICRO=2; fi
echo "free_mib=$FREE micro_batch=$MICRO"
.venv/bin/python -m src.corpus.sft train \
  --checkpoint /home/ec2-user/retrain/corpus-v1-8k.pt \
  --pack $R/pack/mix_real1 \
  --out $R/real-v1-8k.pt \
  --log $R/logs/train.jsonl \
  --steps 8000 --batch 32 --micro-batch "$MICRO" \
  --lr 2e-5 --warmup 200 --min-lr-ratio 0.1 \
  --weight-decay 0.0 --grad-clip 1.0 --log-every 50 --ckpt-every 4000 \
  --seed 7701 --shuffle-seed 4113
echo TRAIN_DONE
