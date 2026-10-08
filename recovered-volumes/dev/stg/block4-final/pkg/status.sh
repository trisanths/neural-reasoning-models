#!/bin/bash
# One-screen status for the kill-test runs: per run the trainer liveness,
# last logged step and loss, tokens consumed, recent tok/s, and newest
# checkpoint; then per-GPU utilization and disk free. Uses only the system
# python (json is stdlib; the config is read with awk, not yaml).
set -u

RUNS_ROOT="${RUNS_ROOT:-/home/ec2-user/runs}"
PATTERN="${PATTERN:-killtest-}"
RL_PATTERN="${RL_PATTERN:-rl-}"

printf "%-22s %-6s %8s %8s %14s %9s  %s\n" \
  "RUN" "ALIVE" "STEP" "LOSS" "TOKENS" "TOK/S" "LAST_CKPT"

for dir in "$RUNS_ROOT/$PATTERN"*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  rundir=${dir%/}

  alive=no
  pgrep -f "[s]rc.train.cli.*--out $rundir " > /dev/null 2>&1 && alive=yes

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
  printf "%-22s %-6s %8s %8s %14s %9s  %s\n" \
    "$name" "$alive" "$step" "$loss" "$tokens" "$toks" "${ckpt:--}"
done

echo
printf "%-22s %-6s %8s %8s %8s %8s\n" "RL_RUN" "ALIVE" "STEP" "REWARD" "ACC" "ROUNDS"
for dir in "$RUNS_ROOT/$RL_PATTERN"*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  rundir=${dir%/}
  alive=no
  pgrep -f "[s]rc.rl.cli.*--out $rundir " > /dev/null 2>&1 && alive=yes
  read -r step reward acc rounds <<< "$(tail -n 1 "$rundir/rl.jsonl" 2>/dev/null | \
    python3 -c '
import json, sys
line = sys.stdin.readline().strip()
if not line:
    print("- - - -")
    raise SystemExit
r = json.loads(line)
print(r["step"], "{:.4f}".format(r["reward_mean"]), "{:.4f}".format(r["accuracy"]),
      "{:.2f}".format(r["mean_rounds"]))
')"
  printf "%-22s %-6s %8s %8s %8s %8s\n" "$name" "$alive" "$step" "$reward" "$acc" "$rounds"
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
