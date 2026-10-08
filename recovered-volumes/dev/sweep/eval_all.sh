#!/bin/bash
# Evaluate a list of arms in order on one card.
# usage: eval_all.sh GPU BATCH ARM [ARM ...]      ARM is base|arm001|...
set -u
GPU=$1; BS=$2; shift 2
O=/home/ec2-user/sweep
for A in "$@"; do
  if [ "$A" = base ]; then
    CK=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
  else
    CK=$O/ckpt/$A.pt
  fi
  if [ ! -s "$CK" ]; then echo "MISSING $CK"; exit 1; fi
  bash $O/eval_arm.sh "$A" "$CK" "$GPU" "$BS" || exit 1
done
echo "EVAL_ALL_DONE $(date -u +%FT%TZ)"
