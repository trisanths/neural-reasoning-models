#!/bin/bash
# Evaluate each checkpoint as its training run lands, then stop.
cd /home/ec2-user/decoupled-reasoner
V=.venv/bin/python
SPL=train_frames_eval,qframe,lexicon,mode
until grep -q EXDONE /tmp/normex.log 2>/dev/null; do sleep 30; done
echo "=== examples ladder done $(date -u +%T) ==="
for T in e30000 e120000 e480000; do
  $V -m src.norm.nreport --ckpt results/norm/train/ckpt_$T.pt --n 2800 \
     --splits $SPL --out results/norm/eval > /tmp/nrep_$T.log 2>&1
  echo "=== $T rc=$? $(date -u +%T) ==="
done
until grep -q ALLDONE /tmp/normsweep.log 2>/dev/null; do sleep 30; done
echo "=== size sweep done $(date -u +%T) ==="
for T in l xs; do
  $V -m src.norm.nreport --ckpt results/norm/train/ckpt_$T.pt --n 2800 \
     --out results/norm/eval > /tmp/nrep_$T.log 2>&1
  echo "=== report $T rc=$? $(date -u +%T) ==="
  $V -m src.norm.ndiff --ckpt results/norm/train/ckpt_$T.pt --n 2800 \
     > /tmp/ndiff_$T.log 2>&1
  echo "=== ndiff $T rc=$? $(date -u +%T) ==="
  $V -m src.norm.nattack --ckpt results/norm/train/ckpt_$T.pt --split qframe \
     --n 1400 > /tmp/natk_$T.log 2>&1
  echo "=== attack $T rc=$? $(date -u +%T) ==="
done
echo AFTERDONE
