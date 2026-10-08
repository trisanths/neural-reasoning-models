#!/bin/bash
# The second ladder: acquiring a new operation from a network that already
# knows the family and the notation. It starts from the family trained
# checkpoint instead of the shipped one, so the only thing k buys here is this
# operation rather than the family it belongs to.
cd ~/decoupled-reasoner
set -u
P=.venv/bin/python
L=logs/oneshot
R=results/norm/oneshot
mkdir -p $L $R

for i in $(seq 1 400); do
  grep -q "ALL DONE" $L/drive.log && break
  sleep 15
done
grep -q "ALL DONE" $L/drive.log || { echo "first driver never finished" >> $L/drive2.log; exit 1; }
echo "=== second ladder $(date) ===" >> $L/drive2.log

for TAG in acq_a2c1_2 acq_a3c1_26 acq_a3c2_144 acq_a2c2_157; do
  for K in 1 2 4; do
    $P -m src.norm.opft --ckpt $R/ft_family.pt \
       --pool data/norm/oneshot/$TAG.npz --k $K --steps 1500 \
       --out $R/ft2_${TAG}_k$K.pt >> $L/ft2.log 2>&1
    $P -m src.norm.opneural --ckpt $R/ft2_${TAG}_k$K.pt --vocab ext \
       --max-len 320 --items $R/ladder_items.jsonl.gz \
       --out $R/n2_${TAG}_k${K}_ladder.jsonl.gz >> $L/ft2.log 2>&1
    rm -f $R/ft2_${TAG}_k$K.pt
    echo "$TAG k$K done $(date)" >> $L/drive2.log
  done
done
echo "SECOND DONE $(date)" >> $L/drive2.log
