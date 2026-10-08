#!/bin/bash
# Self-driving kill-test launch. Runs on the dev box, needs no laptop and no user session.
LOG=$HOME/logs/autolaunch.log
exec >> "$LOG" 2>&1
R="--region us-east-1"
B=s3://decoupled-reasoner-009398924577
TARGET=$(python3 -c 'import datetime;print(int(datetime.datetime(2026,8,25,11,30,30,tzinfo=datetime.timezone.utc).timestamp()))')
echo "autolaunch armed at $(date -u +%FT%TZ), firing at 11:30:30 UTC"
while [ "$(date +%s)" -lt "$TARGET" ]; do sleep 60; done
echo "firing at $(date -u +%FT%TZ)"
IID=""
for i in $(seq 1 30); do
  OUT=$(aws ec2 run-instances $R --image-id ami-0eb4d8bc9eb48d8ae --instance-type p5.48xlarge --instance-market-options MarketType=capacity-block --capacity-reservation-specification 'CapacityReservationTarget={CapacityReservationId=cr-0fc31baec48544a59}' --iam-instance-profile Name=decoupled-reasoner-ec2 --security-group-ids sg-05ae7cbcedfdccff3 --subnet-id subnet-019942fb8eda1e2c1 --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":300,"VolumeType":"gp3"}}]' --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=decoupled-reasoner-killtest},{Key=project,Value=decoupled-reasoner}]' --count 1 --query 'Instances[0].InstanceId' --output text 2>&1)
  if echo "$OUT" | grep -q '^i-'; then IID=$OUT; echo "launched $IID"; break; fi
  echo "attempt $i failed: $OUT"
  sleep 30
done
if [ -z "$IID" ]; then echo "LAUNCH_FAILED"; aws s3 cp "$LOG" $B/logs/autolaunch.log $R; exit 1; fi
echo "$IID" > "$HOME/killtest_instance_id"
for i in $(seq 1 60); do
  ST=$(aws ssm describe-instance-information $R --filters "Key=InstanceIds,Values=$IID" --query 'InstanceInformationList[0].PingStatus' --output text 2>/dev/null)
  [ "$ST" = "Online" ] && break
  sleep 20
done
echo "ssm status: $ST at $(date -u +%FT%TZ)"
run_remote() {
  CID=$(aws ssm send-command $R --instance-ids "$IID" --document-name AWS-RunShellScript --timeout-seconds "$2" --parameters "$(python3 -c 'import json,sys;print(json.dumps({"commands":[sys.argv[1]]}))' "$1")" --query Command.CommandId --output text) || { echo "send-command failed"; return 1; }
  while :; do
    S=$(aws ssm get-command-invocation $R --command-id "$CID" --instance-id "$IID" --query Status --output text 2>/dev/null)
    case "$S" in Pending|InProgress|Delayed) sleep 20;; *) break;; esac
  done
  aws ssm get-command-invocation $R --command-id "$CID" --instance-id "$IID" --query StandardOutputContent --output text
  echo "[remote status: $S]"
}
echo "== bootstrap =="
BOUT=$(run_remote "aws s3 cp $B/code/killtest/bootstrap.sh /root/bootstrap.sh --region us-east-1 && bash /root/bootstrap.sh" 5400)
echo "$BOUT" | tail -40
if ! echo "$BOUT" | grep -q "BOOTSTRAP DONE"; then echo "BOOTSTRAP_FAILED"; aws s3 cp "$LOG" $B/logs/autolaunch.log $R; exit 1; fi
echo "== launch runs =="
run_remote 'sudo -u ec2-user bash -lc "bash ~/killtest/launch_runs.sh"' 900
echo "== early status =="
run_remote 'sudo -u ec2-user bash -lc "sleep 180; bash ~/killtest/status.sh"' 900
aws s3 cp "$LOG" $B/logs/autolaunch.log $R
aws s3 cp "$HOME/killtest_instance_id" $B/logs/killtest_instance_id $R
echo "AUTOLAUNCH_DONE at $(date -u +%FT%TZ)"
aws s3 cp "$LOG" $B/logs/autolaunch.log $R
