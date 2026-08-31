#!/bin/bash
cd ~/decoupled-reasoner
.venv/bin/python -m src.norm.cmpwork.xmode \
  --ckpts results/norm/train/ckpt_l.pt,results/norm/train/ckpt_xs.pt,results/norm/compare/ft_xs_k64.pt,results/norm/compare/ft_xs_k1024.pt \
  --out results/norm/compare/xmode.json > logs/cmp/xmode.log 2>&1
