#!/bin/bash
# The role experiment, one job at a time, behind the ladder queue.
#
# The card is a single L40S and the 167M rung owns it until queue4.sh ends, so
# this waits for that script to leave and for the card to report no compute
# process before it starts, and never runs two jobs of its own at once.
#
# Order: a short smoke on the card, then arm A because everything downstream is
# meaningless if it does not reproduce, then arm B which is the primary arm,
# then the auxiliary weight probes, then arms C and D. Each arm skips itself if
# its checkpoint is already there, so this script is safe to rerun.
cd ~/decoupled-reasoner
set -u
export PYTHONPATH=.
P=.venv/bin/python
L=logs/role
T=results/role/train
E=results/system/eval
mkdir -p $L $T $E results/role
say () { echo "$(date -u +'%F %H:%M:%S') $*" >> $L/queue.log; }

say "role queue waiting"
while pgrep -f "src/system/queue4.sh" > /dev/null; do sleep 60; done
say "queue4 gone"
while [ "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)" -gt 0 ]; do sleep 60; done
say "card free"

if [ ! -f $L/smoke.ok ]; then
  $P -m src.role.rtrain --tag gpusmoke --steps 100 --smoke 1 --pairs 1 \
     --aux 1.0 --train-split data/role/paired_train --out /tmp/rsmoke \
     > $L/smoke.log 2>&1 && touch $L/smoke.ok
  say "gpu smoke rc=$?"
fi

# tag pairs aux train-split steps
arm () {
  tag=$1; pairs=$2; aux=$3; sp=$4; steps=${5:-30000}
  if [ ! -f $T/ckpt_$tag.pt ]; then
    $P -m src.role.rtrain --size l45 --tag $tag --pairs $pairs --aux $aux \
       --train-split $sp --steps $steps --seed 1 --eval-every 3000 \
       --eval-n 700 --out $T >> $L/train_$tag.log 2>&1
    say "train $tag rc=$?"
  else
    say "train $tag already there"
  fi
  if [ ! -f $E/$tag/summary.json ]; then
    $P -m src.system.sreport --ckpt $T/ckpt_$tag.pt --tag $tag \
       --data data/norm --n 7000 --batch 64 \
       --splits train_frames_eval,qframe,lexicon,mode \
       >> $L/eval_$tag.log 2>&1
    say "eval $tag rc=$?"
  fi
  $P -m src.role.rsplit --tags $tag >> $L/split_$tag.log 2>&1
  say "split $tag rc=$?"
  if [ "$aux" != "0" ]; then
    $P -m src.role.raux --ckpt $T/ckpt_$tag.pt --tag $tag \
       >> $L/aux_$tag.log 2>&1
    say "aux probe $tag rc=$?"
  fi
}

arm roleA 0 0 data/norm/train
arm roleB 1 0 data/role/paired_train

# The auxiliary weight. Three probes at 3,000 steps against arm A's own quick
# eval at the same step, and the choice is the rule below and not a look at the
# answer: the largest weight whose trained-frame quick score is within 0.01 of
# arm A's.
for w in 0.25 1.0 4.0; do
  if [ ! -f $T/ckpt_probe$w.pt ]; then
    $P -m src.role.rtrain --size l45 --tag probe$w --pairs 0 --aux $w \
       --train-split data/norm/train --steps 3000 --seed 1 --eval-every 3000 \
       --eval-n 700 --out $T >> $L/train_probe$w.log 2>&1
    say "probe $w rc=$?"
  fi
done
W=$($P -m src.role.rpick 2>> $L/pick.log)
say "auxiliary weight chosen: $W"

arm roleC 0 "$W" data/norm/train
arm roleD 1 "$W" data/role/paired_train
say "role queue done"
