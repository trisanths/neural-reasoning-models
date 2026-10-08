#!/bin/bash
# v2 sweep: every arm reads out through the same autoregressive bit decoder.
#   oo_tok      replication arm, paper recipe: batch 256 x 40k steps
#   seven arms  oo_tok os oo_lat oo_rec oo_mat oo_pause oo_bansal: batch 512 x 20k (same example budget)
#   os-spec     rule stated vs inferred at k=1, 3 seeds, batch 512 x 20k
# 38 jobs; the 256x40k oo_tok jobs carry a 40k tag so they never collide with the 512x20k ones; BOX=0 takes even-indexed, BOX=1 odd-indexed; 6 concurrent per box.
set -u
cd /home/ec2-user/ca
PY=/opt/pytorch/bin/python
OUT=/home/ec2-user/ca/results_v2
BOX=${BOX:-0}
mkdir -p "$OUT" logs_v2
{
  for k in 1 2 4; do
    echo "$PY ca_arms.py --arm oo_tok --ks $k --steps 40000 --batch 256 --tag perk40k_k$k --out $OUT > logs_v2/perk40k_k${k}_oo_tok.log 2>&1"
  done
  echo "$PY ca_arms.py --arm oo_tok --ks 1,2,3,4 --k-eval 1,2,4,8,16,32 --steps 40000 --batch 256 --tag extrap40k_mixedk --out $OUT > logs_v2/extrap40k_oo_tok.log 2>&1"
  for arm in oo_tok os oo_lat oo_rec oo_mat oo_pause oo_bansal; do
    for k in 1 2 4; do
      echo "$PY ca_arms.py --arm $arm --ks $k --steps 20000 --batch 512 --tag perk_k$k --out $OUT > logs_v2/perk_k${k}_$arm.log 2>&1"
    done
    echo "$PY ca_arms.py --arm $arm --ks 1,2,3,4 --k-eval 1,2,4,8,16,32 --steps 20000 --batch 512 --tag extrap_mixedk --out $OUT > logs_v2/extrap_$arm.log 2>&1"
  done
  for seed in 0 1 2; do
    for spec in orbit table; do
      echo "$PY ca_arms.py --arm os --ks 1 --steps 20000 --batch 512 --seed $seed --spec $spec --tag spec_${spec}_k1 --out $OUT > logs_v2/spec_${spec}_s$seed.log 2>&1"
    done
  done
} | awk -v b="$BOX" 'NR % 2 == b' > jobs_v2.txt
echo "box $BOX: $(wc -l < jobs_v2.txt) jobs" > logs_v2/launcher.log
nohup bash -c 'xargs -P 6 -I{} bash -c "{}" < jobs_v2.txt; echo ALL_DONE >> logs_v2/launcher.log' > logs_v2/xargs.log 2>&1 &
echo "launched, pid $!" >> logs_v2/launcher.log
cat logs_v2/launcher.log
