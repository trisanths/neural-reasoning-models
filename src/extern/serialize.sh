#!/bin/bash
# Serialize what is left so the box stops thrashing.
#
# Three jobs chained to start at once on four cores starved the SSM agent to
# the point where the control plane stopped responding. This kills the
# parallel chain wrappers and runs the remainder strictly one at a time,
# waiting for every python job of this lane to exit before starting the next.
set -u
cd /home/ec2-user/decoupled-reasoner
exec >> logs/extern/serialize.log 2>&1
echo "=== serialize start $(date -u +%FT%TZ)"

# Drop the parallel chain wrappers (they only sleep; no work is lost).
for P in $(pgrep -f "while kill -0" 2>/dev/null); do
  kill "$P" 2>/dev/null && echo "dropped chain wrapper $P"
done

wait_quiet () {
  while pgrep -f "src\.extern\.(retrieval_mmlu|retrieval_ours|bench_ours|bench_gsm|gsm_retrieval)" >/dev/null 2>&1; do
    sleep 30
  done
  echo "lane quiet $(date -u +%T)  load: $(uptime | sed 's/.*load/load/')"
}

wait_quiet
echo "--- eot prefix control ---"
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES="" \
  .venv/bin/python -m src.extern.bench_ours \
  --ckpt /home/ec2-user/retrain/corpus-v1-8k.pt --tag corpus-v1-8k \
  --task mmlu --n 200 --eot-prefix \
  --out results/extern/bench/ours_mmlu_eotprefix_n200.json
echo "eot rc=$?"

wait_quiet
echo "--- gsm8k method retrieval ---"
. /home/ec2-user/.exa_env
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES="" \
  .venv/bin/python -m src.extern.gsm_retrieval \
  --model LiquidAI/LFM2-350M --n 60 --shots 8 --seed 1234 \
  --conditions closed,method --bos --budget 150 \
  --cache results/extern/exa_cache \
  --out results/extern/bench/gsm_lfm2_350m_n60.json
echo "gsm rc=$?"

echo "--- rendering ---"
.venv/bin/python src/extern/fourcell.py > /dev/null 2>&1 && echo "FOURCELL.md written"
.venv/bin/python src/extern/manifest.py > /dev/null 2>&1 && echo "manifest written"
.venv/bin/python -m src.extern.bench_report > /dev/null 2>&1 && echo "bench summary written"
git add -A src/extern results/extern 2>/dev/null
git -c user.email=ztrisanth@gmail.com -c user.name=Claude commit -q -m "Retrieval cells, eot control and GSM8K, run serially after the box thrashed

Three jobs starting at once on four cores starved the SSM agent until the
control plane stopped answering. The remainder runs one at a time." 2>/dev/null
echo "SERIALIZE_DONE $(date -u +%FT%TZ)"
