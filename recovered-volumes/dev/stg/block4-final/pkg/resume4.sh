#!/bin/bash
# Block-4 launch: defensively resume any block-3 curve lane that did not
# finish, then start the six new block-4 lanes. Run as ec2-user after
# bootstrap4.sh:
#   bash ~/block4/resume4.sh
#
# Defensive resume (GPU 7 only): every lane that ran on the block-3 box is
# checked against its S3 log copy (logs/block3-logs/<lane>.log, pushed by the
# block-3 final flush at 11:15 UTC 2026-08-28). A lane whose log copy holds
# "done at step" is finished and skipped. If the log copy is missing (flush
# failed), the fallback compares the mirrored loss.jsonl's last step against
# the mirrored config's max_steps. Anything still unfinished is resumed from
# the S3 checkpoint mirror with the select_ckpt plan, exactly the block-3
# flow. At the boundary nothing should be mid-flight (the E2 lanes finish
# around 04:00 UTC), so the expected outcome is seven DONE lines and no
# resumes. A defensive failure warns and continues; it never blocks the new
# lanes. Block 4 keeps only GPU 7 for stragglers because six of the eight
# GPUs carry new lanes and GPU 6 is reserved for the NRM benchmark and the
# eval batteries.
#
# New block-4 lanes:
#   gpu 0  curve-350me3-701      350m.yaml       26700 steps  regime E3
#   gpu 1  curve-350me3loop-711  350m-loop.yaml   9000 steps  regime E3
#   gpu 2  curve-350me3loop-712  350m-loop.yaml   9000 steps  regime E3
#   gpu 3  curve-700me-721       700m.yaml       26700 steps  regime E
#   gpu 4  rl-350me503-741       rl-350m-wide.yaml  GRPO from curve-350me-503
#   gpu 5  rl-350me501-742       rl-350m-wide.yaml  GRPO from curve-350me-501
#   gpu 6  left free for the NRM benchmark and the eval batteries
#   gpu 7  stragglers and grading overflow
#
# 701 is the data lever control: the standard architecture on regime E3 at
# the recipe blocks 2 and 3 used, micro 8 x accum 8, compile on, 26700 steps
# for a 6,999,244,800 token budget. Its intermediate checkpoints are what the
# two looped lanes are read against at matched tokens.
#
# 711 and 712 are the depth lever, both parameter matched to 701 within 0.1
# percent and both on the same 9000 step budget so they are comparable to
# each other and to 701's step-9000 checkpoint. 711 is the recurrent-depth
# builder's recommended config unchanged: 14 unique layers, an 11 layer core,
# and a depth drawn per step from 1 to 8 loops. 712 fixes the depth at 2
# loops with the draw switched off, which is 25 effective layers against the
# standard stack's 24. That pair asks two separate questions: whether a
# weight-tied core at matched effective depth matches a plain stack (712
# against 701), and whether training across a range of depths buys anything
# (711 against 712). Two lanes that both sample cannot differ at train time
# at all, because with train_loop_sampling on, model.recurrent.loops only
# steers eval and generate, so a bracketing loop count has to come with the
# draw switched off.
#
# The 9000 step budget is measured, not chosen. bench_recurrent on the dev
# L40S gives seconds per step that fit t = 0.1404 + 0.2618 * loops for a
# 16384 token step, so the sampled lane averages 12,426 tokens per second
# there against the standard 350m's 44,326. Carrying the standard model's
# L40S-to-H100 ratio across conservatively, the sampled lane lands near
# 37,000 tokens per second on one H100, and 9000 steps of 262,144 tokens is
# about 17.6 hours inside a block that opens 11:30 UTC 2026-08-28 and is
# flushed at 11:15 UTC 2026-08-29. 26700 steps would have needed 52 hours.
# 712 is cheaper and finishes near 8 hours; its GPU then joins the grading
# pool.
#
# 721 is the 700m regime E scale control. It stands in for the evidence
# cross-attention lane that was planned for GPU 3. That lane is deferred:
# throughput and memory are fine (bench_evidence measures 39.0 GiB peak and
# 0.865 s per micro step at batch 8 with a 256 chunk bank on the L40S, which
# projects inside the block on an H100), but src/train/evidence_trainer.py
# is documented as existing for the tests and the bench, there is no CLI, no
# checkpointing, no resume and no shard streaming behind it, and nothing
# outside src/train imports the evidence model, so the eval battery, the
# interactive loop and the NRM benchmark could not score whatever the lane
# produced. The architecture and its tests are in the repo; only the lane
# waits.
#
# 741 and 742 are GRPO with retrieval in the rollout, from the two best
# graded pretrained checkpoints. Interactive heldout accuracy ranks
# curve-350me-503 at 0.8332 and curve-350me-501 at 0.8250 ahead of every
# other graded lane (502 at 0.7615, 700m-c at 0.7442, 1300m-c at 0.7269).
# They train on freshly generated worldgen episodes and are evaluated on the
# regime C heldout set the battery uses, so the RL eval numbers sit on the
# same scale as the interactive heldout column. The rlvr builder's dev run
# from 503 moved eval accuracy 0.4479 to 0.9479 in 400 steps and 0.37 hours
# on an L40S, so both lanes finish early and free their GPUs.
#
# DATA SWITCH: if s3://.../code/block4/DATA_OVERRIDE exists at fire time,
# its single line "e3_seeds_data=<path>" repoints the three E3 lanes (701,
# 711, 712; default ~/data/regime_e3) without editing scripts. A malformed
# override fails hard: the operator wrote it intending an effect.
#
# Ends by starting two 30-minute sync-and-prune loops (KEEP=1), one for
# curve-* and one for rl-*, and arming the final flush for 11:15 UTC
# 2026-08-29. Idempotent: live trainers are skipped, downloads are skipped
# when the local size already matches, and every loop has a liveness guard.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

BUCKET="${BUCKET:-s3://decoupled-reasoner-009398924577}"
S3RUNS="${S3RUNS:-$BUCKET/runs/curve}"
S3RL="${S3RL:-$BUCKET/runs/rl4}"
B4_S3="${B4_S3:-$BUCKET/code/block4}"
B3_LOGS_S3="${B3_LOGS_S3:-$BUCKET/logs/block3-logs}"
REPO="${REPO:-/home/ec2-user/decoupled-reasoner}"
PKG="${PKG:-$(cd "$(dirname "$0")" && pwd)}"
RUNS_ROOT="${RUNS_ROOT:-/home/ec2-user/runs}"
LOGS="${LOGS:-/home/ec2-user/logs}"
DATA_ROOT="${DATA_ROOT:-/home/ec2-user/data}"
DATA_E="${DATA_E:-$DATA_ROOT/regime_e}"
DATA_E3="${DATA_E3:-$DATA_ROOT/regime_e3}"
TOKENIZER="${TOKENIZER:-$DATA_ROOT/tokenizer_v2.json}"
RL_TRAIN_EPISODES="${RL_TRAIN_EPISODES:-$DATA_ROOT/rl_episodes.jsonl}"
RL_EVAL_EPISODES="${RL_EVAL_EPISODES:-$DATA_ROOT/rl_eval_episodes.jsonl}"
RL_CKPT_DIR="${RL_CKPT_DIR:-$DATA_ROOT/rlckpt}"
E_BUDGET_TOKENS=6999244800

# Every lane that ran on the block-3 box, eligible for defensive resume.
B3_LANES="curve-1300m-a curve-1300m-c curve-350me-502 curve-350me-503 \
curve-350me2-601 curve-350me2-602 curve-350me2-603"
# Stragglers take GPU 7 only; every other GPU is spoken for.
SPARES=(7)
SP_IDX=0

mkdir -p "$RUNS_ROOT" "$LOGS"
ulimit -n 65536 2>/dev/null || true   # regime E mmaps hundreds of chunk shards

# Checkpoints must land on instance-store scratch, not the root volume.
if [ "${ALLOW_ROOT_RUNS:-0}" != "1" ]; then
  if [ "$(readlink -f "$RUNS_ROOT")" != "/mnt/scratch/runs" ]; then
    echo "FAIL $RUNS_ROOT does not resolve to /mnt/scratch/runs; run bootstrap4.sh first"
    exit 1
  fi
fi

# ---- data switch for the E3 lanes ----
E3_SEEDS_DATA="$DATA_E3"
if aws s3 ls "$B4_S3/DATA_OVERRIDE" > /dev/null 2>&1; then
  OV_RAW=$(aws s3 cp --only-show-errors "$B4_S3/DATA_OVERRIDE" -)
  OV=$(printf '%s' "$OV_RAW" | head -n 1 | tr -d '[:space:]')
  case "$OV" in
    e3_seeds_data=?*) E3_SEEDS_DATA="${OV#e3_seeds_data=}" ;;
    *)
      echo "FAIL DATA_OVERRIDE exists but is malformed: '$OV' (want e3_seeds_data=<path>)"
      exit 1
      ;;
  esac
  E3_SEEDS_DATA="${E3_SEEDS_DATA/#\~/$HOME}"
  echo "DATA_OVERRIDE active: E3 lanes train on $E3_SEEDS_DATA"
else
  echo "no DATA_OVERRIDE at $B4_S3/DATA_OVERRIDE, E3 lanes train on $E3_SEEDS_DATA"
fi

check_tokens() {
  # $1 dataset dir, $2 budget; must hold index.json with total_tokens >= budget
  [ -f "$1/index.json" ] || { echo "FAIL $1 has no index.json"; return 1; }
  local total
  total=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["total_tokens"])' \
      "$1/index.json")
  if [ "$total" -lt "$2" ]; then
    echo "FAIL $1 holds $total tokens, budget needs $2"
    return 1
  fi
  echo "data ok: $1 $total tokens"
}

check_tokens "$E3_SEEDS_DATA" "$E_BUDGET_TOKENS"
check_tokens "$DATA_E" "$E_BUDGET_TOKENS"

alive() { pgrep -f "[s]rc.train.cli.*--out $1 " > /dev/null 2>&1; }
alive_rl() { pgrep -f "[s]rc.rl.cli.*--out $1 " > /dev/null 2>&1; }

gpu_free() {
  # $1 gpu index; 0 MiB used or refuse
  local used
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$1")
  if [ "$used" != "0" ]; then
    echo "gpu $1 shows $used MiB used"
    return 1
  fi
}

# ---- defensive resume of block-3 stragglers ----
lane_done() {
  # 0 when the lane's block-3 log copy shows completion; grep without -q so
  # the aws cp pipe drains fully (pipefail would turn an early close into a
  # false negative).
  local lane=$1
  if aws s3 ls "$B3_LOGS_S3/$lane.log" > /dev/null 2>&1; then
    if aws s3 cp --only-show-errors "$B3_LOGS_S3/$lane.log" - \
        | grep "done at step" > /dev/null; then
      echo "DONE $lane: log copy shows done at step"
      return 0
    fi
    return 1
  fi
  # No log copy (final flush may have failed): compare the mirrored
  # loss.jsonl against the mirrored config's max_steps.
  local last max
  last=$(aws s3 cp "$S3RUNS/$lane/loss.jsonl" - 2>/dev/null | tail -n 1 \
    | python3 -c 'import json,sys
line = sys.stdin.readline().strip()
print(json.loads(line)["step"] if line else -1)' 2>/dev/null) || last=-1
  max=$(aws s3 cp "$S3RUNS/$lane/config.yaml" - 2>/dev/null \
    | awk '/^ *max_steps:/{print $2; exit}') || max=""
  if [ -n "$max" ] && [ "$last" -ge "$max" ] 2>/dev/null; then
    echo "DONE $lane: no log copy, but mirrored loss.jsonl at step $last >= max_steps $max"
    return 0
  fi
  return 1
}

resume_lane() {
  # $1 lane, $2 gpu. Returns nonzero on any failure; never exits the script.
  local lane=$1 gpu=$2
  local rundir="$RUNS_ROOT/$lane"
  gpu_free "$gpu" || { echo "FAIL $lane: refusing gpu $gpu"; return 1; }
  mkdir -p "$rundir"
  local plan="/tmp/fetch-plan-$lane"
  aws s3 ls "$S3RUNS/$lane/" | python3 "$PKG/select_ckpt.py" "$lane" > "$plan" \
    || { echo "FAIL plan for $lane:"; cat "$plan"; return 1; }
  local latest_from=""
  local verb name size
  while read -r verb name size; do
    case "$verb" in
      GET)
        if [ -f "$rundir/$name" ] && [ "$(stat -c %s "$rundir/$name")" = "$size" ]; then
          echo "have $lane/$name ($size bytes)"
        else
          echo "fetch $lane/$name ($size bytes)"
          aws s3 cp --only-show-errors "$S3RUNS/$lane/$name" "$rundir/$name" \
            || { echo "FAIL $lane/$name download"; return 1; }
          [ "$(stat -c %s "$rundir/$name")" = "$size" ] \
            || { echo "FAIL $lane/$name downloaded short"; return 1; }
        fi
        ;;
      LATEST_FROM) latest_from=$name ;;
      FAIL) echo "FAIL plan for $lane: $name $size"; return 1 ;;
    esac
  done < "$plan"
  if [ -n "$latest_from" ]; then
    echo "restoring $lane/latest.pt from $latest_from"
    cp "$rundir/$latest_from" "$rundir/latest.pt"
  fi
  [ -s "$rundir/latest.pt" ] || { echo "FAIL $lane has no latest.pt"; return 1; }

  local raw cmd
  raw=$(tr -d '\n' < "$rundir/cmd.txt")
  cmd=$(printf '%s' "$raw" | sed -E 's/^CUDA_VISIBLE_DEVICES=[0-9]+ +//')
  case " $cmd " in *" --resume "*) ;; *) cmd="$cmd --resume" ;; esac

  # Block 4 only downloads regimes E/E2/E3; any other lane data syncs on
  # demand from the bucket's matching data/ prefix.
  local dpath wpath rel
  dpath=$(printf '%s\n' "$cmd" | sed -nE 's/.*--data ([^ ]+).*/\1/p')
  if [ -n "$dpath" ] && [ ! -e "$dpath" ]; then
    case "$dpath" in
      "$DATA_ROOT"/*)
        rel=${dpath#"$DATA_ROOT"/}
        echo "$lane data $dpath missing, syncing $BUCKET/data/$rel"
        aws s3 sync --only-show-errors "$BUCKET/data/$rel" "$dpath" \
          || { echo "FAIL $lane data sync $rel"; return 1; }
        ;;
      *) echo "FAIL $lane data $dpath outside $DATA_ROOT and missing"; return 1 ;;
    esac
  fi
  if [ -n "$dpath" ]; then
    if [ -d "$dpath" ]; then
      [ -f "$dpath/index.json" ] || { echo "FAIL $lane data $dpath has no index.json"; return 1; }
    elif [ ! -f "$dpath" ]; then
      echo "FAIL $lane data $dpath does not exist"; return 1
    fi
  fi
  wpath=$(printf '%s\n' "$cmd" | sed -nE 's/.*--warmup-bin ([^ ]+).*/\1/p')
  if [ -n "$wpath" ] && [ ! -f "$wpath" ]; then
    echo "FAIL $lane warm-up bin $wpath does not exist"; return 1
  fi

  printf 'CUDA_VISIBLE_DEVICES=%s %s\n' "$gpu" "$cmd" > "$rundir/cmd.txt"
  (cd "$REPO" && setsid nohup env CUDA_VISIBLE_DEVICES="$gpu" bash -c "$cmd" \
      > "$LOGS/$lane.log" 2>&1 < /dev/null &)
  echo "RESUMED $lane gpu $gpu log $LOGS/$lane.log"
  echo "  cmd: $cmd"
}

DEFENSIVE_FAILS=0
for lane in $B3_LANES; do
  if alive "$RUNS_ROOT/$lane"; then
    echo "SKIP $lane: trainer already running"
    continue
  fi
  if lane_done "$lane"; then
    continue
  fi
  gpu="${SPARES[$SP_IDX]:-}"
  if [ -z "$gpu" ]; then
    echo "FAIL $lane unfinished but no spare gpu left (pool 7 exhausted)"
    DEFENSIVE_FAILS=$((DEFENSIVE_FAILS + 1))
    continue
  fi
  echo "UNFINISHED $lane: resuming on gpu $gpu (grading pool shrinks)"
  if resume_lane "$lane" "$gpu"; then
    SP_IDX=$((SP_IDX + 1))
  else
    DEFENSIVE_FAILS=$((DEFENSIVE_FAILS + 1))
  fi
done

# ---- new pretraining lanes, GPUs 0-3 ----
launch_new_lane() {
  # $1 lane, $2 gpu, $3 seed, $4 base yaml, $5 micro, $6 accum, $7 ckpt,
  # $8 data, $9 max_steps, ${10} extra make_run_config args (may be empty)
  local lane=$1 gpu=$2 seed=$3 base=$4 micro=$5 accum=$6 ckpt=$7 data=$8
  local steps=$9 extra=${10:-}
  local rundir="$RUNS_ROOT/$lane"
  if alive "$rundir"; then
    echo "SKIP $lane: trainer already running"
    return 0
  fi
  gpu_free "$gpu" || { echo "FAIL refusing to launch $lane"; exit 1; }
  mkdir -p "$rundir"
  # shellcheck disable=SC2086
  (cd "$REPO" && uv run python "$PKG/make_run_config.py" \
      --base "configs/$base" --out "$rundir/config.yaml" --seed "$seed" \
      --micro-batch "$micro" --grad-accum "$accum" --ckpt-interval "$ckpt" \
      --compile 1 --max-steps "$steps" $extra) \
    || { echo "FAIL config for $lane"; exit 1; }
  local cmd="uv run python -m src.train.cli --config $rundir/config.yaml --data $data --out $rundir --resume"
  printf 'CUDA_VISIBLE_DEVICES=%s %s\n' "$gpu" "$cmd" > "$rundir/cmd.txt"
  (cd "$REPO" && setsid nohup env CUDA_VISIBLE_DEVICES="$gpu" bash -c "$cmd" \
      > "$LOGS/$lane.log" 2>&1 < /dev/null &)
  echo "LAUNCHED $lane gpu $gpu ckpt_interval $ckpt max_steps $steps log $LOGS/$lane.log"
  echo "  cmd: $cmd"
}

# Staggered ckpt_intervals keep the lanes out of the sync window at the same
# moment, matching the block-3 convention.
launch_new_lane curve-350me3-701     0 701 350m.yaml      8 8  990 "$E3_SEEDS_DATA" 26700 ""
launch_new_lane curve-350me3loop-711 1 711 350m-loop.yaml 4 16 500 "$E3_SEEDS_DATA"  9000 ""
launch_new_lane curve-350me3loop-712 2 712 350m-loop.yaml 4 16 510 "$E3_SEEDS_DATA"  9000 \
  "--loops 2 --loop-sampling off"
launch_new_lane curve-700me-721      3 721 700m.yaml      4 16 510 "$DATA_E"        26700 ""

# ---- RL lanes, GPUs 4-5 ----
launch_rl_lane() {
  # $1 lane, $2 gpu, $3 seed, $4 init checkpoint, $5 rl yaml
  local lane=$1 gpu=$2 seed=$3 ckpt=$4 base=$5
  local rundir="$RUNS_ROOT/$lane"
  if alive_rl "$rundir"; then
    echo "SKIP $lane: rl trainer already running"
    return 0
  fi
  if [ ! -s "$ckpt" ]; then
    echo "FAIL $lane: init checkpoint $ckpt missing"
    return 1
  fi
  for f in "$TOKENIZER" "$RL_TRAIN_EPISODES" "$RL_EVAL_EPISODES"; do
    [ -s "$f" ] || { echo "FAIL $lane: $f missing"; return 1; }
  done
  gpu_free "$gpu" || { echo "FAIL refusing to launch $lane"; return 1; }
  mkdir -p "$rundir"
  cp "$REPO/configs/$base" "$rundir/config.yaml"
  local cmd="uv run python -m src.rl.cli --init-checkpoint $ckpt \
--config $rundir/config.yaml --episodes-jsonl $RL_TRAIN_EPISODES \
--eval-episodes-jsonl $RL_EVAL_EPISODES --tokenizer $TOKENIZER \
--out $rundir --seed $seed --resume"
  printf 'CUDA_VISIBLE_DEVICES=%s %s\n' "$gpu" "$cmd" > "$rundir/cmd.txt"
  (cd "$REPO" && setsid nohup env CUDA_VISIBLE_DEVICES="$gpu" bash -c "$cmd" \
      > "$LOGS/$lane.log" 2>&1 < /dev/null &)
  echo "LAUNCHED $lane gpu $gpu init $ckpt log $LOGS/$lane.log"
  echo "  cmd: $cmd"
}

RL_FAILS=0
launch_rl_lane rl-350me503-741 4 741 "$RL_CKPT_DIR/350me503-26700.pt" rl-350m-wide.yaml \
  || RL_FAILS=$((RL_FAILS + 1))
launch_rl_lane rl-350me501-742 5 742 "$RL_CKPT_DIR/350me501-26700.pt" rl-350m-wide.yaml \
  || RL_FAILS=$((RL_FAILS + 1))

# ---- sync loops, 30 minutes, KEEP=1 ----
start_sync() {
  # $1 tag, $2 pattern, $3 s3 destination
  if pgrep -f "[s]ync_loop.sh $1" > /dev/null 2>&1; then
    echo "SKIP sync loop $1: already running"
    return 0
  fi
  setsid nohup env RUNS_ROOT="$RUNS_ROOT" PATTERN="$2" S3DEST="$3" KEEP=1 \
      bash "$PKG/sync_loop.sh" "$1" > "$LOGS/$1-sync.log" 2>&1 < /dev/null &
  echo "LAUNCHED sync loop $1 (pattern $2 -> $3, KEEP=1), log $LOGS/$1-sync.log"
}
start_sync curve "curve-" "$S3RUNS"
start_sync rl "rl-" "$S3RL"

# ---- final flush, 11:15 UTC 2026-08-29 ----
if pgrep -f "[f]inal_flush.sh" > /dev/null 2>&1; then
  echo "SKIP final flush: already armed"
else
  setsid nohup bash "$PKG/final_flush.sh" > "$LOGS/final-flush.log" 2>&1 < /dev/null &
  echo "ARMED final flush for 11:15 UTC 2026-08-29, log $LOGS/final-flush.log"
fi

if [ "$DEFENSIVE_FAILS" -gt 0 ]; then
  echo "WARNING DEFENSIVE_RESUME_FAILURES=$DEFENSIVE_FAILS (see FAIL lines above)"
fi
if [ "$RL_FAILS" -gt 0 ]; then
  echo "WARNING RL_LAUNCH_FAILURES=$RL_FAILS (see FAIL lines above)"
fi
echo "ALL_LAUNCHED"
