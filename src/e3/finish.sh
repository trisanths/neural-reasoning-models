# Everything after the pretrain finishes, unattended.
#
# Stage A is the regime_e3 pretrain. It answers the closed-book questions:
# MMLU and whether the model issues retrieval queries.
#
# Stage B applies the corpus-v1-8k SFT recipe unchanged to the Stage A
# checkpoint, on the identical pack (mix1, 253,972 examples, 77,021,506
# tokens). corpus-v1-8k is (old pretrain + RL) + that SFT, so Stage B is
# (regime_e3 pretrain) + that same SFT, and the pair differs only in the
# pretrain. The frame and hop measurements are defined on a model that has had
# corpus training, so they are read off Stage B, not Stage A.
set -u
cd /home/ec2-user/decoupled-reasoner || exit 1
export PYTHONPATH=.
PY=/home/ec2-user/decoupled-reasoner/.venv/bin/python
R=/mnt/nvme/e3eval
RUN=/mnt/nvme/runs/e3-350m
S3=s3://decoupled-reasoner-009398924577/runs/e3-350m
mkdir -p $R/logs
echo "FINISH_WAIT $(date -u +%FT%TZ)"
until grep -q "done at step" $RUN/train.log 2>/dev/null; do sleep 120; done
echo "PRETRAIN_DONE $(date -u +%FT%TZ)"
sleep 30

# Stage A final weights, slim, to S3.
$PY - <<'PY'
import torch
sd = torch.load("/mnt/nvme/runs/e3-350m/latest.pt", map_location="cpu",
                weights_only=False)
slim = {"model": sd["model"], "step": sd["step"], "config": sd["config"]}
torch.save(slim, "/mnt/nvme/e3eval/e3-final.pt")
print("stage A step", sd["step"])
PY
aws s3 cp $R/e3-final.pt $S3/final.pt --only-show-errors
echo "STAGEA_UPLOADED $(date -u +%FT%TZ)"

# Stage A closed book.
for N in 500 1000; do
  $PY -m src.extern.bench_ours --ckpt $R/e3-final.pt --tag e3final \
    --task mmlu --n $N --seed 1234 --out $R/mmlu_e3final_n$N.json \
    --device cuda > $R/logs/mmlu_e3final_n$N.log 2>&1 || echo "FAIL mmlu $N"
done
$PY -m src.extern.retrieval_ours --ckpt $R/e3-final.pt --tag e3final --n 200 \
  --seed 1234 --passes none --max-new-tokens 256 --device cuda \
  --cache $R/exacache_e3_none --out $R/ret_e3final_n200.json \
  > $R/logs/ret_e3final.log 2>&1 || echo "FAIL ret e3final"
aws s3 cp $R/mmlu_e3final_n500.json $S3/eval/ --only-show-errors
aws s3 cp $R/mmlu_e3final_n1000.json $S3/eval/ --only-show-errors
aws s3 cp $R/ret_e3final_n200.json $S3/eval/ --only-show-errors
echo "STAGEA_EVAL_DONE $(date -u +%FT%TZ)"

# Stage B, the corpus-v1-8k SFT recipe unchanged.
$PY -m src.corpus.sft train --checkpoint $R/e3-final.pt \
  --pack /mnt/nvme/pack/mix1 --out $R/e3-sft8k.pt \
  --log $R/logs/sft_e3.jsonl --steps 8000 --batch 32 --micro-batch 8 \
  --lr 2e-5 --warmup 200 --device cuda > $R/logs/sft_e3.log 2>&1 \
  || echo "FAIL sft"
aws s3 cp $R/e3-sft8k.pt $S3/e3-sft8k.pt --only-show-errors
aws s3 cp $R/logs/sft_e3.jsonl $S3/eval/sft_e3_loss.jsonl --only-show-errors
echo "STAGEB_DONE $(date -u +%FT%TZ)"

# Stage B closed book, then the battery.
for N in 500 1000; do
  $PY -m src.extern.bench_ours --ckpt $R/e3-sft8k.pt --tag e3sft \
    --task mmlu --n $N --seed 1234 --out $R/mmlu_e3sft_n$N.json \
    --device cuda > $R/logs/mmlu_e3sft_n$N.log 2>&1 || echo "FAIL mmlu sft $N"
  aws s3 cp $R/mmlu_e3sft_n$N.json $S3/eval/ --only-show-errors
done
$PY -m src.extern.retrieval_ours --ckpt $R/e3-sft8k.pt --tag e3sft --n 200 \
  --seed 1234 --passes none --max-new-tokens 256 --device cuda \
  --cache $R/exacache_e3_none --out $R/ret_e3sft_n200.json \
  > $R/logs/ret_e3sft.log 2>&1 || echo "FAIL ret e3sft"
aws s3 cp $R/ret_e3sft_n200.json $S3/eval/ --only-show-errors

bash /home/ec2-user/e3/battery_e3.sh e3sft $R/e3-sft8k.pt \
  > $R/logs/battery_e3sft.log 2>&1
echo "FINISH_ALL_DONE $(date -u +%FT%TZ)"
