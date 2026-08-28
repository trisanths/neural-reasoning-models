#!/usr/bin/env bash
# Data parallel training launcher.
#
# usage: scripts/train_ddp.sh CONFIG DATA_DIR OUT_DIR [GPUS] [extra cli args...]
#
#   CONFIG    yaml under configs/
#   DATA_DIR  shard directory holding index.json
#   OUT_DIR   run directory for checkpoints and loss.jsonl
#   GPUS      comma separated physical GPU ids, for example 4,5,6,7. Defaults
#             to every GPU nvidia-smi reports. nproc_per_node is the length of
#             this list, so the GPU list alone decides the world size.
#
# Anything after the GPU list is handed to src.train.cli, so --resume,
# --max-steps and --micro-batch-size work unchanged.
#
# The global batch in the config is sequences per optimizer step summed over
# ranks. Adding GPUs shortens each rank's gradient accumulation and leaves the
# tokens per step alone; src.train.distributed asserts that before step one and
# fails the run if the world size does not divide the global batch.
#
# Safe to background:
#   setsid nohup bash scripts/train_ddp.sh CONFIG DATA OUT 4,5,6,7 \
#     > OUT/train.log 2>&1 < /dev/null &
# It reads no stdin, needs no tty, and execs torchrun so the pid the caller
# holds is the one that owns the workers.
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "usage: $0 CONFIG DATA_DIR OUT_DIR [GPUS] [extra cli args...]" >&2
  exit 2
fi

CONFIG=$1
DATA_DIR=$2
OUT_DIR=$3
shift 3

GPUS=""
if [ "$#" -gt 0 ] && [[ "$1" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
  GPUS=$1
  shift
fi

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPO_ROOT"

if [ ! -f "$CONFIG" ]; then echo "no such config: $CONFIG" >&2; exit 2; fi
if [ ! -f "$DATA_DIR/index.json" ]; then echo "no index.json under $DATA_DIR" >&2; exit 2; fi
mkdir -p "$OUT_DIR"

if [ -n "$GPUS" ]; then
  export CUDA_VISIBLE_DEVICES="$GPUS"
elif [ -n "${CUDA_VISIBLE_DEVICES:-}" ]; then
  GPUS="$CUDA_VISIBLE_DEVICES"
else
  GPUS=$(nvidia-smi --query-gpu=index --format=csv,noheader | paste -sd, -)
  export CUDA_VISIBLE_DEVICES="$GPUS"
fi
NPROC=$(awk -F, '{print NF}' <<< "$GPUS")

PYTHON=${PYTHON:-}
if [ -z "$PYTHON" ]; then
  if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
    PYTHON="$REPO_ROOT/.venv/bin/python"
  else
    PYTHON=$(command -v python3)
  fi
fi
if ! "$PYTHON" -c "import torch" >/dev/null 2>&1; then
  echo "train_ddp: $PYTHON cannot import torch. Point PYTHON at the interpreter that can, for example PYTHON=$REPO_ROOT/.venv/bin/python" >&2
  exit 2
fi

# A free ephemeral port, so a launch never collides with a run already on the
# box. Override with DDP_MASTER_PORT to pin it.
if [ -z "${DDP_MASTER_PORT:-}" ]; then
  DDP_MASTER_PORT=$("$PYTHON" - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
)
fi

# One OMP thread per worker by default: torch spawns as many workers as GPUs on
# this node and they share the same cores.
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}
export NCCL_DEBUG=${NCCL_DEBUG:-WARN}
export PYTHONUNBUFFERED=1
export TORCH_NCCL_ASYNC_ERROR_HANDLING=${TORCH_NCCL_ASYNC_ERROR_HANDLING:-1}

echo "train_ddp: config=$CONFIG data=$DATA_DIR out=$OUT_DIR gpus=$GPUS nproc=$NPROC port=$DDP_MASTER_PORT"
echo "train_ddp: python=$PYTHON"

exec "$PYTHON" -m torch.distributed.run \
  --nnodes=1 \
  --nproc-per-node="$NPROC" \
  --rdzv-backend=c10d \
  --rdzv-endpoint="127.0.0.1:$DDP_MASTER_PORT" \
  -m src.train.cli \
  --config "$CONFIG" \
  --data "$DATA_DIR" \
  --out "$OUT_DIR" \
  "$@"
