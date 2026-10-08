#!/bin/bash
# Stage the regime B dataset for the Phase 2 scaling curve. Runs detached on
# the dev box while the render is still going: polls the render log until the
# renderer prints its final DONE line, then syncs ~/data/regime_b (chunk
# shards, merged index.json, manifest.json) to S3 and prints READY with the
# S3 path and the manifest token total. The training box downloads the same
# tree with aws s3 sync; the merged index.json makes the directory directly
# loadable by ShardReader, no consolidation pass needed.
#
# Idempotent: safe to rerun after the render is done; a rerun just re-syncs
# (a no-op when S3 is current) and prints READY again.
set -u

LOG="${LOG:-/home/ec2-user/logs/regime_b_full.log}"
SRC="${SRC:-/home/ec2-user/data/regime_b}"
DEST="${DEST:-s3://decoupled-reasoner-009398924577/data/regime_b}"
POLL="${POLL:-30}"

stamp() { date -u +%FT%TZ; }

waited=0
while ! grep -q '^DONE ' "$LOG" 2>/dev/null; do
  if ! pgrep -f '[r]ender_regime_b' > /dev/null 2>&1; then
    # Renderer gone without a DONE line. It is chunk-resumable, so someone
    # may restart it; warn every 10 minutes and keep watching.
    if [ $(( waited % 600 )) -eq 0 ]; then
      echo "$(stamp) WAIT_NO_RENDERER: no render_regime_b process and no DONE line yet"
    fi
  fi
  sleep "$POLL"
  waited=$(( waited + POLL ))
done

echo "$(stamp) render finished:"
grep '^DONE ' "$LOG" | tail -1

for f in "$SRC/manifest.json" "$SRC/index.json"; do
  [ -f "$f" ] || { echo "$(stamp) FAIL missing $f"; exit 1; }
done

ok=0
for attempt in 1 2 3; do
  if aws s3 sync "$SRC" "$DEST/" --only-show-errors; then
    ok=1
    break
  fi
  echo "$(stamp) sync attempt $attempt failed, retrying in 60s"
  sleep 60
done
[ "$ok" = "1" ] || { echo "$(stamp) FAIL sync to $DEST"; exit 1; }
# Second pass must be a no-op; proves the first pass left nothing behind.
aws s3 sync "$SRC" "$DEST/" --only-show-errors || { echo "$(stamp) FAIL verify sync"; exit 1; }

TOKENS=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["total_tokens"])' "$SRC/manifest.json")
echo "$(stamp) READY $DEST total_tokens $TOKENS"
