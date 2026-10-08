#!/bin/bash
# Launch the three arms of the composition experiment on the training box.
#
#   bash scripts/opgraph_launch.sh all    detach both lanes and return
#   bash scripts/opgraph_launch.sh lane5  the direct arm, in the foreground
#   bash scripts/opgraph_launch.sh lane7  the opgraph arm then the trace arm
#
# GPU 5 carries one lane and GPU 7 carries the other. Every arm gets the same
# base checkpoint, the same worlds, the same optimizer steps and the same batch
# size in sequences, so the arms differ only in what they are asked to produce.
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
mkdir -p runs logs
COMMON="--base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
--steps 8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000 --log-every 400"

run () {  # run <gpu> <arm>
  echo "[launch] arm=$2 gpu=$1 $(date -Is)"
  PYTHONPATH=$ROOT CUDA_VISIBLE_DEVICES=$1 uv run python scripts/opgraph_train.py \
    $COMMON --arm "$2" --out "$ROOT/runs/$2.pt" > "logs/$2.log" 2>&1
  echo "[done] arm=$2 status=$? $(date -Is)"
}

case "${1:-all}" in
  lane5) run 5 direct ;;
  lane7) run 7 opgraph; run 7 trace ;;
  direct) run "${2:-5}" direct ;;
  opgraph) run "${2:-7}" opgraph ;;
  trace) run "${2:-7}" trace ;;
  all)
    setsid nohup bash "$ROOT/scripts/opgraph_launch.sh" lane5 > logs/lane5.log 2>&1 < /dev/null &
    setsid nohup bash "$ROOT/scripts/opgraph_launch.sh" lane7 > logs/lane7.log 2>&1 < /dev/null &
    sleep 2
    echo "launched"
    ;;
  *) echo "unknown lane $1"; exit 2 ;;
esac
