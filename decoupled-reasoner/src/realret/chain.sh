#!/bin/bash
# The named surviving failure: chaining a retrieved result.
#
# `src/corpus/RETRAIN.md` records chain_rule at 0.220 against a 0.250 floor
# and weighted_chain at 0.039, both after being trained at that depth, as the
# two cells the diversity corpus did not move. HotpotQA is real multi-hop, so
# whether training on it moves these synthetic two-hop cells is the question
# this lane can answer that no other data intervention could.
#
# Two instruments on the same items. `mc` scores the four stored candidates
# by negative log likelihood after the answer marker, which gives a forced
# choice with a stated floor. `gen` drives the retrieval environment and
# grades the emitted span, which is what shipped accuracy means here.
set -u
REPO=/home/ec2-user/decoupled-reasoner
R=/mnt/nvme/realret
P=$REPO/.venv/bin/python
TK=/home/ec2-user/data/tokenizer_v2.json
O=$R/results
OLD=/home/ec2-user/ckpt/corpus-v1-8k-final.pt
NEW=$R/real-v1-8k.pt
cd $REPO

# Wait for the CPU cell already running so only one job uses the card.
while pgrep -f "extern.retrieval_mmlu" >/dev/null; do sleep 60; done

for fam in chain_rule weighted_chain; do
  $P - "$fam" <<'PYEOF'
import json, sys
fam = sys.argv[1]
src = "/mnt/nvme/realret/corpus/relation_heldout.jsonl"
out = f"/mnt/nvme/realret/corpus/{fam}_heldout.jsonl"
n = 0
with open(src) as fh, open(out, "w") as sink:
    for line in fh:
        if json.loads(line).get("family") == fam:
            sink.write(line); n += 1
print(f"{fam}: {n} episodes -> {out}")
PYEOF
done

for pair in "corpus-v1-8k:$OLD" "real-v1-8k:$NEW"; do
  tag=${pair%%:*}; ck=${pair#*:}
  for fam in chain_rule weighted_chain; do
    $P -m src.corpus.evalrun mc --checkpoint "$ck" --tokenizer $TK \
       --episodes $R/corpus/${fam}_heldout.jsonl \
       --out $O/chain_mc_${fam}_${tag}.jsonl || echo "MC_FAILED $fam $tag"
    $P -m src.corpus.evalrun gen --checkpoint "$ck" --tokenizer $TK \
       --episodes $R/corpus/${fam}_heldout.jsonl --label greedy \
       --samples 1 --temperature 0.0 --batch 32 --max-rounds 4 \
       --max-new-tokens 192 --max-len 1280 --query-max-tokens 24 \
       --questions-per-episode 1 --min-hops 1 --seed 1234 \
       --out $O/chain_gen_${fam}_${tag}.jsonl || echo "GEN_FAILED $fam $tag"
  done
done

$P - <<'PYEOF'
import json, glob, os, math
O = "/mnt/nvme/realret/results"
def wilson(k, n, z=1.96):
    if not n: return (0.0, 0.0)
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n)
    s = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return round((c-s)/d, 4), round((c+s)/d, 4)
res = {}
for f in sorted(glob.glob(f"{O}/chain_mc_*.jsonl")):
    rows = [json.loads(l) for l in open(f)]
    if not rows: continue
    n = len(rows); k = sum(r["correct"] for r in rows)
    floor = sum(1.0/len(r["nlls"]) for r in rows)/n
    lo, hi = wilson(k, n)
    res[os.path.basename(f)] = {"instrument": "forced choice", "n": n,
        "acc": round(k/n, 4), "floor": round(floor, 4), "ci": [lo, hi],
        "chance_corrected": round((k/n - floor)/(1 - floor), 4)}
for f in sorted(glob.glob(f"{O}/chain_gen_*.jsonl")):
    rows = [json.loads(l) for l in open(f)]
    if not rows: continue
    n = len(rows); k = sum(bool(r["shipped_ok"]) for r in rows)
    lo, hi = wilson(k, n)
    res[os.path.basename(f)] = {"instrument": "generation, env grader",
        "n": n, "acc": round(k/n, 4), "ci": [lo, hi],
        "mean_rounds": round(sum(r["n_rounds"] for r in rows)/n, 3),
        "issued_query": round(sum(r["n_rounds"] >= 1 for r in rows)/n, 4)}
json.dump(res, open(f"{O}/chain_summary.json", "w"), indent=1)
print(json.dumps(res, indent=1))
PYEOF
aws s3 sync $O s3://decoupled-reasoner-009398924577/runs/real-v1-8k/results --exclude "*.jsonl" --only-show-errors
aws s3 cp $O/chain_summary.json s3://decoupled-reasoner-009398924577/xfer/realret2/results/chain_summary.json --only-show-errors
echo CHAIN_DONE
