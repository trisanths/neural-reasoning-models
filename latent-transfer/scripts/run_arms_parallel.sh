#!/usr/bin/env bash
# Headline and control, run concurrently.
#
#   PY=$HOME/venv/bin/python bash scripts/run_arms_parallel.sh
#
# Each arm holds both models at batch 2 and uses roughly 60 GB, so on a 143 GB
# card they fit side by side. Running them together rather than back to back
# halves wall-clock for free, which matters because the control is not optional:
# without it the headline cannot be distinguished from the projectors having
# learned the task on their own, which is exactly what the ProsQA round showed.
set -uo pipefail
cd "$(dirname "$0")/.."

PY=${PY:-$HOME/venv/bin/python}
N=${N:-1500}
BS=${BS:-2}
SMALL=runs/hp_small/model.pt
BIG=runs/hp_big/model.pt

for f in "$SMALL" "$BIG"; do
  [ -f "$f" ] || { echo "!!! missing $f"; exit 1; }
done

common=(--benchmark hotpot --data x --n_train "$N" --n_val 200
        --batch_size "$BS" --max_latent_stage 3 --n_message 32
        --lora_rank 16 --lora_big 16 --epochs_s1 1 --epochs_s2 1 --epochs_s3 0)

echo "### launching both arms :: $(date -u +%H:%M:%S)"

CUDA_MEM_FRACTION=0.46 $PY -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/hp_pipe_m32 "${common[@]}" > ~/arm_head.log 2>&1 &
HEAD=$!

CUDA_MEM_FRACTION=0.46 $PY -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/hp_pipe_random "${common[@]}" --random_big 1 > ~/arm_ctrl.log 2>&1 &
CTRL=$!

echo "headline pid=$HEAD  control pid=$CTRL"
wait $HEAD; echo "### headline exited $? :: $(date -u +%H:%M:%S)"
wait $CTRL; echo "### control exited $? :: $(date -u +%H:%M:%S)"
echo "### both arms complete :: $(date -u +%H:%M:%S)"
