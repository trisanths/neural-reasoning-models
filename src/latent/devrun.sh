#!/bin/bash
# The matched compute control, on the dev box's single card, detached.
# usage: bash /home/ec2-user/opg/src/latent/devrun.sh
#
# One lane, jobs in sequence, each with its own JSON and .done marker so a
# re-run resumes rather than repeats.
set -u
R=/home/ec2-user/opg
PY=/home/ec2-user/decoupled-reasoner/.venv/bin/python
cd $R
mkdir -p logs results/latent
TOK=/home/ec2-user/data/tokenizer_v2.json
DEPTHS=1,2,3,4,5,6,8,12,16,32
NOVEL=2,3,4,5,6
N=64

if pgrep -f latent_devlane > /dev/null; then echo "already running"; exit 0; fi

cat > $R/src/latent/devlane.sh <<EOF
set -u; cd $R
run () {
  local job=\$1; shift
  if [ -f results/latent/\$job.done ]; then echo "skip \$job"; return 0; fi
  echo "=== \$job \$(date -u +%FT%TZ)"
  PYTHONPATH=$R CUDA_VISIBLE_DEVICES=0 $PY "\$@" && touch results/latent/\$job.done
}
for S in 0 1; do
  run m_direct_s\$S -m src.latent.matched --ckpt runs/direct.pt --arm direct \\
    --tokenizer $TOK --out results/latent/m_direct_s\$S.json \\
    --budgets 0,1,2,4,8,16,32,64 --depths $DEPTHS --novel-depths $NOVEL \\
    --kinds sequential,novel --n $N --style \$S --batch-size 16
  run m_opgraph_s\$S -m src.latent.matched --ckpt runs/opgraph2.pt --arm opgraph \\
    --tokenizer $TOK --out results/latent/m_opgraph_s\$S.json \\
    --budgets 0,1,2,4,8,16,32,64 --depths $DEPTHS --novel-depths $NOVEL \\
    --kinds sequential,novel --n $N --style \$S --batch-size 16
done
run m_trace_s0 -m src.latent.matched --ckpt runs/trace.pt --arm trace \\
  --tokenizer $TOK --out results/latent/m_trace_s0.json --budgets 0,16,64 \\
  --depths $DEPTHS --kinds sequential --n $N --style 0 --batch-size 16
run bench -m src.latent.bench --base ckpt/base350.pt \\
  --out results/latent/bench_sweep.json --prompt-len 600 \\
  --r 0,1,2,4,8,16,32,64 --batches 1,16
echo "[devlane] finished \$(date -u +%FT%TZ)"
EOF

setsid nohup bash $R/src/latent/devlane.sh latent_devlane \
  > $R/logs/latent_devlane.log 2>&1 < /dev/null &
sleep 3
echo "[devrun] launched"
