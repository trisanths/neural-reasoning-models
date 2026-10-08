#!/bin/bash
# The GPU side of the one shot lane, start to finish.
cd ~/decoupled-reasoner
set -u
P=.venv/bin/python
L=logs/oneshot
R=results/norm/oneshot
mkdir -p $L $R

echo "=== data ===" >> $L/drive.log
$P -m src.norm.opdata --n 256 --each 2 --family 1024 >> $L/data.log 2>&1
$P -m src.norm.opladder >> $L/data.log 2>&1
$P -m src.norm.oprun >> $L/data.log 2>&1
$P -m src.norm.oprun --items $R/ladder_items.jsonl.gz \
   --out $R/ladder_sys.jsonl.gz >> $L/data.log 2>&1
echo "data done $(date)" >> $L/drive.log

echo "=== base, no gradient ===" >> $L/drive.log
$P -m src.norm.opneural --ckpt results/norm/train/ckpt_l.pt --vocab base \
   --items $R/items.jsonl.gz --out $R/n_base_l.jsonl.gz \
   >> $L/base.log 2>&1
echo "base main done $(date)" >> $L/drive.log
$P -m src.norm.opneural --ckpt results/norm/train/ckpt_l.pt --vocab base \
   --items $R/ladder_items.jsonl.gz --out $R/n_base_l_ladder.jsonl.gz \
   >> $L/base.log 2>&1
echo "base ladder done $(date)" >> $L/drive.log

echo "=== ladder ===" >> $L/drive.log
$P -m src.norm.opft --ckpt results/norm/train/ckpt_l.pt \
   --pool data/norm/oneshot/family.npz --k 0 --steps 1500 \
   --out $R/ft_k0.pt >> $L/ft.log 2>&1
$P -m src.norm.opneural --ckpt $R/ft_k0.pt --vocab ext --max-len 320 \
   --items $R/ladder_items.jsonl.gz --out $R/n_k0_ladder.jsonl.gz \
   >> $L/ft.log 2>&1
echo "k0 done $(date)" >> $L/drive.log

for TAG in acq_a2c1_2 acq_a3c1_26 acq_a3c2_144 acq_a2c2_157; do
  for K in 1 2 4 16 64; do
    $P -m src.norm.opft --ckpt results/norm/train/ckpt_l.pt \
       --pool data/norm/oneshot/$TAG.npz --k $K --steps 1500 \
       --out $R/ft_${TAG}_k$K.pt >> $L/ft.log 2>&1
    $P -m src.norm.opneural --ckpt $R/ft_${TAG}_k$K.pt --vocab ext \
       --max-len 320 --items $R/ladder_items.jsonl.gz \
       --out $R/n_${TAG}_k${K}_ladder.jsonl.gz >> $L/ft.log 2>&1
    rm -f $R/ft_${TAG}_k$K.pt
    echo "$TAG k$K done $(date)" >> $L/drive.log
  done
done

echo "=== family trained ===" >> $L/drive.log
$P -m src.norm.opft --ckpt results/norm/train/ckpt_l.pt \
   --pool data/norm/oneshot/family.npz --k 1024 --steps 1500 \
   --out $R/ft_family.pt >> $L/fam.log 2>&1
$P -m src.norm.opneural --ckpt $R/ft_family.pt --vocab ext --max-len 800 \
   --items $R/items.jsonl.gz --out $R/n_family.jsonl.gz >> $L/fam.log 2>&1
$P -m src.norm.opneural --ckpt $R/ft_family.pt --vocab ext --max-len 320 \
   --items $R/ladder_items.jsonl.gz --out $R/n_family_ladder.jsonl.gz \
   >> $L/fam.log 2>&1
echo "ALL DONE $(date)" >> $L/drive.log
