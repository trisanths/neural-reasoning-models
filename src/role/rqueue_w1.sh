#!/bin/bash
# The role experiment on worker 1, which has the card to itself.
#
# Same order and same commands as src/role/rqueue.sh. What is gone is the wait
# on the ladder queue and on a clear nvidia-smi, because nothing else runs here.
# Still one training job at a time, so a failure belongs to one arm.
#
# Every arm's artifacts go to S3 as soon as it finishes, because this box is an
# unpacked tarball with no git history and nothing here is safe until it is
# back on the box that has one.
cd ~/decoupled-reasoner
set -u
export PYTHONPATH=.
P=.venv/bin/python
L=logs/role
T=results/role/train
E=results/system/eval
B=s3://decoupled-reasoner-009398924577/role-back
mkdir -p $L $T $E results/role
say () { echo "$(date -u +'%F %H:%M:%S') $*" >> $L/queue.log; }

ship () {
  aws s3 sync results/role $B/results/role --exclude "*.pt" --only-show-errors
  aws s3 sync $E $B/results/system/eval --only-show-errors
  aws s3 sync $L $B/logs/role --only-show-errors
  say "shipped $1"
}

say "worker 1 queue starts"
if [ ! -f $L/smoke.ok ]; then
  $P -m src.role.rtrain --tag gpusmoke --steps 100 --smoke 1 --pairs 1 \
     --aux 1.0 --train-split data/role/paired_train --out /tmp/rsmoke \
     > $L/smoke.log 2>&1
  rc=$?; say "gpu smoke rc=$rc"
  [ $rc -eq 0 ] && touch $L/smoke.ok || exit 1
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
  $P -m src.role.rshapes --tags $tag --split mode >> $L/shapes_$tag.log 2>&1
  say "shapes $tag rc=$?"
  if [ "$aux" != "0" ]; then
    $P -m src.role.raux --ckpt $T/ckpt_$tag.pt --tag $tag \
       >> $L/aux_$tag.log 2>&1
    say "aux probe $tag rc=$?"
  fi
  $P -m src.role.rswap --ckpt $T/ckpt_$tag.pt --tag $tag --split mode \
     >> $L/swap_$tag.log 2>&1
  say "swap $tag rc=$?"
  ship "$tag"
}

arm roleA 0 0 data/norm/train
arm roleB 1 0 data/role/paired_train

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
ship probes

arm roleC 0 "$W" data/norm/train
arm roleD 1 "$W" data/role/paired_train

if [ -f results/norm/train/ckpt_l.pt ]; then
  $P -m src.role.rswap --ckpt results/norm/train/ckpt_l.pt --tag l45 \
     --split mode >> $L/swap_l45.log 2>&1
  say "swap l45 rc=$?"
fi
ship final
say "worker 1 queue done"
