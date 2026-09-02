# The corpus-v1-8k battery, unchanged in its flags, pointed at one checkpoint.
# Item files are the same ones the published numbers were read from:
#   relation  rel_heldout.jsonl  from runs/corpus-v1-8k/artifacts/relation/
#   frames    ~/sweep/eval/gen   from the dev box
# usage: bash battery_e3.sh TAG CKPT
set -u
cd /home/ec2-user/decoupled-reasoner || exit 1
export PYTHONPATH=.
PY=/home/ec2-user/decoupled-reasoner/.venv/bin/python
TK=/home/ec2-user/data/tokenizer_v2.json
W=$1
CK=$2
R=/mnt/nvme/e3eval
mkdir -p $R/relation $R/frames $R/logs
echo "BATTERY_START $W $(date -u +%FT%TZ)"

# ---------------------------------------------------------- relation, held out
BAND=heldout
for T in greedy t1; do
  [ "$T" = greedy ] && TEMP=0.0 || TEMP=1.0
  echo "STEP relation $W $BAND $T $(date -u +%FT%TZ)"
  $PY -m src.corpus.evalrun gen --checkpoint "$CK" --tokenizer $TK \
    --episodes $R/relation/rel_$BAND.jsonl \
    --out $R/relation/gen_${W}_${BAND}_$T.jsonl --label $T --samples 1 \
    --temperature $TEMP --batch 32 --max-rounds 6 --max-new-tokens 256 \
    --max-len 1920 --questions-per-episode 2 \
    > $R/logs/rel_${W}_${BAND}_$T.log 2>&1 || echo "FAIL rel $W $BAND $T"
done
cat $R/relation/gen_${W}_${BAND}_greedy.jsonl \
    $R/relation/gen_${W}_${BAND}_t1.jsonl > $R/relation/all_${W}_$BAND.jsonl
$PY -m src.corpus.rescore relation --rolls $R/relation/all_${W}_$BAND.jsonl \
  --out $R/relation/score_${W}_$BAND.json \
  > $R/logs/rel_score_${W}_$BAND.log 2>&1 || echo "FAIL relscore $W"
echo "RELATION_DONE $W $(date -u +%FT%TZ)"

# ------------------------------------------------------------------- frames
for T in greedy t07; do
  [ "$T" = greedy ] && TEMP=0.0 || TEMP=0.7
  echo "STEP frames $W $T $(date -u +%FT%TZ)"
  DD=$R/frames/dump_$W-$T
  rm -rf "$DD"; mkdir -p "$DD"
  $PY -m src.frames.cli eval --dir /home/ec2-user/sweep/eval/gen \
    --checkpoint "$CK" --tokenizer $TK \
    --out $R/frames/eval_$W-$T.json --dump-dir "$DD" \
    --samples 1 --temperature $TEMP --batch 48 --max-len 800 \
    --max-prompt-tokens 384 --max-rounds 4 --max-new-tokens 192 \
    --questions-per-episode 2 --seed 99 \
    > $R/logs/frames_$W-$T.log 2>&1 || echo "FAIL frames $W $T"
  $PY -m src.frames.cli score --dir /home/ec2-user/sweep/eval/gen \
    --dump-dir "$DD" --out $R/frames/score_$W-$T.json \
    >> $R/logs/frames_$W-$T.log 2>&1 || echo "FAIL framescore $W $T"
done
echo "FRAMES_DONE $W $(date -u +%FT%TZ)"

# ------------------------------------------------------- hop curve, from rolls
$PY -m src.e3.hopcurve --rolls $R/relation/all_${W}_$BAND.jsonl \
  --out $R/relation/hops_${W}_$BAND.json > $R/logs/hops_$W.log 2>&1 \
  || echo "FAIL hops $W"

aws s3 cp $R/relation/score_${W}_$BAND.json \
  s3://decoupled-reasoner-009398924577/runs/e3-350m/eval/ --only-show-errors
aws s3 cp $R/relation/hops_${W}_$BAND.json \
  s3://decoupled-reasoner-009398924577/runs/e3-350m/eval/ --only-show-errors
for T in greedy t07; do
  aws s3 cp $R/frames/score_$W-$T.json \
    s3://decoupled-reasoner-009398924577/runs/e3-350m/eval/ --only-show-errors
done
echo "BATTERY_DONE $W $(date -u +%FT%TZ)"
