#!/bin/bash
# The 1.2B instruct rung on CPU, at the sample the clock allows.
#
# The 350M arm runs the whole 850 item set; this one runs a stride sample of
# the same questions because a 1.2B model decodes about three times slower on
# the same two cores. The n is in every table it appears in and it is never
# put beside an 850 item number as though the two were the same measurement.
set -u
cd ~/decoupled-reasoner
M=lfm1b2i
PY=.venv/bin/python
REPO=$($PY -m src.extern.models $M repo)
CARD=$($PY -m src.extern.models $M)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES=""
WAITPID=${1:-0}
if [ "$WAITPID" != "0" ]; then
  while kill -0 "$WAITPID" 2>/dev/null; do sleep 20; done
  echo "predecessor $WAITPID ended $(date -u +%T)"
fi
run () { # variant out pages stride maxnew items conds batch
  [ -f "$2" ] && { echo "skip $2"; return; }
  echo "=== $M $1 pages=$3 stride=$4 $(date -u +%T)"
  $PY -m src.extern.run --model "$REPO" --variant "$1" --out "$2" \
     --items "${6:-results/norm/oneshot/items.jsonl.gz}" \
     --conds "${7:-acq}" --pages "$3" --stride "$4" --batch "${8:-12}" \
     --max-new "$5" --device cpu --dtype float32 $CARD \
     >> logs/extern/cpu_${M}.log 2>&1 || echo "FAILED $M $1 p$3"
}
# The general check first: it is 26 short items and it is the axis this model
# is expected to win, so it should exist even if the rest runs out of clock.
run bare results/extern/gen_${M}.jsonl.gz 1 1 128 \
    results/extern/general_items.jsonl.gz general 26
run worked results/extern/sel_${M}_worked.jsonl.gz 1 21 128
run bare   results/extern/sel_${M}_bare.jsonl.gz   1 21 128
run worked results/extern/full_${M}_worked_p1.jsonl.gz 1 4 128
echo "CPU_DRIVE3_DONE $(date -u +%FT%TZ)"
