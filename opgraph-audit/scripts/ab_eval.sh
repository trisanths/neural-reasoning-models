#!/bin/bash
# Score one rung of the ladder over the whole grid, then over the deep
# sequential tail.
#
# Two budgets, because the two grids need different ones. The main grid is run
# at 320, the number the shared harness uses, so a cell here is directly
# comparable to the record. The deep grid is run at 512, which is what rung A's
# gold plan at sequential depth 32 needs: 443 tokens, measured, against 228 for
# rung B. Depth 8 is repeated inside the deep grid at 512 so the budget change
# itself is visible as a control rather than confounded with the depth change.
set -u
GPU="$1"; ARM="$2"
cd /home/ec2-user/opg
TOK=/home/ec2-user/data/tokenizer_v2.json
CKPT=runs/ladder_ab/ladder_$ARM.pt
R=results/ladder_ab

run () {  # tag temperature maxnew extra...
  local tag="$1"; shift
  local temp="$1"; shift
  local mx="$1"; shift
  echo "=== $ARM $tag temp=$temp max_new=$mx ==="
  PYTHONPATH=$PWD CUDA_VISIBLE_DEVICES=$GPU uv run python scripts/vocab_eval_ab.py \
    --ckpt $CKPT --tokenizer $TOK --out $R/${ARM}_${tag}.json \
    --n 150 --temperature $temp --max-new $mx "$@"
  echo "=== exit $? for $ARM $tag ==="
}

run main_greedy  0.0 320
run main_sampled 0.8 320
run deep_greedy  0.0 512 --kinds sequential --seq-depths 8,16,32
run deep_sampled 0.8 512 --kinds sequential --seq-depths 8,16,32
echo "EVAL_DONE $ARM"
