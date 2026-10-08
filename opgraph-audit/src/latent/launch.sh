#!/bin/bash
# Start the two training lanes of the depth by recurrence sweep, detached.
# usage: bash src/latent/launch.sh
#
# Each lane waits for a card with real headroom rather than crowding one, since
# an out of memory kill on this box takes someone else's run with it.
set -u
cd /home/ec2-user/opg
mkdir -p logs runs/latent results/latent
export PYTHONPATH=$PWD

# --r-choices is sampled uniformly, so the repeats are weights: R is drawn from
# {1,2,4,8,16,32} with the small values more likely. Mean 7.8, which is the
# forward pass multiplier this run pays over the token channel arms' one.
# --backprop-last-k 3 is truncated backpropagation through the chain: the head
# is trained at every slot, the backbone only over the last three passes.
# Backpropagating through all thirty three passes of an R = 32 chain does not
# fit at batch 32 on an 80 GiB card and this is the compromise, reported rather
# than buried.
COMMON="--steps 8000 --batch-size 32 --max-len 1024 --lr 2e-5 --warmup 200 \
--worlds 40000 --seed 0 --log-every 50 --save-every 1000 \
--r-choices 1,1,2,2,4,4,8,8,16,32 --backprop-last-k 3"

start () {   # start LANE ARM MICRO NEED_GIB
  local lane=$1 arm=$2 micro=$3 need=$4
  if pgrep -f "src.latent.train.*runs/latent/$lane.pt" > /dev/null; then
    echo "[$lane] already running"; return 0
  fi
  local gpu
  gpu=$(uv run python src/latent/pick_gpu.py --need "$need" --count 1 \
        --wait 7200 --poll 90) || { echo "[$lane] no free card"; return 1; }
  echo "[$lane] gpu $gpu"
  CUDA_VISIBLE_DEVICES=$gpu setsid nohup uv run python -m src.latent.train \
    --base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
    --arm "$arm" --out "runs/latent/$lane.pt" --micro-batch "$micro" \
    $COMMON > "logs/latent_$lane.log" 2>&1 < /dev/null &
  sleep 5
  echo "[$lane] pid $!"
}

start dsweep latent_answer 8 28
start esweep latent_plan 32 22
echo "[launch] done"
