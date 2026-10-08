#!/bin/bash
set -euo pipefail
cd /home/ec2-user/decoupled-reasoner
EXA_API_KEY=$(aws ssm get-parameter --region us-east-1 \
  --name /decoupled-reasoner/exa-api-key --with-decryption \
  --query Parameter.Value --output text)
export EXA_API_KEY
uv run python -m scripts.run_nrm_bench \
  --ckpt /home/ec2-user/runs/webdemo/ckpt-curve-350md-401.pt \
  --tokenizer /home/ec2-user/runs/tokenizer_v2/tokenizer_v2.json \
  --out-dir /home/ec2-user/runs/nrm-bench/dry \
  --model-name curve-350md-401 \
  --parquet-dir /home/ec2-user/data/regime_a/parquet \
  --n-episodes 60 --n-synthetic 60 \
  --n-bundles 20 --n-scrubbed 40 \
  --n-real 60 \
  --api-budget 300
echo DRY-DONE
