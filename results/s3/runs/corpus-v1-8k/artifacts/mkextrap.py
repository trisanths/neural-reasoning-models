"""Plans longer than anything the corpus trains, for the extrapolation cell.

The corpus runs to 48 steps. If the emitted length ceiling is a corpus
property it should now sit at 48, and these lengths are where that shows.
Seeds sit at 760,000,000, outside every range RESERVED_SEED_RANGES names and
outside both corpus bands.
"""
import json, random, sys, collections
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")
from src.corpus.build import build_plan_records
from src.corpus.plans import PLAN_QUESTION_FRAMES

SEED0 = 760_000_000
LENGTHS = [56, 64, 72, 80, 96]
PER = 60
frames = sorted(PLAN_QUESTION_FRAMES)
out_w = open("/home/ec2-user/retrain/plan/extrap_whole.jsonl", "w")
out_s = open("/home/ec2-user/retrain/plan/extrap_step.jsonl", "w")
counts = collections.Counter(); rej = collections.Counter()
seed = SEED0
for n in LENGTHS:
    made = 0
    while made < PER and seed < SEED0 + 200000:
        rng = random.Random(seed * 7 + n)
        res, why = build_plan_records(seed, n, min(5, 1 + n % 5), frames[seed % len(frames)], rng, band="extrap")
        seed += 1
        if res is None:
            rej[str(why)[:40]] += 1
            continue
        w, st = res
        w["band"] = "extrap"
        out_w.write(json.dumps(w) + "\n")
        for s in st:
            out_s.write(json.dumps(s) + "\n")
        counts[n] += 1
        made += 1
out_w.close(); out_s.close()
print(json.dumps({"per_length": dict(counts), "rejects": dict(rej)}, indent=1))
