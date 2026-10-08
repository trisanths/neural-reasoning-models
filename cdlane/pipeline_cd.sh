#!/bin/bash
# Train and score ladder rungs C (opcode) and D (typed), end to end.
#
# Safe to fire more than once: it takes a lock and exits if an instance is
# already alive, and it skips a stage whose output is already on disk. The SSM
# queue on this box has re-delivered commands before, so a second copy of this
# arriving is expected rather than exceptional.
#
# It never places work on a card that is short of memory. An OOM here would
# land on somebody else's run, so it waits for a card instead of squeezing onto
# a busy one.
set -u
cd /home/ec2-user/opg || exit 1
export PYTHONPATH=/home/ec2-user/opg
PY=/home/ec2-user/opg/.venv/bin/python3
TOK=/home/ec2-user/data/tokenizer_v2.json
R=/home/ec2-user/opg/runs/ladder_cd
O=/home/ec2-user/opg/results/ladder_cd
L=/home/ec2-user/opg/logs/ladder_cd
mkdir -p "$R" "$O" "$L" /home/ec2-user/opg/cdlane

LOCK=/home/ec2-user/opg/cdlane/.pipeline.lock
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -f "$LOCK/pid" ] && kill -0 "$(cat "$LOCK/pid")" 2>/dev/null; then
    echo "pipeline already running as pid $(cat "$LOCK/pid"); exiting"
    exit 0
  fi
  echo "stale lock, taking it over"
fi
echo $$ > "$LOCK/pid"

STEPS=8000
BS=32
WORLDS=40000
NEVAL=150
EBS=96
GRID="sequential=1,2,3,4,5,6,7,8,10,12,14,16,20,24,32;novel=2,3,4,5,6,8,12,16,24,32;breadth=1,2,3,4,5,6;sequential_paren=2,3,4,5,6"
MINFREE=42000

say () { echo "[$(date -u +%FT%TZ)] $*"; }

# Index of a card with at least $1 MiB free, preferring the least utilised.
# Empty when there is none, which is the signal to wait rather than crowd.
pick () {
  nvidia-smi --query-gpu=index,utilization.gpu,memory.total,memory.used \
    --format=csv,noheader,nounits \
  | awk -F', ' -v need="$1" '{free=$3-$4; if (free>=need) print $2, -free, $1}' \
  | sort -k1,1n -k2,2n | head -1 | awk '{print $3}'
}

wait_for_gpu () {
  local need="$1" label="$2" g=""
  for i in $(seq 1 240); do
    g=$(pick "$need")
    if [ -n "$g" ]; then echo "$g"; return 0; fi
    say "no card with ${need}MiB free for $label, waiting (attempt $i)" >&2
    sleep 60
  done
  return 1
}

free_on () {
  nvidia-smi --query-gpu=memory.total,memory.used --format=csv,noheader,nounits \
    -i "$1" | awk -F', ' '{print $1-$2}'
}

# ------------------------------------------------------------------ training

train () {
  local arm="$1" gpu="$2"
  if [ -f "$R/ladder_$arm.pt" ]; then
    say "$arm checkpoint already on disk, skipping training"; return 0
  fi
  say "$arm training on gpu $gpu"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" scripts/opgraph_train.py \
    --base ckpt/base350.pt --tokenizer "$TOK" \
    --arm "ladder_$arm" --out "$R/ladder_$arm.pt" \
    --steps $STEPS --batch-size $BS --lr 2e-5 --warmup 200 --worlds $WORLDS \
    > "$L/train_$arm.log" 2>&1
  say "$arm training exit $?"
}

# A two item pass over a checkpoint that already exists, to find a bug in the
# scoring script in one minute rather than after several hours of training.
preflight () {
  local ck
  ck=$(ls -1 /home/ec2-user/opg/runs/ladder/ladder_opcode.pt \
             /home/ec2-user/opg/runs/ladder/ladder_typed.pt \
             /home/ec2-user/opg/runs/ladder/*.pt 2>/dev/null | head -1)
  if [ -z "$ck" ]; then say "no checkpoint to preflight against, skipping"; return 0; fi
  local g
  g=$(pick 20000)
  if [ -z "$g" ]; then say "no card free for preflight, skipping"; return 0; fi
  say "preflight on $ck, gpu $g"
  CUDA_VISIBLE_DEVICES="$g" "$PY" /home/ec2-user/opg/cdlane/eval_cd.py \
    --ckpt "$ck" --tokenizer "$TOK" --out "$O/preflight.json" \
    --n 2 --batch-size 4 --styles 0,1 --temperature 0.0 --para-oracles 1 \
    --depths "sequential=2,16,20;novel=3;breadth=2" \
    > "$L/preflight.log" 2>&1
  local rc=$?
  say "preflight exit $rc"
  if [ $rc -ne 0 ] && [ $rc -ne 2 ]; then
    say "PREFLIGHT FAILED, not starting training"; tail -30 "$L/preflight.log"
    return 1
  fi
  return 0
}
preflight || { rmdir "$LOCK" 2>/dev/null; exit 1; }

GC=$(wait_for_gpu $MINFREE opcode) || { say "gave up waiting for a card"; exit 1; }
train opcode "$GC" &
PC=$!
sleep 420

if [ "$(free_on "$GC")" -ge $MINFREE ]; then
  GD="$GC"
  say "gpu $GC still has $(free_on "$GC") MiB free, typed joins it there"
else
  GD=$(wait_for_gpu $MINFREE typed) || { say "gave up waiting for a card"; exit 1; }
fi
train typed "$GD" &
PD=$!

wait $PC; say "opcode stage done"
wait $PD; say "typed stage done"

# -------------------------------------------------------------------- eval

evalone () {
  local arm="$1" gpu="$2" temp="$3" tag="$4"
  local out="$O/${arm}_${tag}.json"
  if [ -f "$out" ]; then say "$out exists, skipping"; return 0; fi
  if [ ! -f "$R/ladder_$arm.pt" ]; then
    say "no checkpoint for $arm, cannot evaluate"; return 1
  fi
  say "eval $arm $tag on gpu $gpu"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" /home/ec2-user/opg/cdlane/eval_cd.py \
    --ckpt "$R/ladder_$arm.pt" --tokenizer "$TOK" --out "$out" \
    --n $NEVAL --batch-size $EBS --depths "$GRID" --styles 0,1 \
    --temperature "$temp" --para-oracles 1 \
    > "$L/eval_${arm}_${tag}.log" 2>&1
  say "eval $arm $tag exit $?"
}

GE1=$(wait_for_gpu $MINFREE eval-opcode) || exit 1
( evalone opcode "$GE1" 0.0 greedy; evalone opcode "$GE1" 0.8 sampled ) &
E1=$!
sleep 120
GE2=$(wait_for_gpu $MINFREE eval-typed) || GE2="$GE1"
( evalone typed "$GE2" 0.0 greedy; evalone typed "$GE2" 0.8 sampled ) &
E2=$!
wait $E1; wait $E2

# ------------------------------------------------------------------ report

say "report"
"$PY" /home/ec2-user/opg/cdlane/report_cd.py \
  --glob "$O/*.json" --out "$O/REPORT_CD.txt" --summary "$O/summary_cd.json" \
  > "$L/report.log" 2>&1
say "report exit $?"
say "PIPELINE COMPLETE"
rmdir "$LOCK" 2>/dev/null || rm -rf "$LOCK"
