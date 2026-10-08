#!/bin/bash
cd ~/decoupled-reasoner
for i in $(seq 1 400); do
  if [ -f logs/cmp/hs_done.txt ] && [ -f logs/cmp/sampled_done.txt ]; then break; fi
  sleep 10
done
bash src/norm/cmpwork/build_all.sh > logs/cmp/build_all.log 2>&1
echo DONE >> logs/cmp/build_all.log
