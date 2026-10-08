#!/bin/bash
# Cells the first pass did not cover: R = 0 for both latent conditions, and the
# compute matched control on relational breadth. Own lane, own card, resumable.
set -u
cd /home/ec2-user/opg
export PYTHONPATH=$PWD
mkdir -p logs results/latent
TOK=/home/ec2-user/data/tokenizer_v2.json
G=$(uv run python src/latent/pick_gpu.py --need 14 --count 1 --wait 3600 --poll 60) || exit 1
echo "[extra] gpu $G"
export CUDA_VISIBLE_DEVICES=$G
run () {
  local job=$1; shift
  [ -f "results/latent/$job.done" ] && { echo "skip $job"; return 0; }
  echo "=== $job $(date -u +%FT%TZ)"
  uv run python "$@" && touch "results/latent/$job.done"
}
for S in 0 1; do
  run e_r0_s$S -m src.latent.eval --ckpt runs/latent/esweep.pt --tokenizer $TOK \
    --out results/latent/e_r0_s$S.json --r 0 --depths 1,2,3,4,5,6,8,12,16,32 \
    --breadths 1,2,3,4,5,6 --novel-depths 2,3,4,5,6 \
    --kinds sequential,breadth,novel --n 64 --samples 2 --batch-size 32 --style $S
  run mb_direct_s$S -m src.latent.matched --ckpt runs/direct.pt --arm direct \
    --tokenizer $TOK --out results/latent/mb_direct_s$S.json \
    --budgets 0,1,2,4,8,16,32,64 --breadths 1,2,3,4,5,6 --kinds breadth \
    --n 64 --style $S --batch-size 24
  run mb_opgraph_s$S -m src.latent.matched --ckpt runs/opgraph2.pt --arm opgraph \
    --tokenizer $TOK --out results/latent/mb_opgraph_s$S.json \
    --budgets 0,1,2,4,8,16,32,64 --breadths 1,2,3,4,5,6 --kinds breadth \
    --n 64 --style $S --batch-size 24
done
run verify_stream -m src.latent.verify --worlds 40000 --match-worlds 2000 \
  --out results/latent/verify.json
echo "[extra] finished $(date -u +%FT%TZ)"
