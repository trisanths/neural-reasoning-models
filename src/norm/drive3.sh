#!/bin/bash
# The far end of the ladder. The pools here are drawn with the same seed as the
# 256 row ones, so their first 256 rows are the same rows and the ladder stays
# nested: k = 256 sees everything k = 64 saw and more.
cd ~/decoupled-reasoner
set -u
P=.venv/bin/python
L=logs/oneshot
R=results/norm/oneshot
mkdir -p $L $R

for i in $(seq 1 400); do
  grep -q "SECOND DONE" $L/drive2.log 2>/dev/null && break
  sleep 15
done
grep -q "SECOND DONE" $L/drive2.log 2>/dev/null || { echo "second driver never finished" >> $L/drive3.log; exit 1; }
echo "=== far end $(date) ===" >> $L/drive3.log

$P -m src.norm.opdata --out data/norm/oneshot/big --n 1024 --each 2 \
   --family 0 >> $L/data3.log 2>&1

for TAG in acq_a2c1_2 acq_a3c1_26 acq_a3c2_144 acq_a2c2_157; do
  for K in 256; do
    $P -m src.norm.opft --ckpt results/norm/train/ckpt_l.pt \
       --pool data/norm/oneshot/big/$TAG.npz --k $K --steps 1500 \
       --out $R/ft_${TAG}_k$K.pt >> $L/ft3.log 2>&1
    $P -m src.norm.opneural --ckpt $R/ft_${TAG}_k$K.pt --vocab ext \
       --max-len 320 --items $R/ladder_items.jsonl.gz \
       --out $R/n_${TAG}_k${K}_ladder.jsonl.gz >> $L/ft3.log 2>&1
    rm -f $R/ft_${TAG}_k$K.pt
    echo "$TAG k$K done $(date)" >> $L/drive3.log
  done
done

for TAG in acq_a2c1_2 acq_a3c1_26; do
  $P -m src.norm.opft --ckpt results/norm/train/ckpt_l.pt \
     --pool data/norm/oneshot/big/$TAG.npz --k 1024 --steps 1500 \
     --out $R/ft_${TAG}_k1024.pt >> $L/ft3.log 2>&1
  $P -m src.norm.opneural --ckpt $R/ft_${TAG}_k1024.pt --vocab ext \
     --max-len 320 --items $R/ladder_items.jsonl.gz \
     --out $R/n_${TAG}_k1024_ladder.jsonl.gz >> $L/ft3.log 2>&1
  rm -f $R/ft_${TAG}_k1024.pt
  echo "$TAG k1024 done $(date)" >> $L/drive3.log
done
echo "THIRD DONE $(date)" >> $L/drive3.log
