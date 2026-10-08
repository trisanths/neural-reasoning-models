#!/bin/bash
# The projects own two checkpoints on the public benchmarks, closed book.
#
# Waits for the page benchmark run to release its cores before starting, so
# the box is never oversubscribed past the parameter ladder that owns the card.
set -u
cd ~/decoupled-reasoner
PY=.venv/bin/python
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES=""
N=${N:-200}
CORPUS=/home/ec2-user/retrain/corpus-v1-8k.pt
BASE=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
W=${1:-0}
if [ "$W" != "0" ]; then
  while kill -0 "$W" 2>/dev/null; do sleep 20; done
  echo "predecessor $W ended $(date -u +%T)"
fi
o () { # ckpt tag task n
  OUT=results/extern/bench/ours_${2}_${3}.json
  [ -f "$OUT" ] && { echo "skip $OUT"; return; }
  echo "=== ours $2 $3 n=$4 $(date -u +%T)"
  $PY -m src.extern.bench_ours --ckpt "$1" --tag "$2" --task "$3" --n "$4" \
     --out "$OUT" >> logs/extern/ours_bench.log 2>&1 || echo "FAILED $2 $3"
}
o "$CORPUS" corpus-v1-8k mmlu       $N
o "$CORPUS" corpus-v1-8k arc        $N
o "$CORPUS" corpus-v1-8k winogrande $N
o "$BASE"   rlsimple-base mmlu      $N
echo "OURS_DRIVE_DONE $(date -u +%FT%TZ)"
