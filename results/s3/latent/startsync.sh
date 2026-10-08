#!/bin/bash
# Start the S3 status loop if it is not already up.
# A wrapper file rather than an inline guard: pgrep reads command lines, and an
# inline guard written into an SSM command matches the command's own line.
cd /home/ec2-user/opg
if pgrep -f "bash src/latent/sync.sh" > /dev/null; then
  echo "sync loop already up"; exit 0
fi
setsid nohup bash src/latent/sync.sh > logs/latent_sync.log 2>&1 < /dev/null &
sleep 3
pgrep -af "bash src/latent/sync.sh" | head -2
