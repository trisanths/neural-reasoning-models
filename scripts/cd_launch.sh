#!/bin/bash
# Wait for a genuinely quiet GPU, claim it, and start one rung's pipeline.
# usage: cd_launch.sh ARM DEPTHSPEC MAXWAITMIN
# A card counts as quiet when three samples twenty seconds apart all show
# utilisation under the threshold and memory under the threshold. Process
# liveness is not consulted: on this box a wrapper shell has outlived the job
# it wrapped. The claim file stops two of these from taking the same card.
main() {
  set -u
  local ARM="$1" DEPTHS="$2" MAXWAIT="${3:-720}"
  local UTIL_MAX=25 MEM_MAX=9000
  local CLAIMDIR=/home/ec2-user/opg/logs/cd/claims
  mkdir -p "$CLAIMDIR" /home/ec2-user/opg/logs/cd
  local deadline=$(( $(date +%s) + MAXWAIT * 60 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    for g in 0 1 2 3 4 5 6 7; do
      [ -e "$CLAIMDIR/$g" ] && continue
      local ok=1
      for s in 1 2 3; do
        local line util mem
        line=$(nvidia-smi --id=$g --query-gpu=utilization.gpu,memory.used \
               --format=csv,noheader,nounits 2>/dev/null)
        util=$(echo "$line" | cut -d, -f1 | tr -d ' ')
        mem=$(echo "$line" | cut -d, -f2 | tr -d ' ')
        [ -z "$util" ] && ok=0 && break
        if [ "$util" -ge "$UTIL_MAX" ] || [ "$mem" -ge "$MEM_MAX" ]; then
          ok=0; break
        fi
        [ "$s" -lt 3 ] && sleep 20
      done
      if [ "$ok" = 1 ]; then
        # mkdir is the atomic claim; two launchers racing cannot both win.
        if mkdir "$CLAIMDIR/$g.lock" 2>/dev/null; then
          echo "$ARM" > "$CLAIMDIR/$g"
          echo "[$(date -u +%H:%M:%S)] $ARM claims gpu $g"
          bash /home/ec2-user/opg/scripts/cd_pipeline.sh "$g" "$ARM" "$DEPTHS"
          rm -f "$CLAIMDIR/$g"; rmdir "$CLAIMDIR/$g.lock" 2>/dev/null
          return 0
        fi
      fi
    done
    sleep 60
  done
  echo "[$(date -u +%H:%M:%S)] $ARM gave up waiting for a quiet gpu"
  return 1
}
main "$@"
