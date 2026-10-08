"""Replace or append one `## ` section of FOURCELL.md, idempotently.

The report generators print a whole section to stdout. Rerunning one has to
land the new text where the old text was rather than accumulating copies, and
it must not touch the sections above the sentinel that `fourcell.py` owns.
"""
from __future__ import annotations

import sys

dest, src = sys.argv[1], sys.argv[2]
new = open(src).read().rstrip("\n") + "\n"
head = new.split("\n", 1)[0]
assert head.startswith("## "), f"section must start with a level 2 heading: {head!r}"

cur = open(dest).read()
i = cur.find(head + "\n")
if i < 0:
    out = cur.rstrip("\n") + "\n\n" + new
    action = "appended"
else:
    j = cur.find("\n## ", i + len(head))
    end = len(cur) if j < 0 else j + 1
    out = cur[:i] + new + ("\n" + cur[end:] if j >= 0 else "")
    action = "replaced"
open(dest, "w").write(out)
print(f"{action} {head!r} in {dest}")
