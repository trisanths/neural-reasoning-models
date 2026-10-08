#!/bin/bash
# Commit each stage's artifacts as it lands, so nothing waits on a person.
#
# The lane runs for the better part of a day and every stage writes records,
# a summary and a regenerated THRESHOLD.md. This puts them in git as they
# appear, naming the stage that produced them, and stops when queue2.sh does.
cd ~/decoupled-reasoner
set -u
L=logs/system
while true; do
  if [ -n "$(git status --porcelain -- results/system logs/system src/system)" ]; then
    STAGE=$(tail -1 $L/queue.log 2>/dev/null | sed 's/^[0-9:]* //')
    git add -A results/system logs/system src/system
    git -c user.name="Claude" -c user.email="noreply@anthropic.com" \
        commit -q -m "Ladder artifacts through: ${STAGE:-no stage recorded}

Written by src/system/queue2.sh and rebuilt into src/system/THRESHOLD.md by
src/system/threport.py, which refuses a records file newer than the summary
that reports it." || true
  fi
  if grep -q "^[0-9:]* done$" $L/queue.log 2>/dev/null; then
    exit 0
  fi
  sleep 900
done
