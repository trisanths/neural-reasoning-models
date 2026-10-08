#!/bin/bash
# After the review fixes: likelihood check, smoke run, smoke report, throughput probe.
export HF_HOME=/mnt/nvme/hf HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1
export PATH=/home/ec2-user/.local/bin:$PATH
cd /home/ec2-user/decoupled-reasoner
PY=/mnt/nvme/vllm-venv/bin/python
I=/mnt/nvme/pilot/items
S3=s3://decoupled-reasoner-009398924577/runs/pilot-acq
date -u +%FT%TZ; echo "== ll_check"
for m in lfm2.5-350m-base qwen3-0.6b-base; do
  $PY /mnt/nvme/pilot/dev/ll_check2.py $m 200 $I/popqa_fc_v2.jsonl > /mnt/nvme/pilot/dev/ll_check2_$m.log 2>&1
  grep '^{"model"' /mnt/nvme/pilot/dev/ll_check2_$m.log
  pkill -u ec2-user -f "VLLM::EngineCore" ; sleep 5
done
date -u +%FT%TZ; echo "== smoke"
mkdir -p /mnt/nvme/pilot/smoke_v2
$PY scripts/pilot_run.py --items /mnt/nvme/pilot/smoke/items_smoke_v2.jsonl \
  --popqa $I/popqa_fc_v2.jsonl --popqa-limit 200 \
  --out /mnt/nvme/pilot/smoke_v2/records --s3 $S3/smoke_v2/records \
  --models lfm2.5-350m-base,qwen3-0.6b > /mnt/nvme/pilot/smoke_v2/run.log 2>&1
echo "smoke exit $?"
uv run python scripts/pilot_report.py --items /mnt/nvme/pilot/smoke/items_smoke_v2.jsonl \
  --popqa $I/popqa_fc_v2.jsonl --records /mnt/nvme/pilot/smoke_v2/records \
  --out /mnt/nvme/pilot/smoke_v2/report
echo "report exit $?"
aws s3 cp --quiet --recursive /mnt/nvme/pilot/smoke_v2/report $S3/smoke_v2/report
date -u +%FT%TZ; echo "== probe"
mkdir -p /mnt/nvme/pilot/probe_v2
$PY scripts/pilot_run.py --items $I/items_v2.jsonl \
  --out /mnt/nvme/pilot/probe_v2 --s3 $S3/probe_v2 \
  --probe 384 --skip-popqa --models all > /mnt/nvme/pilot/probe_v2/probe.log 2>&1
echo "probe exit $?"
date -u +%FT%TZ
echo GPU_V2_DONE
