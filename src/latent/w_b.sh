set -u; cd /home/ec2-user/opg; export PYTHONPATH=$PWD
for S in 0 1; do
  JOB=e_s$S
  [ -f results/latent/$JOB.done ] || { uv run python -m src.latent.eval \
    --ckpt runs/latent/esweep.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json --out results/latent/$JOB.json \
    --r 0,1,2,4,8,16,32,64 --depths 1,2,3,4,5,6,8,12,16,32 --breadths 1,2,3,4,5,6 --novel-depths 2,3,4,5,6 \
    --kinds sequential,breadth,novel --n 64 --samples 2 --batch-size 32 \
    --style $S && touch results/latent/$JOB.done; }
done
JOB=check_e
[ -f results/latent/$JOB.done ] || { uv run python -m src.latent.check \
  --ckpt runs/latent/esweep.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json --out results/latent/check_esweep.json \
  --r 0,1,2,4,8,16,32,64 --depth 2 --n 32 --batch-size 16 \
  && touch results/latent/$JOB.done; }
JOB=e_ind_s0
[ -f results/latent/$JOB.done ] || { uv run python -m src.latent.eval \
  --ckpt runs/latent/esweep.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json --out results/latent/$JOB.json \
  --r 0,1,4,16 --depths 1,2,3,4,5,6,8,12,16,32 --breadths 1,2,3,4,5,6 --novel-depths 2,3,4,5,6 \
  --kinds sequential,breadth,novel --n 64 --samples 1 --batch-size 32 \
  --style 0 --induce && touch results/latent/$JOB.done; }
echo "[b] finished"
