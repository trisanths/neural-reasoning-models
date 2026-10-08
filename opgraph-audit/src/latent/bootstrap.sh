#!/bin/bash
# One command that installs the sweep code, checks it, and starts everything.
#
# Written for a box whose command queue backs up for tens of minutes at a time:
# it is idempotent, it returns in seconds, and every long thing it starts is
# detached, so a single delivery carries training, scoring and the transfer the
# second box needs.
set -u
cd /home/ec2-user/opg
mkdir -p logs runs/latent results/latent
export PYTHONPATH=$PWD
{
  echo "=== $(date -u +%FT%TZ) bootstrap ==="
  aws s3 cp s3://decoupled-reasoner-009398924577/latent/latent_bundle.tgz \
    /tmp/lb.tgz --quiet && tar xzf /tmp/lb.tgz -C src/latent/ \
    && echo "bundle ok" || { echo "BUNDLE FAILED"; exit 1; }
  # the second box needs the base checkpoint and the three arms; start that
  # first, it is the piece that unblocks a whole card of work elsewhere
  pgrep -f latent_publish > /dev/null || setsid nohup bash \
    src/latent/publish.sh latent_publish > /dev/null 2>&1 < /dev/null &
  CUDA_VISIBLE_DEVICES="" uv run python -m pytest src/latent/tests -q \
    > logs/latent_tests.log 2>&1
  rc=$?
  tail -3 logs/latent_tests.log
  if [ $rc -ne 0 ]; then echo "TESTS FAILED rc=$rc"; exit 1; fi
  nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader
  df -h / | tail -1
  # launch.sh waits for a card with headroom rather than crowding one, so it
  # runs detached too
  pgrep -f latent_launcher > /dev/null || setsid nohup bash \
    src/latent/launch.sh latent_launcher > logs/latent_launch.log 2>&1 \
    < /dev/null &
  pgrep -f latent_chain > /dev/null || setsid nohup bash src/latent/chain.sh \
    latent_chain > logs/latent_chain.log 2>&1 < /dev/null &
  sleep 2
  pgrep -af "latent_publish|latent_launcher|latent_chain" | head
  echo "=== bootstrap done ==="
} 2>&1 | tee -a logs/latent_bootstrap.log
