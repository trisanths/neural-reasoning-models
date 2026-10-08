#!/bin/bash
# Seeds for the decisive cells: oo_tok (O-O), os_tok (O-S), oo_pause_a, oo_lat_a,
# rope, paper recipe 256x40k, k in {1,2,4}, seeds 1 and 2 (seed 0 is in v3).
# 24 jobs; BOX=0 even, BOX=1 odd; N concurrent.
set -u
cd /home/ec2-user/ca
PY=/opt/pytorch/bin/python
OUT=/home/ec2-user/ca/results_v3
BOX=${BOX:-0}; N=${N:-6}
mkdir -p "$OUT" logs_v3
{
  for seed in 1 2; do
    for arm in oo_tok os_tok oo_pause_a oo_lat_a; do
      for k in 1 2 4; do
        echo "$PY ca_arms.py --arm $arm --ks $k --steps 40000 --batch 256 --pos rope --seed $seed --tag rope40k_k$k --out $OUT > logs_v3/rope40k_k${k}_${arm}_s$seed.log 2>&1"
      done
    done
  done
} | awk -v b="$BOX" 'NR % 2 == b' > jobs_seeds.txt
echo "seeds box $BOX: $(wc -l < jobs_seeds.txt) jobs" >> logs_v3/launcher.log
nohup bash runq2.sh jobs_seeds.txt $N logs_v3/launcher.log > logs_v3/runq_seeds.log 2>&1 &
echo "launched, pid $!" >> logs_v3/launcher.log
tail -2 logs_v3/launcher.log
