#!/bin/bash
# The full run for one model on the prompt its selection sweep picked.
#
#   bash src/extern/full.sh MODEL_KEY VARIANT [PAGES] [STRIDE] [EXTRA...]
#
# PAGES is the acquisition curve rung or rungs, so 1,2,4 runs all three over
# the same question items and the three columns are comparable to the library
# system's three in src/norm/ONESHOT.md.
set -u
M=$1; V=$2; PAGES=${3:-1,2,4}; STRIDE=${4:-1}; shift 4 || shift $#
PY=.venv/bin/python
REPO=$($PY -m src.extern.models $M repo)
MAXNEW=$($PY -m src.extern.models $M maxnew)
BATCH=$($PY -m src.extern.models $M batch)
CARD=$($PY -m src.extern.models $M)
mkdir -p results/extern logs/extern
for PG in ${PAGES//,/ }; do
  OUT=results/extern/full_${M}_${V}_p${PG}.jsonl.gz
  if [ -f "$OUT" ]; then echo "skip $OUT"; continue; fi
  echo "=== full $M $V p$PG $(date -u +%T)"
  $PY -m src.extern.run --model "$REPO" --variant "$V" --out "$OUT" \
      --conds acq --pages "$PG" --stride "$STRIDE" \
      --batch "$BATCH" --max-new "$MAXNEW" $CARD "$@" \
      >> logs/extern/full_${M}.log 2>&1 || echo "FAILED $M $V p$PG"
done
# Greedy beside the card's sampled settings, on the one page rung only. The
# project's own reader reports a greedy headline, and a decode the publisher
# did not recommend is still worth one look before a number is called final.
GOUT_G=results/extern/full_${M}_${V}_greedy_p1.jsonl.gz
if [ ! -f "$GOUT_G" ]; then
  echo "=== greedy $M $V p1 $(date -u +%T)"
  $PY -m src.extern.run --model "$REPO" --variant "$V" --out "$GOUT_G" \
      --conds acq --pages 1 --stride "$STRIDE" \
      --batch "$BATCH" --max-new "$MAXNEW" --greedy \
      >> logs/extern/full_${M}.log 2>&1 || echo "FAILED $M $V greedy"
fi

# The general check, same model, same harness, so the axis these models win on
# is measured by the same code as the axis they do not.
GOUT=results/extern/gen_${M}.jsonl.gz
if [ ! -f "$GOUT" ]; then
  # The general questions get the plain formulation. The worked scaffold talks
  # about definition pages and lookup maps, and pointing it at "what is the
  # capital of Japan" would handicap the models on the one axis where they are
  # expected to win.
  $PY -m src.extern.run --model "$REPO" --variant bare --out "$GOUT" \
      --items results/extern/general_items.jsonl.gz --conds general \
      --pages 1 --batch 26 --max-new "$MAXNEW" $CARD \
      >> logs/extern/full_${M}.log 2>&1 || echo "FAILED $M general"
fi
echo "FULL_DONE $M $(date -u +%FT%TZ)"
