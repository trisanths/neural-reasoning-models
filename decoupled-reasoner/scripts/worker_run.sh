#!/usr/bin/env bash
# Run a command on one worker over SSM and print what it said.
#
# usage: bash scripts/worker_run.sh <worker> 'CMD' [TIMEOUT_SECONDS]
#   worker   1, 2, 3 for nrm-worker-N; dev for the original box; a full Name tag;
#            or an i-xxxx instance id
#   CMD      runs as ec2-user under bash -lc, so ~/.bashrc and ~/.exa_env apply
#   TIMEOUT  how long to wait for the result, default 280
#
# SSM itself gives up near 300 seconds and the reply truncates near 24 KB, so
# anything long should be started detached and polled:
#   bash scripts/worker_run.sh 2 'cd ~/decoupled-reasoner && setsid nohup uv run python -m src.foo > ~/logs/foo.log 2>&1 < /dev/null & echo started'
#   bash scripts/worker_run.sh 2 'tail -5 ~/logs/foo.log'
set -u
export AWS_PROFILE="${AWS_PROFILE:-chronos}"
REGION="${AWS_REGION:-us-east-1}"

TARGET="${1:?usage: worker_run.sh <worker> \"CMD\" [timeout]}"
CMD="${2:?usage: worker_run.sh <worker> \"CMD\" [timeout]}"
TO="${3:-280}"

case "$TARGET" in
  i-*)            IID="$TARGET";;
  [0-9]|[0-9][0-9]) TAG="nrm-worker-$TARGET";;
  dev)            TAG="decoupled-reasoner-dev";;
  *)              TAG="$TARGET";;
esac

if [ -z "${IID:-}" ]; then
  IID=$(aws ec2 describe-instances --region "$REGION" \
        --filters "Name=tag:Name,Values=$TAG" "Name=instance-state-name,Values=running" \
        --query 'Reservations[].Instances[].InstanceId' --output text)
  if [ -z "$IID" ] || [ "$IID" = "None" ]; then
    echo "no running instance tagged $TAG" >&2; exit 1
  fi
  case "$IID" in *[[:space:]]*) echo "more than one running instance tagged $TAG: $IID" >&2; exit 1;; esac
fi

PARAMS=$(python3 -c 'import json,shlex,sys; print(json.dumps({"commands":["sudo -u ec2-user bash -lc " + shlex.quote(sys.argv[1])]}))' "$CMD")
CID=$(aws ssm send-command --region "$REGION" --instance-ids "$IID" \
      --document-name AWS-RunShellScript --timeout-seconds 3600 \
      --parameters "$PARAMS" --query Command.CommandId --output text) || {
  echo "send-command to $IID failed" >&2; exit 1; }

END=$(( $(date +%s) + TO ))
ST=Pending
while [ "$(date +%s)" -lt "$END" ]; do
  ST=$(aws ssm get-command-invocation --region "$REGION" --command-id "$CID" \
       --instance-id "$IID" --query Status --output text 2>/dev/null || echo Pending)
  case "$ST" in InProgress|Pending|Delayed) sleep 4;; *) break;; esac
done

aws ssm get-command-invocation --region "$REGION" --command-id "$CID" --instance-id "$IID" \
  --query StandardOutputContent --output text
E=$(aws ssm get-command-invocation --region "$REGION" --command-id "$CID" --instance-id "$IID" \
    --query StandardErrorContent --output text)
if [ -n "$E" ] && [ "$E" != "None" ]; then echo "--- stderr ---"; echo "$E"; fi
echo "--- $IID status: $ST  id: $CID ---"
case "$ST" in Success) exit 0;; *) exit 1;; esac
