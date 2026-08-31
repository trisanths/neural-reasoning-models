#!/bin/bash
# The comparison on CPU, because the card is not free for many hours.
#
# The ladder queue holds the one card through three more 30,000 step training
# runs and a 350M arm, so waiting for it would mean reporting nothing. These
# models answer this task in a handful of tokens, which makes CPU decoding
# affordable, and float32 on CPU is if anything a more faithful decode than
# bfloat16 on the card. Thread count is held at 2 of the 4 cores so the
# ladder keeps its own.
set -u
cd ~/decoupled-reasoner
M=$1; shift
PY=.venv/bin/python
REPO=$($PY -m src.extern.models $M repo)
CARD=$($PY -m src.extern.models $M)
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES=""
run () { # variant out pages stride maxnew batch
  [ -f "$2" ] && { echo "skip $2"; return; }
  echo "=== $M $1 pages=$3 stride=$4 $(date -u +%T)"
  $PY -m src.extern.run --model "$REPO" --variant "$1" --out "$2" \
     --conds acq --pages "$3" --stride "$4" --batch "$6" --max-new "$5" \
     --device cpu --dtype float32 $CARD >> logs/extern/cpu_${M}.log 2>&1 \
     || echo "FAILED $M $1 p$3"
}
# The headline first: the whole one page set on the formulation that led the
# subsample, so the number that matters exists even if nothing else finishes.
run worked results/extern/full_${M}_worked_p1.jsonl.gz 1 1 128 16
# The rest of the selection table, at the stride sample.
run bare    results/extern/sel_${M}_bare.jsonl.gz    1 4 128 16
run reader  results/extern/sel_${M}_reader.jsonl.gz  1 4 128 16
run worked  results/extern/sel_${M}_worked.jsonl.gz  1 4 128 16
run options results/extern/sel_${M}_options.jsonl.gz 1 4 128 16
run prefill results/extern/sel_${M}_prefill.jsonl.gz 1 4 384 16
# The acquisition curve rungs.
run worked results/extern/full_${M}_worked_p2.jsonl.gz 2 1 128 16
run worked results/extern/full_${M}_worked_p4.jsonl.gz 4 1 128 16
echo "CPU_DRIVE_DONE $M $(date -u +%FT%TZ)"
