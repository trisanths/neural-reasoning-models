set -u; cd /home/ec2-user/opg; export PYTHONPATH=$PWD
for S in 0 1; do
  JOB=m_opgraph_s$S
  [ -f results/latent/$JOB.done ] || { uv run python -m src.latent.matched \
    --ckpt runs/opgraph2.pt --arm opgraph --tokenizer /home/ec2-user/data/tokenizer_v2.json \
    --out results/latent/$JOB.json --budgets 0,1,2,4,8,16,32,64 \
    --depths 1,2,3,4,5,6,8,12,16,32 --novel-depths 2,3,4,5,6 --kinds sequential,novel \
    --n 64 --style $S --batch-size 24 && touch results/latent/$JOB.done; }
done
JOB=m_trace_s0
[ -f results/latent/$JOB.done ] || { uv run python -m src.latent.matched \
  --ckpt runs/trace.pt --arm trace --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --out results/latent/$JOB.json --budgets 0,16,64 \
  --depths 1,2,3,4,5,6,8,12,16,32 --kinds sequential --n 64 --style 0 --batch-size 24 \
  && touch results/latent/$JOB.done; }
echo "[d] finished"
