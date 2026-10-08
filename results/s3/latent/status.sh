#!/bin/bash
# One line per lane. Keeps the number of commands this box has to serve small.
cd /home/ec2-user/opg
echo "== $(date -u +%FT%TZ)"
for f in dsweep esweep; do
  printf "%-8s " "$f"
  tail -n 1 logs/latent_$f.log 2>/dev/null | python3 -c "
import sys,json
try:
  d=json.loads(sys.stdin.read())
  print(f\"step {d.get('step')} loss {d.get('loss'):.4f} R {d.get('n_latent')} peak {d.get('peak_gib')} secs {d.get('secs')}\")
except Exception as e: print('(', sys.argv[0], e, ')')
" 2>/dev/null || echo "-"
done
for w in a b c d; do
  printf "w_%s      " "$w"
  if pgrep -f "w_$w[.]sh" > /dev/null; then printf "RUNNING "; else printf "stopped "; fi
  tail -n 1 logs/latent_w_$w.log 2>/dev/null | cut -c1-150
  echo
done
echo "-- results"
ls -la results/latent/*.json 2>/dev/null | awk '{print $5, $9}' | tail -14
echo "-- done markers"; ls results/latent/*.done 2>/dev/null | tr '\n' ' '; echo
echo "-- gpus"; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader | tr '\n' '|'
echo
