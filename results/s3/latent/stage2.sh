#!/bin/bash
# Score everything, once the two training lanes have finished.
# usage: bash src/latent/stage2.sh [worker ...]      default: all four
#
# Four workers, each holding one card for a sequential list of jobs. A worker
# waits for a card with headroom rather than crowding one. Every job writes its
# own JSON and touches a .done marker, so re-running this script picks up where
# a killed worker left off instead of redoing hours of decoding.
set -u
cd /home/ec2-user/opg
mkdir -p logs results/latent
export PYTHONPATH=$PWD

TOK=/home/ec2-user/data/tokenizer_v2.json
DCK=runs/latent/dsweep.pt
ECK=runs/latent/esweep.pt
RS=0,1,2,4,8,16,32,64
DEPTHS=1,2,3,4,5,6,8,12,16,32
BREADTHS=1,2,3,4,5,6
NOVEL=2,3,4,5,6
N=64

worker () {   # worker NAME NEED_GIB
  local name=$1 need=$2
  if pgrep -f "latent_worker_$name" > /dev/null; then
    echo "[$name] already running"; return 0
  fi
  local gpu
  gpu=$(uv run python src/latent/pick_gpu.py --need "$need" --count 1 \
        --wait 600 --poll 60) || { echo "[$name] no card"; return 1; }
  echo "[$name] gpu $gpu"
  CUDA_VISIBLE_DEVICES=$gpu setsid nohup bash "src/latent/w_$name.sh" \
    latent_worker_"$name" > "logs/latent_w_$name.log" 2>&1 < /dev/null &
  sleep 3
}

# ------------------------------------------------------------------ jobs
cat > src/latent/w_a.sh <<EOF
set -u; cd /home/ec2-user/opg; export PYTHONPATH=\$PWD
for S in 0 1; do
  JOB=d_s\$S
  [ -f results/latent/\$JOB.done ] || { uv run python -m src.latent.eval \\
    --ckpt $DCK --tokenizer $TOK --out results/latent/\$JOB.json \\
    --r $RS --depths $DEPTHS --breadths $BREADTHS --novel-depths $NOVEL \\
    --kinds sequential,breadth,novel --n $N --samples 2 --batch-size 16 \\
    --style \$S && touch results/latent/\$JOB.done; }
done
JOB=check_d
[ -f results/latent/\$JOB.done ] || { uv run python -m src.latent.check \\
  --ckpt $DCK --tokenizer $TOK --out results/latent/check_dsweep.json \\
  --r 0,1,2,4,8,16,32,64 --depth 2 --n 32 --batch-size 16 \\
  && touch results/latent/\$JOB.done; }
echo "[a] finished"
EOF

cat > src/latent/w_b.sh <<EOF
set -u; cd /home/ec2-user/opg; export PYTHONPATH=\$PWD
for S in 0 1; do
  JOB=e_s\$S
  [ -f results/latent/\$JOB.done ] || { uv run python -m src.latent.eval \\
    --ckpt $ECK --tokenizer $TOK --out results/latent/\$JOB.json \\
    --r $RS --depths $DEPTHS --breadths $BREADTHS --novel-depths $NOVEL \\
    --kinds sequential,breadth,novel --n $N --samples 2 --batch-size 32 \\
    --style \$S && touch results/latent/\$JOB.done; }
done
JOB=check_e
[ -f results/latent/\$JOB.done ] || { uv run python -m src.latent.check \\
  --ckpt $ECK --tokenizer $TOK --out results/latent/check_esweep.json \\
  --r 0,1,2,4,8,16,32,64 --depth 2 --n 32 --batch-size 16 \\
  && touch results/latent/\$JOB.done; }
JOB=e_ind_s0
[ -f results/latent/\$JOB.done ] || { uv run python -m src.latent.eval \\
  --ckpt $ECK --tokenizer $TOK --out results/latent/\$JOB.json \\
  --r 0,1,4,16 --depths $DEPTHS --breadths $BREADTHS --novel-depths $NOVEL \\
  --kinds sequential,breadth,novel --n $N --samples 1 --batch-size 32 \\
  --style 0 --induce && touch results/latent/\$JOB.done; }
echo "[b] finished"
EOF

cat > src/latent/w_c.sh <<EOF
set -u; cd /home/ec2-user/opg; export PYTHONPATH=\$PWD
for S in 0 1; do
  JOB=m_direct_s\$S
  [ -f results/latent/\$JOB.done ] || { uv run python -m src.latent.matched \\
    --ckpt runs/direct.pt --arm direct --tokenizer $TOK \\
    --out results/latent/\$JOB.json --budgets 0,1,2,4,8,16,32,64 \\
    --depths $DEPTHS --novel-depths $NOVEL --kinds sequential,novel \\
    --n $N --style \$S --batch-size 24 && touch results/latent/\$JOB.done; }
done
JOB=bench
[ -f results/latent/\$JOB.done ] || { uv run python -m src.latent.bench \\
  --base ckpt/base350.pt --out results/latent/bench_sweep.json \\
  --prompt-len 600 --r 0,1,2,4,8,16,32,64 --batches 1,16 \\
  && touch results/latent/\$JOB.done; }
echo "[c] finished"
EOF

cat > src/latent/w_d.sh <<EOF
set -u; cd /home/ec2-user/opg; export PYTHONPATH=\$PWD
for S in 0 1; do
  JOB=m_opgraph_s\$S
  [ -f results/latent/\$JOB.done ] || { uv run python -m src.latent.matched \\
    --ckpt runs/opgraph2.pt --arm opgraph --tokenizer $TOK \\
    --out results/latent/\$JOB.json --budgets 0,1,2,4,8,16,32,64 \\
    --depths $DEPTHS --novel-depths $NOVEL --kinds sequential,novel \\
    --n $N --style \$S --batch-size 24 && touch results/latent/\$JOB.done; }
done
JOB=m_trace_s0
[ -f results/latent/\$JOB.done ] || { uv run python -m src.latent.matched \\
  --ckpt runs/trace.pt --arm trace --tokenizer $TOK \\
  --out results/latent/\$JOB.json --budgets 0,16,64 \\
  --depths $DEPTHS --kinds sequential --n $N --style 0 --batch-size 24 \\
  && touch results/latent/\$JOB.done; }
echo "[d] finished"
EOF

chmod +x src/latent/w_*.sh
for w in ${@:-a b c d}; do
  case $w in
    a) worker a 14;;
    b) worker b 14;;
    c) worker c 14;;
    d) worker d 14;;
  esac
done
echo "[stage2] launched"
