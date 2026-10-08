#!/bin/bash
# Publish a small status snapshot to S3 once a minute, and the full results
# once the pipeline finishes. The SSM command queue on this box is congested
# enough that polling through it is unreliable, so status goes out over a
# channel that is not contended.
set -u
cd /home/ec2-user/opg || exit 1
B=s3://decoupled-reasoner-009398924577/ladder_cd
R=--region
G=us-east-1
LOCK=/home/ec2-user/opg/cdlane/.uploader.lock
mkdir "$LOCK" 2>/dev/null || {
  if [ -f "$LOCK/pid" ] && kill -0 "$(cat "$LOCK/pid")" 2>/dev/null; then exit 0; fi
}
echo $$ > "$LOCK/pid"

push_results () {
  for f in results/ladder_cd/*.json results/ladder_cd/*.txt; do
    [ -f "$f" ] && aws s3 cp --quiet $R $G "$f" "$B/$(basename "$f")" 2>/dev/null
  done
  for f in logs/ladder_cd/*.log; do
    [ -f "$f" ] && aws s3 cp --quiet $R $G "$f" "$B/logs/$(basename "$f")" 2>/dev/null
  done
}

for i in $(seq 1 2880); do
  {
    echo "ts $(date -u +%FT%TZ)  cycle $i"
    echo "--- pipeline ---"; tail -30 logs/ladder_cd/pipeline.log 2>/dev/null
    echo "--- train opcode ---"; tail -3 logs/ladder_cd/train_opcode.log 2>/dev/null
    echo "--- train typed ---"; tail -3 logs/ladder_cd/train_typed.log 2>/dev/null
    for f in logs/ladder_cd/eval_*.log; do
      [ -f "$f" ] && { echo "--- $f ---"; tail -2 "$f"; }
    done
    echo "--- results ---"; ls -l results/ladder_cd/ 2>/dev/null
    echo "--- runs ---"; ls -l runs/ladder_cd/ 2>/dev/null
    echo "--- gpu ---"
    nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader
    echo "--- mine ---"; pgrep -af "ladder_cd|eval_cd|pipeline_cd" | head -8
  } > /tmp/cd_status.txt 2>&1
  aws s3 cp --quiet $R $G /tmp/cd_status.txt "$B/status.txt" 2>/dev/null
  if grep -q "PIPELINE COMPLETE" logs/ladder_cd/pipeline.log 2>/dev/null; then
    push_results
    aws s3 cp --quiet $R $G /tmp/cd_status.txt "$B/status_final.txt" 2>/dev/null
    break
  fi
  if [ $((i % 15)) -eq 0 ]; then push_results; fi
  sleep 60
done
rm -rf "$LOCK"
