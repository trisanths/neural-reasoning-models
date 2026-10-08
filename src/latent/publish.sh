#!/bin/bash
# Put what a second box needs into S3, in the background.
# usage: bash src/latent/publish.sh [extra paths...]
#
# The p5 is shared and its command queue backs up for tens of minutes at a
# time. A second card that already has the base checkpoint, the tokenizer and
# the three token channel arms can carry the matched compute control and the
# scoring lanes without waiting on it.
set -u
cd /home/ec2-user/opg
B=s3://decoupled-reasoner-009398924577/latent
{
  for f in ckpt/base350.pt runs/direct.pt runs/trace.pt runs/opgraph.pt \
           /home/ec2-user/data/tokenizer_v2.json "$@"; do
    [ -f "$f" ] || { echo "missing $f"; continue; }
    aws s3 cp "$f" "$B/xfer/$(basename "$f")" --quiet \
      && echo "put $f" || echo "FAILED $f"
  done
  tar czf /tmp/opgsrc.tgz src/opgraph src/latent src/train src/rl src/latentret \
    pyproject.toml uv.lock 2>/dev/null
  aws s3 cp /tmp/opgsrc.tgz "$B/xfer/opgsrc.tgz" --quiet && echo "put src"
  echo "publish done $(date -u +%FT%TZ)"
} >> logs/latent_publish.log 2>&1
