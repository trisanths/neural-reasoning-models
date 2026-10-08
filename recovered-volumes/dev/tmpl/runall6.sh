#!/bin/bash
cd /home/ec2-user/decoupled-reasoner
export PYTHONPATH=.
P=.venv/bin/python
CK=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
TK=/home/ec2-user/data/tokenizer_v2.json
O=/home/ec2-user/tmpl
while pgrep -f "runall5.sh" >/dev/null; do sleep 20; done
SIMP="--dir $O/eps --group simple --checkpoint $CK --tokenizer $TK --batch 32 --max-len 640 --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 96 --questions-per-episode 2"
echo "=== D5 simple twin T0.7 ==="
$P -m scripts.template_ablation eval $SIMP --filter=twin --out $O/d_simple_twin.json --samples 1 --temperature 0.7 --dump-dir $O/dump_simple_twin
echo "=== D6 simple twin greedy ==="
$P -m scripts.template_ablation eval $SIMP --filter=twin --out $O/d_simple_twing.json --samples 1 --temperature 0.0 --dump-dir $O/dump_simple_twing
echo "=== ALL DONE 6 ==="
