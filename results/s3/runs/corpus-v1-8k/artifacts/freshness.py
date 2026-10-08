"""Every report must be newer than the records it was scored from.

A stale-records rescore silently mixed two differently-graded runs on this
project once. This walks the artifacts this lane reports from and refuses any
pair where the score file predates its rollout file.
"""
import json, os, sys, glob

R = "/home/ec2-user/retrain"
PAIRS = []
for w in ("base", "new", "opgrapharm", "directarm"):
    PAIRS += [
        (f"{R}/gate/roll_gate_{w}.jsonl", f"{R}/gate/strict_gate_{w}.json"),
        (f"{R}/transposed/all_{w}.jsonl", f"{R}/transposed/score_{w}.json"),
        (f"{R}/transposed/direct_all_{w}.jsonl", f"{R}/transposed/score_direct_{w}.json"),
        (f"{R}/transposed/induce_all_{w}.jsonl", f"{R}/transposed/score_induce_{w}.json"),
    ]
    for s in ("heldout_whole_sample", "extrap_whole"):
        PAIRS.append((f"{R}/plan/all_{w}_{s}.jsonl", f"{R}/plan/score_{w}_{s}.json"))
    for b in ("heldout", "train"):
        PAIRS.append((f"{R}/relation/all_{w}_{b}.jsonl", f"{R}/relation/score_{w}_{b}.json"))
    for t in ("greedy", "t07"):
        PAIRS.append((f"{R}/frames/dump_{w}-{t}", f"{R}/frames/score_{w}-{t}.json"))
        PAIRS.append((f"{R}/frames/dumpext_{w}-{t}", f"{R}/frames/scoreext_{w}-{t}.json"))
PAIRS += [
    (f"{R}/plan/parser_heldout_whole_sample.jsonl",
     f"{R}/plan/score_parser_heldout_whole_sample.json"),
    (f"{R}/plan/parser_extrap_whole.jsonl", f"{R}/plan/score_parser_extrap_whole.json"),
    (f"{R}/transposed/ep.jsonl", f"{R}/transposed/parsers.json"),
]

def mt(p):
    if os.path.isdir(p):
        fs = glob.glob(os.path.join(p, "*"))
        return max((os.path.getmtime(f) for f in fs), default=None)
    return os.path.getmtime(p) if os.path.exists(p) else None

bad = missing = ok = 0
for rec, rep in PAIRS:
    a, b = mt(rec), mt(rep)
    if a is None or b is None:
        missing += 1
        continue
    if b < a - 1:
        bad += 1
        print("STALE  %s is older than %s" % (rep, rec))
    else:
        ok += 1
print(json.dumps({"pairs_checked": ok, "stale": bad, "not_present": missing}))
sys.exit(1 if bad else 0)
