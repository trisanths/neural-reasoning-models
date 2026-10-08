"""Splice the generated tables into the prose and write PLANHEADS_AR.md.

Every number in the document comes from `results/ar/*.json` through
`ar_blocks.py`. Nothing is typed by hand, so the report and the artifacts it
reports from cannot drift apart.
"""

from __future__ import annotations

import json
import re
import sys

TEMPLATE_PATH, BLOCKS_PATH, OUT_PATH = sys.argv[1], sys.argv[2], sys.argv[3]

with open(BLOCKS_PATH) as fh:
    blocks = json.load(fh)
with open(TEMPLATE_PATH) as fh:
    text = fh.read()

missing = []


def sub(m):
    k = m.group(1)
    if k not in blocks:
        missing.append(k)
        return f"[MISSING BLOCK {k}]"
    return blocks[k]


out = re.sub(r"\{\{([a-zA-Z0-9_]+)\}\}", sub, text)
if missing:
    raise SystemExit(f"missing blocks: {sorted(set(missing))}\n"
                     f"available: {sorted(blocks)}")
with open(OUT_PATH, "w") as fh:
    fh.write(out)
print(f"[written] {OUT_PATH} {len(out)} chars")
