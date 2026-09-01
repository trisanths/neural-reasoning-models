#!/usr/bin/env bash
# One line per GPU box: instance id, state, zone, SSM reachability, GPU load,
# system load, free disk, and whether the bootstrap finished.
#
# usage: bash scripts/fleet_status.sh [--json]
#
# The on-box numbers come from a single SSM command fanned out to every running
# instance at once, so this stays one round trip however many workers there are.
set -u
export AWS_PROFILE="${AWS_PROFILE:-chronos}"
REGION="${AWS_REGION:-us-east-1}"
NAMES="${FLEET_NAMES:-decoupled-reasoner-dev,nrm-worker-*}"
JSON=0
[ "${1:-}" = "--json" ] && JSON=1

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

aws ec2 describe-instances --region "$REGION" \
  --filters "Name=tag:Name,Values=$NAMES" \
            "Name=instance-state-name,Values=running,pending,stopping,stopped,shutting-down" \
  --query 'Reservations[].Instances[].[Tags[?Key==`Name`]|[0].Value,InstanceId,InstanceType,State.Name,Placement.AvailabilityZone,LaunchTime]' \
  --output text | sort > "$TMP/inst"

if [ ! -s "$TMP/inst" ]; then
  echo "no instances match $NAMES"; exit 0
fi

# SSM agent reachability
aws ssm describe-instance-information --region "$REGION" \
  --query 'InstanceInformationList[].[InstanceId,PingStatus]' --output text 2>/dev/null > "$TMP/ping" || true
touch "$TMP/ping"

# Probe only the boxes SSM can actually reach. A box that is running but still
# booting would otherwise reject the whole fan-out and blank the healthy rows.
RUNNING=""
for i in $(awk '$4=="running"{print $2}' "$TMP/inst"); do
  awk -v i="$i" '$1==i && $2=="Online"{f=1} END{exit !f}' "$TMP/ping" && RUNNING="$RUNNING $i"
done
RUNNING="${RUNNING# }"

# One probe, fanned out to every reachable instance.
if [ -n "$RUNNING" ]; then
  PROBE='G=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d " "); \
L=$(cut -d" " -f1-3 /proc/loadavg); \
R=$(df -h --output=avail / | tail -1 | tr -d " "); \
V=$(df -h --output=avail /mnt/nvme 2>/dev/null | tail -1 | tr -d " "); \
B=none; [ -f ~/BOOTSTRAP_OK ] && B=ok; [ -f ~/BOOTSTRAP_FAILED ] && B=FAILED; \
[ -z "$V" ] && V=-; \
P=$(pgrep -c -f "python" 2>/dev/null || echo 0); \
U=$(cut -d. -f1 /proc/uptime); \
echo "FLEET|${G:-nogpu}|$L|$R|$V|$B|$P|$U"'
  PARAMS=$(python3 -c 'import json,shlex,sys; print(json.dumps({"commands":["sudo -u ec2-user bash -lc " + shlex.quote(sys.argv[1])]}))' "$PROBE")
  # shellcheck disable=SC2086
  CID=$(aws ssm send-command --region "$REGION" --instance-ids $RUNNING \
        --document-name AWS-RunShellScript --timeout-seconds 120 \
        --parameters "$PARAMS" --query Command.CommandId --output text 2>/dev/null) || CID=""
  if [ -n "$CID" ]; then
    for _ in $(seq 1 20); do
      N=$(aws ssm list-command-invocations --region "$REGION" --command-id "$CID" \
          --query 'length(CommandInvocations[?Status!=`Pending` && Status!=`InProgress` && Status!=`Delayed`])' \
          --output text 2>/dev/null || echo 0)
      W=$(echo "$RUNNING" | wc -w | tr -d ' ')
      [ "$N" -ge "$W" ] && break
      sleep 3
    done
    for i in $RUNNING; do
      aws ssm get-command-invocation --region "$REGION" --command-id "$CID" --instance-id "$i" \
        --query StandardOutputContent --output text 2>/dev/null \
        | grep '^FLEET|' | head -1 | sed "s|^FLEET|$i|" >> "$TMP/probe" || true
    done
  fi
fi
touch "$TMP/probe"

if [ "$JSON" = 1 ]; then
  echo "["
  SEP=""
fi
[ "$JSON" = 0 ] && printf '%-22s %-20s %-12s %-9s %-11s %-8s %-8s %-16s %-7s %-6s %-7s %s\n' \
  NAME ID TYPE STATE ZONE SSM GPU% "GPU MEM" LOAD1 "/ FREE" "NVME" BOOT

while read -r NAME ID TYPE STATE AZ LAUNCH; do
  PING=$(awk -v i="$ID" '$1==i{print $2}' "$TMP/ping"); PING=${PING:--}
  LINE=$(grep "^$ID|" "$TMP/probe" | head -1)
  if [ -n "$LINE" ]; then
    IFS='|' read -r _ GPU LOAD ROOTF NVMEF BOOT NPY UP <<< "$LINE"
    GUTIL=${GPU%%,*}; GMEM=${GPU#*,}
    GMEM="${GMEM%%,*}/${GPU##*,}MiB"
    LOAD1=${LOAD%% *}
  else
    GUTIL=-; GMEM=-; LOAD1=-; ROOTF=-; NVMEF=-; BOOT=-; NPY=-; UP=-
  fi
  if [ "$JSON" = 1 ]; then
    printf '%s  {"name":"%s","id":"%s","type":"%s","state":"%s","zone":"%s","ssm":"%s","gpu_pct":"%s","gpu_mem":"%s","load1":"%s","root_free":"%s","nvme_free":"%s","bootstrap":"%s","python_procs":"%s","uptime_s":"%s","launched":"%s"}\n' \
      "$SEP" "$NAME" "$ID" "$TYPE" "$STATE" "$AZ" "$PING" "$GUTIL" "$GMEM" "$LOAD1" "$ROOTF" "$NVMEF" "$BOOT" "$NPY" "$UP" "$LAUNCH"
    SEP=","
  else
    printf '%-22s %-20s %-12s %-9s %-11s %-8s %-8s %-16s %-7s %-6s %-7s %s\n' \
      "$NAME" "$ID" "$TYPE" "$STATE" "$AZ" "$PING" "$GUTIL" "$GMEM" "$LOAD1" "$ROOTF" "$NVMEF" "$BOOT"
  fi
done < "$TMP/inst"
[ "$JSON" = 1 ] && echo "]"

if [ "$JSON" = 0 ]; then
  NRUN=$(echo "$RUNNING" | wc -w | tr -d ' ')
  echo
  echo "$NRUN running. GPU% and load are instantaneous; BOOT is the bootstrap marker."
  echo "Reach one with: bash scripts/worker_run.sh <1|2|3|dev> 'CMD'"
fi
