#!/bin/bash
# Evaluate one or more sweep arms on one card: generated frames and the
# hand-written renderers, greedy and sampled, scored after each pass.
#
#   bash src/frames/sweep_eval.sh GPU BATCH base arm001 arm003 ...
#
# Run from the repo root. Reads $SWEEP (default ~/sweep) for the eval set and
# the arm checkpoints, and writes dumps, per-cell scores and logs back there.
set -u
GPU=$1; BS=$2; shift 2
O=${SWEEP:-/home/ec2-user/sweep}
TK=${TOKENIZER:-/home/ec2-user/data/tokenizer_v2.json}
BASE_CK=${BASE_CK:-/home/ec2-user/rlckpt/rlsimple-503-921-final.pt}
mkdir -p "$O/res" "$O/logs" "$O/dumps"
for A in "$@"; do
  if [ "$A" = base ]; then CK=$BASE_CK; else CK=$O/ckpt/$A.pt; fi
  [ -s "$CK" ] || { echo "MISSING $CK"; exit 1; }
  for KIND in gen hand; do
    for T in greedy t07; do
      if [ "$T" = greedy ]; then TEMP=0.0; else TEMP=0.7; fi
      DD=$O/dumps/$A-$KIND-$T
      rm -rf "$DD"; mkdir -p "$DD"
      L=$O/logs/eval_$A-$KIND-$T.log
      CUDA_VISIBLE_DEVICES=$GPU PYTHONPATH=. .venv/bin/python -m src.frames.cli eval \
        --dir "$O/eval/$KIND" --checkpoint "$CK" --tokenizer "$TK" \
        --out "$O/res/eval_$A-$KIND-$T.json" --dump-dir "$DD" \
        --samples 1 --temperature $TEMP --batch "$BS" --max-len 640 \
        --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 96 \
        --questions-per-episode 2 --seed 99 > "$L" 2>&1 \
        || { echo "EVAL_FAIL $A $KIND $T"; exit 1; }
      PYTHONPATH=. .venv/bin/python -m src.frames.cli score \
        --dir "$O/eval/$KIND" --dump-dir "$DD" \
        --out "$O/res/score_$A-$KIND-$T.json" >> "$L" 2>&1 \
        || { echo "SCORE_FAIL $A $KIND $T"; exit 1; }
      echo "PASS_DONE $A $KIND $T $(date -u +%FT%TZ)"
    done
  done
  echo "ARM_DONE $A $(date -u +%FT%TZ)"
done
echo "EVAL_ALL_DONE $(date -u +%FT%TZ)"
