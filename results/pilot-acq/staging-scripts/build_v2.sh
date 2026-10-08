#!/bin/bash
# Rebuild the pilot instrument after the review: floor pools, items, smoke set, PopQA.
set -e
export PATH=/home/ec2-user/.local/bin:$PATH
cd /home/ec2-user/decoupled-reasoner
D=/mnt/nvme/pilot/items
date -u +%FT%TZ
uv run python scripts/pilot_items.py --manifests /mnt/nvme/pilot/data-manifests \
  --floor-table $D/floor_table_v2.json --out $D/items_v2.jsonl
date -u +%FT%TZ
PYTHONHASHSEED=7 uv run python scripts/pilot_items.py --manifests /mnt/nvme/pilot/data-manifests \
  --floor-table $D/floor_table_v2.json --out /mnt/nvme/pilot/dev/items_v2_hashseed7.jsonl > /dev/null
uv run python scripts/pilot_items.py --smoke --manifests /mnt/nvme/pilot/data-manifests \
  --floor-table $D/floor_table_v2.json --out /mnt/nvme/pilot/smoke/items_smoke_v2.jsonl
HF_HOME=/mnt/nvme/hf HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 /mnt/nvme/vllm-venv/bin/python \
  scripts/pilot_popqa.py --out $D/popqa_fc_v2.jsonl 2>&1 | grep -v "cached\|Warning"
sha256sum $D/items_v2.jsonl /mnt/nvme/pilot/dev/items_v2_hashseed7.jsonl \
  /mnt/nvme/pilot/smoke/items_smoke_v2.jsonl $D/popqa_fc_v2.jsonl $D/floor_table_v2.json
date -u +%FT%TZ
echo BUILD_DONE
