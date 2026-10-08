#!/bin/bash
# Run every evaluation pass of the sweep, a few at a time on one card.
#
#   bash src/frames/sweep_drive.sh GPU BATCH CONCURRENCY [LABEL ...]
#
# A single rollout batch does not saturate a large card, so several passes
# share it. Each pass is independent and skips itself if its score file is
# already there, so this is safe to re-run after an interruption.
set -u
GPU=$1; BS=$2; P=$3; shift 3
LABELS=${*:-"base arm001 arm003 arm010 arm030 arm072"}
for A in $LABELS; do
  for KIND in gen hand; do
    for T in greedy t07; do
      echo "$A $KIND $T"
    done
  done
done | xargs -P "$P" -L 1 bash -c \
  'bash src/frames/sweep_pass.sh $0 $1 $2 '"$GPU $BS"
echo "DRIVE_DONE $(date -u +%FT%TZ)"
