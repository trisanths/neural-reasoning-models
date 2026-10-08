#!/bin/bash
# v3: rotary positions on every arm, and only the arms v2 showed to be informative.
#   oo_tok      paper recipe 256x40k (replication) and 512x20k (same-recipe reference)
#   oo_pause_a  slots carried, main-model readout attending over context, bits never carried
#   oo_lat_a    hidden state fed back, same readout
#   os          no memory, no feedback, single-vector readout (reference)
#   oo_rec      fixed-vector loop, single-vector readout (reference)
# k in {1,2,4} plus mixed-k extrapolation to 32. 24 jobs; BOX=0 even, BOX=1 odd; 6 concurrent.
set -u
cd /home/ec2-user/ca
PY=/opt/pytorch/bin/python
OUT=/home/ec2-user/ca/results_v3
BOX=${BOX:-0}
mkdir -p "$OUT" logs_v3
{
  for k in 1 2 4; do
    echo "$PY ca_arms.py --arm oo_tok --ks $k --steps 40000 --batch 256 --pos rope --tag rope40k_k$k --out $OUT > logs_v3/rope40k_k${k}_oo_tok.log 2>&1"
  done
  echo "$PY ca_arms.py --arm oo_tok --ks 1,2,3,4 --k-eval 1,2,4,8,16,32 --steps 40000 --batch 256 --pos rope --tag ropex40k_mixedk --out $OUT > logs_v3/ropex40k_oo_tok.log 2>&1"
  for arm in oo_tok oo_pause_a oo_lat_a os oo_rec; do
    for k in 1 2 4; do
      echo "$PY ca_arms.py --arm $arm --ks $k --steps 20000 --batch 512 --pos rope --tag perk_k$k --out $OUT > logs_v3/perk_k${k}_$arm.log 2>&1"
    done
    echo "$PY ca_arms.py --arm $arm --ks 1,2,3,4 --k-eval 1,2,4,8,16,32 --steps 20000 --batch 512 --pos rope --tag extrap_mixedk --out $OUT > logs_v3/extrap_$arm.log 2>&1"
  done
} | awk -v b="$BOX" 'NR % 2 == b' > jobs_v3.txt
echo "box $BOX: $(wc -l < jobs_v3.txt) jobs" > logs_v3/launcher.log
nohup bash runq2.sh jobs_v3.txt 6 logs_v3/launcher.log > logs_v3/runq.log 2>&1 &
echo "launched, pid $!" >> logs_v3/launcher.log
cat logs_v3/launcher.log
