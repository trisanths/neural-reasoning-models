#!/bin/bash
cd /home/ec2-user/decoupled-reasoner
export PYTHONPATH=.
P=.venv/bin/python
CK=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
TK=/home/ec2-user/data/tokenizer_v2.json
O=/home/ec2-user/tmpl
while pgrep -f "runall[123].sh" >/dev/null; do sleep 20; done
SIMP="--dir $O/eps --group simple --checkpoint $CK --tokenizer $TK --batch 32 --max-len 640 --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 96 --questions-per-episode 2"
echo "=== simple T0.7 textbook anchor ==="
$P -m scripts.template_ablation eval $SIMP --filter=-textbook.jsonl --out $O/simple_t07.json --samples 1 --temperature 0.7
echo "=== simple T1 textbook ==="
$P -m scripts.template_ablation eval $SIMP --filter=-textbook.jsonl --out $O/simple_t1_tb.json --samples 4 --temperature 1.0
echo "=== ALL DONE 4 ==="
