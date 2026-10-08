#!/bin/bash
# Self-driving block-4 launch. Runs armed on the dev box, needs no laptop and
# no user session (the dev box IAM role signs every call). Fires at 11:32:00
# UTC 2026-08-28, two minutes after capacity block cr-0bdf25326db18c156
# opens (p5.48xlarge, us-east-1f, ends 11:30 UTC 2026-08-29), then: launch
# the p5.48xlarge into the block, wait for SSM, run bootstrap4.sh as root
# gated on its DONE marker, run resume4.sh as ec2-user gated on
# ALL_LAUNCHED, take a status snapshot, and upload the log after every
# phase. New lanes take GPUs 0-3; GPUs 4-7 are left for grading (a
# defensive resume of a block-3 straggler may claim from 7 downward).
LOG=$HOME/logs/autolaunch4.log
exec >> "$LOG" 2>&1
R="--region us-east-1"
B=s3://decoupled-reasoner-009398924577
CR=cr-0bdf25326db18c156
TARGET=$(python3 -c 'import datetime;print(int(datetime.datetime(2026,8,28,11,32,0,tzinfo=datetime.timezone.utc).timestamp()))')
echo "autolaunch4 armed at $(date -u +%FT%TZ), firing at 11:32:00 UTC 2026-08-28 (epoch $TARGET)"
while [ "$(date +%s)" -lt "$TARGET" ]; do sleep 60; done
echo "firing at $(date -u +%FT%TZ)"
push_log() { aws s3 cp "$LOG" $B/logs/autolaunch4.log $R --only-show-errors; }
IID=""
for i in $(seq 1 40); do
  OUT=$(aws ec2 run-instances $R --image-id ami-0eb4d8bc9eb48d8ae --instance-type p5.48xlarge --instance-market-options MarketType=capacity-block --capacity-reservation-specification "CapacityReservationTarget={CapacityReservationId=$CR}" --iam-instance-profile Name=decoupled-reasoner-ec2 --security-group-ids sg-05ae7cbcedfdccff3 --subnet-id subnet-019942fb8eda1e2c1 --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":300,"VolumeType":"gp3"}}]' --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=decoupled-reasoner-block4},{Key=project,Value=decoupled-reasoner}]' --count 1 --query 'Instances[0].InstanceId' --output text 2>&1)
  if echo "$OUT" | grep -q '^i-'; then IID=$OUT; echo "launched $IID"; break; fi
  echo "attempt $i failed: $OUT"
  sleep 30
done
if [ -z "$IID" ]; then echo "LAUNCH_FAILED"; push_log; exit 1; fi
echo "$IID" > "$HOME/block4_instance_id"
aws s3 cp "$HOME/block4_instance_id" $B/logs/block4_instance_id $R --only-show-errors
push_log
ST=""
for i in $(seq 1 60); do
  ST=$(aws ssm describe-instance-information $R --filters "Key=InstanceIds,Values=$IID" --query 'InstanceInformationList[0].PingStatus' --output text 2>/dev/null)
  [ "$ST" = "Online" ] && break
  sleep 20
done
echo "ssm status: $ST at $(date -u +%FT%TZ)"
run_remote() {
  # $1 command, $2 executionTimeout seconds (also used as the delivery timeout)
  CID=$(aws ssm send-command $R --instance-ids "$IID" --document-name AWS-RunShellScript --timeout-seconds "$2" --parameters "$(python3 -c 'import json,sys;print(json.dumps({"commands":[sys.argv[1]],"executionTimeout":[sys.argv[2]]}))' "$1" "$2")" --query Command.CommandId --output text) || { echo "send-command failed"; return 1; }
  sleep 5
  EMPTY=0
  while :; do
    S=$(aws ssm get-command-invocation $R --command-id "$CID" --instance-id "$IID" --query Status --output text 2>/dev/null)
    if [ -z "$S" ] || [ "$S" = "None" ]; then
      EMPTY=$((EMPTY+1)); [ "$EMPTY" -gt 15 ] && break; sleep 10; continue
    fi
    case "$S" in Pending|InProgress|Delayed) sleep 20;; *) break;; esac
  done
  aws ssm get-command-invocation $R --command-id "$CID" --instance-id "$IID" --query StandardOutputContent --output text
  echo "[remote status: $S]"
}
echo "== bootstrap4 =="
BOOT_OK=0
for i in 1 2; do
  BOUT=$(run_remote "aws s3 cp $B/code/block4/bootstrap4.sh /root/bootstrap4.sh --region us-east-1 --only-show-errors && bash /root/bootstrap4.sh > /root/bootstrap4.log 2>&1; tail -c 20000 /root/bootstrap4.log; aws s3 cp /root/bootstrap4.log $B/logs/bootstrap4.log --region us-east-1 --only-show-errors" 7200)
  echo "$BOUT" | tail -60
  if echo "$BOUT" | grep -q "BOOTSTRAP4 DONE"; then BOOT_OK=1; break; fi
  echo "bootstrap4 attempt $i did not reach DONE, retrying (idempotent)"
  push_log
done
if [ "$BOOT_OK" != "1" ]; then echo "BOOTSTRAP4_FAILED"; push_log; exit 1; fi
push_log
echo "== resume4 =="
ROUT=$(run_remote 'sudo -u ec2-user bash -lc "bash ~/block4/resume4.sh > ~/logs/resume4.log 2>&1; tail -c 20000 ~/logs/resume4.log; aws s3 cp ~/logs/resume4.log s3://decoupled-reasoner-009398924577/logs/resume4.log --only-show-errors"' 5400)
echo "$ROUT" | tail -80
if ! echo "$ROUT" | grep -q "ALL_LAUNCHED"; then echo "RESUME_FAILED"; push_log; exit 1; fi
push_log
echo "== status snapshot =="
run_remote 'sudo -u ec2-user bash -lc "sleep 180; RUNS_ROOT=/home/ec2-user/runs PATTERN=curve- bash ~/block4/status.sh; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader"' 900
echo "AUTOLAUNCH4_DONE at $(date -u +%FT%TZ)"
push_log
