#!/bin/bash
# One evaluation worker, pinned to one GPU, taking arms from a shared claim
# directory. It never signals another process; it waits for its own GPU to go
# quiet before starting anything.
#   bash scripts/ceiling_pipeline.sh <gpu> <fast|full>
set -u
R=/home/ec2-user/opg
cd "$R" || exit 1
GPU=$1; PHASE=$2
ARMS="d1s1 d2s1 d3s1 d4s1 d6s1 d8s1 d3s2 d3s3"
mkdir -p "$R/claims" "$R/results/ceiling" "$R/logs/ceiling"

case "$PHASE" in
  fast) N=50; STYLES=0; TEMPS=0.0; KINDS=sequential,novel,breadth
        DEPTHS="sequential=1,2,3,4,5,6,7,8,12,16,32;novel=2,3,4,5,6,8,12,16;breadth=1,2,3,4,5,6" ;;
  full) N=100; STYLES=0,1; TEMPS=0.0,0.8
        KINDS=sequential,sequential_paren,breadth,novel,same_page_pair,units
        DEPTHS="sequential=1,2,3,4,5,6,7,8,12,16,32;novel=2,3,4,5,6,8,12,16,32" ;;
  *) echo "phase must be fast or full"; exit 2 ;;
esac

ready () {
  [ -f "$R/runs/ceiling/$1.pt" ] || return 1
  pgrep -f "ceiling_train.py .*/$1.pt" >/dev/null && return 1
  return 0
}
wait_gpu () {
  for _ in $(seq 1 480); do
    U=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits -i "$GPU")
    M=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU")
    if [ "$U" -lt 35 ] && [ "$M" -lt 8000 ]; then return 0; fi
    sleep 30
  done
  return 1
}

while true; do
  wait_gpu || { echo "[$PHASE gpu=$GPU] gpu never freed"; exit 1; }
  TOOK=""
  for NAME in $ARMS; do
    [ -f "$R/results/ceiling/${PHASE}_$NAME.json" ] && continue
    ready "$NAME" || continue
    mkdir "$R/claims/${PHASE}_$NAME" 2>/dev/null || continue
    TOOK=$NAME
    echo "[eval $PHASE] $NAME gpu=$GPU $(date -Is)"
    PYTHONPATH=$R CUDA_VISIBLE_DEVICES=$GPU $R/.venv/bin/python \
      scripts/ceiling_eval.py --ckpt "$R/runs/ceiling/$NAME.pt" \
      --tokenizer /home/ec2-user/data/tokenizer_v2.json --arm "$NAME" \
      --out "$R/results/ceiling/${PHASE}_$NAME.json" \
      --records "$R/results/ceiling/${PHASE}_$NAME.records.jsonl" \
      --n "$N" --batch-size 64 --styles "$STYLES" --temperatures "$TEMPS" \
      --kinds "$KINDS" --depths "$DEPTHS" \
      > "$R/logs/ceiling/eval_${PHASE}_$NAME.log" 2>&1
    echo "[done $PHASE] $NAME status=$? $(date -Is)"
    break
  done
  LEFT=0
  for NAME in $ARMS; do
    [ -f "$R/results/ceiling/${PHASE}_$NAME.json" ] || LEFT=1
  done
  [ "$LEFT" = "0" ] && break
  [ -z "$TOOK" ] && sleep 45
done
echo "[pipeline $PHASE gpu=$GPU] finished $(date -Is)"
