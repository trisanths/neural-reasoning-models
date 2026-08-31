#!/bin/bash
# The parameter ladder, train and score, one rung at a time.
# The 45M rung is not retrained: it is src/norm/'s own ckpt_l.pt, scored here
# by the same script the new rungs are scored by.
cd ~/decoupled-reasoner
set -u
P=.venv/bin/python
L=logs/system
T=results/system/train
E=results/system/eval
mkdir -p $L $T $E

say () { echo "$(date -u +%H:%M:%S) $*" >> $L/ladder.log; }

say "start"

# The published 45M rung, rescored on this lane's script.
$P -m src.system.sreport --ckpt results/norm/train/ckpt_l.pt --tag l45 \
   --n 2800 --batch 64 >> $L/eval_l45.log 2>&1
say "eval l45 rc=$?"

for R in "xl93 1" "xxl167 2" "xxxl355 2"; do
  set -- $R
  S=$1; M=$2
  $P -m src.system.strain --size $S --micro $M --steps 30000 \
     --eval-every 3000 --eval-n 700 --out $T --tag $S >> $L/train_$S.log 2>&1
  say "train $S rc=$?"
  $P -m src.system.sreport --ckpt $T/ckpt_$S.pt --tag $S \
     --n 2800 --batch 64 >> $L/eval_$S.log 2>&1
  say "eval $S rc=$?"
done
say "done"
