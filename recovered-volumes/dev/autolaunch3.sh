#!/bin/bash
# Self-driving block-3 launch. Runs armed on the dev box, needs no laptop and
# no user session (the dev box IAM role signs every call). Fires at 11:32:00
# UTC 2026-08-27, two minutes after capacity block cr-0a1f939807e1a1f60
# opens, then: launch the p5.48xlarge into the block, wait for SSM, run
# bootstrap3.sh as root gated on its DONE marker, run resume3.sh as ec2-user
# gated on ALL_LAUNCHED, take a status snapshot, and upload the log after
# every phase. GPUs 4-7 are left free for grading and new experiment lanes.
LOG=$HOME/logs/autolaunch3.log
exec >> "$LOG" 2>&1
R="--region us-east-1"
B=s3://decoupled-reasoner-009398924577
CR=cr-0a1f939807e1a1f60
TARGET=$(python3 -c 'import datetime;print(int(datetime.datetime(2026,8,27,11,32,0,tzinfo=datetime.timezone.utc).timestamp()))')
echo "autolaunch3 armed at $(date -u +%FT%TZ), firing at 11:32:00 UTC 2026-08-27 (epoch $TARGET)"
while [ "$(date +%s)" -lt "$TARGET" ]; do sleep 60; done
echo "firing at $(date -u +%FT%TZ)"
push_log() { aws s3 cp "$LOG" $B/logs/autolaunch3.log $R --only-show-errors; }
IID=""
for i in $(seq 1 40); do
  OUT=$(aws ec2 run-instances $R --image-id ami-0eb4d8bc9eb48d8ae --instance-type p5.48xlarge --instance-market-options MarketType=capacity-block --capacity-reservation-specification "CapacityReservationTarget={CapacityReservationId=$CR}" --iam-instance-profile Name=decoupled-reasoner-ec2 --security-group-ids sg-05ae7cbcedfdccff3 --subnet-id subnet-019942fb8eda1e2c1 --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":300,"VolumeType":"gp3"}}]' --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=decoupled-reasoner-block3},{Key=project,Value=decoupled-reasoner}]' --count 1 --query 'Instances[0].InstanceId' --output text 2>&1)
  if echo "$OUT" | grep -q '^i-'; then IID=$OUT; echo "launched $IID"; break; fi
  echo "attempt $i failed: $OUT"
  sleep 30
done
if [ -z "$IID" ]; then echo "LAUNCH_FAILED"; push_log; exit 1; fi
echo "$IID" > "$HOME/block3_instance_id"
aws s3 cp "$HOME/block3_instance_id" $B/logs/block3_instance_id $R --only-show-errors
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
echo "== bootstrap3 =="
BOOT_OK=0
for i in 1 2; do
  BOUT=$(run_remote "aws s3 cp $B/code/block3/bootstrap3.sh /root/bootstrap3.sh --region us-east-1 --only-show-errors && bash /root/bootstrap3.sh > /root/bootstrap3.log 2>&1; tail -c 20000 /root/bootstrap3.log; aws s3 cp /root/bootstrap3.log $B/logs/bootstrap3.log --region us-east-1 --only-show-errors" 7200)
  echo "$BOUT" | tail -60
  if echo "$BOUT" | grep -q "BOOTSTRAP3 DONE"; then BOOT_OK=1; break; fi
  echo "bootstrap3 attempt $i did not reach DONE, retrying (idempotent)"
  push_log
done
if [ "$BOOT_OK" != "1" ]; then echo "BOOTSTRAP3_FAILED"; push_log; exit 1; fi
push_log
echo "== resume3 =="
ROUT=$(run_remote 'sudo -u ec2-user bash -lc "bash ~/block3/resume3.sh > ~/logs/resume3.log 2>&1; tail -c 20000 ~/logs/resume3.log; aws s3 cp ~/logs/resume3.log s3://decoupled-reasoner-009398924577/logs/resume3.log --only-show-errors"' 5400)
echo "$ROUT" | tail -80
if ! echo "$ROUT" | grep -q "ALL_LAUNCHED"; then echo "RESUME_FAILED"; push_log; exit 1; fi
push_log
echo "== status snapshot =="
run_remote 'sudo -u ec2-user bash -lc "sleep 180; RUNS_ROOT=/home/ec2-user/runs PATTERN=curve- bash ~/block3/status.sh; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader"' 900
echo "AUTOLAUNCH3_DONE at $(date -u +%FT%TZ)"
push_log
