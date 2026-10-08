#!/bin/bash
# Stand up a mirror of the training box's tree on the single card dev box and
# run the matched compute control there.
#
# The control needs the three token channel arm checkpoints and the same
# src/opgraph the latent conditions are scored against; it needs nothing the
# training lanes are still producing, so it can run in parallel with them on a
# second card. The source tree is copied from the training box rather than
# taken from the dev box's own repo, because two copies of invent.py that
# differ by one line generate different worlds and the two sets of numbers
# would not be comparable.
#
# The interpreter is the dev repo's existing environment, driven with the
# mirror as the working directory so every import resolves inside the mirror.
set -u
B=s3://decoupled-reasoner-009398924577/latent/xfer
R=/home/ec2-user/opg
PY=/home/ec2-user/decoupled-reasoner/.venv/bin/python
mkdir -p $R/ckpt $R/runs $R/logs $R/results/latent
cd $R
{
  echo "=== $(date -u +%FT%TZ) devsetup ==="
  [ -x "$PY" ] || { echo "NO INTERPRETER at $PY"; ls /home/ec2-user/decoupled-reasoner/.venv/bin 2>/dev/null | head; }
  [ -s ckpt/base350.pt ] || aws s3 cp $B/base350.pt ckpt/base350.pt --quiet \
    || echo "FAILED base350.pt"
  for f in direct.pt trace.pt opgraph.pt; do
    [ -s runs/$f ] || aws s3 cp $B/$f runs/$f --quiet || echo "FAILED $f"
  done
  [ -s /tmp/opgsrc.tgz ] || aws s3 cp $B/opgsrc.tgz /tmp/opgsrc.tgz --quiet
  tar xzf /tmp/opgsrc.tgz -C $R
  aws s3 cp s3://decoupled-reasoner-009398924577/latent/latent_bundle.tgz \
    /tmp/lb.tgz --quiet && tar xzf /tmp/lb.tgz -C $R/src/latent/
  du -sh ckpt runs
  md5sum ckpt/base350.pt runs/*.pt
  PYTHONPATH=$R CUDA_VISIBLE_DEVICES="" $PY -m pytest src/latent/tests -q \
    > logs/latent_tests.log 2>&1
  echo "tests rc=$?"; tail -3 logs/latent_tests.log
  echo "=== devsetup done ==="
} 2>&1 | tee -a $R/logs/devsetup.log
