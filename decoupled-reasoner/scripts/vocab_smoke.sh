#!/bin/bash
# Train and score every rung of the plan-representation ladder at tiny scale.
#
#   bash scripts/vocab_smoke.sh <gpu>
#
# The point is not a number anyone should believe. It is that each rung trains,
# writes a plan the executor accepts, and returns oracle_both at 1.000, which is
# the check that the representation is lossless. Everything is matched across
# the rungs: same base checkpoint, same worlds and seeds, same optimizer steps,
# same batch size in sequences, same held out sets. Only the plan changes.
set -u
GPU=${1:-5}
ROOT=/home/ec2-user/opg
cd "$ROOT" || exit 1
mkdir -p runs/ladder logs/ladder results/ladder

STEPS=${STEPS:-600}
BS=${BS:-16}
WORLDS=${WORLDS:-4000}
N=${N:-8}
KINDS=${KINDS:-sequential,breadth,novel,units}
MAXNEW=${MAXNEW:-320}
COMMON="--base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
--steps $STEPS --batch-size $BS --lr 2e-5 --warmup 50 --worlds $WORLDS --log-every 100"

for rep in ${REPS:-english symbolic opcode typed goalstack slots}; do
  arm=ladder_$rep
  ckpt=$ROOT/runs/ladder/$arm.pt
  if [ "${TRAIN:-1}" = "1" ]; then
    echo "[train] $arm gpu=$GPU $(date -Is)"
    PYTHONPATH=$ROOT CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/opgraph_train.py \
      $COMMON --arm "$arm" --out "$ckpt" > "logs/ladder/$arm.train.log" 2>&1
    echo "[train] $arm status=$? $(date -Is)"
  else
    echo "[train] $arm skipped, scoring the checkpoint already on disk $(date -Is)"
  fi
  for temp in 0.0 0.8; do
    tag=$( [ "$temp" = "0.0" ] && echo greedy || echo sampled )
    echo "[eval] $arm $tag $(date -Is)"
    PYTHONPATH=$ROOT CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/vocab_eval.py \
      --ckpt "$ckpt" --tokenizer /home/ec2-user/data/tokenizer_v2.json \
      --out "$ROOT/results/ladder/smoke_${rep}_${tag}.json" --n $N \
      --batch-size 16 --slot-batch-size 8 --kinds "$KINDS" --styles 0,1 \
      --max-new $MAXNEW \
      --temperature $temp > "logs/ladder/$arm.eval.$tag.log" 2>&1
    echo "[eval] $arm $tag status=$? $(date -Is)"
  done
done
echo "[smoke] done $(date -Is)"
