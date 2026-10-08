#!/usr/bin/env bash
# Splits the two explanations for the m=32 failure.
#
# Uncompressed, every small-model state crosses to the big model, so nothing is
# lost in the handoff itself. If this recovers the big model's accuracy then the
# mechanism works and compression is the tradeoff to characterise; if it lands
# near the small model's 0.734 then the handoff never transferred reasoning at
# all and no amount of compression tuning will help.
#
# Running uncompressed also restores the [gate s1] big-from-projected check,
# which is skipped whenever n_message is set, so a failure can be localised to
# the up- or the down-projector.
set -uo pipefail
cd "$(dirname "$0")/.."

SMALL=runs/qwen05b/model.pt
BIG=runs/qwen7b/model.pt
N=${N:-2000}

step() { echo; echo "### $* :: $(date -u +%H:%M:%S)"; }

step "A. uncompressed pipeline (n_message=None) - the diagnostic"
python3 -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/pipe_full --data data_prosqa --n_train "$N" --n_val 200 \
  --batch_size 4 --max_latent_stage 6 --lora_rank 16

step "B. m=128 - only informative if A worked"
python3 -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/pipe_m128 --data data_prosqa --n_train "$N" --n_val 200 \
  --batch_size 8 --max_latent_stage 6 --n_message 128 --lora_rank 16

step "diagnostic complete"
