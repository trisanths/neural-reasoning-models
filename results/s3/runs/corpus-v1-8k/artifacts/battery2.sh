#!/bin/bash
# The extended frame cell: twelve held-out frames chosen to span the shape
# distance range, including three pure-lexicon frames at shape 0 and three
# imperative-question frames at shape 0.315. Runs after battery.sh.
set -u
cd /home/ec2-user/decoupled-reasoner || exit 1
export PYTHONPATH=.
PY=.venv/bin/python
R=/home/ec2-user/retrain
TK=/home/ec2-user/data/tokenizer_v2.json
BASE=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
NEW=$R/corpus-v1-8k.pt
until grep -q BATTERY_DONE $R/logs/battery.log 2>/dev/null; do sleep 60; done
echo "BATTERY2_START $(date -u +%FT%TZ)"
for W in new base; do
  [ "$W" = base ] && CK=$BASE || CK=$NEW
  for T in greedy t07; do
    [ "$T" = greedy ] && TEMP=0.0 || TEMP=0.7
    echo "STEP framesext $W $T $(date -u +%FT%TZ)"
    DD=$R/frames/dumpext_$W-$T
    rm -rf "$DD"; mkdir -p "$DD"
    $PY -m src.frames.cli eval --dir $R/frames/gen_ext \
      --checkpoint "$CK" --tokenizer $TK \
      --out $R/frames/evalext_$W-$T.json --dump-dir "$DD" \
      --samples 1 --temperature $TEMP --batch 48 --max-len 800 \
      --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 192 \
      --questions-per-episode 2 --seed 99 \
      > $R/logs/framesext_$W-$T.log 2>&1 || echo "FAIL framesext $W $T"
    $PY -m src.frames.cli score --dir $R/frames/gen_ext \
      --dump-dir "$DD" --out $R/frames/scoreext_$W-$T.json \
      >> $R/logs/framesext_$W-$T.log 2>&1 || echo "FAIL framesextscore $W $T"
  done
done
echo "BATTERY2_DONE $(date -u +%FT%TZ)"
