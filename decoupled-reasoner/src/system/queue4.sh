#!/bin/bash
# Everything still owed, in the order the evidence now justifies.
#
# What changed. 30,000 steps at a 32,768 source-token budget is the same token
# budget for every rung, which is 21.36 source tokens per parameter at 45M and
# 10.38 at 93M. A rung that fits its own training file worse than a smaller
# rung at half the tokens per parameter is undertrained, not resistant to
# parameters, so the step count is now set per rung by tokens per parameter
# rather than copied. src/system/tokenbudget.py computes it: 61,724 steps at
# 93M, 110,271 at 167M and 234,238 at 355M to match what 45M had.
#
# 234,238 steps at 355M is about 64 hours on this card and is not run. Saying
# a 355M rung is flat when it saw an eighth of the tokens per parameter the
# 45M rung saw would be worse than not running it.
#
# Order follows what each run can settle: the two new frame splits first, then
# the budget-matched 93M rung, then the 350M arm, then the 167M rung last and
# only because it is the one large rung that can reach a defensible budget.
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

score () {
  if [ -f $E/$1/summary.json ]; then say "eval $1 already present"; return; fi
  $P -m src.system.sreport --ckpt "$2" --tag "$1" --data "$3" \
     --n $NEVAL --batch 64 >> $L/eval_$1.log 2>&1
  say "eval $1 rc=$?"
}
# tag size datadir lr steps micro
rung () {
  if [ ! -f $T/ckpt_$1.pt ]; then
    $P -m src.system.strain --size $2 --micro $6 --steps $5 --lr $4 \
       --data "$3" --eval-every 3000 --eval-n 700 --out $T --tag $1 \
       >> $L/train_$1.log 2>&1
    say "train $1 rc=$?"
  else
    say "train $1 checkpoint already present"
  fi
  score "$1" "$T/ckpt_$1.pt" "$3"
}

say "queue4 starts"

# 1. the xl93 rescore queue3 had already launched
while kill -0 205966 2>/dev/null; do sleep 20; done
say "eval xl93 ended"
doc

# 2. one whole value of the question-form axis withheld. Carries the
#    pre-registered prediction and is the reason this lane exists.
while [ ! -f data/normC/manifest.json ]; do sleep 30; done
rung c45 l45 data/normC 0 30000 1
doc

# 3. a different statement mode withheld, table_row for relative_clause
while [ ! -f data/normB/manifest.json ]; do sleep 30; done
rung b45 l45 data/normB 0 30000 1
doc

# 4. the 93M rung at the 45M rung's tokens per parameter rather than at its
#    step count. Everything else is identical to xl93lr40, including the rate.
rung xl93match xl93 data/norm 4.0e-4 61724 1
doc

# 5. the 350M arm
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

# 6. the transposed test at the two rungs that have it outstanding
bash src/system/tpose_both.sh
doc

# 7. the 167M rung, at its own matched budget, last. About fourteen hours.
#    355M is not here: 234,238 steps is about sixty-four hours on this card.
rung xxl167 xxl167 data/norm 4.0e-4 110271 2
bash src/system/tpose.sh xxl167 $T/ckpt_xxl167.pt
doc
say "done"
