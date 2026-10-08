#!/bin/bash
# The "reading number": single-step accuracy a on held-out rules as a function of
# specification form. orbit = infer the rule from 10 prior states (the paper's setup),
# table = the 32-bit rule is given in context. Then oo_tok at k=1,2,4 with the table
# to test whether the k-curve follows a^k once a is raised. 3 seeds each.
set -u
cd /home/ec2-user/ca
PY=/opt/pytorch/bin/python
OUT=/home/ec2-user/ca/results_spec
STEPS=${STEPS:-20000}
mkdir -p "$OUT" logs_spec
{
  # (os orbit/table k=1 x 3 seeds launched separately, earlier)
  for k in 1 2 4; do
    echo "$PY ca_arms.py --arm oo_tok --ks $k --steps $STEPS --seed 0 --spec table --tag spec_table_k$k --out $OUT > logs_spec/oo_tok_table_k$k.log 2>&1"
  done
  # the two arms added after the main sweep launched: Bansal recipe and pause slots
  for arm in oo_bansal oo_pause; do
    for k in 1 2 4; do
      echo "$PY ca_arms.py --arm $arm --ks $k --steps $STEPS --tag perk_k$k --out /home/ec2-user/ca/results > logs_spec/perk_k${k}_$arm.log 2>&1"
    done
    echo "$PY ca_arms.py --arm $arm --ks 1,2,3,4 --k-eval 1,2,4,8,16,32 --steps $STEPS --tag extrap_mixedk --out /home/ec2-user/ca/results > logs_spec/extrap_$arm.log 2>&1"
  done
} > jobs_spec.txt
echo "spec: $(wc -l < jobs_spec.txt) jobs" > logs_spec/launcher.log
nohup bash -c 'xargs -P 6 -I{} bash -c "{}" < jobs_spec.txt; echo ALL_DONE >> logs_spec/launcher.log' > logs_spec/xargs.log 2>&1 &
echo "launched, pid $!" >> logs_spec/launcher.log
cat logs_spec/launcher.log
