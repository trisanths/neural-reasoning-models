#!/bin/bash
# Train the depth-horizon arms. One lane per GPU, arms run in sequence.
#   bash src/horizon/launch.sh lane <gpu> <D> [<D> ...]
#
# Every flag matches scripts/ceiling_launch.sh exactly, so an arm trained here
# is comparable to d1s1..d8s1 cell for cell: same base checkpoint, same worlds
# from the same seeds, 8000 optimizer steps at batch size 32 in sequences, the
# same learning rate, warmup and schedule, the same 1024 token limit. Only
# --max-depth changes. Symbols are held at one throughout; the symbol ceiling
# is another lane's question.
#
# The 1024 token limit is checked rather than assumed: the longest prompt plus
# plan at depth 64 tokenizes to 793, so no example is dropped at any depth this
# lane trains, and the deep arms are not quietly missing their deepest items.
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
OUTDIR=/mnt/scratch/horizon/runs
mkdir -p "$OUTDIR" logs/horizon
COMMON="--base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
--steps 8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000 --log-every 400 \
--max-len 1024 --arm opgraph"

case "${1:-}" in
lane)
  GPU=$2; shift 2
  for D in "$@"; do
    NAME="d${D}s1"
    if [ -f "$OUTDIR/$NAME.pt" ]; then echo "[skip] $NAME exists"; continue; fi
    echo "[launch] $NAME gpu=$GPU $(date -Is)"
    S=$(date +%s)
    PYTHONPATH=$ROOT CUDA_VISIBLE_DEVICES=$GPU $ROOT/.venv/bin/python \
      scripts/ceiling_train.py --max-depth "$D" --max-symbols 1 \
      $COMMON --out "$OUTDIR/$NAME.pt" \
      > "logs/horizon/$NAME.log" 2>&1
    echo "[done] $NAME status=$? wall=$(( $(date +%s) - S ))s $(date -Is)"
  done
  ;;
*) echo "usage: launch.sh lane <gpu> <D>..."; exit 2 ;;
esac
