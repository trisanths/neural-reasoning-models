set -e
cd ~/mgeval3
PY=~/decoupled-reasoner/.venv/bin/python
export CUDA_VISIBLE_DEVICES=5
$PY -m scripts.mg_threeway_eval --checkpoint ~/mgeval-ckpt/final.pt \
  --tokenizer ~/data/tokenizer_v2.json --config configs/mg3-gate-wide.yaml \
  --suite gate --episodes-dir ~/mg3/gate --out ~/mg3/roll_gate_wide.jsonl \
  --samples 4 --batch 48
$PY -m scripts.mg_threeway_eval --checkpoint ~/mgeval-ckpt/final.pt \
  --tokenizer ~/data/tokenizer_v2.json --config configs/mg3-mathgen.yaml \
  --suite mathgen --episodes-dir ~/mg3/episodes --out ~/mg3/roll_mathgen.jsonl \
  --samples 4 --batch 48
echo ALLDONE
