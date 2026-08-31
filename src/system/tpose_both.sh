#!/bin/bash
# The transposed-operand test after a fine tune that shows both operand orders.
#
# data/norm/grid_train.npz lists its nine key pairs in row major order on all
# 4,096 of its pages, so the rung that was fine tuned on it never saw the
# layout the test asks it to read. data/norm/grid_both.npz carries 512 pages
# in that order and 512 in another, is disjoint from grid_train and from both
# versions of the item set, and is otherwise the same construction. Everything
# else about the protocol is unchanged: k = 1024, 1,500 steps, 24 rows, half
# of every batch from the original training file, the same rate.
#
# This is the data fix for that failure. If the test still reads 0, the
# failure survives its own fix.
cd ~/decoupled-reasoner
set -u
export PYTHONPATH=.
P=.venv/bin/python
X=results/system/tpose
L=logs/system
mkdir -p $X $L
say () { echo "$(date -u +%H:%M:%S) $*" >> $L/queue.log; }

run () {
  R=$1; C=$2
  FT=$X/ft_${R}_both_k1024.pt
  if [ ! -f "$FT" ]; then
    $P -m src.norm.cmpwork.ftune --ckpt "$C" --k 1024 --steps 1500 \
       --grids data/norm/grid_both.npz --out "$FT" \
       > $L/tposeboth_ft_$R.log 2>&1
    say "tpose-both $R ftune rc=$?"
  fi
  $P -m src.norm.cmpwork.xmode --ckpts "$FT" \
     --items results/norm/compare/x_items.jsonl.gz \
     --out $X/xmode_${R}_both.json > $L/tposeboth_xmode_$R.log 2>&1
  say "tpose-both $R xmode rc=$?"
}

run l45 results/norm/train/ckpt_l.pt
run xl93 results/system/train/ckpt_xl93.pt
say "tpose-both done"
