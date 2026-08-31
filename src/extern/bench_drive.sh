#!/bin/bash
# The closed book table, one benchmark and one model at a time.
#
# The card is held by the parameter ladder, so this runs on CPU at one thread
# and everything here is a stride sample with its n reported. The first two
# rows are the calibration: LFM2-350M is the model whose MMLU 43.43 and GSM8K
# 30.1 are published, so reproducing it is what says whether this harness can
# be trusted with any other number.
set -u
cd ~/decoupled-reasoner
PY=.venv/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=""
N=${N:-200}
mkdir -p results/extern/bench logs/extern
b () { # model tag task fmt n
  OUT=results/extern/bench/${2}_${3}_${4}.json
  [ -f "$OUT" ] && { echo "skip $OUT"; return; }
  echo "=== $2 $3 $4 n=$5 $(date -u +%T)"
  $PY -m src.extern.bench --model "$1" --task "$3" --fmt "$4" --n "$5" \
     --out "$OUT" >> logs/extern/bench_${2}.log 2>&1 || echo "FAILED $2 $3 $4"
}
# calibration first
b LiquidAI/LFM2-350M           lfm2_350m  mmlu completion $N
b LiquidAI/LFM2-350M           lfm2_350m  mmlu chat       $N
# the generation this project has been comparing against
b LiquidAI/LFM2.5-350M         lfm25_350m mmlu completion $N
b LiquidAI/LFM2-350M           lfm2_350m  arc  completion $N
b LiquidAI/LFM2.5-350M         lfm25_350m arc  completion $N
b LiquidAI/LFM2-350M           lfm2_350m  winogrande completion $N
b LiquidAI/LFM2.5-350M         lfm25_350m winogrande completion $N
b LiquidAI/LFM2.5-1.2B-Instruct lfm25_1b2i mmlu completion $N
echo "BENCH_DRIVE_DONE $(date -u +%FT%TZ)"
