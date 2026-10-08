#!/bin/bash
# Round one of the retrieval sweep: query formulation, one at a time, on a
# fixed 50 item subset. Every condition asks for 20 results with highlights,
# so the same searches also answer the rank cutoff question and the
# highlights question without a second round of spend.
set -u
cd ~/decoupled-reasoner
. ~/.exa_env
PY=.venv/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
for F in question question_options keywords subject_question; do
  echo "=== $F $(date -u +%T)"
  $PY -m src.extern.retsweep --name "f_$F" --formulation "$F" \
      --num-results 20 --highlights --budget 60 --subset-n 50 --workers 4 \
      >> logs/extern/retsweep.log 2>&1 || echo "FAILED $F"
done
echo "=== done $(date -u +%T)"
