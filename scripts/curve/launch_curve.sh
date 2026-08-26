#!/bin/bash
# Launch the eight Phase 2 scaling-curve trainings on the 8x H100 box, one
# GPU each, plus the 30-minute checkpoint sync-and-prune companion. This is
# the knowledge-free reasoning scaling curve at iso-data 7.0B tokens:
#
#   gpu 0  curve-150m-a   seed 111  regime A (natural shards)
#   gpu 1  curve-150m-c   seed 211  regime C (synthetic worlds + retrieval
#   gpu 2  curve-700m-a   seed 111                traces, procgen warm-up)
#   gpu 3  curve-700m-c   seed 211
#   gpu 4  curve-1300m-a  seed 111
#   gpu 5  curve-1300m-c  seed 211
#   gpu 6  curve-350m-b   seed 311  regime B (additive control mix)
#   gpu 7  curve-150m-b   seed 311
#
# Budget: schedule.max_steps 26700 x 262,144 tokens per step =
# 6,999,244,800 tokens (7.0B) for EVERY size. Iso-data is the design: at 20
# tokens per parameter 150m would want 3.0B and 1300m would want 26B, so
# 150m is over-trained and 1300m under-trained relative to that heuristic,
# deliberately, to hold data constant across the curve.
#
# Global batch is 262,144 tokens per step (64 sequences x 4096) for every
# size; only the micro-batch x grad-accum split differs per size, from the
# L40S probe audit (probe_l40s.sh results recorded in CURVE.md). Regime C
# runs front-load the procedural warm-up via --warmup-bin; regimes A and B
# do not get it.
#
# Idempotent: a run whose trainer is already alive is skipped, and every run
# starts with --resume so a relaunch after an interruption (including a
# capacity-block boundary) continues from latest.pt. Logs go to
# ~/logs/curve-<name>.log; checkpoints sync every 30 minutes to
# s3://decoupled-reasoner-009398924577/runs/curve/ and confirmed-synced
# local checkpoints are pruned.
#
# Every default can be overridden through the environment; the dry
# verification drives this exact script with smoke-config values on the dev
# box (DEVICE=cpu COMPILE=0 MAX_STEPS=2 MAKE_CONFIG_EXTRA=--allow-global-change).
set -euo pipefail

REPO="${REPO:-/home/ec2-user/decoupled-reasoner}"
PKG="${PKG:-$(cd "$(dirname "$0")" && pwd)}"
CONFIG_DIR="${CONFIG_DIR:-$REPO/configs}"
DATA_A="${DATA_A:-/home/ec2-user/data/regime_a/shards}"
DATA_B="${DATA_B:-/home/ec2-user/data/regime_b}"
DATA_C="${DATA_C:-/home/ec2-user/data/regime_c/flat}"
WARMUP_BIN="${WARMUP_BIN:-/home/ec2-user/data/proc_warmup_15m.bin}"
RUNS_ROOT="${RUNS_ROOT:-/home/ec2-user/runs}"
LOGS="${LOGS:-/home/ec2-user/logs}"
S3DEST="${S3DEST:-s3://decoupled-reasoner-009398924577/runs/curve}"
SEED_A="${SEED_A:-111}"
SEED_B="${SEED_B:-311}"
SEED_C="${SEED_C:-211}"
MAX_STEPS="${MAX_STEPS:-26700}"
COMPILE="${COMPILE:-1}"
DEVICE="${DEVICE:-}"                # e.g. cpu for a dry run
START_SYNC="${START_SYNC:-1}"
DATA_CHECK="${DATA_CHECK:-1}"       # 0 skips the token-total preflight
MAKE_CONFIG_EXTRA="${MAKE_CONFIG_EXTRA:-}"

# name gpu regime size micro accum ckpt_interval
# micro x accum = 64 for every row; ckpt_interval targets ~30 minutes at the
# projected per-size H100 step time. Micro-batches are the L40S-validated
# values (46GB), strictly safe on 80GB; see CURVE.md for measured peaks.
RUN_TABLE="${RUN_TABLE:-
curve-150m-a  0 a 150m  16 4 2500
curve-150m-c  1 c 150m  16 4 2500
curve-700m-a  2 a 700m  4 16 500
curve-700m-c  3 c 700m  4 16 500
curve-1300m-a 4 a 1300m 2 32 300
curve-1300m-c 5 c 1300m 2 32 300
curve-350m-b  6 b 350m  8 8 1000
curve-150m-b  7 b 150m  16 4 2500
}"

mkdir -p "$RUNS_ROOT" "$LOGS"
ulimit -n 65536 2>/dev/null || true   # regime B mmaps ~420 chunk shards

for path in "$REPO" "$DATA_A" "$DATA_B" "$DATA_C"; do
  [ -e "$path" ] || { echo "FAIL missing $path"; exit 1; }
done
[ -f "$DATA_A/index.json" ] || { echo "FAIL $DATA_A has no index.json"; exit 1; }
[ -f "$DATA_B/index.json" ] || { echo "FAIL $DATA_B has no index.json"; exit 1; }
[ -f "$DATA_C/index.json" ] || { echo "FAIL $DATA_C has no index.json"; exit 1; }
[ -f "$WARMUP_BIN" ] || { echo "FAIL missing $WARMUP_BIN"; exit 1; }

if [ "$DATA_CHECK" = "1" ]; then
  BUDGET=$(( MAX_STEPS * 262144 ))
  for dir in "$DATA_A" "$DATA_B" "$DATA_C"; do
    total=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["total_tokens"])' \
        "$dir/index.json" 2>/dev/null) || total=0
    if [ "${total:-0}" -lt "$BUDGET" ]; then
      echo "FAIL $dir holds $total tokens, budget needs $BUDGET"
      exit 1
    fi
    echo "data ok: $dir $total tokens"
  done
fi

launch_one() {
  local name=$1 gpu=$2 regime=$3 size=$4 micro=$5 accum=$6 ckpt=$7
  local rundir="$RUNS_ROOT/$name"
  if pgrep -f "[s]rc.train.cli.*--out $rundir " > /dev/null 2>&1; then
    echo "SKIP $name: trainer already running"
    return 0
  fi
  local seed data
  case "$regime" in
    a) seed=$SEED_A; data=$DATA_A ;;
    b) seed=$SEED_B; data=$DATA_B ;;
    c) seed=$SEED_C; data=$DATA_C ;;
    *) echo "FAIL unknown regime $regime"; exit 1 ;;
  esac
  mkdir -p "$rundir"
  local mkargs=(--base "$CONFIG_DIR/$size.yaml" --out "$rundir/config.yaml"
      --seed "$seed" --micro-batch "$micro" --grad-accum "$accum"
      --ckpt-interval "$ckpt" --compile "$COMPILE" --max-steps "$MAX_STEPS")
  [ -n "$MAKE_CONFIG_EXTRA" ] && mkargs+=($MAKE_CONFIG_EXTRA)
  (cd "$REPO" && uv run python "$PKG/make_run_config.py" "${mkargs[@]}")

  local cli=(uv run python -m src.train.cli --config "$rundir/config.yaml"
      --data "$data" --out "$rundir" --resume)
  [ "$regime" = "c" ] && cli+=(--warmup-bin "$WARMUP_BIN")
  [ -n "$DEVICE" ] && cli+=(--device "$DEVICE")
  printf '%s ' "CUDA_VISIBLE_DEVICES=$gpu" "${cli[@]}" > "$rundir/cmd.txt"
  echo >> "$rundir/cmd.txt"
  (cd "$REPO" && setsid nohup env CUDA_VISIBLE_DEVICES="$gpu" "${cli[@]}" \
      > "$LOGS/$name.log" 2>&1 < /dev/null &)
  echo "LAUNCHED $name regime $regime seed $seed gpu $gpu micro $micro" \
       "accum $accum ckpt $ckpt log $LOGS/$name.log"
}

while read -r name gpu regime size micro accum ckpt; do
  [ -n "$name" ] || continue
  launch_one "$name" "$gpu" "$regime" "$size" "$micro" "$accum" "$ckpt"
done <<< "$RUN_TABLE"

if [ "$START_SYNC" = "1" ]; then
  # The trailing "curve" argv marker keeps this guard from matching the
  # kill-test sync loop, which may still be alive on the same box.
  if pgrep -f "[s]ync_loop.sh curve" > /dev/null 2>&1; then
    echo "SKIP sync loop: already running"
  else
    setsid nohup env RUNS_ROOT="$RUNS_ROOT" PATTERN="curve-" S3DEST="$S3DEST" \
        bash "$PKG/sync_loop.sh" curve > "$LOGS/curve-sync.log" 2>&1 < /dev/null &
    echo "LAUNCHED sync loop, log $LOGS/curve-sync.log"
  fi
fi
echo "ALL_LAUNCHED"
