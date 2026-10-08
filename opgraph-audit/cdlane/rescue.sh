#!/bin/bash
# Move my own typed eval off a card that has filled up since it was placed.
#
# The decoding budget grows with depth, so a process that fits now will not fit
# at depth sixteen. The card it is on is shared, and an OOM there would land on
# whichever process asks for memory next, which may not be mine. Only processes
# whose command line names my own checkpoints are ever signalled.
set -u
cd /home/ec2-user/opg || exit 1
export PYTHONPATH=/home/ec2-user/opg
PY=/home/ec2-user/opg/.venv/bin/python3
TOK=/home/ec2-user/data/tokenizer_v2.json
R=/home/ec2-user/opg/runs/ladder_cd
O=/home/ec2-user/opg/results/ladder_cd
L=/home/ec2-user/opg/logs/ladder_cd
GRID="sequential=1,2,3,4,5,6,7,8,10,12,14,16,20,24,32;novel=2,3,4,5,6,8,12,16,24,32;breadth=1,2,3,4,5,6;sequential_paren=2,3,4,5,6"

echo "=== per process gpu memory ==="
nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader
echo "=== per gpu ==="
nvidia-smi --query-gpu=index,uuid,utilization.gpu,memory.total,memory.used --format=csv,noheader
echo "=== my eval processes ==="
pgrep -af "cdlane/eval_cd.py" || echo none

# Which physical card is my typed eval actually on, and how full is it?
MYPID=$(pgrep -f "cdlane/eval_cd.py --ckpt $R/ladder_typed.pt" | head -1)
if [ -z "$MYPID" ]; then echo "no typed eval running; nothing to move"; exit 0; fi
UUID=$(nvidia-smi --query-compute-apps=pid,gpu_uuid --format=csv,noheader \
       | awk -F', ' -v p="$MYPID" '$1==p {print $2}' | head -1)
IDX=$(nvidia-smi --query-gpu=uuid,index --format=csv,noheader \
      | awk -F', ' -v u="$UUID" '$1==u {print $2}' | head -1)
FREE=$(nvidia-smi --query-gpu=memory.total,memory.used --format=csv,noheader,nounits -i "$IDX" \
       | awk -F', ' '{print $1-$2}')
echo "typed eval pid $MYPID is on gpu $IDX with $FREE MiB free on that card"

if [ "$FREE" -ge 12000 ]; then
  echo "card has room; leaving it alone"
  exit 0
fi

TARGET=$(nvidia-smi --query-gpu=index,utilization.gpu,memory.total,memory.used \
         --format=csv,noheader,nounits \
       | awk -F', ' -v skip="$IDX" '{free=$3-$4; if (free>=45000 && $1!=skip) print $2, -free, $1}' \
       | sort -k1,1n -k2,2n | head -1 | awk '{print $3}')
if [ -z "$TARGET" ]; then echo "no roomier card free; leaving it alone"; exit 0; fi
echo "moving typed eval to gpu $TARGET"

# Make the pipeline skip its own typed stages: evalone returns early when the
# output file is already there. The placeholders are overwritten by the run
# started below.
touch "$O/typed_sampled.json"
kill "$MYPID" 2>/dev/null
sleep 12
kill -0 "$MYPID" 2>/dev/null && { sleep 20; kill -9 "$MYPID" 2>/dev/null; }
rm -f "$O/typed_greedy.json"

cat > /home/ec2-user/opg/cdlane/typed_on_free.sh <<'INNER'
#!/bin/bash
set -u
cd /home/ec2-user/opg
export PYTHONPATH=/home/ec2-user/opg
PY=/home/ec2-user/opg/.venv/bin/python3
TOK=/home/ec2-user/data/tokenizer_v2.json
R=/home/ec2-user/opg/runs/ladder_cd
O=/home/ec2-user/opg/results/ladder_cd
L=/home/ec2-user/opg/logs/ladder_cd
G="$1"; GRID="$2"
for pair in "0.0 greedy" "0.8 sampled"; do
  set -- $pair
  t="$1"; tag="$2"
  echo "[$(date -u +%FT%TZ)] typed $tag on gpu $G"
  CUDA_VISIBLE_DEVICES="$G" "$PY" /home/ec2-user/opg/cdlane/eval_cd.py \
    --ckpt "$R/ladder_typed.pt" --tokenizer "$TOK" --out "$O/typed_${tag}.json" \
    --n 150 --batch-size 48 --depths "$GRID" --styles 0,1 \
    --temperature "$t" --para-oracles 1 > "$L/eval_typed_${tag}.log" 2>&1
  echo "[$(date -u +%FT%TZ)] typed $tag exit $?"
done
echo "[$(date -u +%FT%TZ)] TYPED BRANCH DONE"
INNER

setsid nohup bash /home/ec2-user/opg/cdlane/typed_on_free.sh "$TARGET" "$GRID" \
  > "$L/typed_branch.log" 2>&1 < /dev/null &
sleep 20
echo "=== relaunched ==="
cat "$L/typed_branch.log"
pgrep -af "cdlane/eval_cd.py" || echo none
