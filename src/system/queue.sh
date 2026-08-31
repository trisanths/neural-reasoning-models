#!/bin/bash
# Everything the ladder still owes, one job at a time on the one card.
#
# ladder.sh started the xl93 rung and this takes over from it, so the order is
# under one script rather than two. Rungs are trained at the fixed budget
# src/system/strain.py defines and nothing about the data, the split or the
# grader moves between them.
cd ~/decoupled-reasoner
set -u
export PYTHONPATH=.
export AWS_PROFILE=chronos
P=.venv/bin/python
L=logs/system
T=results/system/train
E=results/system/eval
F=results/system/lmframe
G=results/system/gate
M=results/system/lm
TK=/home/ec2-user/data/tokenizer_v2.json
BASE=/home/ec2-user/rlckpt/rlsimple-503-921-final.pt
CORPUS=/home/ec2-user/retrain/corpus-v1-8k.pt
mkdir -p $L $T $E $F $G $M results/system/lmeval results/system/tpose
say () { echo "$(date -u +%H:%M:%S) $*" >> $L/queue.log; }

say "queue starts"

# 1. the xl93 rung ladder.sh launched, left to finish
while pgrep -f "src.system.strain --size xl93" > /dev/null 2>&1; do sleep 30; done
say "xl93 train ended"
$P -m src.system.sreport --ckpt $T/ckpt_xl93.pt --tag xl93 --n 2800 \
   --batch 64 >> $L/eval_xl93.log 2>&1
say "eval xl93 rc=$?"

# 2. the transposed-operand test at the two rungs that already have weights
bash src/system/tpose.sh l45 results/norm/train/ckpt_l.pt \
     results/norm/compare/ft_l_k1024.pt
bash src/system/tpose.sh xl93 $T/ckpt_xl93.pt

# 3. the 350M arm, the half that does not need the fine tune yet. Run early
#    because it is the first exercise of this harness and a break in it is
#    worth finding now rather than ten hours from now.
$P scripts/mg_threeway_eval.py --checkpoint $BASE --tokenizer $TK \
   --config configs/mg3-gate.yaml --suite gate \
   --episodes-dir /home/ec2-user/mg3/gate \
   --out $G/roll_gate_base.jsonl --samples 4 --temperature 1.0 --batch 24 \
   > $L/gate.log 2>&1
say "gate gen rc=$?"
$P scripts/mg_strict_rescore.py --rollouts $G/roll_gate_base.jsonl \
   --suite gate --episodes-dir /home/ec2-user/mg3/gate \
   --out $G/strict_gate_base.json --graded-out $G/graded_gate_base.jsonl \
   >> $L/gate.log 2>&1
say "gate rescore rc=$?"
$P -m src.system.lmframe --ckpt $CORPUS --tag corpus_before --mode greedy \
   --out $F/corpus_before_greedy.json --cap 25 > $L/frame_before.log 2>&1
say "frame before rc=$?"
$P -m src.system.lmeval --ckpt $CORPUS --tag corpus_nosft --n 400 \
   --max-new 640 --modes greedy > $L/lmeval_nosft.log 2>&1
say "lmeval nosft rc=$?"

# 4. the 167M rung
$P -m src.system.strain --size xxl167 --micro 2 --steps 30000 \
   --eval-every 3000 --eval-n 700 --out $T --tag xxl167 \
   >> $L/train_xxl167.log 2>&1
say "train xxl167 rc=$?"
$P -m src.system.sreport --ckpt $T/ckpt_xxl167.pt --tag xxl167 --n 2800 \
   --batch 64 >> $L/eval_xxl167.log 2>&1
say "eval xxl167 rc=$?"
bash src/system/tpose.sh xxl167 $T/ckpt_xxl167.pt

# 5. the 350M arm, the structure fine tune and what it costs the frame reading
$P -m src.system.lmtrain --ckpt $CORPUS --pack data/system/lm \
   --out $M/norm-sft.pt --log $M/train.jsonl \
   --steps 8000 --batch 32 --micro 4 --lr 2e-5 > $L/lmtrain.log 2>&1
say "lmtrain rc=$?"
$P -m src.system.lmeval --ckpt $M/norm-sft.pt --tag lm350 --n 1400 \
   --max-new 640 > $L/lmeval.log 2>&1
say "lmeval rc=$?"
$P -m src.system.lmframe --ckpt $M/norm-sft.pt --tag corpus_after \
   --mode greedy --out $F/corpus_after_greedy.json --cap 25 \
   > $L/frame_after.log 2>&1
say "frame after rc=$?"

# 6. the top rung
$P -m src.system.strain --size xxxl355 --micro 2 --steps 30000 \
   --eval-every 3000 --eval-n 700 --out $T --tag xxxl355 \
   >> $L/train_xxxl355.log 2>&1
say "train xxxl355 rc=$?"
$P -m src.system.sreport --ckpt $T/ckpt_xxxl355.pt --tag xxxl355 --n 2800 \
   --batch 64 >> $L/eval_xxxl355.log 2>&1
say "eval xxxl355 rc=$?"
bash src/system/tpose.sh xxxl355 $T/ckpt_xxxl355.pt
say "done"
