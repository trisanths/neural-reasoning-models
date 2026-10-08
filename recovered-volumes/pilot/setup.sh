#!/bin/bash
set -x
export HOME=/home/ec2-user HF_HOME=/mnt/nvme/hf PATH=/home/ec2-user/.local/bin:$PATH
cd /home/ec2-user/decoupled-reasoner
git config core.fileMode false
git checkout -b pilot/acq-bench
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync 2>&1 | tail -5
uv venv -p 3.12 /mnt/nvme/vllm-venv
VIRTUAL_ENV=/mnt/nvme/vllm-venv uv pip install vllm datasets 2>&1 | tail -3
/mnt/nvme/vllm-venv/bin/python -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__, torch.cuda.is_available())"
for m in LiquidAI/LFM2.5-350M-Base LiquidAI/LFM2.5-350M Qwen/Qwen3-0.6B-Base Qwen/Qwen3-0.6B Qwen/Qwen3-1.7B-Base Qwen/Qwen3-1.7B Qwen/Qwen3-4B Qwen/Qwen3-8B; do
  /mnt/nvme/vllm-venv/bin/hf download $m --exclude "*.pth" "original/*" > /dev/null 2>&1 && echo "OK $m" || echo "FAIL $m"
done
/mnt/nvme/vllm-venv/bin/python -c "from datasets import load_dataset; d=load_dataset('akariasai/PopQA', split='test'); print('popqa', len(d), d.column_names)"
echo SETUP_DONE
