#!/bin/bash
# Smoke the sweep code on the dev box's own card, before the training box runs
# a line of it. Numbers here mean nothing: the weights are a reference artifact
# rather than the arms' base checkpoint. What is being checked is that every
# path the sweep will spend hours in actually runs.
set -u
R=/home/ec2-user/decoupled-reasoner
PY=$R/.venv/bin/python
cd $R
mkdir -p /tmp/smoke logs
export PYTHONPATH=$R
{
  echo "=== $(date -u +%FT%TZ) devsmoke ==="
  aws s3 cp s3://decoupled-reasoner-009398924577/latent/latent_devbundle.tgz \
    /tmp/lb.tgz --quiet && mkdir -p src/latent && tar xzf /tmp/lb.tgz \
    -C src/latent/ && echo "bundle ok"
  [ -f src/latent/__init__.py ] || touch src/latent/__init__.py

  $PY - <<'PY'
import torch, os
src = "/home/ec2-user/runs/ref350/ref_350m.pt"
dst = "/tmp/smoke/fakebase.pt"
if not os.path.exists(dst):
    s = torch.load(src, map_location="cpu", weights_only=False)
    cfg = dict(s["model_config"])
    sd = s["state_dict"]
    sd = {k[len("_orig_mod."):] if k.startswith("_orig_mod.") else k: v
          for k, v in sd.items()}
    torch.save({"model": sd, "config": {"model": cfg}}, dst)
print("fake base written", os.path.getsize(dst))
import json; print(json.dumps(torch.load(dst, map_location="cpu",
                                         weights_only=False)["config"]))
PY

  CUDA_VISIBLE_DEVICES="" $PY -m pytest src/latent/tests -q 2>&1 | tail -4

  TOK=/home/ec2-user/data/tokenizer_v2.json
  echo "--- train latent_answer, 12 steps, micro batching on ---"
  CUDA_VISIBLE_DEVICES=0 $PY -m src.latent.train \
    --base /tmp/smoke/fakebase.pt --tokenizer $TOK --arm latent_answer \
    --out /tmp/smoke/d.pt --steps 12 --batch-size 8 --micro-batch 4 \
    --max-len 1024 --lr 2e-5 --warmup 4 --worlds 200 --log-every 4 \
    --save-every 8 --r-choices 1,2,4,8 --backprop-last-k 3 2>&1 | tail -8

  echo "--- train latent_plan, 12 steps ---"
  CUDA_VISIBLE_DEVICES=0 $PY -m src.latent.train \
    --base /tmp/smoke/fakebase.pt --tokenizer $TOK --arm latent_plan \
    --out /tmp/smoke/e.pt --steps 12 --batch-size 8 --micro-batch 8 \
    --max-len 1024 --lr 2e-5 --warmup 4 --worlds 200 --log-every 4 \
    --r-choices 1,2,4,8 --backprop-last-k 3 2>&1 | tail -6

  echo "--- eval condition D, deep grid, tiny n ---"
  CUDA_VISIBLE_DEVICES=0 $PY -m src.latent.eval \
    --ckpt /tmp/smoke/d.pt --tokenizer $TOK --out /tmp/smoke/d_eval.json \
    --r 1,64 --depths 1,32 --breadths 1,6 --novel-depths 2,6 \
    --kinds sequential,breadth,novel --n 6 --samples 1 --batch-size 6 \
    2>&1 | tail -8

  echo "--- eval condition E, deep grid, plan diagnostics, induced ops ---"
  CUDA_VISIBLE_DEVICES=0 $PY -m src.latent.eval \
    --ckpt /tmp/smoke/e.pt --tokenizer $TOK --out /tmp/smoke/e_eval.json \
    --r 1,64 --depths 1,32 --breadths 1,6 --novel-depths 2,6 \
    --kinds sequential,breadth,novel --n 6 --samples 1 --batch-size 6 \
    --induce 2>&1 | tail -8

  echo "--- matched control, all three arms, tiny ---"
  for A in direct trace opgraph; do
    CUDA_VISIBLE_DEVICES=0 $PY -m src.latent.matched \
      --ckpt /tmp/smoke/fakebase.pt --arm $A --tokenizer $TOK \
      --out /tmp/smoke/m_$A.json --budgets 0,4,64 --depths 1,32 \
      --kinds sequential --n 6 --batch-size 6 2>&1 | tail -3
  done

  echo "--- check, is the segment load bearing ---"
  CUDA_VISIBLE_DEVICES=0 $PY -m src.latent.check \
    --ckpt /tmp/smoke/d.pt --tokenizer $TOK --out /tmp/smoke/check.json \
    --r 2,8 --depth 2 --n 6 --batch-size 6 2>&1 | tail -4

  echo "--- report ---"
  $PY -m src.latent.report --latent D=/tmp/smoke/d_eval.json \
    E=/tmp/smoke/e_eval.json --matched direct=/tmp/smoke/m_direct.json \
    opgraph=/tmp/smoke/m_opgraph.json --frontier-depths 1 \
    --out /tmp/smoke/report.md 2>&1 | tail -3
  echo "=== devsmoke done $(date -u +%FT%TZ) ==="
} 2>&1 | tee -a /tmp/smoke/devsmoke.log
