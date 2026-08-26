#!/bin/bash
# Kill-test eval battery orchestrator. Run this detached once the six
# training runs have finished:
#
#   setsid nohup bash killtest/run_evals.sh \
#       > /home/ec2-user/logs/eval_battery.log 2>&1 < /dev/null &
#
# It resolves the highest numbered checkpoint in each run dir, splits
# the six evaluations across GPUs 6 and 7 (three each, sequential per
# GPU), merges the per-checkpoint JSONs, computes the verdict, uploads
# everything to S3, and prints BATTERY_DONE or BATTERY_FAIL.
set -uo pipefail

REPO=/home/ec2-user/decoupled-reasoner
PY=$REPO/.venv/bin/python
RUNS=/home/ec2-user/runs
OUT=${OUT:-/home/ec2-user/eval-out/killtest-final}
LOGS=/home/ec2-user/logs
TOKENIZER=/home/ec2-user/data/tokenizer_v2.json
HELDOUT=/home/ec2-user/data/regime_c/heldout.jsonl
S3DEST=s3://decoupled-reasoner-009398924577/runs/killtest/evals

RUNS_GPU6="$RUNS/killtest-a-101 $RUNS/killtest-a-102 $RUNS/killtest-c-201"
RUNS_GPU7="$RUNS/killtest-a-103 $RUNS/killtest-c-202 $RUNS/killtest-c-203"

fail() {
    echo "BATTERY_FAIL: $1"
    aws s3 sync "$OUT" "$S3DEST/" --no-progress >/dev/null 2>&1 || true
    exit 1
}

mkdir -p "$OUT" "$LOGS"
[ -x "$PY" ] || fail "missing venv python at $PY"
[ -f "$TOKENIZER" ] || fail "missing tokenizer at $TOKENIZER"
if [ ! -f "$HELDOUT" ]; then
    aws s3 cp s3://decoupled-reasoner-009398924577/data/regime_c/heldout.jsonl \
        "$HELDOUT" --no-progress || fail "heldout.jsonl download"
fi

cd "$REPO" || fail "cd $REPO"

# The trainers all target step 26700. Evaluate the six checkpoints at
# that common step when every run has it; otherwise fall back to each
# run's highest numbered checkpoint and say so in the log.
STEP=${STEP:-26700}
STEP_FILE=$(printf "ckpt-%07d.pt" "$STEP")
STEP_ARG="--step $STEP"
for d in $RUNS_GPU6 $RUNS_GPU7; do
    ck=$(ls "$d"/ckpt-*.pt 2>/dev/null | sort | tail -1)
    [ -n "$ck" ] || fail "no numbered checkpoint in $d"
    echo "highest checkpoint for $(basename "$d"): $ck"
    if [ ! -f "$d/$STEP_FILE" ]; then
        echo "WARNING: $d has no $STEP_FILE, falling back to per-run max"
        STEP_ARG=""
    fi
done
if [ -n "$STEP_ARG" ]; then
    echo "evaluating every run at common step $STEP"
else
    echo "evaluating each run at its own highest numbered checkpoint"
fi

COMMON="--tokenizer $TOKENIZER --heldout $HELDOUT --out $OUT --device cuda \
    --heldout-episodes 500 --noise-episodes 200 --max-rounds 6 \
    --skip-existing $STEP_ARG"

echo "launching GPU 6 group: $RUNS_GPU6"
CUDA_VISIBLE_DEVICES=6 $PY -m scripts.eval_battery \
    --checkpoints $RUNS_GPU6 $COMMON \
    > "$LOGS/eval_battery_gpu6.log" 2>&1 &
PID6=$!

echo "launching GPU 7 group: $RUNS_GPU7"
CUDA_VISIBLE_DEVICES=7 $PY -m scripts.eval_battery \
    --checkpoints $RUNS_GPU7 $COMMON \
    > "$LOGS/eval_battery_gpu7.log" 2>&1 &
PID7=$!

wait $PID6 || fail "GPU 6 group failed, see $LOGS/eval_battery_gpu6.log"
wait $PID7 || fail "GPU 7 group failed, see $LOGS/eval_battery_gpu7.log"

$PY -m scripts.eval_battery --combine --tokenizer "$TOKENIZER" \
    --heldout "$HELDOUT" --out "$OUT" || fail "combine step"

N_PARTS=$(ls "$OUT"/*.eval.json 2>/dev/null | wc -l)
[ "$N_PARTS" -eq 6 ] || fail "expected 6 per-checkpoint JSONs, found $N_PARTS"

$PY -m scripts.compute_verdict --results "$OUT/results.json" --out "$OUT" \
    || fail "compute_verdict"

aws s3 sync "$OUT" "$S3DEST/" --no-progress || fail "S3 upload"

echo "results and verdict uploaded to $S3DEST/"
echo BATTERY_DONE
