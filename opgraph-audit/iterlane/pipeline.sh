#!/bin/bash
# Everything left for the P3 and P4 lane, run detached so SSM latency does not
# gate it. Each stage writes a line to iterlane/PROGRESS so one cheap poll shows
# where it is.
set -u
cd /home/ec2-user/opg
export PYTHONPATH=/home/ec2-user/opg
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY="uv run python"
TOK=/home/ec2-user/data/tokenizer_v2.json
P=iterlane/PROGRESS
say() { echo "$(date +%H:%M:%S) $*" >> $P; }

# A card with enough free memory and not already saturated. Never kill anything,
# never crowd: if no card qualifies, wait.
pick_gpu() {
  need=$1
  for _ in $(seq 1 240); do
    best=""; bestfree=0
    while IFS=, read -r idx used total util; do
      idx=$(echo $idx | tr -d ' '); used=$(echo $used | tr -d ' MiB'); total=$(echo $total | tr -d ' MiB')
      free=$(( total - used ))
      if [ $free -gt $bestfree ]; then bestfree=$free; best=$idx; fi
    done < <(nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits)
    if [ $bestfree -ge $need ]; then echo $best; return 0; fi
    sleep 30
  done
  echo ""; return 1
}

wait_for() { while [ ! -f "$1" ]; do sleep 30; done; sleep 20; }

say "pipeline start"
wait_for runs/iter/p3.pt
say "p3 checkpoint present"
wait_for runs/iter/p4.pt
say "p4 checkpoint present"

# ---- stage 1: the main grid, both wordings, both temperatures
for H in p3 p4; do
  OUT=results/iter/main_${H}.json
  [ -f "$OUT" ] && { say "skip main $H"; continue; }
  G=$(pick_gpu 20000); say "main $H on gpu $G"
  CUDA_VISIBLE_DEVICES=$G $PY iterlane/eval_iter.py \
    --ckpt runs/iter/${H}.pt --tokenizer $TOK --out $OUT \
    --n 150 --batch-size 24 --gen-batch-size 96 \
    --styles 0,1 --iters 8 --temperatures 0.0,0.8 \
    --conditions plan_execute,oracle_ops,oracle_plan \
    --record-revisions --verify-counter > logs/iter/main_${H}.log 2>&1
  say "main $H rc=$?"
done

# ---- stage 2: accuracy against refinement budget, with the trajectory kept
for H in p3 p4; do
  OUT=results/iter/iters_${H}.json
  [ -f "$OUT" ] && { say "skip iters $H"; continue; }
  G=$(pick_gpu 20000); say "iters $H on gpu $G"
  CUDA_VISIBLE_DEVICES=$G $PY iterlane/eval_iter.py \
    --ckpt runs/iter/${H}.pt --tokenizer $TOK --out $OUT \
    --n 150 --batch-size 24 --gen-batch-size 96 \
    --kinds sequential --depths 1,2,3,4,6,8,12 --styles 0 \
    --iters 1,2,4,8,16,32 --temperatures 0.0,0.8 \
    --conditions plan_execute --skip-gold --record-revisions \
    > logs/iter/iters_${H}.log 2>&1
  say "iters $H rc=$?"
done

# ---- stage 3: the rest of the convergence series
for H in p3 p4; do
  G=$(pick_gpu 20000); say "conv $H on gpu $G"
  bash iterlane/conv.sh $G $H >> logs/iter/conv_${H}.log 2>&1
  say "conv $H rc=$?"
done

# ---- stage 4: does the head read its own array, and per field accuracy
for H in p3 p4; do
  G=$(pick_gpu 15000); say "probe $H on gpu $G"
  CUDA_VISIBLE_DEVICES=$G $PY scripts/planheads_condprobe.py \
    --ckpt runs/iter/${H}.pt --tokenizer $TOK \
    --out results/iter/cond_${H}.json --n 48 --depths 1,2,3,4,6,8,12 \
    > logs/iter/cond_${H}.log 2>&1
  say "cond $H rc=$?"
  CUDA_VISIBLE_DEVICES=$G $PY scripts/planheads_slotdiag.py \
    --ckpt runs/iter/${H}.pt --tokenizer $TOK \
    --out results/iter/slotdiag_${H}.json --n 48 \
    > logs/iter/slotdiag_${H}.log 2>&1
  say "slotdiag $H rc=$?"
done

say "core done"

# ---- stage 5, secondary: the widened schema, which is the only way to reach
# depth 16 and 32 at all. Waits for a genuinely free card rather than crowding.
for H in p3 p4; do
  CK=runs/iter/${H}w.pt
  [ -f "$CK" ] && continue
  G=$(pick_gpu 45000); say "wide train $H on gpu $G"
  [ -z "$G" ] && { say "wide train $H skipped, no free card"; continue; }
  CUDA_VISIBLE_DEVICES=$G $PY iterlane/train_wide.py \
    --base ckpt/base350.pt --tokenizer $TOK --head $H --out $CK \
    --steps 16000 --batch-size 32 --worlds 40000 --log-every 500 \
    > logs/iter/${H}w.log 2>&1
  say "wide train $H rc=$?"
done
for H in p3 p4; do
  OUT=results/iter/wide_${H}.json
  [ -f "$OUT" ] && continue
  [ -f runs/iter/${H}w.pt ] || continue
  G=$(pick_gpu 25000); say "wide eval $H on gpu $G"
  CUDA_VISIBLE_DEVICES=$G $PY iterlane/eval_iter.py \
    --ckpt runs/iter/${H}w.pt --tokenizer $TOK --out $OUT --wide \
    --n 150 --batch-size 24 --gen-batch-size 96 \
    --styles 0,1 --iters 8 --temperatures 0.0,0.8 \
    --conditions plan_execute,oracle_ops,oracle_plan \
    --record-revisions --verify-counter > logs/iter/wide_${H}.log 2>&1
  say "wide eval $H rc=$?"
done
say "ALL DONE"
