#!/bin/bash
# Evaluate the 45.5M run the moment its checkpoint lands.
cd /home/ec2-user/decoupled-reasoner
V=.venv/bin/python
until [ -f results/norm/train/ckpt_l.pt ]; do sleep 30; done
sleep 20
echo "=== ckpt_l seen $(date -u +%T) ==="
$V -m src.norm.nreport --ckpt results/norm/train/ckpt_l.pt --n 2800 \
   --out results/norm/eval > /tmp/nrep_l.log 2>&1
echo "=== report l rc=$? $(date -u +%T) ==="
$V -m src.norm.ndiff --ckpt results/norm/train/ckpt_l.pt --n 2800 \
   > /tmp/ndiff_l.log 2>&1
echo "=== ndiff l rc=$? $(date -u +%T) ==="
$V -m src.norm.nattack --ckpt results/norm/train/ckpt_l.pt --split qframe \
   --n 1400 > /tmp/natk_l.log 2>&1
echo "=== attack l rc=$? $(date -u +%T) ==="
$V -m src.norm.ndiff --ckpt results/norm/train/ckpt_xs.pt --n 2800 \
   > /tmp/ndiff_xs.log 2>&1
echo "=== ndiff xs rc=$? $(date -u +%T) ==="
$V -m src.norm.nattack --ckpt results/norm/train/ckpt_xs.pt --split qframe \
   --n 1400 > /tmp/natk_xs.log 2>&1
echo "=== attack xs rc=$? $(date -u +%T) ==="
echo LDONE
