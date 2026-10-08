#!/usr/bin/env bash
# HotpotQA on the H200, with every fix from the ProsQA round applied.
#
#   PY=$HOME/venv/bin/python bash scripts/run_hotpot.sh
#
# HotpotQA rather than ProsQA or GSM8K because the pipeline's saving comes from
# compressing the input before the big model reads it. Measured context lengths:
# GSM8K 62 tokens (pipeline costs 10.5x the small model), ProsQA 326 (2.66x),
# HotpotQA 1403 (1.45x, and 12.3x cheaper than the big model with CoT). ProsQA
# also had no capacity gap to transfer: the 0.5B scored 0.723 at 3 hops and
# 0.833 at 6, so a larger model had nothing to add.
#
# The receiver is adapted (--lora_big), which the frozen-receiver runs and
# Interlat's ablation both show is required.
set -uo pipefail
cd "$(dirname "$0")/.."

PY=${PY:-$HOME/venv/bin/python}
N_SMALL=${N_SMALL:-4000}
N_BIG=${N_BIG:-4000}
N_PIPE=${N_PIPE:-4000}
BS=${BS:-8}
SMALL=runs/hp_small/model.pt
BIG=runs/hp_big/model.pt
DATA=data_hotpot   # unused for hotpot (HF datasets cache), kept for the arg

step() { echo; echo "### $* :: $(date -u +%H:%M:%S)"; }

step "0/3 stage 0, Qwen2.5-0.5B on HotpotQA"
[ -f "$SMALL" ] || $PY -u scripts/train_hf.py --model Qwen/Qwen2.5-0.5B --out runs/hp_small \
  --benchmark hotpot --data "$DATA" --n_train "$N_SMALL" --n_val 200 --n_test 500 \
  --epochs_per_stage 1 --batch_size "$BS" --max_latent_stage 4 --lr 2e-5 --dtype bfloat16

step "1/3 stage 0, Qwen2.5-7B on HotpotQA (LoRA)"
[ -f "$BIG" ] || $PY -u scripts/train_hf.py --model Qwen/Qwen2.5-7B --out runs/hp_big \
  --benchmark hotpot --data "$DATA" --n_train "$N_BIG" --n_val 200 --n_test 500 \
  --epochs_per_stage 1 --batch_size "$BS" --max_latent_stage 4 --lora 16 --lr 1e-4 --dtype bfloat16

if [ ! -f "$BIG" ] || [ ! -f "$SMALL" ]; then
  echo "!!! stage 0 did not produce both checkpoints; stopping"
  exit 1
fi

step "2/3 pipeline m=32, adapted receiver (headline)"
$PY -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/hp_pipe_m32 --benchmark hotpot --data "$DATA" --n_train "$N_PIPE" --n_val 200 \
  --batch_size "$BS" --max_latent_stage 4 --n_message 32 --lora_rank 16 --lora_big 16

step "3/3 CONTROL: random receiver (does the big model contribute?)"
$PY -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/hp_pipe_random --benchmark hotpot --data "$DATA" --n_train "$N_PIPE" --n_val 200 \
  --batch_size "$BS" --max_latent_stage 4 --n_message 32 --lora_rank 16 --lora_big 16 --random_big 1

step "hotpot sprint complete"
