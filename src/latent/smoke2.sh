#!/bin/bash
# Condition D lanes, run one after another on a single GPU.
#   bash src/latent/smoke2.sh <gpu>
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
GPU=${1:-0}
mkdir -p runs/latent logs results/latent
TOK=/home/ec2-user/data/tokenizer_v2.json
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
COMMON="--base ckpt/base350.pt --tokenizer $TOK --steps 800 --batch-size 4 \
--max-len 1024 --lr 2e-5 --warmup 80 --worlds 4000 --log-every 25"

train () {  local name=$1; shift
  echo "[launch] $name gpu=$GPU $(date -Is)"
  CUDA_VISIBLE_DEVICES=$GPU PYTHONPATH=$ROOT uv run python -m src.latent.train \
    $COMMON "$@" --out "$ROOT/runs/latent/$name.pt" > "logs/latent_$name.log" 2>&1
  echo "[done] $name status=$? $(date -Is)"
}

evaluate () { local name=$1 rl=$2
  CUDA_VISIBLE_DEVICES=$GPU PYTHONPATH=$ROOT uv run python -m src.latent.eval \
    --ckpt "$ROOT/runs/latent/$name.pt" --tokenizer $TOK \
    --out "$ROOT/results/latent/$name.json" --r "$rl" \
    --depths 1,2,3,4,5,8 --breadths 1,2,3,4,5 --kinds sequential,breadth \
    --n 24 --samples 2 --batch-size 8 >> "logs/latent_$name.log" 2>&1
  echo "[eval done] $name status=$? $(date -Is)"
}

train answer_nocur --arm latent_answer --r 4
evaluate answer_nocur 0,2,4,8
train answer_stage --arm latent_answer --r 6 --curriculum stage \
  --latents-per-step 2 --stage-steps 200 --stage-mix 0.3 --backprop-last-k 2
evaluate answer_stage 0,2,4,6,8
echo "[lane done] $(date -Is)"
