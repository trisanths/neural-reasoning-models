#!/bin/bash
# Idempotent launcher, run as root by AWS-RunRemoteScript.
if pgrep -u ec2-user -f "realret/pipeline.sh" >/dev/null; then
  echo ALREADY_RUNNING; exit 0
fi
sudo -u ec2-user bash -lc 'cd ~/decoupled-reasoner && aws s3 cp s3://decoupled-reasoner-009398924577/xfer/realret_sync.tgz /tmp/rs.tgz --only-show-errors && tar xzf /tmp/rs.tgz -C ~/decoupled-reasoner && rm -f src/realret/._* && mkdir -p ~/realret/logs && setsid nohup bash src/realret/pipeline.sh > ~/realret/logs/pipeline_out.log 2>&1 < /dev/null & sleep 3'
echo REMOTE_LAUNCH_OK
