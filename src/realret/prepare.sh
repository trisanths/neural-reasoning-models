#!/bin/bash
# Verify, audit, pack and mix the real-document training data.
# Nothing here touches the GPU.
set -eu
cd /home/ec2-user/decoupled-reasoner
P=.venv/bin/python
R=/home/ec2-user/realret
TK=/home/ec2-user/data/tokenizer_v2.json
mkdir -p $R/pack $R/eval $R/reports $R/logs

# ---------------------------------------------------------------- eval split
# A seeded sample of each validation file, never its head.
# 600 items per source for the greedy cell, which clears the n >= 500 the
# re-measurement asks for, and a 300 item subset of that file for the
# sampled cell, which costs four rollouts each.
for s in hotpot_qa natural_questions trivia_qa; do
  $P -m src.realret.split sample --episodes $R/eps/$s.validation.jsonl \
     --out $R/eval/$s.eval.jsonl --take 600 --seed 8412
  $P -m src.realret.split sample --episodes $R/eval/$s.eval.jsonl \
     --out $R/eval/$s.evalS.jsonl --take 300 --seed 8413
done

# ------------------------------------------------------------------- verify
$P -m src.realret.verify --tokenizer $TK --sample 4000 \
   --episodes $R/eps/hotpot_qa.train.jsonl $R/eps/natural_questions.train.jsonl \
              $R/eps/trivia_qa.train.jsonl \
              $R/eval/hotpot_qa.eval.jsonl $R/eval/natural_questions.eval.jsonl \
              $R/eval/trivia_qa.eval.jsonl \
   --out $R/reports/verify.json

# -------------------------------------------------------------- leakage check
$P -m src.realret.split check --out $R/reports/leakage.json --doc-stride 5 \
   --pairs $R/eps/hotpot_qa.train.jsonl,$R/eval/hotpot_qa.eval.jsonl \
           $R/eps/natural_questions.train.jsonl,$R/eval/natural_questions.eval.jsonl \
           $R/eps/trivia_qa.train.jsonl,$R/eval/trivia_qa.eval.jsonl

# ------------------------------------------------------- benchmark contamination
$P -m src.realret.contam --root data/extern --out $R/reports/contamination.json \
   --episodes $R/eps/hotpot_qa.train.jsonl $R/eps/natural_questions.train.jsonl \
              $R/eps/trivia_qa.train.jsonl

# ---------------------------------------------------------------------- packs
# Quotas. HotpotQA takes the largest share because chaining a retrieved
# result is this project's one unfixed failure; the two single-hop sources
# split the rest evenly so neither sets the single-hop policy alone.
$P -m src.realret.pack build --tokenizer $TK --take 56000 \
   --episodes $R/eps/hotpot_qa.train.jsonl --out $R/pack/hotpot_qa
$P -m src.realret.pack build --tokenizer $TK --take 36000 \
   --episodes $R/eps/natural_questions.train.jsonl --out $R/pack/natural_questions
$P -m src.realret.pack build --tokenizer $TK --take 36000 \
   --episodes $R/eps/trivia_qa.train.jsonl --out $R/pack/trivia_qa

# The synthetic half, a seeded sample of the corpus pack the previous run
# trained on, so the invented-system ability measured elsewhere is not
# dropped from the mixture. One to one with the real half by example count.
$P -m src.realret.pack subsample --pack /home/ec2-user/retrain/pack/mix1 \
   --out $R/pack/synthetic --take 128000

$P -m src.corpus.sft merge --seed 90210 --out $R/pack/mix_real1 \
   --packs $R/pack/hotpot_qa $R/pack/natural_questions $R/pack/trivia_qa \
           $R/pack/synthetic
echo PREPARE_DONE
