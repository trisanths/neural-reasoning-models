#!/bin/bash
# How much context, and does the passage selector need the options. Both are
# scored from results already fetched, so this round spends nothing.
set -u
cd ~/decoupled-reasoner
PY=.venv/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
for C in 3000 6000 12000 18000; do
  $PY -m src.extern.retsweep --name "c_${C}" --formulation question_options \
      --num-results 20 --highlights --budget 0 --subset-n 50 \
      --max-context-chars "$C" --keep 5,10,20 \
      >> logs/extern/retsweep.log 2>&1 || echo "FAILED c_$C"
done
echo "=== done $(date -u +%T)"
