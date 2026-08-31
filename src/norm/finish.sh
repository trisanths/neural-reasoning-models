#!/bin/bash
# Everything that runs once the three drivers are done: the structural
# diagnostic on the family trained network, then the report and the document.
cd ~/decoupled-reasoner
set -u
P=.venv/bin/python
R=results/norm/oneshot
L=logs/oneshot

if [ -f $R/ft_family.pt ]; then
  $P -m src.norm.opdiag --ckpt $R/ft_family.pt --vocab ext --only compose \
     --out $R/diag_family_compose.json >> $L/diag.log 2>&1
  $P -m src.norm.opdiag --ckpt $R/ft_family.pt --vocab ext --only acq \
     --out $R/diag_family_acq.json >> $L/diag.log 2>&1
fi
$P -m src.norm.opdiag --ckpt results/norm/train/ckpt_l.pt --vocab base \
   --only compose --out $R/diag_base_compose.json >> $L/diag.log 2>&1
$P -m src.norm.opdiag --ckpt results/norm/train/ckpt_l.pt --vocab base \
   --only acq --out $R/diag_base_acq.json >> $L/diag.log 2>&1
$P -m src.norm.opreport
$P -m src.norm.opdoc
