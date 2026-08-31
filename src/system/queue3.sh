#!/bin/bash
# Everything still owed, one job at a time on the one card.
#
# Three things changed from queue2. Scoring reads the whole 7,000 item eval
# file rather than the first 2,800 of it, because that prefix is not a sample:
# the qframe file lists its 35 key-first frames before its 35 value-first ones,
# so 2,800 of 7,000 was every key-first item and no value-first one, and the
# two rungs already scored are scored again. The two new frame splits run
# early, because whether the positional collapse is about one withheld constant
# or about any withheld axis value is worth more than another rung of a ladder
# that is already flat. And the 350M arm runs as one block, its harness having
# been exercised on a handful of items first.
#
# Every stage is skipped when its output is already there, so this can be
# killed and restarted without repeating work.
cd ~/decoupled-reasoner
set -u
export PYTHONPATH=.
export AWS_PROFILE=chronos
P=.venv/bin/python
L=logs/system
T=results/system/train
E=results/system/eval
F=results/system/lmframe
G=results/system/gate
M=results/system/lm
TK=/home/ec2-user/data/tokenizer_v2.json
BASE=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
CORPUS=/home/ec2-user/retrain/corpus-v1-8k.pt
NEVAL=7000
mkdir -p $L $T $E $F $G $M results/system/lmeval results/system/tpose
say () { echo "$(date -u +%H:%M:%S) $*" >> $L/queue.log; }
doc () { $P -m src.system.threport >> $L/threport.log 2>&1; say "threport rc=$?"; }
lrof () { cat results/system/lr_$1 2>/dev/null || echo 0; }

# tag ckpt datadir  -- scores the whole eval file, skipping work already done
score () {
  if [ -f $E/$1/summary.json ]; then say "eval $1 already present"; return; fi
  $P -m src.system.sreport --ckpt "$2" --tag "$1" --data "$3" \
     --n $NEVAL --batch 64 >> $L/eval_$1.log 2>&1
  say "eval $1 rc=$?"
}
rescore () {
  if [ -f $E/$1/summary.json ] && \
     grep -q "\"eval_n\": $NEVAL" $E/$1/summary.json 2>/dev/null; then
    say "eval $1 already at n=$NEVAL"; return
  fi
  rm -f $E/$1/summary.json
  score "$1" "$2" "$3"
}
# tag size datadir lr
rung () {
  if [ ! -f $T/ckpt_$1.pt ]; then
    $P -m src.system.strain --size $2 --micro 1 --steps 30000 --lr $4 \
       --data "$3" --eval-every 3000 --eval-n 700 --out $T --tag $1 \
       >> $L/train_$1.log 2>&1
    say "train $1 rc=$?"
  else
    say "train $1 checkpoint already present"
  fi
  score "$1" "$T/ckpt_$1.pt" "$3"
}

say "queue3 starts"

# 1. the rate control queue2 had already launched
while kill -0 180771 2>/dev/null; do sleep 20; done
say "train xl93lr40 ended"
score xl93lr40 $T/ckpt_xl93lr40.pt data/norm
doc

# 2. the two rungs, on the whole eval file this time
rescore l45 results/norm/train/ckpt_l.pt data/norm
rescore xl93 $T/ckpt_xl93.pt data/norm
doc

# 3. one whole value of the question-form axis withheld, in place of the band.
#    Its held-out group carries 70 key-first frames and 70 value-first ones,
#    which the band's group did not, so the key-position split can be read on
#    an axis that is not statement mode.
while [ ! -f data/normC/manifest.json ]; do sleep 30; done
rung c45 l45 data/normC 0
doc

# 4. a different statement mode withheld, table_row for relative_clause, the
#    split otherwise identical at 490 training frames
while [ ! -f data/normB/manifest.json ]; do sleep 30; done
rung b45 l45 data/normB 0
doc

# 5. the 350M arm, whole
if [ ! -f $G/strict_gate_base.json ]; then
  $P scripts/mg_threeway_eval.py --checkpoint $BASE --tokenizer $TK \
     --config configs/mg3-gate.yaml --suite gate \
     --episodes-dir /home/ec2-user/mg3/gate \
     --out $G/roll_gate_base.jsonl --samples 4 --temperature 1.0 --batch 24 \
     > $L/gate.log 2>&1
  say "gate gen rc=$?"
  $P scripts/mg_strict_rescore.py --rollouts $G/roll_gate_base.jsonl \
     --suite gate --episodes-dir /home/ec2-user/mg3/gate \
     --out $G/strict_gate_base.json --graded-out $G/graded_gate_base.jsonl \
     >> $L/gate.log 2>&1
  say "gate rescore rc=$?"
fi
if [ ! -f $F/corpus_before_greedy.json ]; then
  $P -m src.system.lmframe --ckpt $CORPUS --tag corpus_before --mode greedy \
     --out $F/corpus_before_greedy.json --cap 25 > $L/frame_before.log 2>&1
  say "frame before rc=$?"
fi
if [ ! -f results/system/lmeval/corpus_nosft/summary.json ]; then
  $P -m src.system.lmeval --ckpt $CORPUS --tag corpus_nosft --n 1400 \
     --max-new 640 --modes greedy > $L/lmeval_nosft.log 2>&1
  say "lmeval nosft rc=$?"
fi
doc
if [ ! -f $M/norm-sft.pt ]; then
  $P -m src.system.lmtrain --ckpt $CORPUS --pack data/system/lm \
     --out $M/norm-sft.pt --log $M/train.jsonl \
     --steps 8000 --batch 32 --micro 4 --lr 2e-5 > $L/lmtrain.log 2>&1
  say "lmtrain rc=$?"
fi
if [ ! -f results/system/lmeval/lm350/summary.json ]; then
  $P -m src.system.lmeval --ckpt $M/norm-sft.pt --tag lm350 --n 1400 \
     --max-new 640 > $L/lmeval.log 2>&1
  say "lmeval rc=$?"
fi
if [ ! -f $F/corpus_after_greedy.json ]; then
  $P -m src.system.lmframe --ckpt $M/norm-sft.pt --tag corpus_after \
     --mode greedy --out $F/corpus_after_greedy.json --cap 25 \
     > $L/frame_after.log 2>&1
  say "frame after rc=$?"
fi
doc

# 6. the 167M rung
R=$(lrof xxl167); say "xxl167 lr $R"
if [ ! -f $T/ckpt_xxl167.pt ]; then
  $P -m src.system.strain --size xxl167 --micro 2 --steps 30000 --lr $R \
     --eval-every 3000 --eval-n 700 --out $T --tag xxl167 \
     >> $L/train_xxl167.log 2>&1
  say "train xxl167 rc=$?"
fi
score xxl167 $T/ckpt_xxl167.pt data/norm
bash src/system/tpose.sh xxl167 $T/ckpt_xxl167.pt
doc

# 7. the top rung
R=$(lrof xxxl355); say "xxxl355 lr $R"
if [ ! -f $T/ckpt_xxxl355.pt ]; then
  $P -m src.system.strain --size xxxl355 --micro 2 --steps 30000 --lr $R \
     --eval-every 3000 --eval-n 700 --out $T --tag xxxl355 \
     >> $L/train_xxxl355.log 2>&1
  say "train xxxl355 rc=$?"
fi
score xxxl355 $T/ckpt_xxxl355.pt data/norm
bash src/system/tpose.sh xxxl355 $T/ckpt_xxxl355.pt
doc
say "done"
