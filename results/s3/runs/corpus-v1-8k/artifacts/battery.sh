#!/bin/bash
# The whole re-measurement, both checkpoints, one harness, run in the order the
# report is written in: gate first, then the transposed rule, then frames, then
# plan length and symbols, then relation type.
set -u
cd /home/ec2-user/decoupled-reasoner || exit 1
export PYTHONPATH=.
PY=.venv/bin/python
R=/home/ec2-user/retrain
TK=/home/ec2-user/data/tokenizer_v2.json
BASE=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
NEW=$R/corpus-v1-8k.pt
mkdir -p $R/gate $R/transposed $R/plan $R/relation $R/frames $R/logs

# wait for training to land
while [ ! -f "$NEW" ]; do sleep 60; done
sleep 30
echo "BATTERY_START $(date -u +%FT%TZ)"

step () { echo "STEP $* $(date -u +%FT%TZ)"; }

# ---------------------------------------------------------------- 1. gate
for W in base new; do
  [ "$W" = base ] && CK=$BASE || CK=$NEW
  step gate $W
  $PY scripts/mg_threeway_eval.py --checkpoint "$CK" --tokenizer $TK \
    --config configs/mg3-gate.yaml --suite gate \
    --episodes-dir /home/ec2-user/mg3/gate \
    --out $R/gate/roll_gate_$W.jsonl --samples 4 --temperature 1.0 --batch 24 \
    > $R/logs/gate_$W.log 2>&1 || echo "FAIL gate $W"
  $PY scripts/mg_strict_rescore.py --rollouts $R/gate/roll_gate_$W.jsonl \
    --suite gate --episodes-dir /home/ec2-user/mg3/gate \
    --out $R/gate/strict_gate_$W.json \
    --graded-out $R/gate/graded_gate_$W.jsonl \
    >> $R/logs/gate_$W.log 2>&1 || echo "FAIL rescore $W"
done
echo "GATE_DONE $(date -u +%FT%TZ)"

# --------------------------------------------------------- 2. transposed rule
for W in new base; do
  [ "$W" = base ] && CK=$BASE || CK=$NEW
  step transposed $W
  $PY -m src.corpus.evalrun gen --checkpoint "$CK" --tokenizer $TK \
    --episodes $R/transposed/ep.jsonl --out $R/transposed/gen_${W}_greedy.jsonl \
    --label greedy --samples 1 --temperature 0.0 --batch 32 --max-rounds 2 \
    --max-new-tokens 256 --max-len 1280 --questions-per-episode 1 \
    > $R/logs/tr_${W}_greedy.log 2>&1 || echo "FAIL tr $W greedy"
  $PY -m src.corpus.evalrun gen --checkpoint "$CK" --tokenizer $TK \
    --episodes $R/transposed/ep.jsonl --out $R/transposed/gen_${W}_t1.jsonl \
    --label t1 --samples 4 --temperature 1.0 --batch 32 --max-rounds 2 \
    --max-new-tokens 256 --max-len 1280 --questions-per-episode 1 \
    > $R/logs/tr_${W}_t1.log 2>&1 || echo "FAIL tr $W t1"
  $PY -m src.corpus.evalrun mc --checkpoint "$CK" --tokenizer $TK \
    --episodes $R/transposed/ep.jsonl.incontext --out $R/transposed/mc_$W.jsonl \
    > $R/logs/tr_${W}_mc.log 2>&1 || echo "FAIL tr $W mc"
  cat $R/transposed/gen_${W}_greedy.jsonl $R/transposed/gen_${W}_t1.jsonl \
      $R/transposed/mc_$W.jsonl > $R/transposed/all_$W.jsonl
  $PY -m src.corpus.rescore transposed --rolls $R/transposed/all_$W.jsonl \
    --out $R/transposed/score_$W.json > $R/logs/tr_score_$W.log 2>&1
done
echo "TRANSPOSED_DONE $(date -u +%FT%TZ)"

# ------------------------------------------------------------------ 3. frames
for W in new base; do
  [ "$W" = base ] && CK=$BASE || CK=$NEW
  for T in greedy t07; do
    [ "$T" = greedy ] && TEMP=0.0 || TEMP=0.7
    step frames $W $T
    DD=$R/frames/dump_$W-$T
    rm -rf "$DD"; mkdir -p "$DD"
    $PY -m src.frames.cli eval --dir /home/ec2-user/sweep/eval/gen \
      --checkpoint "$CK" --tokenizer $TK \
      --out $R/frames/eval_$W-$T.json --dump-dir "$DD" \
      --samples 1 --temperature $TEMP --batch 48 --max-len 800 \
      --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 192 \
      --questions-per-episode 2 --seed 99 \
      > $R/logs/frames_$W-$T.log 2>&1 || echo "FAIL frames $W $T"
    $PY -m src.frames.cli score --dir /home/ec2-user/sweep/eval/gen \
      --dump-dir "$DD" --out $R/frames/score_$W-$T.json \
      >> $R/logs/frames_$W-$T.log 2>&1 || echo "FAIL framescore $W $T"
  done
done
echo "FRAMES_DONE $(date -u +%FT%TZ)"

# ------------------------------------------------- 4. plan length and symbols
for W in new base; do
  [ "$W" = base ] && CK=$BASE || CK=$NEW
  for SET in heldout_whole_sample extrap_whole; do
    for T in greedy t1; do
      [ "$T" = greedy ] && TEMP=0.0 || TEMP=1.0
      step plan $W $SET $T
      $PY -m src.corpus.evalrun plan --checkpoint "$CK" --tokenizer $TK \
        --records $R/plan/$SET.jsonl --out $R/plan/gen_${W}_${SET}_$T.jsonl \
        --label $T --temperature $TEMP --batch 32 --max-new-tokens 1200 \
        > $R/logs/plan_${W}_${SET}_$T.log 2>&1 || echo "FAIL plan $W $SET $T"
    done
    cat $R/plan/gen_${W}_${SET}_greedy.jsonl $R/plan/gen_${W}_${SET}_t1.jsonl \
      > $R/plan/all_${W}_${SET}.jsonl
    $PY -m src.corpus.rescore plan --rolls $R/plan/all_${W}_${SET}.jsonl \
      --out $R/plan/score_${W}_${SET}.json \
      --records-out $R/plan/rows_${W}_${SET}.jsonl \
      > $R/logs/plan_score_${W}_${SET}.log 2>&1
  done
done
echo "PLAN_DONE $(date -u +%FT%TZ)"

# ------------------------------------------------------------- 5. relation type
for W in new base; do
  [ "$W" = base ] && CK=$BASE || CK=$NEW
  for BAND in heldout train; do
    for T in greedy t1; do
      [ "$T" = greedy ] && TEMP=0.0 || TEMP=1.0
      step relation $W $BAND $T
      $PY -m src.corpus.evalrun gen --checkpoint "$CK" --tokenizer $TK \
        --episodes $R/relation/rel_$BAND.jsonl \
        --out $R/relation/gen_${W}_${BAND}_$T.jsonl --label $T --samples 1 \
        --temperature $TEMP --batch 32 --max-rounds 6 --max-new-tokens 256 \
        --max-len 1920 --questions-per-episode 2 \
        > $R/logs/rel_${W}_${BAND}_$T.log 2>&1 || echo "FAIL rel $W $BAND $T"
    done
    cat $R/relation/gen_${W}_${BAND}_greedy.jsonl \
        $R/relation/gen_${W}_${BAND}_t1.jsonl > $R/relation/all_${W}_$BAND.jsonl
    $PY -m src.corpus.rescore relation --rolls $R/relation/all_${W}_$BAND.jsonl \
      --out $R/relation/score_${W}_$BAND.json \
      > $R/logs/rel_score_${W}_$BAND.log 2>&1
  done
done
echo "BATTERY_DONE $(date -u +%FT%TZ)"
