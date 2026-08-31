"""Key position against sentence mode in the training draw.

Key position is half the draw for every shape, so the seven zeros are not a
marginal hole. What is held out is the sentence mode, so the question becomes
whether the draw carries both key positions inside every mode it does contain,
and whether the held-out mode is absent in both positions rather than one.
"""
import gzip
import json
import os
from collections import Counter

ROOT = os.path.expanduser("~/decoupled-reasoner")
SEVEN = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
         "precedence")

mk = Counter()
smk = Counter()
for line in gzip.open(os.path.join(ROOT, "data/norm/train.meta.jsonl.gz"),
                      "rt"):
    d = json.loads(line)
    f = d["fid"].split(".")
    mk[(f[1], f[2])] += 1
    if d["shape"] in SEVEN:
        smk[(d["shape"], f[1], f[2])] += 1

modes = sorted({m for m, _ in mk})
print("sentence modes in the training draw:", modes)
print()
print("mode".ljust(18) + "key_first".rjust(10) + "value_first".rjust(13))
for m in modes:
    print(m.ljust(18) + f"{mk[(m, 'key_first')]:10d}"
          + f"{mk[(m, 'value_first')]:13d}")
print()
print("the seven shapes that score 0.0000, value_first count per mode")
print("shape".ljust(12) + "".join(m[:9].rjust(11) for m in modes))
for sh in SEVEN:
    print(sh.ljust(12)
          + "".join(f"{smk[(sh, m, 'value_first')]:11d}" for m in modes))
print()
print("relative_clause present in the draw:",
      any(m == "relative_clause" for m in modes))

out = os.path.join(ROOT, "results/system/keypos_by_mode.json")
with open(out, "w") as fh:
    json.dump({"source": os.path.join(ROOT, "data/norm/train.meta.jsonl.gz"),
               "modes": modes,
               "mode_by_keypos": {f"{m}|{k}": v for (m, k), v in
                                  sorted(mk.items())},
               "seven_shapes_by_mode_keypos":
                   {f"{s}|{m}|{k}": v for (s, m, k), v in sorted(smk.items())}},
              fh, indent=1)
print("wrote", out)
