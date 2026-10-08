#!/bin/bash
# The second ladder again, from the family network that actually converged.
#
# `drive2.sh` started from the 1500 step family checkpoint, whose training loss
# was still falling. This runs the same rungs from the 6000 step one, so the
# starting point is a network that has finished learning the family.
cd ~/decoupled-reasoner
set -u
P=.venv/bin/python
L=logs/oneshot
R=results/norm/oneshot
mkdir -p $L $R

for i in $(seq 1 500); do
  grep -q "FOURTH DONE" $L/drive4.log 2>/dev/null && break
  sleep 20
done
grep -q "FOURTH DONE" $L/drive4.log 2>/dev/null || { echo "fourth driver never finished" >> $L/drive5.log; exit 1; }
echo "=== third ladder $(date) ===" >> $L/drive5.log

for TAG in acq_a2c1_2 acq_a3c1_26 acq_a3c2_144 acq_a2c2_157; do
  for K in 1 2 4; do
    $P -m src.norm.opft --ckpt $R/ft_family2.pt \
       --pool data/norm/oneshot/$TAG.npz --k $K --steps 1500 \
       --out $R/ft3_${TAG}_k$K.pt >> $L/ft5.log 2>&1
    $P -m src.norm.opneural --ckpt $R/ft3_${TAG}_k$K.pt --vocab ext \
       --max-len 320 --items $R/ladder_items.jsonl.gz \
       --out $R/n3_${TAG}_k${K}_ladder.jsonl.gz >> $L/ft5.log 2>&1
    rm -f $R/ft3_${TAG}_k$K.pt
    echo "$TAG k$K done $(date)" >> $L/drive5.log
  done
done
echo "FIFTH DONE $(date)" >> $L/drive5.log
