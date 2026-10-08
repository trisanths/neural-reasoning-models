#!/bin/bash
export HOME=/home/ec2-user HF_HOME=/mnt/nvme/hf HF_HUB_ENABLE_HF_TRANSFER=0
for m in LiquidAI/LFM2.5-350M-Base LiquidAI/LFM2.5-350M Qwen/Qwen3-0.6B-Base Qwen/Qwen3-0.6B Qwen/Qwen3-1.7B-Base Qwen/Qwen3-1.7B Qwen/Qwen3-4B Qwen/Qwen3-8B; do
  /mnt/nvme/vllm-venv/bin/hf download $m --exclude "*.pth" --exclude "original/*" > /mnt/nvme/pilot/dl_$(basename $m).log 2>&1 && echo "OK $m" || echo "FAIL $m"
done
echo DL_DONE
