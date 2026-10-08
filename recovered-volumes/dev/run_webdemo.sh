#!/bin/bash
# Full web-demo driver: fetch checkpoints, run all three models both
# passes, merge the report, upload to S3. The Exa key is exported from
# SSM and never printed.
set -euo pipefail
cd ~/decoupled-reasoner
mkdir -p ~/runs/webdemo ~/logs
EXA_API_KEY=$(aws ssm get-parameter --region us-east-1 \
  --name /decoupled-reasoner/exa-api-key --with-decryption \
  --query Parameter.Value --output text)
export EXA_API_KEY
for run in curve/curve-350me-501 killtest/killtest-c-201 curve/curve-350md-401; do
  name=$(basename "$run")
  ck=~/runs/webdemo/ckpt-$name.pt
  [ -f "$ck" ] || aws s3 cp "s3://decoupled-reasoner-009398924577/runs/$run/latest.pt" "$ck" --quiet
  echo "checkpoint ready: $name"
done
for name in curve-350me-501 killtest-c-201 curve-350md-401; do
  uv run python -m scripts.web_qa_demo run \
    --checkpoint ~/runs/webdemo/ckpt-$name.pt \
    --model-name "$name" \
    --questions scripts/web_qa_questions.json \
    --out-dir ~/runs/webdemo
done
uv run python -m scripts.web_qa_demo report \
  --runs-dir ~/runs/webdemo \
  --out ~/runs/webdemo/results-webdemo.json
aws s3 cp ~/runs/webdemo/results-webdemo.json \
  s3://decoupled-reasoner-009398924577/runs/webdemo/results-webdemo.json --quiet
echo "WEBDEMO-DONE"
