#!/bin/bash
# Checkpoint sync companion for the kill-test runs. Every SYNC_INTERVAL
# seconds each run directory is mirrored to S3, then local numbered
# checkpoints that are confirmed present in S3 are pruned down to the newest
# KEEP, so local disk stays bounded while S3 keeps the full history.
# latest.pt is never pruned. A sync that fails (including a checkpoint that
# was mid-write during the pass) leaves everything in place and retries on
# the next cycle.
set -u

RUNS_ROOT="${RUNS_ROOT:-/home/ec2-user/runs}"
PATTERN="${PATTERN:-killtest-}"
S3DEST="${S3DEST:-s3://decoupled-reasoner-009398924577/runs/killtest}"
SYNC_INTERVAL="${SYNC_INTERVAL:-1800}"
KEEP="${KEEP:-2}"
ONCE="${ONCE:-0}"

stamp() { date -u +%FT%TZ; }

while :; do
  for dir in "$RUNS_ROOT/$PATTERN"*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    if aws s3 sync "$dir" "$S3DEST/$name/" --only-show-errors; then
      echo "$(stamp) synced $name"
      ls -1 "$dir"ckpt-*.pt 2>/dev/null | sort | head -n -"$KEEP" | while read -r f; do
        base=$(basename "$f")
        if aws s3 ls "$S3DEST/$name/$base" > /dev/null 2>&1; then
          rm -f -- "$f"
          echo "$(stamp) pruned $name/$base (kept in S3)"
        fi
      done
    else
      echo "$(stamp) SYNC_FAIL $name, will retry next cycle"
    fi
  done
  [ "$ONCE" = "1" ] && exit 0
  sleep "$SYNC_INTERVAL"
done
