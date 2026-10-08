#!/bin/bash
# semaphore runner: N concurrent, never aborts on a child signal (unlike xargs)
# usage: runq.sh <jobs file> <N> <done-marker log>
N=${2:-4}; LOG=${3:-logs_v2/launcher.log}
while IFS= read -r job; do
  while [ "$(jobs -rp | wc -l)" -ge "$N" ]; do sleep 30; done
  bash -c "$job" &
done < "$1"
wait
echo QUEUE_DONE >> "$LOG"
