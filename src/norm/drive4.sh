#!/bin/bash
# The family condition, trained until the loss stops falling.
#
# At 1500 steps the family run's training loss was still coming down, 0.36 to
# 0.12 over the run, so what it scored was a network that had not finished
# learning its own training set. That is a statement about the budget and not
# about the network, so the same condition is run again for four times as long
# and both are reported.
cd ~/decoupled-reasoner
set -u
P=.venv/bin/python
R=results/norm/oneshot
L=logs/oneshot
mkdir -p $L $R

for i in $(seq 1 500); do
  grep -q "THIRD DONE" $L/drive3.log 2>/dev/null && break
  sleep 20
done
grep -q "THIRD DONE" $L/drive3.log 2>/dev/null || { echo "third driver never finished" >> $L/drive4.log; exit 1; }
echo "=== long family $(date) ===" >> $L/drive4.log

$P -m src.norm.opft --ckpt results/norm/train/ckpt_l.pt \
   --pool data/norm/oneshot/family.npz --k 1024 --steps 6000 --rows 24 \
   --out $R/ft_family2.pt >> $L/fam2.log 2>&1
echo "trained $(date)" >> $L/drive4.log
$P -m src.norm.opneural --ckpt $R/ft_family2.pt --vocab ext --max-len 800 \
   --items $R/items.jsonl.gz --out $R/n_family2.jsonl.gz >> $L/fam2.log 2>&1
$P -m src.norm.opneural --ckpt $R/ft_family2.pt --vocab ext --max-len 320 \
   --items $R/ladder_items.jsonl.gz --out $R/n_family2_ladder.jsonl.gz \
   >> $L/fam2.log 2>&1
echo "FOURTH DONE $(date)" >> $L/drive4.log
