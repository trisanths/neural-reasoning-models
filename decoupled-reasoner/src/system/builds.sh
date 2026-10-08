#!/bin/bash
# Two more frame splits, built the way data/norm was built.
#
# splitB withholds a different statement mode, table_row instead of
# relative_clause, and is otherwise identical: 490 training frames, the same
# group sizes. It says whether the positional collapse is about
# relative_clause or about an unseen mode.
#
# splitC withholds one whole value of the question-form axis, wh, in place of
# the every-eighth-frame band. Its held-out group spans both key positions, 70
# frames each, which the band's group did not. It says whether the collapse is
# about the statement-mode axis or about any unseen axis value.
#
# Same generator, same seed, same counts as data/norm. CPU only.
cd ~/decoupled-reasoner
set -u
export PYTHONPATH=.
P=.venv/bin/python
L=logs/system
mkdir -p $L
say () { echo "$(date -u +%H:%M:%S) $*" >> $L/queue.log; }

if [ ! -f data/normB/manifest.json ]; then
  NORM_HELD_MODE=table_row $P -m src.norm.ndata --out data/normB \
     --train 1200000 --eval 7000 --procs 4 --seed 20260830 \
     > $L/build_normB.log 2>&1
  say "build normB rc=$?"
fi
if [ ! -f data/normC/manifest.json ]; then
  NORM_HELD_QFORM=wh $P -m src.norm.ndata --out data/normC \
     --train 1200000 --eval 7000 --procs 4 --seed 20260830 \
     > $L/build_normC.log 2>&1
  say "build normC rc=$?"
fi
say "builds done"
