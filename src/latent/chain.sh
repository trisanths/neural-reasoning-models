#!/bin/bash
# Watch the training lanes and start each scoring worker as its checkpoint
# lands. One SSM command on a box whose command queue backs up for tens of
# minutes has to be able to carry the whole run, so nothing here waits for a
# second one.
set -u
cd /home/ec2-user/opg
export PYTHONPATH=$PWD
for i in $(seq 1 300); do
  [ -f runs/latent/dsweep.pt ] && bash src/latent/stage2.sh a
  [ -f runs/latent/esweep.pt ] && bash src/latent/stage2.sh b
  if [ -f results/latent/check_d.done ] && [ -f results/latent/e_ind_s0.done ]; then
    echo "[chain] all scoring finished $(date -u +%FT%TZ)"; break
  fi
  sleep 120
done
