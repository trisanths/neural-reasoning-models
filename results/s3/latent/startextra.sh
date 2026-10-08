#!/bin/bash
cd /home/ec2-user/opg
if pgrep -f "bash src/latent/extra.sh" > /dev/null; then echo "extra lane already up"; exit 0; fi
setsid nohup bash src/latent/extra.sh > logs/latent_extra.log 2>&1 < /dev/null &
sleep 3
pgrep -af "bash src/latent/extra.sh" | head -2
