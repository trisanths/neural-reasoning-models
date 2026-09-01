#!/usr/bin/env bash
# Take a fresh Deep Learning AMI instance to a working state, unattended.
#
# Run as ec2-user. It is safe to run again on a box that is already set up; each
# step checks for its own result first. Everything it does is logged to
# ~/bootstrap.log, and it finishes by writing ~/BOOTSTRAP_OK (or ~/BOOTSTRAP_FAILED),
# which is what a launcher polls to know the box is ready.
#
# Configuration comes from the environment, so user-data or an SSM call can set it:
#   WORKER_NAME   label recorded in the marker file            (default: hostname)
#   CODE_KEY      code snapshot to unpack                      (default: read code/LATEST)
#   CKPTS         space separated S3 URIs to pull into ~/ckpt  (default: none)
#   DATASETS      space separated S3 URIs or prefixes into ~/data (default: none)
#   NEED_EXA      1 to write ~/.exa_env from Parameter Store   (default: 0)
#   BUCKET        project bucket                               (default: the one below)
#
# WARNING about instance-store NVMe. If the instance has one it is mounted at
# /mnt/nvme and the large-artifact directories are pointed at it. That disk is
# EPHEMERAL: everything on it disappears when the instance stops, and it does not
# come back on start. Never leave the only copy of a result there. Push anything
# worth keeping to S3.
set -uo pipefail

# Unpacking the code snapshot overwrites this file when it is run from the repo
# copy, and bash reads a script as it executes it, so the rest of the run would
# come from whatever bytes landed at those offsets. Work from a copy instead.
if [ "${BOOTSTRAP_RELOCATED:-0}" != "1" ]; then
  _self=$(mktemp /tmp/bootstrap_worker.XXXXXX)
  cat "$0" > "$_self"
  BOOTSTRAP_RELOCATED=1 BOOTSTRAP_SELF="$_self" exec bash "$_self" "$@"
fi
[ -n "${BOOTSTRAP_SELF:-}" ] && trap 'rm -f "$BOOTSTRAP_SELF"' EXIT

BUCKET="${BUCKET:-s3://decoupled-reasoner-009398924577}"
REGION="${AWS_REGION:-us-east-1}"
HOME_DIR="${HOME:-/home/ec2-user}"
REPO="$HOME_DIR/decoupled-reasoner"
LOG="$HOME_DIR/bootstrap.log"
OK="$HOME_DIR/BOOTSTRAP_OK"
FAILED="$HOME_DIR/BOOTSTRAP_FAILED"
NVME=/mnt/nvme
WORKER_NAME="${WORKER_NAME:-$(hostname)}"
NEED_EXA="${NEED_EXA:-0}"
CKPTS="${CKPTS:-}"
DATASETS="${DATASETS:-}"
TOKENIZER_KEY="${TOKENIZER_KEY:-data/tokenizer_v2.json}"
EXA_PARAM="${EXA_PARAM:-/decoupled-reasoner/exa-api-key}"
UV="$HOME_DIR/.local/bin/uv"
START=$(date +%s)

exec >>"$LOG" 2>&1
rm -f "$OK" "$FAILED"

say() { echo "[$(date -u +%FT%TZ)] $*"; }
die() {
  say "FAILED: $*"
  printf '{"worker":"%s","failed_at":"%s","stage":"%s"}\n' \
    "$WORKER_NAME" "$(date -u +%FT%TZ)" "$*" > "$FAILED"
  exit 1
}

say "=== bootstrap start on $WORKER_NAME ($(uname -r)) ==="

# ---------------------------------------------------------------- instance store
# The root volume filling up has killed training lanes on this project before, so
# anything big goes on the instance store when the instance type has one.
NVME_STATE=absent
if mountpoint -q "$NVME"; then
  NVME_STATE=already-mounted
  say "instance store already mounted at $NVME"
else
  DEV=""
  for d in /dev/disk/by-id/nvme-Amazon_EC2_NVMe_Instance_Storage_*; do
    case "$d" in *-part[0-9]*) continue;; esac
    [ -b "$d" ] || continue
    DEV=$(readlink -f "$d"); break
  done
  if [ -n "$DEV" ]; then
    say "found instance store $DEV"
    if ! sudo blkid "$DEV" >/dev/null 2>&1; then
      if command -v mkfs.xfs >/dev/null 2>&1; then
        sudo mkfs.xfs -f -q "$DEV" || die "mkfs.xfs on $DEV"
      else
        sudo mkfs.ext4 -F -q -m 0 "$DEV" || die "mkfs.ext4 on $DEV"
      fi
      say "formatted $DEV"
    fi
    sudo mkdir -p "$NVME"
    sudo mount "$DEV" "$NVME" || die "mount $DEV on $NVME"
    sudo chown "$(id -u):$(id -g)" "$NVME"
    NVME_STATE=mounted
    say "mounted $DEV at $NVME ($(df -h "$NVME" | awk 'NR==2{print $2}') EPHEMERAL)"
  else
    say "no instance store on this instance type, everything stays on the root volume"
  fi
fi

# Point the large-artifact directories at the instance store when there is one.
# The names match what the project's scripts already expect, both under $HOME and
# inside the repo, so nothing else has to know where the bytes actually live.
link_dir() {  # link_dir <path> <nvme-subdir>
  local path="$1" sub="$2"
  if [ "$NVME_STATE" = absent ]; then
    mkdir -p "$path"; return
  fi
  mkdir -p "$NVME/$sub"
  if [ -L "$path" ]; then return; fi
  if [ -d "$path" ]; then
    # Move anything already there instead of hiding it behind a symlink.
    cp -an "$path/." "$NVME/$sub/" 2>/dev/null || true
    rm -rf "$path"
  fi
  ln -sfn "$NVME/$sub" "$path"
}

for d in data runs results logs ckpt; do
  link_dir "$HOME_DIR/$d" "$d"
done

# ------------------------------------------------------------------------- uv
if [ ! -x "$UV" ]; then
  say "installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh || die "uv install"
fi
export PATH="$HOME_DIR/.local/bin:$PATH"
say "uv $($UV --version)"

# ----------------------------------------------------------------------- code
if [ -z "${CODE_KEY:-}" ]; then
  CODE_KEY=$(aws s3 cp "$BUCKET/code/LATEST" - --region "$REGION" 2>/dev/null | tr -d '[:space:]')
  [ -n "$CODE_KEY" ] || die "cannot read $BUCKET/code/LATEST and CODE_KEY was not set"
fi
say "code snapshot $CODE_KEY"
TARBALL="/tmp/$(basename "$CODE_KEY")"
aws s3 cp "$BUCKET/$CODE_KEY" "$TARBALL" --region "$REGION" --quiet || die "download $CODE_KEY"
mkdir -p "$REPO"
tar xzf "$TARBALL" -C "$REPO" || die "unpack $CODE_KEY"
rm -f "$TARBALL"
COMMIT=$(basename "$CODE_KEY" .tar.gz | sed 's/^repo-//')
printf '%s\n' "$COMMIT" > "$REPO/.snapshot_commit"
say "unpacked $(find "$REPO" -type f | wc -l) files at commit $COMMIT"

# The repo's own generated trees are not in the snapshot. Create them, on the
# instance store when there is one.
for d in data results runs logs; do
  link_dir "$REPO/$d" "repo-$d"
done

# ------------------------------------------------------------------ python env
# uv.lock is in the snapshot, so --frozen gives every worker the same resolution.
cd "$REPO" || die "no repo at $REPO"
say "uv sync --frozen (this is the slow step, torch is about 3 GB)"
if ! "$UV" sync --frozen; then
  die "uv sync"
fi
PYV=$("$UV" run python -c 'import sys;print(sys.version.split()[0])' 2>/dev/null)
TORCHV=$("$UV" run python -c 'import torch;print(torch.__version__)' 2>/dev/null)
say "python $PYV, torch $TORCHV"

# --------------------------------------------------------------------- payload
mkdir -p "$HOME_DIR/data" "$HOME_DIR/ckpt"
if [ ! -s "$HOME_DIR/data/$(basename "$TOKENIZER_KEY")" ]; then
  aws s3 cp "$BUCKET/$TOKENIZER_KEY" "$HOME_DIR/data/$(basename "$TOKENIZER_KEY")" \
    --region "$REGION" --quiet || die "tokenizer $TOKENIZER_KEY"
fi
say "tokenizer at $HOME_DIR/data/$(basename "$TOKENIZER_KEY")"

for u in $CKPTS; do
  case "$u" in s3://*) src="$u";; *) src="$BUCKET/$u";; esac
  # Half the runs call their checkpoint final.pt, so a bare basename would make
  # two different models collide in ~/ckpt. Keep the run name on the front.
  base=$(basename "$src")
  case "$base" in
    final.pt|latest.pt|model.pt|best.pt) base="$(basename "$(dirname "$src")")-$base";;
  esac
  dst="$HOME_DIR/ckpt/$base"
  if [ -s "$dst" ]; then say "checkpoint already present: $dst"; continue; fi
  say "pulling checkpoint $src"
  aws s3 cp "$src" "$dst" --region "$REGION" --quiet || die "checkpoint $src"
  say "  $(du -h "$dst" | cut -f1) $dst"
done

for u in $DATASETS; do
  case "$u" in s3://*) src="$u";; *) src="$BUCKET/$u";; esac
  case "$src" in
    */) dst="$HOME_DIR/data/$(basename "$src")"
        say "syncing dataset prefix $src"
        aws s3 sync "$src" "$dst" --region "$REGION" --quiet || die "dataset $src";;
    *)  dst="$HOME_DIR/data/$(basename "$src")"
        [ -s "$dst" ] && { say "dataset already present: $dst"; continue; }
        say "pulling dataset $src"
        aws s3 cp "$src" "$dst" --region "$REGION" --quiet || die "dataset $src";;
  esac
done

# ------------------------------------------------------------------- exa key
# Only the lanes that call Exa get the key, and it comes from Parameter Store via
# the instance role, so it is never typed into a launch command or a log.
if [ "$NEED_EXA" = "1" ]; then
  umask 077
  KEY=$(aws ssm get-parameter --name "$EXA_PARAM" --with-decryption \
        --region "$REGION" --query Parameter.Value --output text 2>/dev/null)
  [ -n "$KEY" ] && [ "$KEY" != "None" ] || die "cannot read $EXA_PARAM"
  printf 'export EXA_API_KEY=%s\n' "$KEY" > "$HOME_DIR/.exa_env"
  chmod 600 "$HOME_DIR/.exa_env"
  unset KEY
  grep -q 'exa_env' "$HOME_DIR/.bashrc" 2>/dev/null || \
    echo '[ -f ~/.exa_env ] && . ~/.exa_env' >> "$HOME_DIR/.bashrc"
  umask 022
  say "wrote ~/.exa_env mode 600"
else
  # Only the lanes that ask for it get to hold the key, so a worker that stops
  # needing it stops having it.
  rm -f "$HOME_DIR/.exa_env"
  say "no Exa key requested for this worker"
fi

# ---------------------------------------------------------------------- checks
GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
[ -n "$GPU" ] || die "no GPU visible to nvidia-smi"
CUDA_OK=$("$UV" run python -c 'import torch;print(int(torch.cuda.is_available()))' 2>/dev/null)
[ "$CUDA_OK" = "1" ] || die "torch cannot see the GPU"
say "GPU $GPU, torch.cuda ok"

# Remind anyone who logs in that the big directories evaporate on stop.
if [ "$NVME_STATE" != absent ]; then
  grep -q 'instance store' "$HOME_DIR/.bashrc" 2>/dev/null || cat >> "$HOME_DIR/.bashrc" <<'RC'
# ~/data ~/runs ~/results ~/logs ~/ckpt live on the instance store at /mnt/nvme.
# That disk is EPHEMERAL and is wiped when the instance stops. Sync anything you
# care about to S3.
RC
fi

ELAPSED=$(( $(date +%s) - START ))
cat > "$OK" <<JSON
{
  "worker": "$WORKER_NAME",
  "ready_utc": "$(date -u +%FT%TZ)",
  "bootstrap_seconds": $ELAPSED,
  "code_key": "$CODE_KEY",
  "commit": "$COMMIT",
  "repo": "$REPO",
  "python": "$PYV",
  "torch": "$TORCHV",
  "gpu": "$GPU",
  "instance_store": "$NVME_STATE",
  "scratch": "$([ "$NVME_STATE" = absent ] && echo none || echo $NVME)",
  "exa_env": $([ "$NEED_EXA" = "1" ] && echo true || echo false)
}
JSON
say "=== bootstrap ok in ${ELAPSED}s, wrote $OK ==="
cat "$OK"
