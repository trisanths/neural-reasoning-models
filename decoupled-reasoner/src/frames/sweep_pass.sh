#!/bin/bash
# One evaluation pass: one checkpoint, one episode set, one decode setting.
#
#   bash src/frames/sweep_pass.sh LABEL KIND DECODE GPU BATCH
#     LABEL   base | arm001 | arm003 | arm010 | arm030 | arm072
#     KIND    gen | hand
#     DECODE  greedy | t07
#
# Run from the repo root. Skips a pass whose score file is already newer than
# every dump it would rescore, so a driver can be re-run without redoing work.
set -u
A=$1; KIND=$2; T=$3; GPU=$4; BS=$5
O=${SWEEP:-/home/ec2-user/sweep}
TK=${TOKENIZER:-/home/ec2-user/data/tokenizer_v2.json}
BASE_CK=${BASE_CK:-/home/ec2-user/rlckpt/rlsimple-503-921-final.pt}
if [ "$A" = base ]; then CK=$BASE_CK; else CK=$O/ckpt/$A.pt; fi
[ -s "$CK" ] || { echo "MISSING $CK"; exit 1; }
if [ "$T" = greedy ]; then TEMP=0.0; else TEMP=0.7; fi
S=$O/res/score_$A-$KIND-$T.json
[ -s "$S" ] && { echo "SKIP $A $KIND $T"; exit 0; }
DD=$O/dumps/$A-$KIND-$T
rm -rf "$DD"; mkdir -p "$DD" "$O/res" "$O/logs"
L=$O/logs/eval_$A-$KIND-$T.log
CUDA_VISIBLE_DEVICES=$GPU PYTHONPATH=. .venv/bin/python -m src.frames.cli eval \
  --dir "$O/eval/$KIND" --checkpoint "$CK" --tokenizer "$TK" \
  --out "$O/res/eval_$A-$KIND-$T.json" --dump-dir "$DD" \
  --samples 1 --temperature $TEMP --batch "$BS" --max-len 640 \
  --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 96 \
  --questions-per-episode 2 --seed 99 > "$L" 2>&1 \
  || { echo "EVAL_FAIL $A $KIND $T"; exit 1; }
PYTHONPATH=. .venv/bin/python -m src.frames.cli score \
  --dir "$O/eval/$KIND" --dump-dir "$DD" --out "$S" >> "$L" 2>&1 \
  || { echo "SCORE_FAIL $A $KIND $T"; exit 1; }
echo "PASS_DONE $A $KIND $T $(date -u +%FT%TZ)"
