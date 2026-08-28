#!/bin/bash
# Copy the finished results off the training box, through S3, so they can be
# committed on the box that holds the git checkout.
set -u
aws s3 sync /home/ec2-user/opg/results/ \
  s3://decoupled-reasoner-009398924577/staging/prototype-results/ --quiet
aws s3 cp /home/ec2-user/opg/runs/direct.pt.log.json \
  s3://decoupled-reasoner-009398924577/staging/prototype-results/train-direct.log.json --quiet
aws s3 cp /home/ec2-user/opg/runs/opgraph.pt.log.json \
  s3://decoupled-reasoner-009398924577/staging/prototype-results/train-opgraph.log.json --quiet
for arm in trace opgraph2 opgraph_step; do
  aws s3 cp "/home/ec2-user/opg/runs/$arm.pt.log.json" \
    "s3://decoupled-reasoner-009398924577/staging/prototype-results/train-$arm.log.json" \
    --quiet 2>/dev/null
done
echo shipped
