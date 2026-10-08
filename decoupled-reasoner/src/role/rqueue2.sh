#!/bin/bash
# What the wrong emissions are made of, once every arm has a checkpoint.
# Waits for the arm queue to leave the card, then one job at a time.
cd ~/decoupled-reasoner
set -u
export PYTHONPATH=.
P=.venv/bin/python
L=logs/role
say () { echo "$(date -u +'%F %H:%M:%S') $*" >> $L/queue.log; }

say "swap queue waiting"
while pgrep -f "src/role/rqueue.sh" > /dev/null; do sleep 60; done
while [ "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)" -gt 0 ]; do sleep 60; done
say "swap queue starts"

swap () {
  tag=$1; ck=$2
  [ -f "$ck" ] || { say "swap $tag: no checkpoint"; return; }
  [ -f results/role/swap_${tag}_mode.json ] && { say "swap $tag already"; return; }
  $P -m src.role.rswap --ckpt "$ck" --tag "$tag" --split mode \
     >> $L/swap_$tag.log 2>&1
  say "swap $tag rc=$?"
}

swap l45 results/norm/train/ckpt_l.pt
for t in roleA roleB roleC roleD; do swap $t results/role/train/ckpt_$t.pt; done
say "swap queue done"
