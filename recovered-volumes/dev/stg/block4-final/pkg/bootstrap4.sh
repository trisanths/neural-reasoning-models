#!/bin/bash
# Bootstrap the block-4 p5.48xlarge (DLAMI, Amazon Linux 2023) for the
# decoupled-reasoner E3 seeds and the 700m regime-E scale lane. Run as root
# via SSM:
#   aws s3 cp s3://decoupled-reasoner-009398924577/code/block4/bootstrap4.sh - | bash
# Same shape as bootstrap3 with the same lesson baked in: the instance-store
# NVMe is formatted and mounted at /mnt/scratch FIRST, and ~/runs becomes a
# symlink onto it BEFORE any download, so checkpoints can never land on the
# 300GB root volume. Block 4 downloads regimes E, E2, and E3 only; the
# defensive resume in resume4.sh syncs any other lane's data on demand.
# Regime E3 was rendered on the block-3 box; its S3 sync was confirmed
# (E3_SYNCED in ~/logs/e3_render.log there) and the manifest total recorded
# here on 2026-08-27 before this script shipped. Idempotent: every stage
# checks its own end state, so rerunning after a partial failure only redoes
# what is missing. Each stage ends with "=== STAGE <name> DONE|FAIL ===" and
# the script ends with "=== BOOTSTRAP4 DONE ===" or "=== BOOTSTRAP4 FAIL ===".
#
# Block 4 also provisions what the two GRPO lanes need: worldgen episodes
# generated here at a fresh seed, an eval slice of the regime C held-out
# file, and the two best pretrained checkpoints. It ends with a preflight
# that generates every pretraining lane's config and instantiates each model
# on the meta device, so a config that cannot build a model fails before any
# GPU is claimed.
set -u

BUCKET=s3://decoupled-reasoner-009398924577
EXPECT_COMMIT="${EXPECT_COMMIT:-d24d348}"
REPO_TGZ="${REPO_TGZ:-$BUCKET/code/repo-$EXPECT_COMMIT.tar.gz}"
B4_S3="$BUCKET/code/block4"
EC2_HOME=/home/ec2-user
REPO="$EC2_HOME/decoupled-reasoner"
B4="$EC2_HOME/block4"
DATA="$EC2_HOME/data"
SCRATCH=/mnt/scratch
SCRATCH_LABEL=b4scratch
REGIME_E_TOKENS=10200763819
REGIME_E2_TOKENS=10200778176
# From data/regime_e3/index.json, written by the block-3 render chain after
# its DONE line (target_reached, 398 chunks) and the E3_SYNCED marker.
REGIME_E3_TOKENS=13354983633
HELDOUT_BYTES=30611574
# RL episode provisioning. The seed is outside every render seed used so far,
# so the worlds are new to the pretrained policy.
RL_EPISODES="${RL_EPISODES:-4000}"
RL_EPISODE_SEED="${RL_EPISODE_SEED:-940828}"
RL_EVAL_EPISODES="${RL_EVAL_EPISODES:-200}"
RL_CKPT_DIR="$DATA/rlckpt"

as_ec2() { sudo -u ec2-user bash -lc "$1"; }

fail() {
  echo "=== STAGE $1 FAIL ==="
  echo "=== BOOTSTRAP4 FAIL ==="
  exit 1
}
done_() { echo "=== STAGE $1 DONE ==="; }

# ---- scratch: instance-store NVMe, before anything else ----
# Pick a large non-EBS nvme device: model reports EC2 instance storage,
# nothing mounted on it, and no filesystem signature. mkfs.xfs exactly one
# device; one 3.5T device is plenty for KEEP=1 checkpoint retention.
pick_instance_store() {
  local dev base model bytes
  for dev in /dev/nvme*n1; do
    [ -b "$dev" ] || continue
    base=$(basename "$dev")
    model=$(cat "/sys/block/$base/device/model" 2>/dev/null || true)
    case "$model" in *"Instance Storage"*) ;; *) continue ;; esac
    lsblk -no MOUNTPOINTS "$dev" 2>/dev/null | grep -q '[^[:space:]]' && continue
    blkid -p "$dev" > /dev/null 2>&1 && continue
    bytes=$(blockdev --getsize64 "$dev" 2>/dev/null || echo 0)
    [ "$bytes" -gt 1099511627776 ] || continue
    echo "$dev"
    return 0
  done
  return 1
}

if mountpoint -q "$SCRATCH"; then
  echo "scratch already mounted: $(findmnt -no SOURCE "$SCRATCH")"
else
  # A rerun that died between mkfs and mount finds the device by label.
  DEV=$(blkid -t "LABEL=$SCRATCH_LABEL" -o device 2>/dev/null | head -1)
  if [ -z "$DEV" ]; then
    DEV=$(pick_instance_store) || {
      echo "=== NO_INSTANCE_STORE: no unmounted signature-free EC2 instance-store nvme device found ==="
      lsblk -dn -o NAME,SIZE,TYPE,MOUNTPOINTS,MODEL
      fail scratch
    }
    echo "formatting $DEV as xfs (label $SCRATCH_LABEL)"
    mkfs.xfs -q -L "$SCRATCH_LABEL" "$DEV" || fail scratch
  else
    echo "reusing labeled device $DEV"
  fi
  mkdir -p "$SCRATCH"
  mount -o noatime "$DEV" "$SCRATCH" || fail scratch
fi
mkdir -p "$SCRATCH/runs"
chown ec2-user:ec2-user "$SCRATCH" "$SCRATCH/runs"

# ~/runs must point at scratch before any download.
if [ -L "$EC2_HOME/runs" ]; then
  [ "$(readlink -f "$EC2_HOME/runs")" = "$SCRATCH/runs" ] || fail scratch
elif [ -e "$EC2_HOME/runs" ]; then
  # A real directory here means something already wrote to the root volume;
  # move its contents onto scratch and replace it with the symlink.
  find "$EC2_HOME/runs" -mindepth 1 -maxdepth 1 -exec mv -t "$SCRATCH/runs/" {} + || fail scratch
  rmdir "$EC2_HOME/runs" || fail scratch
  ln -s "$SCRATCH/runs" "$EC2_HOME/runs"
  chown -h ec2-user:ec2-user "$EC2_HOME/runs"
else
  ln -s "$SCRATCH/runs" "$EC2_HOME/runs"
  chown -h ec2-user:ec2-user "$EC2_HOME/runs"
fi
as_ec2 "mkdir -p ~/data ~/logs && touch ~/runs/.scratch-ok" || fail scratch
df -h "$EC2_HOME" "$SCRATCH" | awk 'NR==1 || $1!="Filesystem"' | sort -u
done_ scratch

# ---- uv ----
if as_ec2 "test -x ~/.local/bin/uv"; then
  echo "uv already installed: $(as_ec2 '~/.local/bin/uv --version')"
else
  as_ec2 "curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null 2>&1" || fail uv
fi
as_ec2 "~/.local/bin/uv --version" || fail uv
done_ uv

# ---- repo ----
if [ "$(cat "$REPO/.bootstrap-commit" 2>/dev/null)" = "$EXPECT_COMMIT" ]; then
  echo "repo already at $EXPECT_COMMIT"
else
  as_ec2 "mkdir -p '$REPO' && aws s3 cp --only-show-errors '$REPO_TGZ' /tmp/repo.tgz \
    && tar xzf /tmp/repo.tgz -C '$REPO' && echo '$EXPECT_COMMIT' > '$REPO/.bootstrap-commit'" \
    || fail repo
fi
done_ repo

# ---- python env ----
as_ec2 "cd '$REPO' && ~/.local/bin/uv sync --quiet" || fail uv-sync
as_ec2 "cd '$REPO' && ~/.local/bin/uv run python -c 'import torch; print(\"torch\", torch.__version__, \"cuda\", torch.cuda.is_available())'" \
  || fail uv-sync
done_ uv-sync

# ---- block4 package ----
as_ec2 "aws s3 sync --only-show-errors '$B4_S3' '$B4'" || fail block4-package
done_ block4-package

# ---- data: tokenizer + warm-up + heldout ----
# The warm-up bin is not used by any block-4 lane; it stays here so a
# defensive resume of a block-3 straggler with --warmup-bin cannot miss it.
as_ec2 "aws s3 cp --only-show-errors $BUCKET/data/tokenizer_v2.json '$DATA/' \
  && aws s3 cp --only-show-errors $BUCKET/data/proc_warmup_15m.bin '$DATA/' \
  && aws s3 cp --only-show-errors $BUCKET/data/proc_warmup_15m.bin.meta.json '$DATA/' \
  && mkdir -p '$DATA/regime_c' \
  && aws s3 cp --only-show-errors $BUCKET/data/regime_c/heldout.jsonl '$DATA/regime_c/'" \
  || fail data-small
WARMUP_BYTES=$(stat -c %s "$DATA/proc_warmup_15m.bin")
[ "$WARMUP_BYTES" = "30000000" ] || fail data-small
echo "warm-up bin $WARMUP_BYTES bytes ($((WARMUP_BYTES / 2)) tokens)"
HB=$(stat -c %s "$DATA/regime_c/heldout.jsonl")
[ "$HB" = "$HELDOUT_BYTES" ] || fail data-small
echo "heldout.jsonl $HB bytes"
done_ data-small

# ---- data: regime E (merged chunk index, loads directly) ----
as_ec2 "aws s3 sync --only-show-errors $BUCKET/data/regime_e '$DATA/regime_e'" \
  || fail data-regime-e
as_ec2 "python3 '$B4/consolidate_regime_c.py' --verify-only '$DATA/regime_e' \
  --expect-tokens $REGIME_E_TOKENS" || fail data-regime-e
done_ data-regime-e

# ---- data: regime E2 (merged chunk index, loads directly) ----
as_ec2 "aws s3 sync --only-show-errors $BUCKET/data/regime_e2 '$DATA/regime_e2'" \
  || fail data-regime-e2
as_ec2 "python3 '$B4/consolidate_regime_c.py' --verify-only '$DATA/regime_e2' \
  --expect-tokens $REGIME_E2_TOKENS" || fail data-regime-e2
done_ data-regime-e2

# ---- data: regime E3 (merged chunk index, loads directly) ----
as_ec2 "aws s3 sync --only-show-errors $BUCKET/data/regime_e3 '$DATA/regime_e3'" \
  || fail data-regime-e3
as_ec2 "python3 '$B4/consolidate_regime_c.py' --verify-only '$DATA/regime_e3' \
  --expect-tokens $REGIME_E3_TOKENS" || fail data-regime-e3
done_ data-regime-e3

# ---- data: RL episodes ----
# The two GRPO lanes need worldgen episodes to train on and a held-out set to
# be scored against. Worldgen is procedural and seeded, so a seed no render
# has used gives worlds the pretrained policy has never seen; generation is
# under a second for thousands of episodes, which is why this is generated
# here rather than shipped. The eval slice is the head of the regime C
# held-out file the eval battery already uses, so the RL eval numbers land on
# the same scale as the battery's interactive heldout column.
as_ec2 "cd '$REPO' && ~/.local/bin/uv run python -m src.worldgen.cli \
  --episodes $RL_EPISODES --seed $RL_EPISODE_SEED --validate \
  --out '$DATA/rl_episodes.jsonl'" || fail rl-data
as_ec2 "head -n $RL_EVAL_EPISODES '$DATA/regime_c/heldout.jsonl' \
  > '$DATA/rl_eval_episodes.jsonl'" || fail rl-data
TRAIN_LINES=$(wc -l < "$DATA/rl_episodes.jsonl")
EVAL_LINES=$(wc -l < "$DATA/rl_eval_episodes.jsonl")
[ "$TRAIN_LINES" = "$RL_EPISODES" ] || fail rl-data
[ "$EVAL_LINES" = "$RL_EVAL_EPISODES" ] || fail rl-data
echo "rl episodes: $TRAIN_LINES train (seed $RL_EPISODE_SEED), $EVAL_LINES eval"
# Read both through the RL task loader, which is the only thing that proves
# the schema the lanes will actually parse.
as_ec2 "cd '$REPO' && ~/.local/bin/uv run python -c \"
from src.rl.env import load_tasks
from src.rl.cli import load_tokenizer
tok = load_tokenizer('$DATA/tokenizer_v2.json')
tr = load_tasks('$DATA/rl_episodes.jsonl', tok, limit_episodes=1500)
ev = load_tasks('$DATA/rl_eval_episodes.jsonl', tok, questions_per_episode=1)
print('rl task loader ok:', len(tr), 'train tasks,', len(ev), 'eval tasks')
assert len(tr) > 500 and len(ev) >= 96
\"" || fail rl-data
done_ rl-data

# ---- data: RL init checkpoints ----
# The two best pretrained lanes by interactive heldout accuracy: 503 at
# 0.8332 and 501 at 0.8250, both final at pretrain step 26700.
as_ec2 "mkdir -p '$RL_CKPT_DIR'" || fail rl-ckpt
for pair in "curve-350me-503:350me503-26700.pt" "curve-350me-501:350me501-26700.pt"; do
  LANE=${pair%%:*}
  DEST="$RL_CKPT_DIR/${pair##*:}"
  if [ -s "$DEST" ]; then
    echo "have $DEST ($(stat -c %s "$DEST") bytes)"
  else
    as_ec2 "aws s3 cp --only-show-errors $BUCKET/runs/curve/$LANE/ckpt-0026700.pt '$DEST'" \
      || fail rl-ckpt
  fi
  as_ec2 "cd '$REPO' && ~/.local/bin/uv run python -c \"
import torch
s = torch.load('$DEST', map_location='cpu', weights_only=False)
print('$LANE ckpt step', s.get('step'), 'keys', sorted(k for k in s)[:5])
assert s.get('step') == 26700 and 'model' in s and 'config' in s
\"" || fail rl-ckpt
done
done_ rl-ckpt

# ---- gpus ----
GPUS=$(nvidia-smi -L 2>/dev/null | grep -c '^GPU') || GPUS=0
echo "nvidia-smi reports $GPUS GPUs"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader 2>/dev/null
[ "$GPUS" = "8" ] || fail gpus
done_ gpus

# ---- decode spot-check: eyeball one random window per dataset ----
as_ec2 "cd '$REPO' && ~/.local/bin/uv run python '$B4/spotcheck_decode.py' \
  --tokenizer '$DATA/tokenizer_v2.json' --window 300 \
  regime_e='$DATA/regime_e' regime_e2='$DATA/regime_e2' regime_e3='$DATA/regime_e3' \
  warmup='$DATA/proc_warmup_15m.bin'" || fail spotcheck
done_ spotcheck

# ---- decode spot-check: one regime_e3 webret trace ----
# A webret episode opens with a world preamble whose domain line decodes as
# "domain: scrubbed_web" (src/scrub/web_retrieval.py DOMAIN). webret holds a
# 0.20 share of E3, so random 4000-token windows hit a preamble quickly;
# 40 attempts bounds the stage. The offset is printed by spotcheck_decode,
# so a hit is reproducible with --offset regime_e3=N.
WEBRET_OK=0
for i in $(seq 1 40); do
  SC=$(as_ec2 "cd '$REPO' && ~/.local/bin/uv run python '$B4/spotcheck_decode.py' \
    --tokenizer '$DATA/tokenizer_v2.json' --window 4000 \
    regime_e3='$DATA/regime_e3'" 2>/dev/null) || continue
  if printf '%s' "$SC" | grep -q "scrubbed_web"; then
    echo "webret trace found on attempt $i:"
    printf '%s\n' "$SC" | sed -n '1p'
    printf '%s\n' "$SC" | awk '/scrubbed_web/{f=1} f{print; c++} c>=40{exit}'
    WEBRET_OK=1
    break
  fi
  echo "attempt $i: window held no webret preamble, retrying"
done
[ "$WEBRET_OK" = "1" ] || fail spotcheck-webret
done_ spotcheck-webret

# ---- lane config preflight ----
# Generate every pretraining lane's config into a throwaway directory and
# instantiate each on the meta device. This is where a recurrent config that
# cannot build a model, or a lane whose global batch drifted from its base,
# fails: before any GPU is claimed, not twenty minutes into the block.
PRE=/tmp/lane-preflight
as_ec2 "rm -rf $PRE && mkdir -p $PRE" || fail preflight
preflight_lane() {
  # $1 lane, $2 base yaml, $3 micro, $4 accum, $5 ckpt, $6 steps, $7 extra
  echo "preflight $1:"
  as_ec2 "cd '$REPO' && ~/.local/bin/uv run python '$B4/make_run_config.py' \
    --base configs/$2 --out $PRE/$1.yaml --seed 1 --micro-batch $3 \
    --grad-accum $4 --ckpt-interval $5 --compile 1 --max-steps $6 $7" \
    || fail preflight
}
preflight_lane curve-350me3-701     350m.yaml      8 8  990 26700 ""
preflight_lane curve-350me3loop-711 350m-loop.yaml 4 16 500  9000 ""
preflight_lane curve-350me3loop-712 350m-loop.yaml 4 16 510  9000 \
  "--loops 2 --loop-sampling off"
preflight_lane curve-700me-721      700m.yaml      4 16 510 26700 ""
done_ preflight

echo "next: sudo -u ec2-user bash -lc 'bash $B4/resume4.sh'"
echo "=== BOOTSTRAP4 DONE ==="
