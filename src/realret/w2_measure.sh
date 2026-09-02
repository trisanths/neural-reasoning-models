#!/bin/bash
# One battery, run identically on the checkpoint before training and the one
# after, so every row of every table has a matched pair.
#
# The first measurement is the one that leads the report: how often the policy
# emits a retrieve token at all when it is shown a real question. It is taken
# twice, once against live web retrieval on MMLU and once against the held-out
# real-document bundles, because a policy that never asks is a policy failure
# whatever the retriever behind it is.
set -u
PHASE="$1"; CK="$2"; TAG="$3"
REPO=/home/ec2-user/decoupled-reasoner
R=/mnt/nvme/realret
P=$REPO/.venv/bin/python
TK=/home/ec2-user/data/tokenizer_v2.json
O=$R/results
cd $REPO
[ -f /home/ec2-user/.exa_env ] && . /home/ec2-user/.exa_env
mkdir -p $O $R/exa_cache

echo "=== $PHASE $TAG issued-query rate, MMLU with live web retrieval ==="
$P -m src.realret.mmluweb agentic --ckpt "$CK" --tag "$TAG" --n 200 --seed 1234 \
   --root $REPO/data/extern --tokenizer $TK --device cuda --max-rounds 3 \
   --cache $R/exa_cache --budget 700 \
   --out $O/mmlu_agentic_${TAG}_n200.json || echo "AGENTIC_FAILED"

echo "=== $PHASE $TAG held-out real documents ==="
for dec in "greedy 0.0 1 eval" "t1 1.0 4 evalS"; do
  set -- $dec; lab=$1; temp=$2; smp=$3; setf=$4
  for s in hotpot_qa natural_questions trivia_qa; do
    $P -m src.corpus.evalrun gen --checkpoint "$CK" --tokenizer $TK \
       --episodes $R/eval/$s.$setf.jsonl \
       --out $O/roll_${s}_${TAG}_${lab}.jsonl --label $lab --samples $smp \
       --temperature $temp --batch 32 --max-rounds 4 --max-new-tokens 192 \
       --max-len 1280 --query-max-tokens 24 --max-prompt-tokens 384 \
       --questions-per-episode 1 --min-hops 1 --seed 1234 \
       || echo "REALGEN_FAILED $s $lab"
  done
done
$P -m src.realret.score --out $O/real_scores_${TAG}.json \
   --rollouts $O/roll_hotpot_qa_${TAG}_greedy.jsonl \
              $O/roll_natural_questions_${TAG}_greedy.jsonl \
              $O/roll_trivia_qa_${TAG}_greedy.jsonl \
              $O/roll_hotpot_qa_${TAG}_t1.jsonl \
              $O/roll_natural_questions_${TAG}_t1.jsonl \
              $O/roll_trivia_qa_${TAG}_t1.jsonl \
   --episodes $R/eval/hotpot_qa.eval.jsonl $R/eval/natural_questions.eval.jsonl \
              $R/eval/trivia_qa.eval.jsonl || echo "SCORE_FAILED"

echo "=== $PHASE $TAG MMLU closed book, n=500 ==="
$P -m src.extern.bench_ours --ckpt "$CK" --tag "$TAG" --task mmlu --n 500 \
   --seed 1234 --device cuda --root $REPO/data/extern --tokenizer $TK \
   --out $O/mmlu_closed_${TAG}_n500.json || echo "CLOSED_FAILED"
$P -m src.extern.bench_ours --ckpt "$CK" --tag "$TAG" --task mmlu --n 500 \
   --seed 1234 --device cuda --eot-prefix --root $REPO/data/extern --tokenizer $TK \
   --out $O/mmlu_closed_${TAG}_n500_eot.json || echo "CLOSEDEOT_FAILED"

if [ "$PHASE" = "before" ]; then
  echo "=== LFM2-350M, the matched-size control, run once ==="
  $P -m src.extern.bench --model LiquidAI/LFM2-350M --task mmlu --fmt completion \
     --n 500 --seed 1234 --bos --device cuda --dtype float32 --root $REPO/data/extern \
     --out $O/mmlu_closed_lfm2-350m_n500_bos.json || echo "LFM2_BOS_FAILED"
  $P -m src.extern.bench --model LiquidAI/LFM2-350M --task mmlu --fmt completion \
     --n 500 --seed 1234 --device cuda --dtype float32 --root $REPO/data/extern \
     --out $O/mmlu_closed_lfm2-350m_n500_nobos.json || echo "LFM2_NOBOS_FAILED"
  # Run before our own paged cell so the pages our reader is given are the
  # ones this run cached, which is what makes "the same pages" checkable.
  $P -m src.extern.retrieval_mmlu --model LiquidAI/LFM2-350M --n 500 --seed 1234 \
     --bos --retriever exa --num-results 5 --budget 700 --cache $R/exa_cache \
     --device cuda --dtype float32 --root $REPO/data/extern \
     --out $O/mmlu_web_lfm2-350m_n500.json || echo "LFM2_WEB_FAILED"
fi

echo "=== $PHASE $TAG MMLU with the same pages in context ==="
$P -m src.realret.mmluweb score --ckpt "$CK" --tag "$TAG" --n 500 --seed 1234 \
   --root $REPO/data/extern --tokenizer $TK --device cuda \
   --cache $R/exa_cache --budget 700 \
   --out $O/mmlu_web_${TAG}_n500.json || echo "WEB_FAILED"

echo "=== $PHASE $TAG held-out synthetic frames ==="
mkdir -p $R/frames
if [ ! -f $R/frames/split.json ]; then
  $P -m src.frames.cli frames --split both --split-seed 20260828 \
     --out $R/frames/split.json > $O/frames_split.txt 2>&1
  FR=$($P - <<'PYEOF'
import json, random
sp = json.load(open("/mnt/nvme/realret/frames/split.json"))
test = sorted(sp["test"])
pick = test if len(test) <= 12 else random.Random(20260828).sample(test, 12)
print(",".join(sorted(pick)))
PYEOF
)
  echo "$FR" > $R/frames/heldout.txt
  $P -m src.frames.cli gen --frames "$FR" --episodes 40 --seed0 2900000 \
     --conditions textbook --out $R/frames/gen_heldout > $O/frames_gen.txt 2>&1
fi
for dec in "greedy 0.0 1" "t1 1.0 2"; do
  set -- $dec; lab=$1; temp=$2; smp=$3
  $P -m src.frames.cli eval --dir $R/frames/gen_heldout --checkpoint "$CK" \
     --tokenizer $TK --samples $smp --temperature $temp --batch 32 \
     --max-new-tokens 192 --max-len 1280 --seed 99 \
     --out $O/frames_eval_${TAG}_${lab}.json \
     --dump-dir $R/frames/dump_${TAG}_${lab} || { echo "FRAMES_FAILED $lab"; continue; }
  $P -m src.frames.cli score --dir $R/frames/gen_heldout \
     --dump-dir $R/frames/dump_${TAG}_${lab} \
     --out $O/frames_score_${TAG}_${lab}.json || echo "FRAMESCORE_FAILED $lab"
done
echo "MEASURE_DONE $PHASE $TAG"
