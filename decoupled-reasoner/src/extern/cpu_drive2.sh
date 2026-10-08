#!/bin/bash
# What is left of the 350M arm on CPU, ordered by what the report needs most.
#
# The headline one page run is already in flight; this waits for it and then
# takes the acquisition curve rungs before the rest of the prompt selection
# table, because the curve is what makes the external column comparable to the
# library systems three columns in src/norm/ONESHOT.md.
#
# Sample sizes differ by cell and every table reports its own n. The curve
# rungs run at a stride 4 sample of the same 850 questions and the selection
# table at stride 21, which is the sample the first three formulations were
# already measured on.
set -u
cd ~/decoupled-reasoner
M=lfm350m
PY=.venv/bin/python
REPO=$($PY -m src.extern.models $M repo)
CARD=$($PY -m src.extern.models $M)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES=""
WAITPID=${1:-0}
if [ "$WAITPID" != "0" ]; then
  echo "waiting for pid $WAITPID"
  while kill -0 "$WAITPID" 2>/dev/null; do sleep 20; done
  echo "pid $WAITPID ended $(date -u +%T)"
fi
run () { # variant out pages stride maxnew
  [ -f "$2" ] && { echo "skip $2"; return; }
  echo "=== $M $1 pages=$3 stride=$4 $(date -u +%T)"
  $PY -m src.extern.run --model "$REPO" --variant "$1" --out "$2" \
     --conds acq --pages "$3" --stride "$4" --batch 16 --max-new "$5" \
     --device cpu --dtype float32 $CARD >> logs/extern/cpu_${M}.log 2>&1 \
     || echo "FAILED $M $1 p$3 stride$4"
}
run worked results/extern/full_${M}_worked_p2.jsonl.gz 2 4 128
run worked results/extern/full_${M}_worked_p4.jsonl.gz 4 4 128
run reader  results/extern/sel_${M}_reader.jsonl.gz  1 21 128
run options results/extern/sel_${M}_options.jsonl.gz 1 21 128
echo "CPU_DRIVE2_DONE $(date -u +%FT%TZ)"
