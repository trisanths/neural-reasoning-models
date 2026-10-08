#!/bin/bash
# The closed book halves of the four cell table, at the calibrated settings.
#
# LFM2 defines a bos token and prepending it is what took the reproduction
# from 0.3550 to 0.4300 against a published 43.43, so every LFM2 row uses it.
# Our tokenizer defines no bos, so there is nothing to prepend and the no-bos
# number is already the calibrated one; the eot-prefix row is the check that
# says so rather than assuming it.
set -u
cd ~/decoupled-reasoner
PY=.venv/bin/python
export CUDA_VISIBLE_DEVICES=""
N=${N:-500}
CORPUS=/home/ec2-user/retrain/corpus-v1-8k.pt
mkdir -p results/extern/bench logs/extern
# cell 1, ours closed book, at the larger n
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 $PY -m src.extern.bench_ours \
  --ckpt "$CORPUS" --tag corpus-v1-8k --task mmlu --n $N \
  --out results/extern/bench/cell1_ours_mmlu_n${N}.json \
  >> logs/extern/cell1.log 2>&1 || echo "FAILED cell1"
# the harness check: does an eot prefix move it the way bos moved LFM2
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 $PY -m src.extern.bench_ours \
  --ckpt "$CORPUS" --tag corpus-v1-8k --task mmlu --n 200 --eot-prefix \
  --out results/extern/bench/ours_mmlu_eotprefix_n200.json \
  >> logs/extern/cell1.log 2>&1 || echo "FAILED eot check"
echo "CELLS_DONE $(date -u +%FT%TZ)"
