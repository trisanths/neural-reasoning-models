set -u; cd /home/ec2-user/opg; export PYTHONPATH=$PWD
for S in 0 1; do
  JOB=d_s$S
  [ -f results/latent/$JOB.done ] || { uv run python -m src.latent.eval \
    --ckpt runs/latent/dsweep.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json --out results/latent/$JOB.json \
    --r 0,1,2,4,8,16,32,64 --depths 1,2,3,4,5,6,8,12,16,32 --breadths 1,2,3,4,5,6 --novel-depths 2,3,4,5,6 \
    --kinds sequential,breadth,novel --n 64 --samples 2 --batch-size 16 \
    --style $S && touch results/latent/$JOB.done; }
done
JOB=check_d
[ -f results/latent/$JOB.done ] || { uv run python -m src.latent.check \
  --ckpt runs/latent/dsweep.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json --out results/latent/check_dsweep.json \
  --r 0,1,2,4,8,16,32,64 --depth 2 --n 32 --batch-size 16 \
  && touch results/latent/$JOB.done; }
echo "[a] finished"
