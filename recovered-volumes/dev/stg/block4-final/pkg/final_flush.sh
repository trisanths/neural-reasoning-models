#!/bin/bash
# Final checkpoint flush before the block-4 capacity block ends at
# 11:30 UTC 2026-08-29. Armed detached by resume4.sh; sleeps until
# 11:15 UTC, then runs two single-pass sync cycles (the second pass picks up
# anything the first one raced with) and mirrors the training logs to S3.
set -u

BUCKET="${BUCKET:-s3://decoupled-reasoner-009398924577}"
S3RUNS="${S3RUNS:-$BUCKET/runs/curve}"
S3RL="${S3RL:-$BUCKET/runs/rl4}"
PKG="${PKG:-$(cd "$(dirname "$0")" && pwd)}"
RUNS_ROOT="${RUNS_ROOT:-/home/ec2-user/runs}"
LOGS="${LOGS:-/home/ec2-user/logs}"
TARGET="${TARGET:-$(python3 -c 'import datetime; print(int(datetime.datetime(2026,8,29,11,15,0,tzinfo=datetime.timezone.utc).timestamp()))')}"

echo "final flush armed at $(date -u +%FT%TZ), firing at 11:15:00 UTC 2026-08-29 (epoch $TARGET)"
while [ "$(date +%s)" -lt "$TARGET" ]; do sleep 30; done
echo "final flush firing at $(date -u +%FT%TZ)"

for pass in 1 2; do
  echo "flush pass $pass"
  env RUNS_ROOT="$RUNS_ROOT" PATTERN="curve-" S3DEST="$S3RUNS" KEEP=1 ONCE=1 \
      bash "$PKG/sync_loop.sh" curvefinal
  env RUNS_ROOT="$RUNS_ROOT" PATTERN="rl-" S3DEST="$S3RL" KEEP=1 ONCE=1 \
      bash "$PKG/sync_loop.sh" rlfinal
done

aws s3 sync "$LOGS" "$BUCKET/logs/block4-logs/" --only-show-errors \
  --exclude "*" --include "*.log"
echo "FINAL_FLUSH_DONE at $(date -u +%FT%TZ)"
