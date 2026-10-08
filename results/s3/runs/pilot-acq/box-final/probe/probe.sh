#!/bin/bash
# Throughput probe on the full item set: generation only, nothing graded or recorded.
export HF_HOME=/mnt/nvme/hf HF_HUB_OFFLINE=1
cd /home/ec2-user/decoupled-reasoner
/mnt/nvme/vllm-venv/bin/python scripts/pilot_run.py --items /mnt/nvme/pilot/items/items.jsonl \
  --out /mnt/nvme/pilot/probe --s3 s3://decoupled-reasoner-009398924577/runs/pilot-acq/probe \
  --probe 384 --skip-popqa --models all
echo PROBE_DONE
