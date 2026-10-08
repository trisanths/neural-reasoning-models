#!/bin/bash
# The shipped opgraph conditions on the transposed pages, on the two arms the
# recorded number came from and on the two checkpoints under test.
set -u
cd /home/ec2-user/decoupled-reasoner || exit 1
export PYTHONPATH=.
PY=.venv/bin/python
R=/home/ec2-user/retrain
TK=/home/ec2-user/data/tokenizer_v2.json
until grep -q BATTERY2_DONE $R/logs/battery2.log 2>/dev/null; do sleep 60; done
echo "BATTERY3_START $(date -u +%FT%TZ)"
run () {  # name ckpt
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
run opgrapharm /home/ec2-user/opg/runs/opgraph.pt
run directarm  /home/ec2-user/opg/runs/direct.pt
run new        $R/corpus-v1-8k.pt
run base       /home/ec2-user/rlckpt/rlsimple-503-921-final.pt
echo "BATTERY3_DONE $(date -u +%FT%TZ)"
