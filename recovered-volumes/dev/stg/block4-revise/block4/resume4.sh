#!/bin/bash
# Block-4 launch: defensively resume any block-3 curve lane that did not
# finish, then start the six new block-4 lanes. Run as ec2-user after
# bootstrap4.sh:
#   bash ~/block4/resume4.sh
#
# The block spends its GPUs on architecture, not only on diet. GPU 0 keeps
# the regime E3 data lever as its control; GPUs 1 and 2 run the same data
# through looped depth at two loop counts; GPU 3 keeps the 700m scale lever
# on regime E; GPUs 4 and 5 run GRPO against the verifiers from the two best
# graded pretrained checkpoints. GPU 6 is left free for the E2 or E3 grading
# batteries. GPU 7 is the only straggler and overflow slot.
#
#   gpu 0  curve-350me3-701       350m standard      data $E3_SEEDS_DATA
#   gpu 1  curve-350me3loop-711   350m looped, 4     data $E3_SEEDS_DATA
#   gpu 2  curve-350me3loop-712   350m looped, 2     data $E3_SEEDS_DATA
#   gpu 3  curve-700me-721        700m standard      data ~/data/regime_e
#   gpu 4  curve-rl-350me503-731  GRPO from curve-350me-503 step 26700
#   gpu 5  curve-rl-350md401-732  GRPO from curve-350md-401 step 26700
#   gpu 6  (no lane: grading)
#   gpu 7  stragglers and grading overflow
#
# The three 350m lanes share the 7.0B token budget: micro 8 x accum 8 at
# 4096 context is 262,144 tokens per optimizer step and 26,700 steps, so 701,
# 711, and 712 are comparable at any common token count. The 700m lane uses
# the audited curve recipe micro 4 x accum 16 (global 64 like the committed
# base's 2 x 32) on the ORIGINAL regime E data for the scale-vs-diet
# comparison.
#
# LOOPED LANES. configs/350m-loop.yaml is parameter matched to configs/350m
# .yaml (375,087,360 against 375,440,384, 0.09 percent under) with 14 unique
# layers instead of 24 and a core of 11 layers applied L times, so 711 and
# 712 differ from 701 in depth per token and not in parameter count. Both
# looped lanes run backprop_last_k 2 and gradient checkpointing: on the L40S
# that combination cut peak memory at 8 loops from 21.16 to 17.46 GiB and
# more than doubled throughput against full backprop, and the k equal to
# loops control landed on the full backprop number to within 0.1 percent,
# which is what makes the rest of that column trustworthy.
#
# 711 is the recommended setting, loops 4 sampled over [1,8]: effective depth
# 47 by default and 14 to 91 across the sampled range. 712 brackets it from
# below, loops 2 sampled over [1,4], effective depth 25 by default and 14 to
# 47 across the range. Below rather than above, for two reasons. At 2 loops
# the effective depth is 25 against the control's 24, so 712 against 701
# isolates the recurrence machinery at matched depth while 711 against 712
# measures what the extra depth buys. And the block is 24 hours: the
# projected H100 rates put 712 at about 20 hours for the full 7.0B budget and
# 711 at about 31 hours, so the lower bracket is the one that actually
# reaches the end of the curve inside the block. Both projections are
# interpolations off L40S measurements scaled by the project's 3.03x anchor,
# so read the real rate off loss.jsonl rather than trusting them.
#
# RL LANES. Base checkpoints are picked off the graded battery in
# runs/curve/evals-e-repl/CURVE-TABLE.md and runs/curve/evals-350md/
# D-REPORT.md, on interactive held-out accuracy and prose reading. The two
# taken are curve-350me-503, the best interactive held-out of any graded
# model at 0.8332 with reading 0.1800, and curve-350md-401, the best regime D
# seed at 0.7878 interactive with reading 0.2000. Both are step 26700. They
# come from different regimes on purpose. Note that 401 carries the regime D
# leakage flag (probes 0.3893 against the 0.3332 threshold), so its RL result
# reads as "RL on a partly memorizing base", not as a clean retrieval result.
#
# Each RL lane runs configs/rl-350m-block.yaml: group 16, 16 prompts per
# step, 256 rollouts per step, kl_coef 0.05, 3000 steps. Episodes are the
# pre-rendered ~/data/regime_c/heldout.jsonl that bootstrap4.sh downloads and
# byte-checks; nothing is generated on the fly, so a lane cannot stall on a
# generator. Before committing a lane the launcher runs two real optimizer
# steps at the full shape into a scratch directory; if that probe dies the
# lane falls back to configs/rl-350m-block-narrow.yaml, which halves prompts
# per step and micro batch. The measured L40S peak was 31.3 GB at 32 rollout
# lanes, and this is 256, so the probe is the thing standing between an
# out-of-memory and a wasted block.
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
# resumes. The spare pool is one GPU now instead of four, so a second
# straggler warns rather than displacing a new lane; a defensive failure
# never blocks the new lanes.
#
# DATA SWITCH: if s3://.../code/block4/DATA_OVERRIDE exists at fire time,
# its single line "e3_seeds_data=<path>" repoints the three E3 lanes
# (default ~/data/regime_e3) without editing scripts. A malformed override
# fails hard: the operator wrote it intending an effect.
#
# Ends by starting the 30-minute sync-and-prune loop (KEEP=1) for every
# curve-* run, which the RL run dirs match by name, and arming the final
# flush for 11:15 UTC 2026-08-29. Idempotent: live trainers are skipped,
# downloads are skipped when the local size already matches, and both loops
# have liveness guards.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

BUCKET="${BUCKET:-s3://decoupled-reasoner-009398924577}"
S3RUNS="${S3RUNS:-$BUCKET/runs/curve}"
B4_S3="${B4_S3:-$BUCKET/code/block4}"
B3_LOGS_S3="${B3_LOGS_S3:-$BUCKET/logs/block3-logs}"
REPO="${REPO:-/home/ec2-user/decoupled-reasoner}"
PKG="${PKG:-$(cd "$(dirname "$0")" && pwd)}"
RUNS_ROOT="${RUNS_ROOT:-/home/ec2-user/runs}"
LOGS="${LOGS:-/home/ec2-user/logs}"
DATA_ROOT="${DATA_ROOT:-/home/ec2-user/data}"
DATA_E="${DATA_E:-$DATA_ROOT/regime_e}"
DATA_E3="${DATA_E3:-$DATA_ROOT/regime_e3}"
RLCKPT="${RLCKPT:-/mnt/scratch/rlckpt}"
RL_EPISODES="${RL_EPISODES:-$DATA_ROOT/regime_c/heldout.jsonl}"
TOKENIZER="${TOKENIZER:-$DATA_ROOT/tokenizer_v2.json}"
RL_CONFIG="${RL_CONFIG:-configs/rl-350m-block.yaml}"
RL_CONFIG_NARROW="${RL_CONFIG_NARROW:-configs/rl-350m-block-narrow.yaml}"
RL_PROBE_TIMEOUT="${RL_PROBE_TIMEOUT:-1200}"
E_BUDGET_TOKENS=6999244800

# Every lane that ran on the block-3 box, eligible for defensive resume.
B3_LANES="curve-1300m-a curve-1300m-c curve-350me-502 curve-350me-503 \
curve-350me2-601 curve-350me2-602 curve-350me2-603"
# Stragglers take GPU 7 and nothing else. GPU 6 is reserved for grading.
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

# ---- data switch for the three 350m E3 lanes ----
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
  echo "DATA_OVERRIDE active: 350m E3 lanes train on $E3_SEEDS_DATA"
else
  echo "no DATA_OVERRIDE at $B4_S3/DATA_OVERRIDE, E3 lanes train on $E3_SEEDS_DATA"
fi

check_tokens() {
  # $1 dataset dir; must hold index.json with total_tokens >= budget
  [ -f "$1/index.json" ] || { echo "FAIL $1 has no index.json"; return 1; }
  local total
  total=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["total_tokens"])' \
      "$1/index.json")
  if [ "$total" -lt "$E_BUDGET_TOKENS" ]; then
    echo "FAIL $1 holds $total tokens, budget needs $E_BUDGET_TOKENS"
    return 1
  fi
  echo "data ok: $1 $total tokens"
}

check_tokens "$E3_SEEDS_DATA"
check_tokens "$DATA_E"

alive() { pgrep -f "[s]rc.train.cli.*--out $1 " > /dev/null 2>&1; }
rl_alive() { pgrep -f "[s]rc.rl.cli.*--out $1 " > /dev/null 2>&1; }

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
    echo "FAIL $lane unfinished but no spare gpu left (pool is GPU 7 only)"
    DEFENSIVE_FAILS=$((DEFENSIVE_FAILS + 1))
    continue
  fi
  echo "UNFINISHED $lane: resuming on gpu $gpu"
  if resume_lane "$lane" "$gpu"; then
    SP_IDX=$((SP_IDX + 1))
  else
    DEFENSIVE_FAILS=$((DEFENSIVE_FAILS + 1))
  fi
done

# ---- new pretraining lanes, GPUs 0-3 ----
launch_new_lane() {
  # $1 lane, $2 gpu, $3 seed, $4 base yaml, $5 micro, $6 accum, $7 ckpt,
  # $8 data, then any extra make_run_config.py flags (the recurrent dial).
  local lane=$1 gpu=$2 seed=$3 base=$4 micro=$5 accum=$6 ckpt=$7 data=$8
  shift 8
  local rundir="$RUNS_ROOT/$lane"
  if alive "$rundir"; then
    echo "SKIP $lane: trainer already running"
    return 0
  fi
  gpu_free "$gpu" || { echo "FAIL refusing to launch $lane"; exit 1; }
  mkdir -p "$rundir"
  (cd "$REPO" && uv run python "$PKG/make_run_config.py" \
      --base "configs/$base" --out "$rundir/config.yaml" --seed "$seed" \
      --micro-batch "$micro" --grad-accum "$accum" --ckpt-interval "$ckpt" \
      --compile 1 --max-steps 26700 "$@") || { echo "FAIL config for $lane"; exit 1; }
  local cmd="uv run python -m src.train.cli --config $rundir/config.yaml --data $data --out $rundir --resume"
  printf 'CUDA_VISIBLE_DEVICES=%s %s\n' "$gpu" "$cmd" > "$rundir/cmd.txt"
  (cd "$REPO" && setsid nohup env CUDA_VISIBLE_DEVICES="$gpu" bash -c "$cmd" \
      > "$LOGS/$lane.log" 2>&1 < /dev/null &)
  echo "LAUNCHED $lane gpu $gpu ckpt_interval $ckpt log $LOGS/$lane.log"
  echo "  cmd: $cmd"
}

# ---- RL lanes, GPUs 4-5 ----
launch_rl_lane() {
  # $1 lane, $2 gpu, $3 seed, $4 init checkpoint
  local lane=$1 gpu=$2 seed=$3 init=$4
  local rundir="$RUNS_ROOT/$lane"
  if rl_alive "$rundir"; then
    echo "SKIP $lane: rl trainer already running"
    return 0
  fi
  gpu_free "$gpu" || { echo "FAIL refusing to launch $lane"; exit 1; }
  [ -s "$init" ] || { echo "FAIL $lane init checkpoint $init missing or empty"; exit 1; }
  [ -s "$RL_EPISODES" ] || { echo "FAIL $lane episodes $RL_EPISODES missing"; exit 1; }
  [ -s "$TOKENIZER" ] || { echo "FAIL $lane tokenizer $TOKENIZER missing"; exit 1; }
  [ -f "$REPO/$RL_CONFIG" ] || { echo "FAIL $lane $RL_CONFIG not in the repo"; exit 1; }
  [ -f "$REPO/$RL_CONFIG_NARROW" ] || { echo "FAIL $lane $RL_CONFIG_NARROW not in the repo"; exit 1; }
  mkdir -p "$rundir"

  # Width probe: two real optimizer steps at the full shape. The probe dir is
  # dot-prefixed so the curve-* sync glob never picks it up, and it is removed
  # either way.
  local probe="$RUNS_ROOT/.rlprobe-$lane"
  local chosen="$RL_CONFIG"
  rm -rf "$probe"
  mkdir -p "$probe"
  if (cd "$REPO" && uv run python "$PKG/make_rl_probe.py" \
        --base "$RL_CONFIG" --out "$probe/config.yaml"); then
    if (cd "$REPO" && timeout "$RL_PROBE_TIMEOUT" env CUDA_VISIBLE_DEVICES="$gpu" \
          uv run python -m src.rl.cli --init-checkpoint "$init" \
          --config "$probe/config.yaml" --episodes-jsonl "$RL_EPISODES" \
          --tokenizer "$TOKENIZER" --out "$probe" --seed "$seed" \
          > "$LOGS/$lane-probe.log" 2>&1); then
      if grep -q '"step": [1-9]' "$probe/rl.jsonl" 2>/dev/null; then
        echo "PROBE OK $lane: full shape took a gradient step, using $RL_CONFIG"
      else
        echo "PROBE WARN $lane: full shape ran without a logged gradient step;"
        echo "  rollout width was exercised, the update width was not. Using $RL_CONFIG."
      fi
    else
      chosen="$RL_CONFIG_NARROW"
      echo "PROBE FAILED $lane: full shape did not survive two steps, falling back"
      echo "  to $RL_CONFIG_NARROW. Probe log tail:"
      tail -n 12 "$LOGS/$lane-probe.log" | sed 's/^/    /'
    fi
  else
    chosen="$RL_CONFIG_NARROW"
    echo "PROBE FAILED $lane: could not write a probe config, falling back to $RL_CONFIG_NARROW"
  fi
  rm -rf "$probe"

  local cmd="uv run python -m src.rl.cli --init-checkpoint $init --config $chosen --episodes-jsonl $RL_EPISODES --tokenizer $TOKENIZER --out $rundir --seed $seed --resume"
  printf 'CUDA_VISIBLE_DEVICES=%s %s\n' "$gpu" "$cmd" > "$rundir/cmd.txt"
  (cd "$REPO" && setsid nohup env CUDA_VISIBLE_DEVICES="$gpu" bash -c "$cmd" \
      > "$LOGS/$lane.log" 2>&1 < /dev/null &)
  echo "LAUNCHED $lane gpu $gpu config $chosen init $init log $LOGS/$lane.log"
  echo "  cmd: $cmd"
}

# Staggered ckpt_intervals keep the lanes out of the sync window at the same
# moment, matching the block-3 convention.
launch_new_lane curve-350me3-701      0 701 350m.yaml      8 8  990  "$E3_SEEDS_DATA"
launch_new_lane curve-350me3loop-711  1 711 350m-loop.yaml 8 8  1050 "$E3_SEEDS_DATA" \
    --loops 4 --loop-sampling 1,8 --backprop-last-k 2 --grad-checkpoint 1
launch_new_lane curve-350me3loop-712  2 712 350m-loop.yaml 8 8  1070 "$E3_SEEDS_DATA" \
    --loops 2 --loop-sampling 1,4 --backprop-last-k 2 --grad-checkpoint 1
launch_new_lane curve-700me-721       3 721 700m.yaml      4 16 510  "$DATA_E"

launch_rl_lane curve-rl-350me503-731 4 731 "$RLCKPT/curve-350me-503-ckpt-0026700.pt"
launch_rl_lane curve-rl-350md401-732 5 732 "$RLCKPT/curve-350md-401-ckpt-0026700.pt"

echo "gpu 6 left free for the E2/E3 grading batteries; gpu 7 is the straggler slot"

# ---- sync loop, 30 minutes, KEEP=1 ----
if pgrep -f "[s]ync_loop.sh curve" > /dev/null 2>&1; then
  echo "SKIP sync loop: already running"
else
  setsid nohup env RUNS_ROOT="$RUNS_ROOT" PATTERN="curve-" S3DEST="$S3RUNS" KEEP=1 \
      bash "$PKG/sync_loop.sh" curve > "$LOGS/curve-sync.log" 2>&1 < /dev/null &
  echo "LAUNCHED sync loop (KEEP=1), log $LOGS/curve-sync.log"
fi

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
echo "ALL_LAUNCHED"
