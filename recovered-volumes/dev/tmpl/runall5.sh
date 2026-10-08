#!/bin/bash
cd /home/ec2-user/decoupled-reasoner
export PYTHONPATH=.
P=.venv/bin/python
CK=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
TK=/home/ec2-user/data/tokenizer_v2.json
O=/home/ec2-user/tmpl
while pgrep -f "runall[1234].sh" >/dev/null; do sleep 20; done
SIMP="--dir $O/eps --group simple --checkpoint $CK --tokenizer $TK --batch 32 --max-len 640 --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 96 --questions-per-episode 2"
CH="--dir $O/eps --group chain --checkpoint $CK --tokenizer $TK --batch 32 --max-len 640 --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 96"
echo "=== D1 simple textbook T0.7 (headline temperature) ==="
$P -m scripts.template_ablation eval $SIMP --filter=-textbook.jsonl --out $O/d_simple_t07.json --samples 1 --temperature 0.7 --dump-dir $O/dump_simple_t07
echo "=== D2 simple textbook greedy ==="
$P -m scripts.template_ablation eval $SIMP --filter=-textbook.jsonl --out $O/d_simple_greedy.json --samples 1 --temperature 0.0 --dump-dir $O/dump_simple_greedy
echo "=== D3 simple gold_only greedy ==="
$P -m scripts.template_ablation eval $SIMP --filter=gold_only --out $O/d_simple_gold.json --samples 1 --temperature 0.0 --dump-dir $O/dump_simple_gold
echo "=== D4 chain d1 greedy both page modes ==="
$P -m scripts.template_ablation eval $CH --filter=-d1 --out $O/d_chain_greedy.json --samples 1 --temperature 0.0 --dump-dir $O/dump_chain_greedy
echo "=== ALL DONE 5 ==="
