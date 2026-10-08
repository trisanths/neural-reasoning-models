#!/bin/bash
# Train the two repaired scheduler arms, then run the authoritative evaluation.
#
# The first evaluation pass, results/opgraph_notrace.json, was run against a
# scheduler that was shown only symbols and arities. It localised the failure
# to the scheduler, and it showed that the scheduler was being asked to decide
# associativity it had never been told. Two repairs follow from that, and both
# are trained here from the same base checkpoint on the same budget:
#
#   opgraph2      the operator object carries the associativity its page states
#   opgraph_step  the same, and the plan is asked for one step at a time
#
# Everything then meets the same eval items in one run.
set -u
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
export PYTHONPATH=$ROOT
mkdir -p results logs
GPU=${1:-5}
COMMON="--base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
--steps 8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000 --log-every 400"

wait_for () {  # wait_for <file>
  while [ ! -f "$1" ]; do sleep 30; done
}

idle_trainer () {
  while pgrep -f "python3 scripts/opgraph_train.py" > /dev/null; do sleep 20; done
}

echo "[finish] waiting for the trace checkpoint $(date -Is)"
wait_for runs/trace.pt
idle_trainer
echo "[finish] trace ready and the gpu is free $(date -Is)"

if [ ! -f runs/opgraph2.pt ]; then
  echo "[finish] training opgraph2 $(date -Is)"
  CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/opgraph_train.py $COMMON \
    --arm opgraph --out "$ROOT/runs/opgraph2.pt" > logs/opgraph2.log 2>&1
  echo "[finish] opgraph2 status=$? $(date -Is)"
fi

if [ ! -f runs/opgraph_step.pt ]; then
  echo "[finish] training opgraph_step $(date -Is)"
  CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/opgraph_train.py $COMMON \
    --arm opgraph_step --out "$ROOT/runs/opgraph_step.pt" > logs/opgraph_step.log 2>&1
  echo "[finish] opgraph_step status=$? $(date -Is)"
fi

echo "[finish] waiting for any evaluation still holding a gpu $(date -Is)"
while pgrep -f "python3 scripts/opgraph_eval.py" > /dev/null; do sleep 30; done

# Split the grid over two gpus. The halves share nothing, so merging their
# result files is a plain dictionary union.
run_half () {  # run_half <gpu> <tag> <kinds>
  CUDA_VISIBLE_DEVICES=$1 uv run python scripts/opgraph_eval.py \
    --direct-ckpt runs/direct.pt \
    --trace-ckpt runs/trace.pt \
    --opgraph-ckpt runs/opgraph2.pt \
    --step-ckpt runs/opgraph_step.pt \
    --tokenizer /home/ec2-user/data/tokenizer_v2.json \
    --kinds "$3" --out "results/opgraph_$2.json" --n 150 --batch-size 32 \
    > "logs/eval_$2.log" 2>&1
  echo "[finish] half $2 status=$? $(date -Is)"
}

echo "[finish] full evaluation, split over two gpus $(date -Is)"
run_half 5 a sequential,sequential_paren,units &
run_half 7 b breadth,novel,same_page_pair &
wait
echo "[finish] both halves back $(date -Is)"

uv run python scripts/opgraph_report.py \
  --results results/opgraph_a.json,results/opgraph_b.json \
  --out results/opgraph_summary.json > results/opgraph_report.txt 2>&1
uv run python scripts/opgraph_report.py --results results/opgraph_notrace.json \
  --out results/opgraph_pass1_summary.json > results/opgraph_pass1_report.txt 2>&1
bash scripts/opgraph_ship.sh
echo "[finish] done $(date -Is)"
