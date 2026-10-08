#!/bin/bash
cd /home/ec2-user/decoupled-reasoner
export PYTHONPATH=.
P=.venv/bin/python
CK=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
TK=/home/ec2-user/data/tokenizer_v2.json
O=/home/ec2-user/tmpl
while pgrep -f runall.sh >/dev/null; do sleep 20; done
echo "=== gen extra renderers ==="
$P -m scripts.template_ablation gen --out $O/eps2 --episodes 20 --depths 1,2 --problems 8 \
  --alphabet 6 --max-depth 4 --page-modes minimal,table_only \
  --chain-renderers routing,routing_keyphrase,routing_postvalue,processing,abstract \
  --simple-count 0 --conditions ""
$P -m scripts.template_ablation audit --dir $O/eps2 --tokenizer $TK > $O/audit_eps2.log 2>&1
CHAIN2="--dir $O/eps2 --group chain --checkpoint $CK --tokenizer $TK --batch 32 --max-len 1536 --max-prompt-tokens 1100 --max-rounds 6 --max-new-tokens 96"
echo "=== extra greedy ==="
$P -m scripts.template_ablation eval $CHAIN2 --out $O/chain2_greedy.json --samples 1 --temperature 0.0
echo "=== extra sampled ==="
$P -m scripts.template_ablation eval $CHAIN2 --filter=-d1 --out $O/chain2_t1.json --samples 4 --temperature 1.0
CHAIN="--dir $O/eps --group chain --checkpoint $CK --tokenizer $TK --batch 32 --max-len 1536 --max-prompt-tokens 1100 --max-rounds 6 --max-new-tokens 96"
echo "=== main chain sampled T1 depth1 ==="
$P -m scripts.template_ablation eval $CHAIN --filter=-d1 --out $O/chain_t1.json --samples 4 --temperature 1.0
echo "=== audit main ==="
$P -m scripts.template_ablation audit --dir $O/eps --tokenizer $TK > $O/audit_main.log 2>&1
echo "=== ALL DONE 2 ==="
