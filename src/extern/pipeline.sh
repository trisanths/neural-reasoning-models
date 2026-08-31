#!/bin/bash
# The external comparison, run whole, once the ladder has let go of the card.
#
#   setsid nohup bash src/extern/pipeline.sh MODEL [MODEL...] &
#
# The card is shared with a parameter ladder that is the decisive experiment of
# this phase, so nothing here starts until the ladder's processes are gone and
# the card has been quiet for three consecutive checks. Nothing is ever killed.
#
# Weights are removed as soon as a model is scored and free space is printed on
# both sides of every model, because a disk full crash on this box takes the
# ladder with it.
set -u
cd ~/decoupled-reasoner
mkdir -p logs/extern results/extern
PY=.venv/bin/python
MIN_FREE_GB=12

log() { echo "$(date -u +%FT%TZ) $*"; }

wait_free() {
  local ok=0 used busy
  while :; do
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits \
           | head -1)
    busy=$(pgrep -f "src[./]system" | wc -l)
    if [ "${used:-99999}" -lt 3000 ] && [ "$busy" -eq 0 ]; then
      ok=$((ok + 1))
    else
      ok=0
    fi
    log "wait_free used=${used}MiB ladder_procs=$busy stable=$ok"
    [ "$ok" -ge 3 ] && { log "card is free"; return 0; }
    sleep 60
  done
}

free_gb() { df --output=avail -BG / | tail -1 | tr -dc '0-9'; }

for M in "$@"; do
  log "=== model $M  free=$(free_gb)GB"
  if [ "$(free_gb)" -lt "$MIN_FREE_GB" ]; then
    log "REFUSING $M: only $(free_gb)GB free, under the ${MIN_FREE_GB}GB floor"
    continue
  fi
  REPO=$($PY -m src.extern.models "$M" repo)
  wait_free

  # The template and padding gate. If the control questions come back as
  # nonsense the benchmark numbers below would be about the harness.
  if [ ! -f "results/extern/verify_${M}.json" ]; then
    log "verify $M"
    $PY -m src.extern.verify --model "$REPO" --max-new 256 \
        --out "results/extern/verify_${M}.json" \
        > "logs/extern/verify_${M}.log" 2>&1 || log "VERIFY FAILED $M"
  fi

  wait_free
  log "select $M"
  bash src/extern/select.sh "$M" 4

  BEST=$($PY -m src.extern.best --model "$M" 2>>"logs/extern/best_${M}.log")
  ANY=$($PY -m src.extern.best --model "$M" --any \
        2>>"logs/extern/best_${M}.log")
  log "best matched prompt for $M is $BEST (best of any is $ANY)"

  wait_free
  log "full $M $BEST"
  bash src/extern/full.sh "$M" "$BEST" 1,2,4 1

  # The advantaged cell, one page only, run when printing the candidate list
  # beat every matched formulation on the subsample.
  if [ "$ANY" != "$BEST" ]; then
    wait_free
    log "advantaged full $M $ANY (one page)"
    bash src/extern/full.sh "$M" "$ANY" 1 1
  fi

  log "scoring $M"
  $PY -m src.extern.score --gen results/extern/full_${M}_*.jsonl.gz \
      --out "results/extern/score_${M}.json" --samples 6 \
      > "logs/extern/score_${M}.log" 2>&1 || log "SCORE FAILED $M"

  BEFORE=$(free_gb)
  SAFE=$(echo "$REPO" | tr '/' '-')
  rm -rf "$HOME/.cache/huggingface/hub/models--${REPO//\//--}"
  log "deleted weights for $REPO: free ${BEFORE}GB -> $(free_gb)GB"
done

log "PIPELINE_DONE"
