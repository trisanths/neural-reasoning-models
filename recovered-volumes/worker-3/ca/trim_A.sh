#!/bin/bash
cd /home/ec2-user/ca
pkill -f "runq2.sh jobs_seeds_A_rest.txt" 2>/dev/null; sleep 1
# kill the 4 newest training processes (by start time)
for p in $(ps -eo pid,etimes,cmd --sort=etimes | grep "bin/python ca_arms.py" | grep -v grep | head -4 | awk '{print $1}'); do kill $p; done
sleep 4
echo "running after trim: $(pgrep -af results_v3 | grep -v 'bash -c' | grep -c 'bin/python')"
# rebuild the remaining list (no json, not running)
: > jobs_seeds_A_rest2.txt
while IFS= read -r job; do
  arm=$(echo "$job" | sed 's/.*--arm \([a-z_]*\).*/\1/'); seed=$(echo "$job" | sed 's/.*--seed \([0-9]\).*/\1/'); tag=$(echo "$job" | sed 's/.*--tag \([a-z0-9_]*\).*/\1/')
  [ -f "results_v3/${tag}_${arm}_s${seed}.json" ] && continue
  pgrep -f -- "--arm $arm --ks [0-9,]* .*--seed $seed --tag $tag " >/dev/null && continue
  echo "$job" >> jobs_seeds_A_rest2.txt
done < jobs_seeds_A.txt
echo "remaining to queue: $(wc -l < jobs_seeds_A_rest2.txt)"
# waiter: hold until <=4 running, then N=4 (max 8 total)
nohup bash -c 'while [ "$(pgrep -af results_v3 | grep -v "bash -c" | grep -c "bin/python")" -gt 4 ]; do sleep 120; done; bash runq2.sh jobs_seeds_A_rest2.txt 4 logs_v3/launcher.log' > logs_v3/runq_seeds_A3.log 2>&1 &
echo "waiter armed"
