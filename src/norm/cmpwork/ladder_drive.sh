#!/bin/bash
cd ~/decoupled-reasoner
set -u
CK="results/norm/train/ckpt_xs.pt"
LIST="results/norm/train/ckpt_xs.pt"
for k in 0 1 4 16 64 256 1024; do
  .venv/bin/python -m src.norm.cmpwork.ftune --ckpt $CK --k $k --steps 1500 \
    --out results/norm/compare/ft_xs_k$k.pt >> logs/cmp/ftune_xs.log 2>&1
  LIST="$LIST,results/norm/compare/ft_xs_k$k.pt"
done
echo "$LIST" > logs/cmp/ladder_xs_list.txt
.venv/bin/python -m src.norm.cmpwork.ladder --ckpts "$LIST" \
  --out results/norm/compare/ladder_xs.json > logs/cmp/ladder_xs.log 2>&1
for k in 0 1024; do
  .venv/bin/python -m src.norm.cmpwork.ftune --ckpt results/norm/train/ckpt_l.pt \
    --k $k --steps 1500 --out results/norm/compare/ft_l_k$k.pt >> logs/cmp/ftune_l.log 2>&1
done
.venv/bin/python -m src.norm.cmpwork.ladder \
  --ckpts "results/norm/train/ckpt_l.pt,results/norm/compare/ft_l_k0.pt,results/norm/compare/ft_l_k1024.pt" \
  --out results/norm/compare/ladder_l.json > logs/cmp/ladder_l.log 2>&1
echo DONE >> logs/cmp/ladder_xs.log
