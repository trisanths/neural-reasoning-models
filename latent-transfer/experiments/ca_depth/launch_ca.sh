#!/bin/bash
# Launch the 1dCA arm sweep split across two L40S boxes.
#   BOX=0 takes even-indexed jobs, BOX=1 takes odd-indexed jobs. 6 concurrent per box.
# 18 per-k jobs (6 arms x k in {1,2,4}) + 6 mixed-k extrapolation jobs = 24 total, 12 per box.
set -u
cd /home/ec2-user/ca
PY=/opt/pytorch/bin/python
OUT=/home/ec2-user/ca/results
BOX=${BOX:-0}
STEPS=${STEPS:-20000}
mkdir -p "$OUT" logs
{
  for arm in os oo_tok oo_split oo_lat oo_rec oo_mat; do
    for k in 1 2 4; do
      echo "$PY ca_arms.py --arm $arm --ks $k --steps $STEPS --tag perk_k$k --out $OUT > logs/perk_k${k}_$arm.log 2>&1"
    done
  done
  for arm in os oo_tok oo_split oo_lat oo_rec oo_mat; do
    echo "$PY ca_arms.py --arm $arm --ks 1,2,3,4 --k-eval 1,2,4,8,16,32 --steps $STEPS --tag extrap_mixedk --out $OUT > logs/extrap_$arm.log 2>&1"
  done
} | awk -v b="$BOX" 'NR % 2 == b' > jobs.txt
echo "box $BOX: $(wc -l < jobs.txt) jobs" > logs/launcher.log
nohup bash -c 'xargs -P 6 -I{} bash -c "{}" < jobs.txt; echo ALL_DONE >> logs/launcher.log' > logs/xargs.log 2>&1 &
echo "launched, pid $!" >> logs/launcher.log
cat logs/launcher.log
