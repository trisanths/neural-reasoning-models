#!/bin/bash
# Train and score one rung of the ladder at full sweep settings.
# usage: cd_pipeline.sh GPU ARM DEPTHSPEC
# The whole body is a function so that an edit to this file while an instance
# is running cannot make the running shell resume at a shifted byte offset.
main() {
  set -u
  local GPU="$1" ARM="$2" DEPTHS="$3"
  local REP="${ARM#ladder_}"
  cd /home/ec2-user/opg || exit 1
  export PYTHONPATH=/home/ec2-user/opg
  export CUDA_VISIBLE_DEVICES="$GPU"
  mkdir -p runs/cd results/cd logs/cd
  local CKPT="runs/cd/${ARM}.pt"

  echo "[$(date -u +%H:%M:%S)] rung=$REP gpu=$GPU start"

  if [ ! -s "$CKPT" ]; then
    uv run python scripts/opgraph_train.py \
      --base ckpt/base350.pt \
      --tokenizer /home/ec2-user/data/tokenizer_v2.json \
      --arm "$ARM" --out "$CKPT" \
      --steps 8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000 \
      2>&1 | tail -40
    echo "[$(date -u +%H:%M:%S)] train exit=$? ckpt=$(ls -l $CKPT 2>/dev/null | awk '{print $5}')"
  else
    echo "[$(date -u +%H:%M:%S)] checkpoint already on disk, skipping training"
  fi
  [ -s "$CKPT" ] || { echo "[FATAL] no checkpoint"; return 1; }

  for T in 0.0 0.8; do
    local TAG=greedy
    [ "$T" = "0.8" ] && TAG=sampled
    echo "[$(date -u +%H:%M:%S)] eval $REP $TAG start"
    uv run python scripts/cd_eval.py \
      --ckpt "$CKPT" \
      --tokenizer /home/ec2-user/data/tokenizer_v2.json \
      --out "results/cd/${REP}_${TAG}.json" \
      --n 150 --batch-size 48 --temperature "$T" --max-new 320 \
      --depths "$DEPTHS" \
      --conditions plan_execute,oracle_plan,oracle_ops,oracle_both \
      --para-conditions plan_execute,oracle_plan,oracle_both
    echo "[$(date -u +%H:%M:%S)] eval $REP $TAG exit=$?"
  done
  echo "[$(date -u +%H:%M:%S)] rung=$REP done"
}
main "$@"
