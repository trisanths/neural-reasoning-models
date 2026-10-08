#!/usr/bin/env bash
# Chains the remaining runs so the GPU never idles waiting to be told what to do.
# Ordered by priority: anything that dies partway still leaves the earlier,
# more important artefacts on disk.
#
#   bash scripts/run_sprint.sh 2>&1 | tee ~/sprint.log
set -uo pipefail
cd "$(dirname "$0")/.."

N_BIG=${N_BIG:-1500}      # 7B examples; the binding constraint is wall-clock
N_PIPE=${N_PIPE:-3000}
BS_BIG=${BS_BIG:-4}   # 8 OOMs: 6 sequential latent passes each retain a graph
SMALL=runs/qwen05b/model.pt
BIG=runs/qwen7b/model.pt

step() { echo; echo "### $* :: $(date -u +%H:%M:%S)"; }

if [ -f "$BIG" ]; then
  echo "### 1/5 skipped: $BIG already exists"
else
step "1/5 stage 0, Qwen2.5-7B (LoRA, n=$N_BIG)"
python3 -u scripts/train_hf.py --model Qwen/Qwen2.5-7B --out runs/qwen7b \
  --n_train "$N_BIG" --n_val 200 --n_test 500 --epochs_per_stage 1 \
  --batch_size "$BS_BIG" --max_latent_stage 6 --lora 16 --lr 1e-4 --dtype bfloat16
fi

if [ ! -f "$BIG" ]; then
  echo "!!! $BIG missing - stage 0 for the 7B failed; skipping every step that needs it"
  exit 1
fi

step "2/5 pipeline stages 1-3, m=32 (headline config)"
python3 -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/pipe_m32 --data data_prosqa --n_train "$N_PIPE" --n_val 200 \
  --batch_size 8 --max_latent_stage 6 --n_message 32 --lora_rank 16

step "3/5 control: random frozen receiver (did the projectors learn it alone?)"
python3 -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
  --out runs/pipe_random --data data_prosqa --n_train "$N_PIPE" --n_val 200 \
  --batch_size 8 --max_latent_stage 6 --n_message 32 --lora_rank 16 --random_big 1

step "4/5 compression sweep, m=8 and m=128"
for M in 8 128; do
  python3 -u scripts/train_pipeline.py --small_ckpt $SMALL --big_ckpt $BIG \
    --out "runs/pipe_m$M" --data data_prosqa --n_train "$N_PIPE" --n_val 200 \
    --batch_size 8 --max_latent_stage 6 --n_message "$M" --lora_rank 16
done

step "5/5 re-score both stage-0 models with the corrected generation budget"
python3 -u scripts/eval_hf.py --ckpt $SMALL --out runs/eval_small.json
python3 -u scripts/eval_hf.py --ckpt $BIG   --out runs/eval_big.json

step "sprint complete"
