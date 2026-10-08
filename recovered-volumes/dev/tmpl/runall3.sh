#!/bin/bash
cd /home/ec2-user/decoupled-reasoner
export PYTHONPATH=.
P=.venv/bin/python
TK=/home/ec2-user/data/tokenizer_v2.json
O=/home/ec2-user/tmpl
while pgrep -f "runall2.sh" >/dev/null; do sleep 20; done
echo "=== pre-RL checkpoint, chain depth1 ==="
$P -m scripts.template_ablation eval --dir $O/eps --group chain \
  --checkpoint /home/ec2-user/rlckpt/350me503-final.pt --tokenizer $TK \
  --filter=-d1 --out $O/chain_prerl.json --samples 1 --temperature 0.0 \
  --batch 32 --max-len 1536 --max-prompt-tokens 1100 --max-rounds 6 --max-new-tokens 96
echo "=== pre-RL checkpoint, simple textbook ==="
$P -m scripts.template_ablation eval --dir $O/eps --group simple \
  --checkpoint /home/ec2-user/rlckpt/350me503-final.pt --tokenizer $TK \
  --filter=-textbook.jsonl --out $O/simple_prerl.json --samples 1 --temperature 0.0 \
  --batch 32 --max-len 640 --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 96 \
  --questions-per-episode 2
echo "=== ALL DONE 3 ==="
