#!/bin/bash
# Everything the ladder still owes, one job at a time on the one card.
#
# The 93M rung finished behind the 45M rung on its own training loss at every
# logged step, 0.1009 against 0.0843 at 8,000 and 0.0182 against 0.0126 at
# 30,000, so the two rungs are not matched on fit and a flat held-out score
# cannot be read as a capacity result yet. The inverse-width learning rate the
# ladder inherited is the first suspect, so the 93M rung is run again at the
# 45M rung's own peak before the two expensive rungs commit thirteen hours to
# the rule. Everything else about the control is identical.
#
# The rate for the two rungs above is read from a file at the moment they
# start, so the control can decide it without leaving the card idle. An empty
# or missing file means src/system/sizes.py:LR, which is the ladder as
# written.
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
lrof () { cat results/system/lr_$1 2>/dev/null || echo 0; }
doc () { $P -m src.system.threport >> $L/threport.log 2>&1; say "threport rc=$?"; }

say "queue2 starts"

# 1. the xl93 scoring the first queue had already launched
while kill -0 177771 2>/dev/null; do sleep 20; done
say "eval xl93 ended"
doc

# 2. the transposed-operand test at the two rungs that have weights
bash src/system/tpose.sh l45 results/norm/train/ckpt_l.pt \
     results/norm/compare/ft_l_k1024.pt
bash src/system/tpose.sh xl93 $T/ckpt_xl93.pt
doc

# 3. the learning rate control at 93M, the 45M rung's own peak
$P -m src.system.strain --size xl93 --micro 1 --steps 30000 --lr 4.0e-4 \
   --eval-every 3000 --eval-n 700 --out $T --tag xl93lr40 \
   >> $L/train_xl93lr40.log 2>&1
say "train xl93lr40 rc=$?"
$P -m src.system.sreport --ckpt $T/ckpt_xl93lr40.pt --tag xl93lr40 --n 2800 \
   --batch 64 >> $L/eval_xl93lr40.log 2>&1
say "eval xl93lr40 rc=$?"
doc

# 4. the 350M arm, the half that needs no fine tune. Early, because this is
#    the first exercise of that harness and a break in it is cheaper to find
#    now than ten hours from now.
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
doc

# 5. the 167M rung
R=$(lrof xxl167); say "xxl167 lr $R"
$P -m src.system.strain --size xxl167 --micro 2 --steps 30000 --lr $R \
   --eval-every 3000 --eval-n 700 --out $T --tag xxl167 \
   >> $L/train_xxl167.log 2>&1
say "train xxl167 rc=$?"
$P -m src.system.sreport --ckpt $T/ckpt_xxl167.pt --tag xxl167 --n 2800 \
   --batch 64 >> $L/eval_xxl167.log 2>&1
say "eval xxl167 rc=$?"
bash src/system/tpose.sh xxl167 $T/ckpt_xxl167.pt
doc

# 6. the 350M arm, the structure fine tune and what it costs the frame reading
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
doc

# 7. the top rung
R=$(lrof xxxl355); say "xxxl355 lr $R"
$P -m src.system.strain --size xxxl355 --micro 2 --steps 30000 --lr $R \
   --eval-every 3000 --eval-n 700 --out $T --tag xxxl355 \
   >> $L/train_xxxl355.log 2>&1
say "train xxxl355 rc=$?"
$P -m src.system.sreport --ckpt $T/ckpt_xxxl355.pt --tag xxxl355 --n 2800 \
   --batch 64 >> $L/eval_xxxl355.log 2>&1
say "eval xxxl355 rc=$?"
bash src/system/tpose.sh xxxl355 $T/ckpt_xxxl355.pt
doc
say "done"
