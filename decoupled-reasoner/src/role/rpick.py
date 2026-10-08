"""Which auxiliary weight the full arm gets, by a rule fixed before the probes.

An auxiliary loss can help by adding a signal or hurt by taking gradient away
from the objective that is being scored, and the second shows up first as the
trained-frame score falling. So the rule is: of the weights probed, keep the
ones whose trained-frame quick score at 3,000 steps is no more than 0.01 below
arm A's at the same step, and take the largest of those, because the point of
the arm is pressure on the role representation. If none qualifies, take the
smallest weight probed.

Prints one number and nothing else, so the queue can use it directly.
"""
import json
import os
import sys

ROOT = os.path.expanduser("~/decoupled-reasoner")
T = os.path.join(ROOT, "results/role/train")
WEIGHTS = ("0.25", "1.0", "4.0")
STEP = 3000
KEY = "train_frames_eval"


def at(tag, step):
    p = os.path.join(T, f"log_{tag}.jsonl")
    best = None
    if not os.path.exists(p):
        return None
    for line in open(p):
        d = json.loads(line)
        if d.get("event") == "eval" and d.get("step") == step:
            best = d
    return best


base = at("roleA", STEP)
if base is None:
    print("1.0")
    sys.exit(0)
rows = {}
for w in WEIGHTS:
    d = at(f"probe{w}", STEP)
    if d is not None:
        rows[w] = d
ok = [w for w in WEIGHTS if w in rows and rows[w][KEY] >= base[KEY] - 0.01]
choice = ok[-1] if ok else WEIGHTS[0]
print(json.dumps({"rule": "largest weight within 0.01 of arm A on "
                          f"{KEY} at step {STEP}",
                  "arm_A": base, "probes": rows, "eligible": ok,
                  "chosen": choice}), file=sys.stderr)
with open(os.path.join(ROOT, "results/role/aux_weight.json"), "w") as fh:
    json.dump({"rule": "largest weight within 0.01 of arm A on "
                       f"{KEY} at step {STEP}", "step": STEP,
               "arm_A": base, "probes": rows, "eligible": ok,
               "chosen": float(choice)}, fh, indent=1)
print(choice)
