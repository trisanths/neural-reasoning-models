#!/bin/bash
# Checkpoint sync companion for the kill-test runs. Every SYNC_INTERVAL
# seconds each run directory is mirrored to S3, then local numbered
# checkpoints that are confirmed present in S3 are pruned down to the newest
# KEEP, so local disk stays bounded while S3 keeps the full history.
# latest.pt is never pruned. A sync that fails (including a checkpoint that
# was mid-write during the pass) leaves everything in place and retries on
# the next cycle.
#
# Two checkpoint families are pruned. Pretraining lanes write ckpt-NNNNNNN.pt
# from src/train/trainer.py; the block-4 RL lanes write rl-NNNNNN.pt from
# src/rl/grpo.py. Both are 4.5 GB apiece at the 350m size, so an RL lane left
# unpruned would put tens of gigabytes on scratch over a block. Each family is
# counted separately, so KEEP=1 keeps one of each in a directory that somehow
# holds both. final.pt is left alone for the same reason as latest.pt: it is
# the object anything downstream reaches for by name.
set -u

RUNS_ROOT="${RUNS_ROOT:-/home/ec2-user/runs}"
PATTERN="${PATTERN:-killtest-}"
S3DEST="${S3DEST:-s3://decoupled-reasoner-009398924577/runs/killtest}"
SYNC_INTERVAL="${SYNC_INTERVAL:-1800}"
KEEP="${KEEP:-2}"
ONCE="${ONCE:-0}"

stamp() { date -u +%FT%TZ; }

prune_family() {
  # $1 run dir, $2 run name, $3 glob prefix (ckpt- or rl-)
  local dir=$1 name=$2 prefix=$3 f base
  ls -1 "$dir$prefix"*.pt 2>/dev/null | sort | head -n -"$KEEP" | while read -r f; do
    base=$(basename "$f")
    if aws s3 ls "$S3DEST/$name/$base" > /dev/null 2>&1; then
      rm -f -- "$f"
      echo "$(stamp) pruned $name/$base (kept in S3)"
    fi
  done
}

while :; do
  for dir in "$RUNS_ROOT/$PATTERN"*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    if aws s3 sync "$dir" "$S3DEST/$name/" --only-show-errors; then
      echo "$(stamp) synced $name"
      prune_family "$dir" "$name" "ckpt-"
      prune_family "$dir" "$name" "rl-"
    else
      echo "$(stamp) SYNC_FAIL $name, will retry next cycle"
    fi
  done
  [ "$ONCE" = "1" ] && exit 0
  sleep "$SYNC_INTERVAL"
done
