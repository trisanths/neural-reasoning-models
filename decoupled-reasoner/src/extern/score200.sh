#!/bin/bash
# Cell 4 rescored twice on the same fetched pages, one arm after the other so
# only one job is ever on the box. The arms differ in one thing: which
# characters of those pages reach the model. Everything else, the items, the
# prompt, the letter scoring, bos and float32 on cpu, is what the published
# cell used. Two threads of four, so the training run keeps its own.
set -u
cd ~/decoupled-reasoner
PY=.venv/bin/python
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES=""
common="--budget 0 --subset-n 200 --highlights --bos --device cpu --dtype float32"
echo "=== passages keep=20 $(date -u +%T)"
$PY -m src.extern.retrun $common --packer passages --keep 20 \
    --out results/extern/bench/cell4b_lfm2_mmlu_passages_n200.json \
    > logs/extern/score_passages.log 2>&1 || echo "FAILED passages"
echo "=== sequential keep=5 $(date -u +%T)"
$PY -m src.extern.retrun $common --packer sequential --keep 5 \
    --out results/extern/bench/cell4c_lfm2_mmlu_seq5_n200.json \
    > logs/extern/score_seq5.log 2>&1 || echo "FAILED sequential"
echo "=== done $(date -u +%T)"
