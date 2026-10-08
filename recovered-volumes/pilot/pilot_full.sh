#!/bin/bash
# Full pilot run, then the report, then mirror and stop this box so it does not sit idle.
cd /home/ec2-user/decoupled-reasoner
export HOME=/home/ec2-user HF_HOME=/mnt/nvme/hf HF_HUB_OFFLINE=1 PATH=/home/ec2-user/.local/bin:$PATH
B=s3://decoupled-reasoner-009398924577/runs/pilot-acq
date -u +%FT%TZ > /mnt/nvme/pilot/run.started
/mnt/nvme/vllm-venv/bin/python scripts/pilot_run.py --items /mnt/nvme/pilot/items/items_v2.jsonl --popqa /mnt/nvme/pilot/items/popqa_fc_v2.jsonl --out /mnt/nvme/pilot/records --s3 $B/records --models all > /mnt/nvme/pilot/run.log 2>&1
rc=$?
echo "run exit $rc" >> /mnt/nvme/pilot/run.log
uv run python scripts/pilot_report.py --items /mnt/nvme/pilot/items/items_v2.jsonl --popqa /mnt/nvme/pilot/items/popqa_fc_v2.jsonl --records /mnt/nvme/pilot/records --out /mnt/nvme/pilot/report > /mnt/nvme/pilot/report.log 2>&1
echo "report exit $?" >> /mnt/nvme/pilot/report.log
git bundle create /mnt/nvme/pilot/pilot.bundle main..pilot/acq-bench
aws s3 sync /mnt/nvme/pilot/report $B/report --only-show-errors
aws s3 cp /mnt/nvme/pilot/run.log $B/run.log --only-show-errors
aws s3 cp /mnt/nvme/pilot/report.log $B/report.log --only-show-errors
aws s3 cp /mnt/nvme/pilot/pilot.bundle $B/pilot.bundle --only-show-errors
aws s3 sync /mnt/nvme/pilot $B/box-final --exclude "hf/*" --exclude "*.bundle" --only-show-errors
echo "run=$rc $(date -u +%FT%TZ)" | aws s3 cp - $B/DONE
sudo shutdown -h +2
