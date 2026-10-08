#!/bin/bash
# Specification form: the 32-bit rule table given in the prefix (--spec table) vs inferred
# from the ten prior states (--spec orbit, already run). os_tok and oo_tok, rope, paper
# recipe 256x40k, k in {1,2,4}, seeds 0..2. 18 jobs; BOX=0 even, BOX=1 odd; N concurrent.
set -u
cd /home/ec2-user/ca
PY=/opt/pytorch/bin/python
OUT=/home/ec2-user/ca/results_v3
BOX=${BOX:-0}; N=${N:-9}
mkdir -p "$OUT" logs_v3
{
  for seed in 0 1 2; do
    for arm in os_tok oo_tok; do
      for k in 1 2 4; do
        echo "$PY ca_arms.py --arm $arm --ks $k --steps 40000 --batch 256 --pos rope --spec table --seed $seed --tag ropetab40k_k$k --out $OUT > logs_v3/ropetab40k_k${k}_${arm}_s$seed.log 2>&1"
      done
    done
  done
} | awk -v b="$BOX" 'NR % 2 == b' > jobs_spec_v3.txt
echo "spec box $BOX: $(wc -l < jobs_spec_v3.txt) jobs" >> logs_v3/launcher.log
nohup bash runq2.sh jobs_spec_v3.txt $N logs_v3/launcher.log > logs_v3/runq_spec.log 2>&1 &
echo "launched, pid $!" >> logs_v3/launcher.log
tail -2 logs_v3/launcher.log
