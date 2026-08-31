#!/bin/bash
# The transposed-operand test at one rung of the ladder.
#
# src/norm/COMPARE.md section 8 is the protocol and it is not changed here.
# The rung is shown 1,024 grids of the one page shape it never trained on,
# half of every batch drawn from the original training file so the measurement
# is acquisition rather than a trade, and then it is asked to read 750 pages
# whose operand roles are transposed and 750 that are not. The item file is
# results/norm/compare/x_items.jsonl.gz, built once by cmpwork/xitems.py, and
# every rung reads the same one.
#
# usage: tpose.sh RUNG CKPT [EXISTING_FT]
cd ~/decoupled-reasoner
set -u
export PYTHONPATH=.
P=.venv/bin/python
R=$1; C=$2; FT=${3:-}
X=results/system/tpose
L=logs/system
mkdir -p $X $L
say () { echo "$(date -u +%H:%M:%S) tpose $R $*" >> $L/queue.log; }

if [ -z "$FT" ]; then
  FT=$X/ft_${R}_k1024.pt
  if [ ! -f "$FT" ]; then
    $P -m src.norm.cmpwork.ftune --ckpt "$C" --k 1024 --steps 1500 \
       --out "$FT" > $L/tpose_ft_$R.log 2>&1
    say "ftune rc=$?"
  else
    say "ftune skipped, $FT present"
  fi
fi

$P -m src.norm.cmpwork.xmode --ckpts "$FT" \
   --items results/norm/compare/x_items.jsonl.gz \
   --out $X/xmode_$R.json > $L/tpose_xmode_$R.log 2>&1
say "xmode rc=$?"

# What the fine tune cost on the frame groups, so a rung that acquired the new
# page shape by forgetting the others is visible rather than silent.
$P -m src.system.sreport --ckpt "$FT" --tag ft$R --n 700 --batch 64 \
   > $L/tpose_reg_$R.log 2>&1
say "regression rc=$?"
