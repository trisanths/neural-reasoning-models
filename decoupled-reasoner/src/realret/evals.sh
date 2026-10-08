#!/bin/bash
# Re-measure. Every cell is written to a file and aggregated in a later pass.
#
# Stage 0 is a harness check and nothing below it means anything if it fails:
# the control checkpoint on this device has to reproduce the MMLU number
# already on record for it. The recorded value is 0.275 at n=200, seed 1234,
# measured on cpu; this runs the same items on cuda. A disagreement there is
# a device artefact and would contaminate every cell that follows.
set -eu
cd /home/ec2-user/decoupled-reasoner
P=.venv/bin/python
R=/home/ec2-user/realret
O=$R/results
TK=/home/ec2-user/data/tokenizer_v2.json
NEW=${NEW:-$R/real-v1-8k.pt}
OLD=/home/ec2-user/retrain/corpus-v1-8k.pt
mkdir -p $O $R/exa_cache

stage="${1:-all}"

if [ "$stage" = "harness" ] || [ "$stage" = "all" ]; then
  $P -m src.extern.bench_ours --ckpt $OLD --tag corpus-v1-8k --task mmlu \
     --n 200 --seed 1234 --device cuda --out $O/harness_ours_n200_cuda.json
  $P -m src.extern.bench --model LiquidAI/LFM2-350M --task mmlu \
     --fmt completion --n 200 --seed 1234 --bos --device cuda --dtype float32 \
     --out $O/harness_lfm2_n200_cuda_bos.json
  echo HARNESS_DONE
fi

if [ "$stage" = "closed" ] || [ "$stage" = "all" ]; then
  for pair in "corpus-v1-8k:$OLD" "real-v1-8k:$NEW"; do
    tag=${pair%%:*}; ck=${pair#*:}
    $P -m src.extern.bench_ours --ckpt $ck --tag $tag --task mmlu --n 500 \
       --seed 1234 --device cuda --out $O/mmlu_closed_${tag}_n500.json
    $P -m src.extern.bench_ours --ckpt $ck --tag $tag --task mmlu --n 500 \
       --seed 1234 --device cuda --eot-prefix \
       --out $O/mmlu_closed_${tag}_n500_eot.json
  done
  $P -m src.extern.bench --model LiquidAI/LFM2-350M --task mmlu \
     --fmt completion --n 500 --seed 1234 --bos --device cuda --dtype float32 \
     --out $O/mmlu_closed_lfm2-350m_n500_bos.json
  $P -m src.extern.bench --model LiquidAI/LFM2-350M --task mmlu \
     --fmt completion --n 500 --seed 1234 --device cuda --dtype float32 \
     --out $O/mmlu_closed_lfm2-350m_n500_nobos.json
  echo CLOSED_DONE
fi

if [ "$stage" = "web" ] || [ "$stage" = "all" ]; then
  # Seed the page cache from the run the external lane already paid for, so
  # a query both lanes ask costs one search between them.
  cp -rn results/extern/exa_cache/. $R/exa_cache/ 2>/dev/null || true
  $P -m src.extern.retrieval_mmlu --model LiquidAI/LFM2-350M --n 500 \
     --seed 1234 --bos --retriever exa --num-results 5 --budget 700 \
     --cache $R/exa_cache --device cuda --dtype float32 \
     --out $O/mmlu_web_lfm2-350m_n500.json
  # --budget 0: every page must come from the cache the line above filled,
  # so both sides of the table are given the same pages by construction.
  for pair in "corpus-v1-8k:$OLD" "real-v1-8k:$NEW"; do
    tag=${pair%%:*}; ck=${pair#*:}
    $P -m src.realret.mmluweb score --ckpt $ck --tag $tag --n 500 --seed 1234 \
       --cache $R/exa_cache --budget 0 --device cuda --tokenizer $TK \
       --out $O/mmlu_web_${tag}_n500.json
  done
  echo WEB_DONE
fi

if [ "$stage" = "agentic" ] || [ "$stage" = "all" ]; then
  for pair in "corpus-v1-8k:$OLD" "real-v1-8k:$NEW"; do
    tag=${pair%%:*}; ck=${pair#*:}
    $P -m src.realret.mmluweb agentic --ckpt $ck --tag $tag --n 200 \
       --seed 1234 --device cuda --tokenizer $TK --max-rounds 3 \
       --cache $R/exa_cache --budget 700 \
       --out $O/mmlu_agentic_${tag}_n200.json
  done
  echo AGENTIC_DONE
fi

if [ "$stage" = "synth" ] || [ "$stage" = "all" ]; then
  # Did real-document training cost the invented-system ability? Held-out
  # frames are the sharpest of the four measurements the corpus run moved,
  # and they are self-contained: the frame split is seeded, so the same
  # twelve frames the corpus never trained on can be regenerated here
  # rather than depended on from another lane's directory.
  mkdir -p $R/frames
  $P -m src.frames.cli frames --split both --split-seed 20260828 \
     --out $R/frames/split.json > $O/frames_split.txt
  FR=$($P - <<'PYEOF'
import json, random
sp = json.load(open("/home/ec2-user/realret/frames/split.json"))
test = sorted(sp["test"])
pick = test if len(test) <= 12 else random.Random(20260828).sample(test, 12)
print(",".join(sorted(pick)))
PYEOF
)
  echo "held_out_frames=$FR" | tee $O/frames_heldout.txt
  $P -m src.frames.cli gen --frames "$FR" --episodes 40 --seed0 2900000 \
     --conditions textbook --out $R/frames/gen_heldout > $O/frames_gen.txt
  for pair in "corpus-v1-8k:$OLD" "real-v1-8k:$NEW"; do
    tag=${pair%%:*}; ck=${pair#*:}
    for dec in "greedy 0.0 1" "t1 1.0 2"; do
      set -- $dec; lab=$1; temp=$2; smp=$3
      $P -m src.frames.cli eval --dir $R/frames/gen_heldout --checkpoint $ck \
         --tokenizer $TK --samples $smp --temperature $temp --batch 32 \
         --max-new-tokens 192 --max-len 1280 --seed 99 \
         --out $O/frames_eval_${tag}_${lab}.json \
         --dump-dir $R/frames/dump_${tag}_${lab}
      $P -m src.frames.cli score --dir $R/frames/gen_heldout \
         --dump-dir $R/frames/dump_${tag}_${lab} \
         --out $O/frames_score_${tag}_${lab}.json
    done
  done
  echo SYNTH_DONE
fi

if [ "$stage" = "real" ] || [ "$stage" = "all" ]; then
  for pair in "corpus-v1-8k:$OLD" "real-v1-8k:$NEW"; do
    tag=${pair%%:*}; ck=${pair#*:}
    # greedy over the 600 item file, sampled over its 300 item subset at
    # four rollouts each, so both decodes are reported and neither costs a
    # day of a shared card.
    for dec in "greedy 0.0 1 eval" "t1 1.0 4 evalS"; do
      set -- $dec; lab=$1; temp=$2; smp=$3; setf=$4
      for s in hotpot_qa natural_questions trivia_qa; do
        $P -m src.corpus.evalrun gen --checkpoint $ck --tokenizer $TK \
           --episodes $R/eval/$s.$setf.jsonl \
           --out $O/roll_${s}_${tag}_${lab}.jsonl --label $lab \
           --samples $smp --temperature $temp --batch 32 --max-rounds 4 \
           --max-new-tokens 192 --max-len 1280 --query-max-tokens 24 \
           --max-prompt-tokens 384 --questions-per-episode 1 --min-hops 1 \
           --seed 1234
      done
    done
    $P -m src.realret.score --out $O/real_scores_${tag}.json \
       --rollouts $O/roll_hotpot_qa_${tag}_greedy.jsonl \
                  $O/roll_natural_questions_${tag}_greedy.jsonl \
                  $O/roll_trivia_qa_${tag}_greedy.jsonl \
                  $O/roll_hotpot_qa_${tag}_t1.jsonl \
                  $O/roll_natural_questions_${tag}_t1.jsonl \
                  $O/roll_trivia_qa_${tag}_t1.jsonl \
       --episodes $R/eval/hotpot_qa.eval.jsonl \
                  $R/eval/natural_questions.eval.jsonl \
                  $R/eval/trivia_qa.eval.jsonl
  done
  echo REAL_DONE
fi
echo EVALS_DONE
