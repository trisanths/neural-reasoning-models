#!/bin/bash
# Arm autolaunch4.sh detached on the dev box. Idempotent: arms only when no
# armed copy exists; always prints the exact-match proof. The bare subshell
# around setsid/nohup with all three fds detached is the autolaunch2 lesson:
# the SSM invocation's process tree exits cleanly while the armed copy
# survives it. The proof matches exact ps fields (NF==4, $3=="bash",
# $4==script path), so no probe or wrapper command line can match itself.
set -u
S=/home/ec2-user/autolaunch4.sh
aws s3 cp --only-show-errors s3://decoupled-reasoner-009398924577/code/block4/autolaunch4.sh "$S"
mkdir -p /home/ec2-user/logs
count() {
  ps -eo pid,etimes,args \
    | awk 'NF==4 && $3=="bash" && $4=="/home/ec2-user/autolaunch4.sh"' | wc -l
}
if [ "$(count)" -eq 0 ]; then
  ( setsid nohup bash "$S" > /dev/null 2>&1 < /dev/null & )
  sleep 2
  echo "armed new copy"
else
  echo "already armed, not arming again"
fi
echo "== proof (pid etimes bash path, exact field match) =="
ps -eo pid,etimes,args | awk 'NF==4 && $3=="bash" && $4=="/home/ec2-user/autolaunch4.sh"'
echo "ARMED_COPIES=$(count)"
echo "== log head =="
head -2 /home/ec2-user/logs/autolaunch4.log 2>/dev/null || true
echo "now_epoch=$(date -u +%s) now=$(date -u +%FT%TZ)"
