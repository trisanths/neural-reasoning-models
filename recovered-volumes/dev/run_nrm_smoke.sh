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
  --out-dir /home/ec2-user/runs/nrm-bench/smoke \
  --model-name smoke-350md-401 \
  --parquet-dir /home/ec2-user/data/regime_a/parquet \
  --n-episodes 8 --n-synthetic 4 --n-bundles 4 --n-scrubbed 3 --n-real 3 \
  --api-budget 20
echo SMOKE-DONE
