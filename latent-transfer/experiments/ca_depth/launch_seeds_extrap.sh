#!/bin/bash
# Seeds on the extrapolation cells: oo_tok, oo_pause_a, oo_lat_a trained on k<=4 and
# evaluated to k=32, rope, paper recipe 256x40k, seeds 1 and 2. 6 jobs, one box, N concurrent.
set -u
cd /home/ec2-user/ca
PY=/opt/pytorch/bin/python
OUT=/home/ec2-user/ca/results_v3
N=${N:-3}
mkdir -p "$OUT" logs_v3
{
  for seed in 1 2; do
    for arm in oo_tok oo_pause_a oo_lat_a; do
      echo "$PY ca_arms.py --arm $arm --ks 1,2,3,4 --k-eval 1,2,4,8,16,32 --steps 40000 --batch 256 --pos rope --seed $seed --tag ropex40k_mixedk --out $OUT > logs_v3/ropex40k_${arm}_s$seed.log 2>&1"
    done
  done
} > jobs_seeds_extrap.txt
echo "extrap seeds: $(wc -l < jobs_seeds_extrap.txt) jobs" >> logs_v3/launcher.log
nohup bash runq2.sh jobs_seeds_extrap.txt $N logs_v3/launcher.log > logs_v3/runq_seeds_extrap.log 2>&1 &
echo "launched, pid $!" >> logs_v3/launcher.log
tail -2 logs_v3/launcher.log
