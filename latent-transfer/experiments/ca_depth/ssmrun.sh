#!/bin/bash
# Usage: ssmrun.sh <instance-id> '<command>' [timeout_s]
# Runs a shell command on an EC2 instance via SSM and prints stdout/stderr.
IID="$1"; CMD="$2"; TO="${3:-120}"
CID=$(aws ssm send-command --profile chronos --region us-east-1 --instance-ids "$IID" \
  --document-name AWS-RunShellScript --timeout-seconds "$TO" \
  --parameters "commands=[\"$(printf '%s' "$CMD" | sed 's/"/\\"/g')\"]" \
  --query 'Command.CommandId' --output text) || { echo "SEND_FAIL"; exit 1; }
for i in $(seq 1 $((TO/2))); do
  sleep 2
  ST=$(aws ssm get-command-invocation --profile chronos --region us-east-1 --command-id "$CID" --instance-id "$IID" --query Status --output text 2>/dev/null)
  case "$ST" in Success|Failed|TimedOut|Cancelled)
    aws ssm get-command-invocation --profile chronos --region us-east-1 --command-id "$CID" --instance-id "$IID" --query '[StandardOutputContent,StandardErrorContent]' --output text
    echo "[status: $ST]"; exit 0;;
  esac
done
echo "[status: still $ST after ${TO}s]"
