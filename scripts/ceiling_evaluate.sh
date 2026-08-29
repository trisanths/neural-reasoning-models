#!/bin/bash
# Score training-ceiling arms. One lane per GPU, arms in sequence.
#   bash scripts/ceiling_evaluate.sh lane <gpu> <name> [<name> ...]
# Names are the checkpoint stems under runs/ceiling, e.g. d3s1.
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
mkdir -p results/ceiling logs/ceiling
N=${N:-100}
BS=${BS:-64}
STYLES=${STYLES:-0,1}
TEMPS=${TEMPS:-0.0,0.8}

case "${1:-}" in
lane)
  GPU=$2; shift 2
  for NAME in "$@"; do
    CK="$ROOT/runs/ceiling/$NAME.pt"
    [ -f "$CK" ] || { echo "[skip] $NAME no checkpoint"; continue; }
    echo "[eval] $NAME gpu=$GPU $(date -Is)"
    PYTHONPATH=$ROOT CUDA_VISIBLE_DEVICES=$GPU $ROOT/.venv/bin/python \
      scripts/ceiling_eval.py --ckpt "$CK" \
      --tokenizer /home/ec2-user/data/tokenizer_v2.json --arm "$NAME" \
      --out "$ROOT/results/ceiling/$NAME.json" \
      --records "$ROOT/results/ceiling/$NAME.records.jsonl" \
      --n "$N" --batch-size "$BS" --styles "$STYLES" --temperatures "$TEMPS" \
      > "logs/ceiling/eval_$NAME.log" 2>&1
    echo "[done] $NAME status=$? $(date -Is)"
  done
  ;;
*) echo "usage: ceiling_evaluate.sh lane <gpu> <name>..."; exit 2 ;;
esac
