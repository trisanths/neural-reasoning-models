#!/bin/bash
# Round three. Two live conditions that ask whether the auto search type is
# actually better once the sites that host copies of exam items are removed,
# and two unions that are scored from cached results and cost nothing.
set -u
cd ~/decoupled-reasoner
. ~/.exa_env
PY=.venv/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
run () { echo "=== $1 $(date -u +%T)"
  $PY -m src.extern.retsweep --name "$1" --num-results 20 --highlights \
      --subset-n 50 --workers 4 "${@:2}" \
      >> logs/extern/retsweep.log 2>&1 || echo "FAILED $1"; }
run x_auto_noleak    --formulation question_options --type auto    --exclude leak --budget 60
run x_neural_noleak  --formulation question_options --type neural  --exclude leak --budget 60
run u_qo_q           --formulation question_options+question       --budget 0
run u_qo_gen         --formulation question_options+generated      --budget 0
run u_qo_subj        --formulation question_options+subject_question --budget 0
echo "=== done $(date -u +%T)"
