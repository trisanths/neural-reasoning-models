#!/usr/bin/env bash
# Full experiment: baselines (floor + ceiling), pipeline, controls, results table.
#
# Usage: scripts/run_all.sh <task> <data_dir> <run_dir> [n_train] [epochs_per_stage] [max_latent_stage] [small_preset]
set -euo pipefail

TASK=${1:-compose}
DATA=${2:-data_c3}
RUNS=${3:-runs/exp}
NTRAIN=${4:-24000}
EPS=${5:-4}
MLS=${6:-3}
SMALL=${7:-xs}
PY=.venv/bin/python

mkdir -p "$RUNS"
COMMON="--task $TASK --data $DATA --n_train $NTRAIN --epochs_per_stage $EPS --max_latent_stage $MLS"

echo "=== Stage 0: baselines ==="
# Ceiling: big model reasoning latently on its own.
$PY -u scripts/train_baseline.py --preset big --mode coconut $COMMON --out "$RUNS/big_coconut"

# Floor + control 2: small model with the same number of latent steps.
$PY -u scripts/train_baseline.py --preset "$SMALL" --mode coconut $COMMON --out "$RUNS/small_coconut"

# Reference points: explicit chain of thought, and answering with no reasoning.
$PY -u scripts/train_baseline.py --preset "$SMALL" --mode cot $COMMON --out "$RUNS/small_cot"
$PY -u scripts/train_baseline.py --preset "$SMALL" --mode nocot $COMMON --out "$RUNS/small_nocot"

echo "=== Stages 1-3: cross-model pipeline ==="
$PY -u scripts/train_pipeline.py --task "$TASK" --data "$DATA" --n_train "$NTRAIN" \
    --max_latent_stage "$MLS" \
    --small_ckpt "$RUNS/small_coconut/model.pt" \
    --big_ckpt "$RUNS/big_coconut/model.pt" \
    --out "$RUNS/pipeline"

echo "=== Control 1: frozen RANDOM big model ==="
# If this matches the pipeline, the big model contributed nothing.
$PY -u scripts/train_pipeline.py --task "$TASK" --data "$DATA" --n_train "$NTRAIN" \
    --max_latent_stage "$MLS" \
    --small_ckpt "$RUNS/small_coconut/model.pt" \
    --big_ckpt "$RUNS/big_coconut/model.pt" \
    --out "$RUNS/pipeline_randbig" --random_big 1

echo "=== Results ==="
cat > "$RUNS/manifest.json" <<EOF
[
  {"name": "small, no reasoning",       "kind": "nocot",   "ckpt": "$RUNS/small_nocot/model.pt"},
  {"name": "small, explicit CoT",       "kind": "cot",     "ckpt": "$RUNS/small_cot/model.pt"},
  {"name": "small, Coconut (floor)",    "kind": "coconut", "ckpt": "$RUNS/small_coconut/model.pt"},
  {"name": "big, Coconut (ceiling)",    "kind": "coconut", "ckpt": "$RUNS/big_coconut/model.pt"},
  {"name": "CROSS-MODEL pipeline",      "kind": "pipeline",
   "ckpt": "$RUNS/pipeline/pipeline.pt",
   "small_ckpt": "$RUNS/small_coconut/model.pt", "big_ckpt": "$RUNS/big_coconut/model.pt"},
  {"name": "control: random big model", "kind": "pipeline",
   "ckpt": "$RUNS/pipeline_randbig/pipeline.pt",
   "small_ckpt": "$RUNS/small_coconut/model.pt", "big_ckpt": "$RUNS/big_coconut/model.pt",
   "random_big": true}
]
EOF

$PY -u scripts/results.py --task "$TASK" --manifest "$RUNS/manifest.json" --data "$DATA" \
    --out "$RUNS/results.json" --max_latent_stage "$MLS"
$PY -u scripts/report.py --results "$RUNS/results.json" --out "$RUNS/report.txt"
