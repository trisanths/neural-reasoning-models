#!/usr/bin/env bash
# One-shot setup for a fresh RunPod H100 (PyTorch template).
#
#   bash scripts/setup_pod.sh
#
# Put the repo and the HF cache on the persistent volume so a pod restart does
# not re-download 16GB of weights.
set -euo pipefail

VOL=${VOL:-/workspace}
export HF_HOME="$VOL/hf"
mkdir -p "$HF_HOME"

python -m pip install -q --upgrade pip
python -m pip install -q "transformers>=4.44" accelerate datasets peft bitsandbytes

python - <<'EOF'
import torch
print("torch", torch.__version__, "cuda", torch.cuda.is_available())
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print(f"{p.name}  {p.total_memory/1e9:.0f} GB  sm_{p.major}{p.minor}")
EOF

echo "HF_HOME=$HF_HOME  (add to ~/.bashrc so restarts reuse the cache)"

# Pre-pull the weights now rather than during the first training step.
python - <<'EOF'
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
for name in ["Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-7B"]:
    print("fetching", name, flush=True)
    AutoTokenizer.from_pretrained(name)
    AutoModelForCausalLM.from_pretrained(name, dtype=torch.bfloat16)
print("weights cached")
EOF

python -c "import sys; sys.path.insert(0,'.'); \
from src.hf_backbone import HFBackbone; print('adapter import OK')"

echo
echo "Next: bash scripts/run_tests.sh   (CPU-only, ~1 min, proves the port)"
