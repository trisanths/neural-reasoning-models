"""Tail-averaged training loss, because one 200-step window is noise.

strain.py logs the mean loss over each 200 steps, so the last logged value is
a sample of a noisy quantity and not the fit. Averaging the last 2,000 steps
gives a number that does not move when the window does.
"""
import json
import os

ROOT = os.path.expanduser("~/decoupled-reasoner")
RUNS = {"l45": "results/norm/train/log_l.jsonl",
        "xl93 3.2e-4": "results/system/train/log_xl93.jsonl",
        "xl93 4.0e-4": "results/system/train/log_xl93lr40.jsonl"}
out = {}
for lab, p in RUNS.items():
    steps = []
    for line in open(os.path.join(ROOT, p)):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("event") == "step":
            steps.append((r["step"], r["loss"]))
    steps.sort()
    for w in (2000, 5000):
        k = w // 200
        tail = [l for _, l in steps[-k:]]
        out.setdefault(lab, {})[f"last_{w}"] = round(sum(tail) / len(tail), 5)
    out[lab]["last_logged"] = steps[-1][1]
    out[lab]["final_step"] = steps[-1][0]

print("run".ljust(14) + "last logged".rjust(13) + "mean last 2,000".rjust(18)
      + "mean last 5,000".rjust(18))
for lab, d in out.items():
    print(lab.ljust(14) + f"{d['last_logged']:13.5f}"
          + f"{d['last_2000']:18.5f}" + f"{d['last_5000']:18.5f}")
dest = os.path.join(ROOT, "results/system/tail_loss.json")
with open(dest, "w") as fh:
    json.dump({"note": "strain.py logs the mean over each 200 steps; the last "
                       "logged value is one sample of a noisy quantity",
               "runs": out}, fh, indent=1)
print("wrote", dest)
