#!/bin/bash
# After the main battery: the two instrument controls first, then the extended
# frame cell.
#
#  A. the shipped opgraph conditions on the transposed pages, on the opgraph
#     arms the recorded 0-of-678 belongs to and on the two checkpoints here
#  B. the corpus plan eval set on the opgraph arm, which is the checkpoint the
#     three-step ceiling was read off, on the same items
#  C. twelve more held-out frames spanning the shape-distance range
set -u
cd /home/ec2-user/decoupled-reasoner || exit 1
export PYTHONPATH=.
PY=.venv/bin/python
R=/home/ec2-user/retrain
TK=/home/ec2-user/data/tokenizer_v2.json
BASE=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
NEW=$R/corpus-v1-8k.pt
OPG=/home/ec2-user/opg/runs/opgraph.pt
DIR=/home/ec2-user/opg/runs/direct.pt
until grep -q BATTERY_DONE $R/logs/battery.log 2>/dev/null; do sleep 60; done
echo "B34_START $(date -u +%FT%TZ)"

# ---------------------------------------------------------------- A
runA () {
  W=$1; CK=$2
  for T in greedy t1; do
    [ "$T" = greedy ] && TEMP=0.0 || TEMP=1.0
    echo "STEP direct $W $T $(date -u +%FT%TZ)"
    $PY -m src.corpus.evalrun plan --checkpoint "$CK" --tokenizer $TK \
      --records $R/transposed/direct_records.jsonl \
      --out $R/transposed/direct_${W}_$T.jsonl --label $T --temperature $TEMP \
      --batch 32 --max-new-tokens 32 > $R/logs/dir_${W}_$T.log 2>&1 \
      || echo "FAIL direct $W $T"
    echo "STEP induce $W $T $(date -u +%FT%TZ)"
    $PY -m src.corpus.evalrun plan --checkpoint "$CK" --tokenizer $TK \
      --records $R/transposed/induce_records.jsonl \
      --out $R/transposed/induce_${W}_$T.jsonl --label $T --temperature $TEMP \
      --batch 32 --max-new-tokens 288 > $R/logs/ind_${W}_$T.log 2>&1 \
      || echo "FAIL induce $W $T"
  done
  cat $R/transposed/direct_${W}_greedy.jsonl $R/transposed/direct_${W}_t1.jsonl \
    > $R/transposed/direct_all_$W.jsonl
  cat $R/transposed/induce_${W}_greedy.jsonl $R/transposed/induce_${W}_t1.jsonl \
    > $R/transposed/induce_all_$W.jsonl
  $PY -m src.corpus.rescore transposed --rolls $R/transposed/direct_all_$W.jsonl \
    --out $R/transposed/score_direct_$W.json > $R/logs/dir_score_$W.log 2>&1
  $PY $R/tr3.py --rolls $R/transposed/induce_all_$W.jsonl \
    --out $R/transposed/score_induce_$W.json > $R/logs/ind_score_$W.log 2>&1
}
runA opgrapharm $OPG
runA directarm  $DIR
runA new        $NEW
runA base       $BASE
echo "A_DONE $(date -u +%FT%TZ)"

# ---------------------------------------------------------------- B
for SET in heldout_whole_sample extrap_whole; do
  for T in greedy t1; do
    [ "$T" = greedy ] && TEMP=0.0 || TEMP=1.0
    echo "STEP planarm $SET $T $(date -u +%FT%TZ)"
    $PY -m src.corpus.evalrun plan --checkpoint $OPG --tokenizer $TK \
      --records $R/plan/$SET.jsonl --out $R/plan/gen_opgrapharm_${SET}_$T.jsonl \
      --label $T --temperature $TEMP --batch 32 --max-new-tokens 1200 \
      > $R/logs/plan_opgrapharm_${SET}_$T.log 2>&1 || echo "FAIL planarm $SET $T"
  done
  cat $R/plan/gen_opgrapharm_${SET}_greedy.jsonl \
      $R/plan/gen_opgrapharm_${SET}_t1.jsonl > $R/plan/all_opgrapharm_$SET.jsonl
  $PY -m src.corpus.rescore plan --rolls $R/plan/all_opgrapharm_$SET.jsonl \
    --out $R/plan/score_opgrapharm_$SET.json \
    --records-out $R/plan/rows_opgrapharm_$SET.jsonl \
    > $R/logs/plan_score_opgrapharm_$SET.log 2>&1
done
echo "B_DONE $(date -u +%FT%TZ)"

# ---------------------------------------------------------------- C
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
echo "B34_DONE $(date -u +%FT%TZ)"
