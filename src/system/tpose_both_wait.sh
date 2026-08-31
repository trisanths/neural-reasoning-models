#!/bin/bash
# The 93M half of the balanced-draw transposed test, deferred.
#
# It was run beside the rate control and ran out of memory against it, which
# cost that run and nothing else. The card is committed to the ladder until
# queue2.sh finishes, so this waits rather than competing: a failed side
# measurement is cheap and a failed rung is not.
cd ~/decoupled-reasoner
set -u
while ! grep -q "^[0-9:]* done$" logs/system/queue.log 2>/dev/null; do
  sleep 300
done
bash src/system/tpose_both.sh
.venv/bin/python -m src.system.threport >> logs/system/threport.log 2>&1
echo "$(date -u +%H:%M:%S) tpose-both deferred half rc=$?" >> logs/system/queue.log
