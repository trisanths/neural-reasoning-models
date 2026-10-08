#!/bin/bash
# Rebuild the seeds queue from jobs_seeds_A.txt: keep only lines whose result JSON does not
# exist and whose exact command is not currently running. Then relaunch at N=$1.
cd /home/ec2-user/ca
N=${1:-8}
pkill -f "runq2.sh jobs_seeds_A.txt" 2>/dev/null; sleep 1
: > jobs_seeds_A_rest.txt
while IFS= read -r job; do
  arm=$(echo "$job" | sed 's/.*--arm \([a-z_]*\).*/\1/')
  seed=$(echo "$job" | sed 's/.*--seed \([0-9]\).*/\1/')
  tag=$(echo "$job" | sed 's/.*--tag \([a-z0-9_]*\).*/\1/')
  json="results_v3/${tag}_${arm}_s${seed}.json"
  if [ -f "$json" ]; then continue; fi
  if pgrep -f -- "--arm $arm --ks [0-9,]* --k-eval [0-9,]* --steps 40000 --batch 256 --pos rope --seed $seed --tag $tag " >/dev/null || pgrep -f -- "--arm $arm --ks [0-9] --steps 40000 --batch 256 --pos rope --seed $seed --tag $tag " >/dev/null; then continue; fi
  echo "$job" >> jobs_seeds_A_rest.txt
done < jobs_seeds_A.txt
echo "remaining: $(wc -l < jobs_seeds_A_rest.txt); running: $(pgrep -af results_v3 | grep -v 'bash -c' | grep -c 'bin/python')"
sed 's/.*--arm/--arm/;s/ --steps.*--seed/ seed/;s/ --tag/ tag=/;s/ --out.*//' jobs_seeds_A_rest.txt
nohup bash runq2.sh jobs_seeds_A_rest.txt $N logs_v3/launcher.log > logs_v3/runq_seeds_A2.log 2>&1 &
echo "relaunched at N=$N"
