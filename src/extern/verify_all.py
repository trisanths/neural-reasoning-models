"""Every number in the two appended sections, checked against its record file.

The report generators read the record files, so regenerating and diffing
proves the sections are not stale. Modification times are printed beside them
because a report older than the file it cites is fine and a report citing a
file written after it is not.
"""
from __future__ import annotations

import json
import os
import subprocess
import time


def mt(p):
    return time.strftime("%Y-%m-%d %H:%M:%S",
                         time.gmtime(os.path.getmtime(p))) if os.path.exists(p) else "MISSING"


REPORT = "src/extern/FOURCELL.md"
FILES = [
    "results/extern/bench/cell2_ours_mmlu_retrieval_n400.json",
    "results/extern/bench/gsm4_lfm2_350m_bos_n200.json",
    "results/extern/bench/gsm4_lfm2_350m_nobos_n200.json",
    "results/extern/bench/gsm4_ours_native_a_n200.json",
    "results/extern/bench/gsm4_ours_native_n200.json",
    "results/extern/bench/gsm4_ours_shots_a_n200.json",
    "results/extern/bench/gsm4_controls.json",
]
print("record files, oldest first:")
for f in sorted(FILES, key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0):
    print(f"  {mt(f)}  {f}")
print(f"report:\n  {mt(REPORT)}  {REPORT}")
newest = max(os.path.getmtime(f) for f in FILES if os.path.exists(f))
print("report newer than every record file it cites:",
      os.path.getmtime(REPORT) > newest)

cur = open(REPORT).read()
ok = True
for mod, head in (("src.extern.cell2report",
                   "## Cell 2 at n=400: the reader driving its own retrieval loop"),
                  ("src.extern.gsmreport", "## GSM8K with method retrieval")):
    gen = subprocess.run([".venv/bin/python", "-m", mod],
                         capture_output=True, text=True)
    assert gen.returncode == 0, gen.stderr[-2000:]
    body = gen.stdout.rstrip("\n")
    i = cur.find(head + "\n")
    if i < 0:
        print(f"MISSING section for {mod}")
        ok = False
        continue
    j = cur.find("\n## ", i + len(head))
    have = (cur[i:] if j < 0 else cur[i:j + 1]).rstrip("\n")
    match = have == body
    print(f"{mod}: section matches a fresh regeneration: {match}")
    if not match:
        ok = False
        a, b = have.split("\n"), body.split("\n")
        for k in range(max(len(a), len(b))):
            x = a[k] if k < len(a) else "<missing>"
            y = b[k] if k < len(b) else "<missing>"
            if x != y:
                print(f"  first difference on line {k}:")
                print(f"    in file: {x[:200]}")
                print(f"    fresh  : {y[:200]}")
                break
print("ALL CONSISTENT" if ok else "INCONSISTENT")
