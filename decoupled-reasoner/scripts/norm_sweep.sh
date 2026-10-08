#!/bin/bash
cd /home/ec2-user/decoupled-reasoner
mkdir -p results/norm/train
for S in s m l xs; do
  echo "=== $S $(date -u +%T) ==="
  .venv/bin/python -m src.norm.ntrain --size $S --steps 30000 \
    --eval-every 3000 --eval-n 700 --out results/norm/train --tag $S \
    >> results/norm/train/stdout_$S.log 2>&1
  echo "=== $S done rc=$? $(date -u +%T) ==="
done
echo ALLDONE
