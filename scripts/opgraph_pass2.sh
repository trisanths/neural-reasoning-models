#!/bin/bash
# Pass two: the two repaired scheduler arms, then the authoritative evaluation.
#
# Pass one localised the failure to the scheduler and showed it was being asked
# to decide an associativity it had never been told. Two repairs follow, both
# trained from the same base checkpoint on the same budget as every other arm:
#
#   opgraph2      the operator object carries the associativity its page states
#   opgraph_step  the same, and the plan is asked for one step at a time
#
# opgraph2 is already trained. This script trains opgraph_step, waits for any
# evaluation still holding a gpu, then runs the grid split over two gpus and
# writes the report. Every step is skipped if its output already exists, so
# the script is safe to rerun after a dropped connection.
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
export PYTHONPATH=$ROOT
mkdir -p results logs
GA=${1:-5}
GB=${2:-7}
COMMON="--base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
--steps 8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000 --log-every 400"

# pgrep patterns match the interpreter the venv actually runs, never this script.
trainer_busy () { pgrep -f "bin/python3 scripts/opgraph_train.py" > /dev/null; }
eval_busy ()    { pgrep -f "bin/python3 scripts/opgraph_eval.py"  > /dev/null; }

if [ ! -f runs/opgraph_step.pt ]; then
  echo "[pass2] training opgraph_step on gpu $GA $(date -Is)"
  CUDA_VISIBLE_DEVICES=$GA uv run python scripts/opgraph_train.py $COMMON \
    --arm opgraph_step --out "$ROOT/runs/opgraph_step.pt" > logs/opgraph_step.log 2>&1
  echo "[pass2] opgraph_step status=$? $(date -Is)"
fi

echo "[pass2] waiting for the pass one evaluation to release its gpu $(date -Is)"
while eval_busy; do sleep 30; done
while trainer_busy; do sleep 30; done
echo "[pass2] gpus free $(date -Is)"

# The halves share no cell, so merging their result files is a dictionary union.
run_half () {  # run_half <gpu> <tag> <kinds>
  CUDA_VISIBLE_DEVICES=$1 uv run python scripts/opgraph_eval.py \
    --direct-ckpt runs/direct.pt \
    --trace-ckpt runs/trace.pt \
    --opgraph-ckpt runs/opgraph2.pt \
    --step-ckpt runs/opgraph_step.pt \
    --base-ckpt ckpt/base350.pt \
    --tokenizer /home/ec2-user/data/tokenizer_v2.json \
    --kinds "$3" --out "results/opgraph_$2.json" --n 150 --batch-size 32 \
    > "logs/eval_$2.log" 2>&1
  echo "[pass2] half $2 status=$? $(date -Is)"
}

echo "[pass2] evaluation, split over gpu $GA and gpu $GB $(date -Is)"
[ -f results/opgraph_a.json ] || run_half "$GA" a sequential,sequential_paren,units &
[ -f results/opgraph_b.json ] || run_half "$GB" b breadth,novel,same_page_pair &
wait
echo "[pass2] both halves back $(date -Is)"

uv run python scripts/opgraph_report.py \
  --results results/opgraph_a.json,results/opgraph_b.json \
  --out results/opgraph_summary.json > results/opgraph_report.txt 2>&1
uv run python scripts/opgraph_report.py --results results/opgraph_notrace.json \
  --out results/opgraph_pass1_summary.json > results/opgraph_pass1_report.txt 2>&1
if [ -f results/opgraph.json ]; then
  uv run python scripts/opgraph_report.py --results results/opgraph.json \
    --out results/opgraph_trace_summary.json > results/opgraph_trace_report.txt 2>&1
fi
bash scripts/opgraph_ship.sh
echo "[pass2] done $(date -Is)"
