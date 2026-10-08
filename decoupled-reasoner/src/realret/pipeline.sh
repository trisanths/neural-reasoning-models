#!/bin/bash
# One self-driving run: prepare, wait for a go, train, wait for a go, evaluate.
#
# The lane that shares this box holds SSM worker slots with long polling
# loops, so this script reports through S3 instead: a heartbeat with the tail
# of every live log, and the reports themselves, pushed every minute. The two
# gates are S3 objects, so a stage that should not start until its inputs have
# been read does not start until they have been.
set -u
cd /home/ec2-user/decoupled-reasoner
R=/home/ec2-user/realret
S3=s3://decoupled-reasoner-009398924577/xfer/realret
mkdir -p $R/logs $R/results $R/reports
STATE=$R/logs/state

note() { echo "$(date -u +%FT%TZ) $*" >> $R/logs/pipeline.log; echo "$*" > $STATE; }

commit() {   # commit only this lane's paths, never -a
  git add src/realret >/dev/null 2>&1
  git -c user.name=realret -c user.email=realret@local \
      commit -q -m "realret: $1" >/dev/null 2>&1 || true
  git log --oneline -1 >> $R/logs/pipeline.log 2>&1
}

heartbeat() {
  while true; do
    {
      echo "== $(date -u +%FT%TZ)  state=$(cat $STATE 2>/dev/null)"
      echo "== disk: $(df -h / | tail -1)"
      echo "== gpu: $(nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader)"
      echo "== load: $(uptime | sed 's/.*load/load/')"
      for f in $R/logs/prepare.log $R/logs/train.jsonl $R/logs/evals.log; do
        [ -f "$f" ] && { echo "== tail $f"; tail -4 "$f"; }
      done
      echo "== results"; ls -la $R/results 2>/dev/null | tail -25
    } > $R/logs/heartbeat.txt 2>&1
    aws s3 cp $R/logs/heartbeat.txt $S3/heartbeat.txt --only-show-errors 2>/dev/null
    sleep 60
  done
}
heartbeat &
HB=$!
trap 'kill $HB 2>/dev/null' EXIT

# A veto window rather than an approval gate. The reports have just been
# pushed to S3; if they show something wrong, dropping an ABORT object there
# stops the run. Nothing waits on someone being awake, which matters on a box
# where a command can sit queued behind another lane for a quarter of an hour.
veto_window() {   # veto_window SECONDS
  local end=$(( $(date +%s) + $1 ))
  while [ "$(date +%s)" -lt "$end" ]; do
    if [ -n "$(aws s3 ls $S3/ABORT 2>/dev/null)" ]; then
      note "aborted by S3 ABORT object"
      return 1
    fi
    sleep 20
  done
  return 0
}

note "prepare"
bash src/realret/prepare.sh > $R/logs/prepare.log 2>&1
RC=$?
aws s3 cp $R/logs/prepare.log $S3/prepare.log --only-show-errors
for f in $R/reports/*.json $R/pack/*.summary.json $R/eps/*.summary.json \
         $R/eval/*.summary.json; do
  [ -f "$f" ] && aws s3 cp "$f" $S3/reports/$(basename "$f") --only-show-errors
done
commit "data prepared"
if [ $RC -ne 0 ]; then note "prepare_failed rc=$RC"; sleep 120; exit 1; fi
note "prepare_done"

# Automatic gate. A trace set that does not verify, or one carrying a
# benchmark test item verbatim, must not be trained on whatever the clock says.
note "gate"
.venv/bin/python -m src.realret.gate --root $R > $R/logs/gate.log 2>&1
GRC=$?
aws s3 cp $R/logs/gate.log $S3/gate.log --only-show-errors
if [ $GRC -ne 0 ]; then note "gate_failed"; sleep 600; exit 1; fi

note "veto_window_train"
veto_window 900 || { sleep 120; exit 1; }

note "train"
RC=1
for M in 8 4 2; do
  note "train micro=$M"
  MICRO=$M bash src/realret/train.sh > $R/logs/train.log 2>&1
  RC=$?
  aws s3 cp $R/logs/train.log $S3/train.log --only-show-errors
  [ -f $R/logs/train.jsonl ] && aws s3 cp $R/logs/train.jsonl $S3/train.jsonl \
      --only-show-errors
  [ $RC -eq 0 ] && break
  # Only a memory failure is worth retrying smaller. Anything else repeats.
  grep -qi "out of memory\|CUDA error" $R/logs/train.log || break
  note "train_oom micro=$M, retrying smaller"
done
if [ $RC -ne 0 ]; then note "train_failed rc=$RC"; sleep 600; exit 1; fi
note "train_done"

note "veto_window_eval"
veto_window 600 || { sleep 120; exit 1; }

note "evals"
# Stages run separately and a failure in one does not abort the rest: a
# missing cell is a gap in a table, a lost run is a gap in the day.
RC=0
for st in harness closed real synth web agentic; do
  note "evals $st"
  bash src/realret/evals.sh $st >> $R/logs/evals.log 2>&1 || {
    RC=1; note "evals_stage_failed $st"; }
  aws s3 cp $R/logs/evals.log $S3/evals.log --only-show-errors
  aws s3 sync $R/results $S3/results --exclude "*.jsonl" --only-show-errors
done
note "report"
.venv/bin/python -m src.realret.report --root $R \
  --out src/realret/tables.md --json-out $R/reports/report.json \
  >> $R/logs/evals.log 2>&1
aws s3 cp src/realret/tables.md $S3/tables.md --only-show-errors
aws s3 cp $R/reports/report.json $S3/reports/report.json --only-show-errors
commit "measurements"
note "evals_done rc=$RC"
sleep 300
