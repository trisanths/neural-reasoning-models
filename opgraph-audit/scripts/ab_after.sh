#!/bin/bash
# Wait for one rung's training to land its checkpoint, then score it.
# Polls the trainer's own completion line rather than the process table, since
# a live wrapper shell has stood in for a dead job on this box before.
set -u
GPU="$1"; ARM="$2"
LOG=/home/ec2-user/opg/logs/ladder_ab/train_$ARM.log
for i in $(seq 1 360); do
  if grep -q "TRAIN_DONE $ARM" "$LOG" 2>/dev/null; then break; fi
  sleep 20
done
if ! grep -q "TRAIN_DONE $ARM" "$LOG" 2>/dev/null; then
  echo "TRAIN did not finish for $ARM within two hours; not scoring"
  exit 1
fi
ls -la /home/ec2-user/opg/runs/ladder_ab/ladder_$ARM.pt
bash /home/ec2-user/opg/scripts/ab_eval.sh "$GPU" "$ARM"
