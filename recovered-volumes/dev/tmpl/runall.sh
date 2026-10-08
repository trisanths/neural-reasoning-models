#!/bin/bash
cd /home/ec2-user/decoupled-reasoner
export PYTHONPATH=.
P=.venv/bin/python
CK=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
TK=/home/ec2-user/data/tokenizer_v2.json
D=/home/ec2-user/tmpl/eps
O=/home/ec2-user/tmpl
CHAIN="--dir $D --group chain --checkpoint $CK --tokenizer $TK --batch 32 --max-len 1536 --max-prompt-tokens 1100 --max-rounds 6 --max-new-tokens 96"
SIMP="--dir $D --group simple --checkpoint $CK --tokenizer $TK --batch 32 --max-len 640 --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 96 --questions-per-episode 2"

echo "=== chain greedy all page modes ==="
$P -m scripts.template_ablation eval $CHAIN --out $O/chain_greedy2.json --samples 1 --temperature 0.0
echo "=== chain sampled T1 depth1 ==="
$P -m scripts.template_ablation eval $CHAIN --filter -d1 --out $O/chain_t1.json --samples 4 --temperature 1.0
echo "=== simple greedy ==="
$P -m scripts.template_ablation eval $SIMP --out $O/simple_greedy.json --samples 1 --temperature 0.0
echo "=== simple T0.7 textbook anchor ==="
$P -m scripts.template_ablation eval $SIMP --filter -textbook --out $O/simple_t07.json --samples 1 --temperature 0.7
echo "=== simple T1 textbook ==="
$P -m scripts.template_ablation eval $SIMP --filter -textbook.jsonl --out $O/simple_t1_tb.json --samples 4 --temperature 1.0
echo "=== simple T1 gold_only ==="
$P -m scripts.template_ablation eval $SIMP --filter gold_only --out $O/simple_t1_gold.json --samples 4 --temperature 1.0
echo "=== simple T1 wrong+blank ==="
$P -m scripts.template_ablation eval $SIMP --filter wrong_textbook --out $O/simple_t1_wrong.json --samples 4 --temperature 1.0
$P -m scripts.template_ablation eval $SIMP --filter no_documents --out $O/simple_t1_blank.json --samples 4 --temperature 1.0
echo "=== ALL DONE ==="
