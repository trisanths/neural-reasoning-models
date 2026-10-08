#!/bin/bash
# One-screen status for the block runs: per run the trainer liveness, last
# logged step and loss, tokens consumed, recent tok/s, and newest checkpoint;
# then per-GPU utilization and disk free. Uses only the system python (json
# is stdlib; the config is read with awk, not yaml).
#
# Block 4 mixes two kinds of run under one curve- prefix. A pretraining lane
# has loss.jsonl and a model config, and its process is src.train.cli. An RL
# lane has rl.jsonl and no loss, and its process is src.rl.cli; for those the
# LOSS column carries held-out accuracy, TOKENS carries the rollout count, and
# TOK/S carries rollouts per second, which are the numbers that mean the same
# thing for an RL lane. The KIND column says which is which.
set -u

RUNS_ROOT="${RUNS_ROOT:-/home/ec2-user/runs}"
PATTERN="${PATTERN:-killtest-}"

printf "%-22s %-6s %-6s %8s %9s %14s %10s  %s\n" \
  "RUN" "KIND" "ALIVE" "STEP" "LOSS/ACC" "TOKENS/ROLL" "TOK|ROLL/S" "LAST_CKPT"

for dir in "$RUNS_ROOT/$PATTERN"*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  rundir=${dir%/}

  kind=train
  if [ -f "$rundir/rl.jsonl" ]; then
    kind=rl
  elif grep -q "src.rl.cli" "$rundir/cmd.txt" 2>/dev/null; then
    kind=rl
  fi

  alive=no
  if [ "$kind" = rl ]; then
    pgrep -f "[s]rc.rl.cli.*--out $rundir " > /dev/null 2>&1 && alive=yes
  else
    pgrep -f "[s]rc.train.cli.*--out $rundir " > /dev/null 2>&1 && alive=yes
  fi

  if [ "$kind" = rl ]; then
    read -r step acc rolls rps <<< "$(tail -n 2 "$rundir/rl.jsonl" 2>/dev/null | \
      python3 -c '
import json, sys
rows = [json.loads(l) for l in sys.stdin if l.strip()]
if not rows:
    print("- - - -")
    raise SystemExit
last = rows[-1]
step = int(last.get("step", 0))
width = int(last.get("n_rollouts", 0))
print(last.get("step", "-"),
      "{:.4f}".format(last.get("accuracy", float("nan"))),
      "{:,}".format(step * width),
      "{:,.2f}".format(last.get("rollouts_per_s", 0.0)))
')"
    ckpt=$(ls -t "$rundir"/rl-*.pt "$rundir"/final.pt 2>/dev/null | head -1)
    ckpt=${ckpt:+$(basename "$ckpt")}
    printf "%-22s %-6s %-6s %8s %9s %14s %10s  %s\n" \
      "$name" "$kind" "$alive" "$step" "$acc" "$rolls" "$rps" "${ckpt:--}"
    continue
  fi

  tps=$(awk '/^ *batch_size:/ {b=$2} /^ *grad_accum_steps:/ {g=$2} \
    /^ *max_seq_len:/ {s=$2} END {if (b && g && s) print b*g*s; else print 0}' \
    "$rundir/config.yaml" 2>/dev/null || echo 0)

  read -r step loss tokens toks <<< "$(tail -n 2 "$rundir/loss.jsonl" 2>/dev/null | \
    python3 -c '
import json, sys
rows = [json.loads(l) for l in sys.stdin if l.strip()]
tps = float(sys.argv[1])
if not rows:
    print("- - - -")
    raise SystemExit
last = rows[-1]
step = last["step"]
toks = "-"
if len(rows) == 2:
    ds = rows[1]["step"] - rows[0]["step"]
    de = rows[1]["elapsed_s"] - rows[0]["elapsed_s"]
    if ds > 0 and de > 0:
        toks = "{:,.0f}".format(ds * tps / de)
print(step, "{:.4f}".format(last["loss"]), "{:,}".format(int(step * tps)), toks)
' "$tps")"

  ckpt=$(ls -t "$rundir"/ckpt-*.pt 2>/dev/null | head -1)
  ckpt=${ckpt:+$(basename "$ckpt")}
  printf "%-22s %-6s %-6s %8s %9s %14s %10s  %s\n" \
    "$name" "$kind" "$alive" "$step" "$loss" "$tokens" "$toks" "${ckpt:--}"
done

echo
if command -v nvidia-smi > /dev/null 2>&1; then
  echo "GPU  UTIL  MEM_USED / MEM_TOTAL"
  nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total \
    --format=csv,noheader,nounits | \
    awk -F', ' '{printf "%-4s %3s%%  %6s MiB / %6s MiB\n", $1, $2, $3, $4}'
else
  echo "nvidia-smi not available"
fi

echo
df -h "$RUNS_ROOT" /home/ec2-user/data/ 2>/dev/null | awk '!seen[$0]++'
