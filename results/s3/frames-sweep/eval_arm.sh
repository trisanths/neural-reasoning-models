#!/bin/bash
# Evaluate one checkpoint over the sweep's eval set: generated frames and the
# hand-written renderers, greedy and sampled, then score each pass.
# usage: eval_arm.sh ARM CKPT GPU [BATCH]
set -u
ARM=$1; CK=$2; GPU=$3; BS=${4:-64}
cd /home/ec2-user/decoupled-reasoner || exit 1
O=/home/ec2-user/sweep
TK=/home/ec2-user/data/tokenizer_v2.json
mkdir -p $O/res $O/logs $O/dumps
for KIND in gen hand; do
  for T in greedy t07; do
    if [ "$T" = greedy ]; then TEMP=0.0; else TEMP=0.7; fi
    DD=$O/dumps/$ARM-$KIND-$T
    rm -rf "$DD"; mkdir -p "$DD"
    L=$O/logs/eval_$ARM-$KIND-$T.log
    CUDA_VISIBLE_DEVICES=$GPU PYTHONPATH=. .venv/bin/python -m src.frames.cli eval \
      --dir $O/eval/$KIND --checkpoint "$CK" --tokenizer $TK \
      --out $O/res/eval_$ARM-$KIND-$T.json --dump-dir "$DD" \
      --samples 1 --temperature $TEMP --batch $BS --max-len 640 \
      --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 96 \
      --questions-per-episode 2 --seed 99 > "$L" 2>&1 || { echo "EVAL_FAIL $ARM $KIND $T"; exit 1; }
    PYTHONPATH=. .venv/bin/python -m src.frames.cli score \
      --dir $O/eval/$KIND --dump-dir "$DD" \
      --out $O/res/score_$ARM-$KIND-$T.json >> "$L" 2>&1 \
      || { echo "SCORE_FAIL $ARM $KIND $T"; exit 1; }
    echo "PASS_DONE $ARM $KIND $T $(date -u +%FT%TZ)"
  done
done
echo "EVAL_DONE $ARM $(date -u +%FT%TZ)"
