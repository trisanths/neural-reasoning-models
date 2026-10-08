#!/usr/bin/env bash
# Pipeline arms only, sized to finish inside a fixed window.
#
#   PY=$HOME/venv/bin/python bash scripts/run_hotpot_pipe.sh
#
# Run this once stage 0 has produced both checkpoints. Kept separate from
# run_hotpot.sh so the epoch counts can be tuned without editing a script bash
# is already executing (bash reads by byte offset, so editing a running script
# corrupts it).
#
# Epochs are cut to 1/1/0 rather than the 2/3/1 default. Both models are
# resident and HotpotQA contexts average 1403 tokens, so each step costs far
# more than on ProsQA. The controls matter more than extra epochs: without the
# random-receiver arm the headline number cannot be distinguished from the
# projectors having learned the task themselves.
set -uo pipefail
cd "$(dirname "$0")/.."

PY=${PY:-$HOME/venv/bin/python}
N=${N:-2000}
BS=${BS:-2}
SMALL=runs/hp_small/model.pt
BIG=runs/hp_big/model.pt

step() { echo; echo "### $* :: $(date -u +%H:%M:%S)"; }

for f in "$SMALL" "$BIG"; do
  [ -f "$f" ] || { echo "!!! missing $f"; exit 1; }
done

step "A. pipeline m=32, adapted receiver (HEADLINE)"
$PY -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/hp_pipe_m32 --benchmark hotpot --data x --n_train "$N" --n_val 200 \
  --batch_size "$BS" --max_latent_stage 3 --n_message 32 --lora_rank 16 --lora_big 16 \
  --epochs_s1 1 --epochs_s2 1 --epochs_s3 0

step "B. CONTROL random receiver (does the big model contribute?)"
$PY -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/hp_pipe_random --benchmark hotpot --data x --n_train "$N" --n_val 200 \
  --batch_size "$BS" --max_latent_stage 3 --n_message 32 --lora_rank 16 --lora_big 16 \
  --random_big 1 --epochs_s1 1 --epochs_s2 1 --epochs_s3 0

step "pipeline arms complete"
