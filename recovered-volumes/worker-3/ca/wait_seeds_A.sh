#!/bin/bash
# wait until box has <= 2 training jobs, then run the box A seeds list at 4 concurrent
cd /home/ec2-user/ca
while [ "$(pgrep -af results_v3 | grep -v 'bash -c' | grep -c 'bin/python')" -gt 2 ]; do sleep 120; done
echo "seeds A firing at $(date)" >> logs_v3/launcher.log
bash runq2.sh jobs_seeds_A.txt 4 logs_v3/launcher.log
