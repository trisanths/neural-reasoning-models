#!/bin/bash
# Two side lanes for the P3/P4 report.
#
# lane wide  the widened array, 32 plan nodes. The shipped codec raises on a
#            plan of 13 steps, so this is the only way the depth 16 and depth 32
#            question can be asked of a slot head at all. It is a separate arm,
#            not a matched one: the slot count changes.
# lane ref   P1 and P2s trained on the same trainer, the same steps, the same
#            seeds. Without them "the plateau is higher" has nothing to be
#            higher than: the P1 numbers in the brief come from a different
#            training run.
set -u
cd /home/ec2-user/opg
export PYTHONPATH=/home/ec2-user/opg
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY="uv run python"
TOK=/home/ec2-user/data/tokenizer_v2.json
P=iterlane/PROGRESS
say() { echo "$(date +%H:%M:%S) [$LANE] $*" >> $P; }
pick_gpu() {
  need=$1
  for _ in $(seq 1 400); do
    best=""; bestfree=0
    while IFS=, read -r idx used total util; do
      idx=$(echo $idx | tr -d ' '); used=$(echo $used | tr -d ' '); total=$(echo $total | tr -d ' ')
      free=$(( total - used ))
      if [ $free -gt $bestfree ]; then bestfree=$free; best=$idx; fi
    done < <(nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits)
    if [ $bestfree -ge $need ]; then echo $best; return 0; fi
    sleep 30
  done
  echo ""; return 1
}

LANE=$1
if [ "$LANE" = wide ]; then
  for H in p3 p4; do
    CK=runs/iter/${H}w.pt
    if [ ! -f "$CK" ]; then
      G=$(pick_gpu 46000)
      if [ -z "$G" ]; then say "train $H skipped, no card with 46G free"; continue; fi
      say "train ${H}w on gpu $G"
      CUDA_VISIBLE_DEVICES=$G $PY iterlane/train_wide.py \
        --base ckpt/base350.pt --tokenizer $TOK --head $H --out $CK \
        --steps 16000 --batch-size 32 --worlds 40000 --log-every 500 \
        > logs/iter/${H}w.log 2>&1
      say "train ${H}w rc=$?"
    fi
    OUT=results/iter/wide_${H}.json
    [ -f "$OUT" ] && continue
    [ -f "$CK" ] || continue
    G=$(pick_gpu 25000); say "eval ${H}w on gpu $G"
    CUDA_VISIBLE_DEVICES=$G $PY iterlane/eval_iter.py \
      --ckpt $CK --tokenizer $TOK --out $OUT --wide \
      --n 150 --batch-size 24 --gen-batch-size 96 \
      --styles 0,1 --iters 8 --temperatures 0.0,0.8 \
      --conditions plan_execute,oracle_ops,oracle_plan \
      --record-revisions --verify-counter > logs/iter/wide_${H}.log 2>&1
    say "eval ${H}w rc=$?"
  done
  say "WIDE DONE"
fi

if [ "$LANE" = ref ]; then
  # how peaked the policy is, which is why sampling reproduces greedy
  for H in p3 p4; do
    OUT=results/iter/peaked_${H}.json
    [ -f "$OUT" ] && continue
    G=$(pick_gpu 15000); say "peaked $H on gpu $G"
    CUDA_VISIBLE_DEVICES=$G $PY iterlane/peaked.py \
      --ckpt runs/iter/${H}.pt --tokenizer $TOK --out $OUT --n 32 \
      --depths 1,2,3,4,6,8,12 > logs/iter/peaked_${H}.log 2>&1
    say "peaked $H rc=$?"
  done
  for H in p1 p2s; do
    CK=runs/iter/${H}.pt
    if [ ! -f "$CK" ]; then
      G=$(pick_gpu 30000); say "train $H on gpu $G"
      CUDA_VISIBLE_DEVICES=$G $PY iterlane/train_iter.py \
        --base ckpt/base350.pt --tokenizer $TOK --head $H --out $CK \
        --steps 16000 --batch-size 32 --worlds 40000 --log-every 500 \
        > logs/iter/${H}.log 2>&1
      say "train $H rc=$?"
    fi
    OUT=results/iter/main_${H}.json
    [ -f "$OUT" ] && continue
    [ -f "$CK" ] || continue
    G=$(pick_gpu 20000); say "eval $H on gpu $G"
    if [ "$H" = p2s ]; then
      # 97 stack invocations per plan, so this arm is scored on the sequential
      # grid at one temperature rather than on the whole grid
      CUDA_VISIBLE_DEVICES=$G $PY iterlane/eval_iter.py \
        --ckpt $CK --tokenizer $TOK --out $OUT \
        --n 150 --batch-size 24 --gen-batch-size 96 --kinds sequential \
        --styles 0 --temperatures 0.0 \
        --conditions plan_execute,oracle_ops,oracle_plan \
        --verify-counter > logs/iter/main_${H}.log 2>&1
    else
      CUDA_VISIBLE_DEVICES=$G $PY iterlane/eval_iter.py \
        --ckpt $CK --tokenizer $TOK --out $OUT \
        --n 150 --batch-size 24 --gen-batch-size 96 \
        --styles 0,1 --temperatures 0.0,0.8 \
        --conditions plan_execute,oracle_ops,oracle_plan \
        --verify-counter > logs/iter/main_${H}.log 2>&1
    fi
    say "eval $H rc=$?"
  done
  say "REF DONE"
fi
