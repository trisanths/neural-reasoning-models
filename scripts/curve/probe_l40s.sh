#!/bin/bash
# Memory and throughput probes for the Phase 2 scaling-curve configs, run on
# the dev box L40S (46,068 MiB). For each (size, micro-batch, grad-accum)
# candidate this starts a real compiled training run against the regime A
# shards, waits until MEASURE_STEPS optimizer steps are logged, records the
# peak nvidia-smi memory while it ran, computes tok/s from the loss.jsonl
# elapsed_s deltas over the post-compile steps, then kills the run before it
# can write a checkpoint. Every candidate keeps micro x accum = 64 sequences
# so the probe exercises the exact global batch the curve will use. A CUDA
# OOM is a result, not an error: the probe reports OOM and moves on.
#
# Output lines (also the machine-readable result):
#   PROBE <size> mb<micro> ga<accum> peak_mib <n> tok_s <n>
#   PROBE <size> mb<micro> ga<accum> OOM peak_mib <n>
# and finally PROBES_DONE.
set -u

REPO="${REPO:-/home/ec2-user/decoupled-reasoner}"
DATA="${DATA:-/home/ec2-user/data/regime_a/shards}"
PROBE_ROOT="${PROBE_ROOT:-/home/ec2-user/probes/phase2}"
MEASURE_STEPS="${MEASURE_STEPS:-8}"
SKIP_STEPS="${SKIP_STEPS:-3}"     # drop the first steps: compile + warmup
TIMEOUT="${TIMEOUT:-1080}"        # per-probe wall clock cap, seconds
GPU="${GPU:-0}"
# size:micro:accum triples, probed in order.
CANDIDATES="${CANDIDATES:-150m:8:8 150m:16:4 700m:2:32 700m:4:16 700m:8:8 1300m:1:64 1300m:2:32 1300m:4:16}"

stamp() { date -u +%FT%TZ; }
mkdir -p "$PROBE_ROOT"

probe_one() {
  local size=$1 micro=$2 accum=$3
  local run="$PROBE_ROOT/$size-mb$micro"
  rm -rf "$run"
  mkdir -p "$run"

  (cd "$REPO" && uv run python - "$size" "$micro" "$accum" "$run" <<'PYEOF'
import sys, yaml
size, micro, accum, run = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
cfg = yaml.safe_load(open(f"configs/{size}.yaml"))
assert micro * accum == 64, "probe must keep the 64-sequence global batch"
cfg["train"].update(batch_size=micro, grad_accum_steps=accum, compile=True,
                    log_interval=1, ckpt_interval=1000000, seed=999)
cfg["schedule"]["max_steps"] = 500  # never reached; the probe kills the run
yaml.safe_dump(cfg, open(f"{run}/config.yaml", "w"), sort_keys=True)
PYEOF
  ) || { echo "PROBE $size mb$micro ga$accum CONFIG_FAIL"; return 0; }

  (cd "$REPO" && setsid nohup env CUDA_VISIBLE_DEVICES="$GPU" \
      uv run python -m src.train.cli --config "$run/config.yaml" \
      --data "$DATA" --out "$run" > "$run/stdout.log" 2>&1 < /dev/null &)
  sleep 2
  local pgid
  pgid=$(pgrep -f "[s]rc.train.cli.*--out $run" | head -1 || true)
  if [ -z "$pgid" ]; then
    echo "PROBE $size mb$micro ga$accum LAUNCH_FAIL"
    return 0
  fi

  local peak=0 waited=0 status=running
  while [ "$waited" -lt "$TIMEOUT" ]; do
    local used
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" 2>/dev/null | head -1)
    [ -n "${used:-}" ] && [ "$used" -gt "$peak" ] && peak=$used
    if grep -qiE "out of memory|OutOfMemoryError" "$run/stdout.log" 2>/dev/null; then
      status=oom
      break
    fi
    if ! pgrep -f "[s]rc.train.cli.*--out $run" > /dev/null 2>&1; then
      status=died
      break
    fi
    local steps
    steps=$(wc -l < "$run/loss.jsonl" 2>/dev/null || echo 0)
    if [ "${steps:-0}" -ge "$MEASURE_STEPS" ]; then
      status=done
      break
    fi
    sleep 3
    waited=$(( waited + 3 ))
  done
  [ "$status" = "running" ] && status=timeout
  pkill -g "$(ps -o pgid= -p "$pgid" 2>/dev/null | tr -d ' ')" 2>/dev/null
  pkill -f "[s]rc.train.cli.*--out $run" 2>/dev/null
  sleep 3

  case "$status" in
    oom)
      echo "PROBE $size mb$micro ga$accum OOM peak_mib $peak" ;;
    done)
      local toks
      toks=$(python3 - "$run/loss.jsonl" "$SKIP_STEPS" "$micro" "$accum" <<'PYEOF'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
skip, micro, accum = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
window = [r for r in rows if r["step"] > skip]
a, b = window[0], window[-1]
tokens = (b["step"] - a["step"]) * micro * accum * 4096
print(round(tokens / (b["elapsed_s"] - a["elapsed_s"])))
PYEOF
      )
      echo "PROBE $size mb$micro ga$accum peak_mib $peak tok_s $toks" ;;
    *)
      echo "PROBE $size mb$micro ga$accum FAIL_$status peak_mib $peak (tail of stdout follows)"
      tail -5 "$run/stdout.log" 2>/dev/null | sed 's/^/    /' ;;
  esac
  # Keep config.yaml and logs for provenance, drop any stray checkpoint.
  rm -f "$run"/*.pt
  return 0
}

echo "$(stamp) probes start: $CANDIDATES"
for cand in $CANDIDATES; do
  IFS=: read -r size micro accum <<< "$cand"
  echo "$(stamp) probing $size micro $micro accum $accum"
  probe_one "$size" "$micro" "$accum"
done
echo "PROBES_DONE"
