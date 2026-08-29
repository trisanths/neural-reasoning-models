#!/bin/bash
# Train the training-ceiling arms. One lane per GPU, arms run in sequence.
#   bash scripts/ceiling_launch.sh lane <gpu> <D:S> [<D:S> ...]
# Every arm shares the base checkpoint, the worlds, the seeds, the optimizer
# steps and the batch size in sequences. Only the ceiling changes.
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
mkdir -p runs/ceiling logs/ceiling
COMMON="--base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
--steps 8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000 --log-every 400 --arm opgraph"

case "${1:-}" in
lane)
  GPU=$2; shift 2
  for spec in "$@"; do
    D=${spec%%:*}; S=${spec##*:}
    NAME="d${D}s${S}"
    echo "[launch] $NAME gpu=$GPU $(date -Is)"
    PYTHONPATH=$ROOT CUDA_VISIBLE_DEVICES=$GPU $ROOT/.venv/bin/python \
      scripts/ceiling_train.py --max-depth "$D" --max-symbols "$S" \
      $COMMON --out "$ROOT/runs/ceiling/$NAME.pt" \
      > "logs/ceiling/$NAME.log" 2>&1
    echo "[done] $NAME status=$? $(date -Is)"
  done
  ;;
*) echo "usage: ceiling_launch.sh lane <gpu> <D:S>..."; exit 2 ;;
esac
