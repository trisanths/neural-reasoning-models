#!/bin/bash
# The whole lane on one dedicated box, one job at a time, launched detached.
#
# Order is deliberate. The data is staged and audited before anything is
# trained, the checkpoint that exists today is measured before the one that
# does not exists yet, and the measurement that leads the report, how often
# the policy emits a retrieve token at all, is taken on both sides of the
# training with the same instrument.
set -u
R=/mnt/nvme/realret
REPO=/home/ec2-user/decoupled-reasoner
P=$REPO/.venv/bin/python
TK=/home/ec2-user/data/tokenizer_v2.json
OLD=/home/ec2-user/ckpt/corpus-v1-8k-final.pt
NEW=$R/real-v1-8k.pt
S3=s3://decoupled-reasoner-009398924577/xfer/realret2
O=$R/results
cd $REPO
mkdir -p $R/logs $O $R/reports $R/eps $R/eval $R/pack $R/items $R/corpus
export HF_HOME=/mnt/nvme/hf
[ -f /home/ec2-user/.exa_env ] && . /home/ec2-user/.exa_env

STATE=$R/logs/state
note() { echo "$(date -u +%FT%TZ) $*" >> $R/logs/pipeline.log; echo "$*" > $STATE; }
done_marker() { [ -f "$R/logs/done.$1" ]; }
mark_done() { touch "$R/logs/done.$1"; }
push() { aws s3 cp "$1" "$S3/$2" --only-show-errors 2>/dev/null; }

heartbeat() {
  while true; do
    {
      echo "== $(date -u +%FT%TZ) state=$(cat $STATE 2>/dev/null)"
      echo "== gpu: $(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader)"
      echo "== disk: $(df -h / | tail -1)"
      for f in $R/logs/*.log $R/logs/train.jsonl; do
        [ -f "$f" ] && { echo "== tail $(basename $f)"; tail -3 "$f"; }
      done
      echo "== results"; ls -la $O 2>/dev/null | tail -30
    } > $R/logs/heartbeat.txt 2>&1
    push $R/logs/heartbeat.txt heartbeat.txt
    sleep 60
  done
}
heartbeat & HB=$!
trap 'kill $HB 2>/dev/null' EXIT

# ------------------------------------------------------------------ 1 stage
if done_marker stage; then note "stage_skipped"; else
note "stage"
$P -m src.realret.stage --corpus-dir $R/corpus --data-dir $REPO/data \
   --manifest $R/reports/stage_manifest.json > $R/logs/stage.log 2>&1
RC=$?; push $R/logs/stage.log stage.log; push $R/reports/stage_manifest.json reports/stage_manifest.json
[ $RC -ne 0 ] && { note "stage_failed"; sleep 300; exit 1; }
mark_done stage; fi

# ------------------------------------------------------------- 2 real data
if done_marker data; then note "data_skipped"; else
note "fetch"
$P -m src.realret.sources fetch --out $R/items --raw $R/raw --drop-raw \
   > $R/logs/fetch.log 2>&1 || { note "fetch_failed"; sleep 300; exit 1; }
push $R/items/fetch.summary.json reports/fetch.summary.json

note "episodes"
for s in hotpot_qa natural_questions trivia_qa; do
  for sp in train validation; do
    $P -m src.realret.episodes build --tokenizer $TK \
       --items $R/items/$s.$sp.jsonl --out $R/eps/$s.$sp.jsonl \
       >> $R/logs/episodes.log 2>&1 || { note "episodes_failed $s $sp"; sleep 300; exit 1; }
    push $R/eps/$s.$sp.jsonl.summary.json reports/eps_$s.$sp.summary.json
  done
done
mark_done data; fi

if done_marker audit; then note "audit_skipped"; else
note "audit"
# Evaluation sets first, because de-contamination removes training episodes
# whose question already appears in one of them.
for s in hotpot_qa natural_questions trivia_qa; do
  $P -m src.realret.split sample --episodes $R/eps/$s.validation.jsonl \
     --out $R/eval/$s.eval.jsonl --take 600 --seed 8412 >> $R/logs/audit.log 2>&1
  $P -m src.realret.split sample --episodes $R/eval/$s.eval.jsonl \
     --out $R/eval/$s.evalS.jsonl --take 300 --seed 8413 >> $R/logs/audit.log 2>&1
done

# The first contamination scan, on the raw build. Kept as the record of what
# the sources actually carry.
$P -m src.realret.contam --root $REPO/data/extern --all-documents \
   --out $R/reports/contamination_before.json \
   --episodes $R/eps/hotpot_qa.train.jsonl $R/eps/natural_questions.train.jsonl \
              $R/eps/trivia_qa.train.jsonl >> $R/logs/audit.log 2>&1

mkdir -p $R/eps_clean
$P -m src.realret.decontam --root $REPO/data/extern --out-dir $R/eps_clean \
   --report $R/reports/decontam.json --near-threshold 0.7 \
   --episodes $R/eps/hotpot_qa.train.jsonl $R/eps/natural_questions.train.jsonl \
              $R/eps/trivia_qa.train.jsonl \
   --eval hotpot_qa=$R/eval/hotpot_qa.eval.jsonl \
          natural_questions=$R/eval/natural_questions.eval.jsonl \
          trivia_qa=$R/eval/trivia_qa.eval.jsonl >> $R/logs/audit.log 2>&1 \
   || { note "decontam_failed"; sleep 300; exit 1; }

# The scan that gates training, on the files that are actually packed.
$P -m src.realret.contam --root $REPO/data/extern --all-documents \
   --out $R/reports/contamination.json \
   --episodes $R/eps_clean/hotpot_qa.train.jsonl \
              $R/eps_clean/natural_questions.train.jsonl \
              $R/eps_clean/trivia_qa.train.jsonl >> $R/logs/audit.log 2>&1
$P -m src.realret.verify --tokenizer $TK --sample 4000 --out $R/reports/verify.json \
   --episodes $R/eps_clean/hotpot_qa.train.jsonl \
              $R/eps_clean/natural_questions.train.jsonl \
              $R/eps_clean/trivia_qa.train.jsonl $R/eval/hotpot_qa.eval.jsonl \
              $R/eval/natural_questions.eval.jsonl $R/eval/trivia_qa.eval.jsonl \
   >> $R/logs/audit.log 2>&1
$P -m src.realret.split check --out $R/reports/leakage.json --doc-stride 5 \
   --pairs $R/eps_clean/hotpot_qa.train.jsonl,$R/eval/hotpot_qa.eval.jsonl \
           $R/eps_clean/natural_questions.train.jsonl,$R/eval/natural_questions.eval.jsonl \
           $R/eps_clean/trivia_qa.train.jsonl,$R/eval/trivia_qa.eval.jsonl \
   >> $R/logs/audit.log 2>&1
push $R/logs/audit.log audit.log
for f in verify leakage contamination contamination_before decontam; do
  push $R/reports/$f.json reports/$f.json
done
mark_done audit
note "audit_done"
fi

# ------------------------------------------------------------------ 3 packs
if done_marker packs; then note "packs_skipped"; else
note "packs"
$P -m src.realret.pack build --tokenizer $TK --take 56000 \
   --episodes $R/eps_clean/hotpot_qa.train.jsonl --out $R/pack/hotpot_qa >> $R/logs/pack.log 2>&1
$P -m src.realret.pack build --tokenizer $TK --take 36000 \
   --episodes $R/eps_clean/natural_questions.train.jsonl --out $R/pack/natural_questions >> $R/logs/pack.log 2>&1
$P -m src.realret.pack build --tokenizer $TK --take 36000 \
   --episodes $R/eps_clean/trivia_qa.train.jsonl --out $R/pack/trivia_qa >> $R/logs/pack.log 2>&1
# The synthetic half, rebuilt from the corpus the previous run trained on,
# at that run's own component proportions halved.
for spec in "relation 64000" "plan_step 24000" "plan_whole 16000" "external 12000" "mathgen 11000"; do
  set -- $spec
  $P -m src.corpus.sft build --corpus $R/corpus --tokenizer $TK --component $1 \
     --out $R/pack/syn_$1 --take $2 >> $R/logs/pack.log 2>&1 \
     || { note "pack_failed $1"; sleep 300; exit 1; }
done
$P -m src.corpus.sft merge --seed 90210 --out $R/pack/mix_real1 \
   --packs $R/pack/hotpot_qa $R/pack/natural_questions $R/pack/trivia_qa \
           $R/pack/syn_relation $R/pack/syn_plan_step $R/pack/syn_plan_whole \
           $R/pack/syn_external $R/pack/syn_mathgen >> $R/logs/pack.log 2>&1 \
   || { note "merge_failed"; sleep 300; exit 1; }
push $R/logs/pack.log pack.log
for f in $R/pack/*.summary.json; do push $f reports/$(basename $f); done

note "gate"
$P -m src.realret.gate --root $R > $R/logs/gate.log 2>&1
GRC=$?; push $R/logs/gate.log gate.log
[ $GRC -ne 0 ] && { note "gate_failed"; sleep 600; exit 1; }
mark_done packs
note "gate_passed"
fi

# -------------------------------------------------- 4 before, then train
if done_marker before; then note "before_skipped"; else
bash src/realret/w2_measure.sh before "$OLD" corpus-v1-8k > $R/logs/before.log 2>&1
push $R/logs/before.log before.log
aws s3 sync $O $S3/results --exclude "*.jsonl" --only-show-errors
mark_done before
note "before_done"
fi

note "train"
RC=1
for M in 16 8 4; do
  note "train micro=$M"
  MICRO=$M bash src/realret/w2_train.sh > $R/logs/train.log 2>&1
  RC=$?
  push $R/logs/train.log train.log
  [ -f $R/logs/train.jsonl ] && push $R/logs/train.jsonl train.jsonl
  [ $RC -eq 0 ] && break
  grep -qi "out of memory\|CUDA error" $R/logs/train.log || break
done
[ $RC -ne 0 ] && { note "train_failed"; sleep 600; exit 1; }
note "train_done"
aws s3 cp $NEW s3://decoupled-reasoner-009398924577/runs/real-v1-8k/final.pt --only-show-errors

# ------------------------------------------------------------- 5 after
bash src/realret/w2_measure.sh after "$NEW" real-v1-8k > $R/logs/after.log 2>&1
push $R/logs/after.log after.log
aws s3 sync $O $S3/results --exclude "*.jsonl" --only-show-errors
note "after_done"

$P -m src.realret.report --root $R --out $R/tables.md \
   --json-out $R/reports/report.json > $R/logs/report.log 2>&1
push $R/tables.md tables.md
push $R/reports/report.json reports/report.json
aws s3 sync $O $S3/results --exclude "*.jsonl" --only-show-errors
note "ALL_DONE"
sleep 600
