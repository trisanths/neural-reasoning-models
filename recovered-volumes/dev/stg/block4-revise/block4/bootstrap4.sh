#!/bin/bash
# Bootstrap the block-4 p5.48xlarge (DLAMI, Amazon Linux 2023) for the E3
# data lane, the two looped-depth lanes, the 700m regime-E scale lane, and
# the two RL lanes. Run as root via SSM:
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
# The repo pin moved from d24d348 to 9f009ad. That is the commit that carries
# looped depth in src/train/model.py, the src/rl GRPO package, and the two RL
# block configs, none of which exist at d24d348, so the old pin would have
# launched four of the six lanes into an ImportError.
#
# Three stages are new. rl-assets downloads the two pretrained checkpoints
# the RL lanes start from onto scratch, byte-checked against their S3 sizes;
# they are 4.5 GB each and have no business on the root volume. rl-episodes
# settles the make-or-generate question in favour of make: the RL lanes read
# the pre-rendered ~/data/regime_c/heldout.jsonl that the data-small stage
# already fetched, so no lane depends on a generator at run time, and this
# stage counts its episodes and checks the two RL configs parse. loop-configs
# builds each looped lane's real config and instantiates the model on CPU, so
# a shape error surfaces here rather than on a GPU ten minutes into the block.
set -u

BUCKET=s3://decoupled-reasoner-009398924577
EXPECT_COMMIT="${EXPECT_COMMIT:-9f009ad}"
REPO_TGZ="${REPO_TGZ:-$BUCKET/code/repo-$EXPECT_COMMIT.tar.gz}"
B4_S3="$BUCKET/code/block4"
EC2_HOME=/home/ec2-user
REPO="$EC2_HOME/decoupled-reasoner"
B4="$EC2_HOME/block4"
DATA="$EC2_HOME/data"
SCRATCH=/mnt/scratch
SCRATCH_LABEL=b4scratch
RLCKPT="$SCRATCH/rlckpt"
REGIME_E_TOKENS=10200763819
REGIME_E2_TOKENS=10200778176
# From data/regime_e3/index.json, written by the block-3 render chain after
# its DONE line (target_reached, 398 chunks) and the E3_SYNCED marker.
REGIME_E3_TOKENS=13354983633
HELDOUT_BYTES=30611574
HELDOUT_EPISODES=5000
# The two RL base checkpoints, name and exact S3 byte size. Sizes read off
# the runs/curve listing on 2026-08-28.
RL_BASE_1=curve-350me-503
RL_BASE_1_BYTES=4505570155
RL_BASE_2=curve-350md-401
RL_BASE_2_BYTES=4505567723
RL_CKPT_NAME=ckpt-0026700.pt

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
mkdir -p "$SCRATCH/runs" "$RLCKPT"
chown ec2-user:ec2-user "$SCRATCH" "$SCRATCH/runs" "$RLCKPT"

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

# ---- rl-assets: the two pretrained checkpoints the RL lanes start from ----
# Chosen off the graded battery on interactive held-out accuracy and prose
# reading: curve-350me-503 is the best interactive of any graded model
# (0.8332, reading 0.1800) and curve-350md-401 is the best regime D seed
# (0.7878, reading 0.2000). Step 26700 for both. Downloaded by exact name
# rather than latest.pt so the provenance is in the filename, and verified by
# byte size so a short download cannot reach a lane.
fetch_rl_ckpt() {
  # $1 run name, $2 expected bytes
  local run=$1 want=$2 dest="$RLCKPT/$1-$RL_CKPT_NAME" have=0
  if [ -f "$dest" ]; then
    have=$(stat -c %s "$dest")
    if [ "$have" = "$want" ]; then
      echo "have $dest ($have bytes)"
      return 0
    fi
    echo "$dest is $have bytes, want $want; refetching"
  fi
  as_ec2 "aws s3 cp --only-show-errors $BUCKET/runs/curve/$run/$RL_CKPT_NAME '$dest'" \
    || return 1
  have=$(stat -c %s "$dest")
  [ "$have" = "$want" ] || { echo "FAIL $dest is $have bytes, want $want"; return 1; }
  echo "fetched $dest ($have bytes)"
}
fetch_rl_ckpt "$RL_BASE_1" "$RL_BASE_1_BYTES" || fail rl-assets
fetch_rl_ckpt "$RL_BASE_2" "$RL_BASE_2_BYTES" || fail rl-assets
df -h "$SCRATCH" | tail -1
done_ rl-assets

# ---- rl-episodes: pre-rendered episodes, not generation on the fly ----
# The RL lanes read ~/data/regime_c/heldout.jsonl, already downloaded and
# byte-checked by the data-small stage. Nothing is generated at run time, so
# no lane can stall on a generator or drift between the two lanes. This stage
# counts the episodes and loads both RL configs through their real dataclasses
# so a typo fails here and not on a GPU.
as_ec2 "cd '$REPO' && ~/.local/bin/uv run python - <<'PY'
import json, yaml
from src.rl.env import EnvConfig
from src.rl.grpo import GRPOConfig
n = sum(1 for line in open('$DATA/regime_c/heldout.jsonl') if line.strip())
print('episodes', n, '(recorded at build time: $HELDOUT_EPISODES)')
json.loads(open('$DATA/regime_c/heldout.jsonl').readline())
for path in ('configs/rl-350m-block.yaml', 'configs/rl-350m-block-narrow.yaml'):
    cfg = yaml.safe_load(open(path))
    env = EnvConfig(**cfg['env'])
    grpo = GRPOConfig(**cfg['grpo'])
    limit = cfg['tasks']['limit_episodes']
    assert limit <= n, f'{path} wants {limit} episodes, file holds {n}'
    print(path, 'group', grpo.group_size, 'prompts', grpo.prompts_per_step,
          'rollouts/step', grpo.group_size * grpo.prompts_per_step,
          'micro', grpo.micro_batch_size, 'kl', grpo.kl_coef,
          'steps', grpo.max_steps, 'max_len', env.max_len,
          'limit_episodes', limit)
PY" || fail rl-episodes
done_ rl-episodes

# ---- loop-configs: build each looped lane's config and the model ----
# make_run_config.py writes the same file resume4.sh will write, and the
# model is instantiated on CPU so a prelude+core+coda mismatch or a bad loop
# count fails here. Parameter counts are printed next to the standard 350m so
# the parameter match is visible in the bootstrap log.
as_ec2 "cd '$REPO' && ~/.local/bin/uv run python '$B4/make_run_config.py' \
    --base configs/350m-loop.yaml --out /tmp/boot-711.yaml --seed 711 \
    --micro-batch 8 --grad-accum 8 --ckpt-interval 1050 --compile 1 \
    --max-steps 26700 --loops 4 --loop-sampling 1,8 --backprop-last-k 2 \
    --grad-checkpoint 1" || fail loop-configs
as_ec2 "cd '$REPO' && ~/.local/bin/uv run python '$B4/make_run_config.py' \
    --base configs/350m-loop.yaml --out /tmp/boot-712.yaml --seed 712 \
    --micro-batch 8 --grad-accum 8 --ckpt-interval 1070 --compile 1 \
    --max-steps 26700 --loops 2 --loop-sampling 1,4 --backprop-last-k 2 \
    --grad-checkpoint 1" || fail loop-configs
as_ec2 "cd '$REPO' && ~/.local/bin/uv run python - <<'PY'
import yaml
from src.train.model import ModelConfig, TransformerLM
def report(tag, path):
    cfg = yaml.safe_load(open(path))['model']
    model = TransformerLM(ModelConfig(**cfg))
    total = sum(p.numel() for p in model.parameters())
    emb = sum(p.numel() for n, p in model.named_parameters() if 'embed' in n or 'lm_head' in n)
    rec = cfg.get('recurrent')
    depth = cfg['n_layers'] if not rec else (
        rec['prelude_layers'] + rec['core_layers'] * rec['loops'] + rec['coda_layers'])
    loops = rec['loops'] if rec else 1
    print(f'{tag}: total {total:,} non-embedding {total - emb:,} '
          f'unique layers {cfg[\"n_layers\"]} loops {loops} effective depth {depth}')
    return total
base = report('350m standard   ', 'configs/350m.yaml')
a = report('711 looped 4    ', '/tmp/boot-711.yaml')
b = report('712 looped 2    ', '/tmp/boot-712.yaml')
# The two looped lanes differ only by the loop conditioning table, which is
# sized by the top of the sampling range: 8 rows against 4 at 2 * d_model
# each, so 10,240 parameters.
print(f'711 minus 712 {a - b:,} parameters (the loop_film table)')
assert abs(a - b) / a < 0.001, 'the looped lanes differ by more than the film table'
for tag, n in (('711', a), ('712', b)):
    drift = abs(n - base) / base
    print(f'{tag} vs standard 350m parameter drift {drift:.4%}')
    assert drift < 0.01, f'{tag} parameter drift {drift:.4%} is over 1 percent'
PY" || fail loop-configs
done_ loop-configs

echo "next: sudo -u ec2-user bash -lc 'bash $B4/resume4.sh'"
echo "=== BOOTSTRAP4 DONE ==="
