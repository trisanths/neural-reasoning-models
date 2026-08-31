#!/bin/bash
# Prompt selection for one model: every variant over the same subsample.
#
#   bash src/extern/select.sh MODEL_KEY [STRIDE]
#
# Each variant is run over the same stride sample of the one page acquisition
# items, under the sampling settings the model card recommends, and the best
# strict score is what the full run then uses. The subsample is fixed by the
# stride rather than drawn, so every variant sees the same items.
set -u
M=$1; STRIDE=${2:-4}
PY=.venv/bin/python
REPO=$($PY -m src.extern.models $M repo)
MAXNEW=$($PY -m src.extern.models $M maxnew)
BATCH=$($PY -m src.extern.models $M batch)
CARD=$($PY -m src.extern.models $M)
mkdir -p results/extern logs/extern
for V in bare reader worked prefill options; do
  OUT=results/extern/sel_${M}_${V}.jsonl.gz
  if [ -f "$OUT" ]; then echo "skip $OUT"; continue; fi
  echo "=== $M $V $(date -u +%T)"
  $PY -m src.extern.run --model "$REPO" --variant "$V" --out "$OUT" \
      --conds acq --pages 1 --stride "$STRIDE" \
      --batch "$BATCH" --max-new "$MAXNEW" $CARD \
      >> logs/extern/sel_${M}.log 2>&1 || echo "FAILED $M $V"
done
# Greedy is run beside the card settings on the one variant that scored best,
# because a decode the publisher did not recommend is still worth one look.
echo "SELECT_DONE $M $(date -u +%FT%TZ)"
