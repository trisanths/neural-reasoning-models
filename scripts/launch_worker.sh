#!/usr/bin/env bash
# Bring up one GPU worker and leave it bootstrapping itself.
#
# usage: bash scripts/launch_worker.sh <n> [az ...]
#   n     worker number, becomes the Name tag nrm-worker-<n>
#   az    availability zones to try in order (default: the list below)
#
# G capacity in us-east-1 comes and goes, so this walks the zones until one of
# them accepts the request, and it refuses to launch at all if the account's
# G and VT vCPU quota would be exceeded.
#
# Environment it passes through to the worker's bootstrap:
#   NEED_EXA=1        write ~/.exa_env on that worker
#   CKPTS="..."       S3 URIs to stage into ~/ckpt
#   DATASETS="..."    S3 URIs or prefixes to stage into ~/data
#   CODE_KEY=...      pin a specific code snapshot instead of code/LATEST
set -euo pipefail

export AWS_PROFILE="${AWS_PROFILE:-chronos}"
REGION="${AWS_REGION:-us-east-1}"
BUCKET="${BUCKET:-s3://decoupled-reasoner-009398924577}"
AMI="${AMI:-ami-0eb4d8bc9eb48d8ae}"           # Deep Learning OSS Nvidia PyTorch 2.12 AL2023
TYPE="${TYPE:-g6e.xlarge}"
SG="${SG:-sg-05ae7cbcedfdccff3}"
PROFILE_ARN="${PROFILE_ARN:-arn:aws:iam::009398924577:instance-profile/decoupled-reasoner-ec2}"
ROOT_GB="${ROOT_GB:-200}"
QUOTA_CODE=L-DB2E81BA

N="${1:?usage: launch_worker.sh <n> [az ...]}"
shift || true
NAME="nrm-worker-$N"

# subnet per zone, all in vpc-0d0b1709b15f7d882
subnet_for() {
  case "$1" in
    us-east-1a) echo subnet-02181846286b1162e;;
    us-east-1b) echo subnet-0f69a93d042ff2313;;
    us-east-1c) echo subnet-0618688cf536c586e;;
    us-east-1d) echo subnet-065dac9e35b255773;;
    us-east-1e) echo subnet-09d89e750863c8c0e;;
    us-east-1f) echo subnet-019942fb8eda1e2c1;;
    *) return 1;;
  esac
}
AZS=("$@")
[ ${#AZS[@]} -gt 0 ] || AZS=(us-east-1d us-east-1b us-east-1a us-east-1f us-east-1c us-east-1e)

# ------------------------------------------------------------------- quota gate
QUOTA=$(aws service-quotas get-service-quota --service-code ec2 --quota-code "$QUOTA_CODE" \
        --region "$REGION" --query 'Quota.Value' --output text)
USED=$(aws ec2 describe-instances --region "$REGION" \
        --filters "Name=instance-state-name,Values=running,pending" \
        --query 'Reservations[].Instances[?starts_with(InstanceType,`g`)||starts_with(InstanceType,`vt`)].[CpuOptions.CoreCount,CpuOptions.ThreadsPerCore]' \
        --output text | awk '{s+=$1*$2} END {print s+0}')
WANT=$(aws ec2 describe-instance-types --region "$REGION" --instance-types "$TYPE" \
        --query 'InstanceTypes[0].VCpuInfo.DefaultVCpus' --output text)
echo "G and VT vCPU quota $QUOTA, in use $USED, this launch needs $WANT"
if [ $(( USED + WANT )) -gt "${QUOTA%.*}" ]; then
  echo "refusing to launch $NAME: would exceed the quota" >&2
  exit 2
fi

if aws ec2 describe-instances --region "$REGION" \
     --filters "Name=tag:Name,Values=$NAME" "Name=instance-state-name,Values=running,pending" \
     --query 'Reservations[].Instances[].InstanceId' --output text | grep -q i-; then
  echo "refusing to launch: $NAME is already running" >&2
  exit 3
fi

# --------------------------------------------------------------- worker user-data
# cloud-init runs as root. The bootstrap itself runs as ec2-user so the files it
# writes are owned by the account every lane logs in as.
UD=$(mktemp)
cat > "$UD" <<CLOUDINIT
#!/bin/bash
exec >>/var/log/worker-userdata.log 2>&1
set -x
export PATH=/usr/local/bin:/usr/bin:/bin:\$PATH
for i in \$(seq 1 30); do command -v aws >/dev/null && break; sleep 5; done
aws s3 cp $BUCKET/code/bootstrap_worker.sh /home/ec2-user/bootstrap_worker.sh --region $REGION
chown ec2-user:ec2-user /home/ec2-user/bootstrap_worker.sh
chmod 0755 /home/ec2-user/bootstrap_worker.sh
runuser -l ec2-user -c 'WORKER_NAME=$NAME NEED_EXA=${NEED_EXA:-0} CODE_KEY="${CODE_KEY:-}" CKPTS="${CKPTS:-}" DATASETS="${DATASETS:-}" bash /home/ec2-user/bootstrap_worker.sh'
CLOUDINIT

BDM="[{\"DeviceName\":\"/dev/xvda\",\"Ebs\":{\"VolumeSize\":$ROOT_GB,\"VolumeType\":\"gp3\",\"DeleteOnTermination\":true}}]"
TAGS="ResourceType=instance,Tags=[{Key=Name,Value=$NAME},{Key=role,Value=nrm-worker},{Key=fleet,Value=decoupled-reasoner}]"

for AZ in "${AZS[@]}"; do
  SUBNET=$(subnet_for "$AZ") || { echo "unknown zone $AZ, skipping"; continue; }
  echo "trying $AZ ($SUBNET)"
  OUT=$(aws ec2 run-instances --region "$REGION" \
      --image-id "$AMI" --instance-type "$TYPE" --count 1 \
      --subnet-id "$SUBNET" --security-group-ids "$SG" \
      --iam-instance-profile "Arn=$PROFILE_ARN" \
      --block-device-mappings "$BDM" \
      --metadata-options "HttpTokens=required,HttpPutResponseHopLimit=2" \
      --tag-specifications "$TAGS" \
      --user-data "file://$UD" \
      --query 'Instances[0].InstanceId' --output text 2>&1) && {
    rm -f "$UD"
    echo "launched $NAME as $OUT in $AZ"
    echo "poll readiness with: bash scripts/fleet_status.sh"
    exit 0
  }
  case "$OUT" in
    *InsufficientInstanceCapacity*|*Unsupported*|*capacity*)
      echo "  no capacity in $AZ";;
    *) echo "  $OUT";;
  esac
done

rm -f "$UD"
echo "no zone had capacity for $TYPE" >&2
exit 1
