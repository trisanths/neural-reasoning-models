#!/bin/bash
# Smoke run for the two latent conditions. Tiny scale on purpose: this shows
# each condition trains, produces answers the harness scores, and that the
# forward pass and wall clock counters are right. It is not the sweep.
#
#   bash src/latent/smoke.sh d6      condition D, no curriculum, GPU 6
#   bash src/latent/smoke.sh e7      condition E, no curriculum, GPU 7
#   bash src/latent/smoke.sh dcur4   condition D, stage curriculum, GPU 4
#   bash src/latent/smoke.sh all     all three, detached
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
mkdir -p runs/latent logs results/latent
TOK=/home/ec2-user/data/tokenizer_v2.json
COMMON="--base ckpt/base350.pt --tokenizer $TOK --steps 800 --batch-size 8 \
--max-len 1024 --lr 2e-5 --warmup 80 --worlds 4000 --log-every 25"

train () {  # train <gpu> <name> <extra args...>
  local gpu=$1 name=$2; shift 2
  echo "[launch] $name gpu=$gpu $(date -Is)"
  CUDA_VISIBLE_DEVICES=$gpu PYTHONPATH=$ROOT uv run python -m src.latent.train \
    $COMMON "$@" --out "$ROOT/runs/latent/$name.pt" > "logs/latent_$name.log" 2>&1
  echo "[done] $name status=$? $(date -Is)"
}

evaluate () {  # evaluate <gpu> <name> <rlist>
  local gpu=$1 name=$2 rl=$3
  CUDA_VISIBLE_DEVICES=$gpu PYTHONPATH=$ROOT uv run python -m src.latent.eval \
    --ckpt "$ROOT/runs/latent/$name.pt" --tokenizer $TOK \
    --out "$ROOT/results/latent/$name.json" --r "$rl" \
    --depths 1,2,3,4,5,8 --breadths 1,2,3,4,5 --kinds sequential,breadth \
    --n 24 --samples 2 --batch-size 12 >> "logs/latent_$name.log" 2>&1
  echo "[eval done] $name status=$?"
}

case "${1:-all}" in
  d6)
    train 6 answer_nocur --arm latent_answer --r 4
    evaluate 6 answer_nocur 0,2,4,8
    ;;
  e7)
    train 7 plan_nocur --arm latent_plan --r 4
    evaluate 7 plan_nocur 0,2,4,8
    ;;
  dcur4)
    train 4 answer_stage --arm latent_answer --r 4 --curriculum stage \
      --latents-per-step 2 --stage-steps 200 --stage-mix 0.3
    evaluate 4 answer_stage 0,2,4,6,8
    ;;
  all)
    setsid nohup bash "$ROOT/src/latent/smoke.sh" d6 > logs/latent_lane6.log 2>&1 < /dev/null &
    setsid nohup bash "$ROOT/src/latent/smoke.sh" e7 > logs/latent_lane7.log 2>&1 < /dev/null &
    setsid nohup bash "$ROOT/src/latent/smoke.sh" dcur4 > logs/latent_lane4.log 2>&1 < /dev/null &
    sleep 2
    echo "launched"
    ;;
  *) echo "unknown lane $1"; exit 2 ;;
esac
