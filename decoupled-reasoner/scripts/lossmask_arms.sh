#!/bin/bash
# Train the four loss masking arms back to back on one GPU.
#
#   usage: bash scripts/lossmask_arms.sh GPU DATA_DIR RUN_ROOT [MAX_STEPS]
#
# Every arm reads the same shards under the same seed and differs only in
# the lossmask.weights block of its config, which this script writes:
#
#   a  every factual span at 0.0     entities, numbers, dates, web anchors
#   b  numbers and dates at 0.0      times and quantities only
#   c  every factual span at 0.1     the same spans, discounted not removed
#   d  no weights                    the control, every token at one
set -eu
GPU="$1"; DATA="$2"; ROOT="$3"; STEPS="${4:-4000}"
cd "$(dirname "$0")/.."
mkdir -p "$ROOT" configs/lossmask

python3 - <<'PY'
import pathlib
base = pathlib.Path("configs/150m-lossmask.yaml").read_text()
head = base.split("lossmask:")[0]
arms = {
    "a": "lossmask:\n  weights:\n    entity: 0.0\n    number: 0.0\n"
         "    date: 0.0\n    web: 0.0\n",
    "b": "lossmask:\n  weights:\n    number: 0.0\n    date: 0.0\n",
    "c": "lossmask:\n  weights:\n    entity: 0.1\n    number: 0.1\n"
         "    date: 0.1\n    web: 0.1\n",
    "d": "lossmask:\n  weights: {}\n",
}
for name, block in arms.items():
    out = pathlib.Path("configs/lossmask") / f"150m-{name}.yaml"
    out.write_text(head + block)
    print(out)
PY

for ARM in a b c d; do
  OUT="$ROOT/lm-$ARM"
  if [ -f "$OUT/DONE" ]; then echo "arm $ARM already done"; continue; fi
  echo "=== arm $ARM starting $(date -Is) ==="
  CUDA_VISIBLE_DEVICES="$GPU" uv run python -m src.train.cli \
    --config "configs/lossmask/150m-$ARM.yaml" \
    --data "$DATA" --out "$OUT" --max-steps "$STEPS" --resume
  touch "$OUT/DONE"
  echo "=== arm $ARM done $(date -Is) ==="
done
echo "ALL_ARMS_DONE"
