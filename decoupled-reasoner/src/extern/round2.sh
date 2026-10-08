#!/bin/bash
# Round two: search type, domain restriction, and the generated query, each
# on the same 50 items as round one so the comparison is paired.
set -u
cd ~/decoupled-reasoner
. ~/.exa_env
PY=.venv/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
run () { echo "=== $1 $(date -u +%T)"
  $PY -m src.extern.retsweep --name "$1" --num-results 20 --highlights \
      --budget 60 --subset-n 50 --workers 4 "${@:2}" \
      >> logs/extern/retsweep.log 2>&1 || echo "FAILED $1"; }
run t_auto      --formulation question_options --type auto
run t_keyword   --formulation question_options --type keyword
run d_reference --formulation question_options --type neural --domains reference
run f_generated --formulation generated --type neural
echo "=== done $(date -u +%T)"
