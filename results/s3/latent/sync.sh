#!/bin/bash
# Push status and every finished result file to S3 on a loop.
#
# This box's command queue backs up for tens of minutes at a time, so the run
# reports on itself through a channel that does not need the queue: one
# detached loop writing to S3, read from anywhere.
set -u
cd /home/ec2-user/opg
B=s3://decoupled-reasoner-009398924577/latent/live
for i in $(seq 1 800); do
  {
    bash src/latent/status.sh
    echo "-- training logs"
    tail -n 1 logs/latent_dsweep.log 2>/dev/null
    tail -n 1 logs/latent_esweep.log 2>/dev/null
    for w in a b c d; do echo "-- w_$w"; tail -n 2 logs/latent_w_$w.log 2>/dev/null; done
    echo "-- chain"; tail -n 3 logs/latent_chain.log 2>/dev/null
  } > /tmp/latent_status.txt 2>&1
  aws s3 cp /tmp/latent_status.txt $B/status.txt --quiet
  aws s3 sync results/latent $B/results --exclude "*" --include "*.json" \
    --include "*.done" --quiet
  aws s3 cp logs/latent_dsweep.log $B/dsweep.log --quiet
  aws s3 cp logs/latent_esweep.log $B/esweep.log --quiet
  sleep 180
done
