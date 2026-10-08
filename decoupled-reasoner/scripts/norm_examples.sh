#!/bin/bash
cd /home/ec2-user/decoupled-reasoner
for N in 30000 120000 480000; do
  echo "=== e$N $(date -u +%T) ==="
  .venv/bin/python -m src.norm.ntrain --size s --steps 30000     --eval-every 10000 --eval-n 700 --train-examples $N     --out results/norm/train --tag e$N     >> results/norm/train/stdout_e$N.log 2>&1
  echo "=== e$N done rc=$? $(date -u +%T) ==="
done
echo EXDONE
