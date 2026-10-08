"""Build src/norm/COMPARE.md from its template and the generated tables.

Every marker of the form TABLE_NAME in the template is replaced by the file
results/norm/compare/tables/t_name.md, which
`src/norm/cmpwork/tables.py` writes out of the summary JSON. No number in the
finished document is typed by hand, and a missing table stops the build rather
than leaving a marker or a stale number in place.

    python scripts/norm_compare_md.py
"""

import os
import re
import sys

TABLES = "results/norm/compare/tables"
TMPL = "src/norm/COMPARE.tmpl.md"
OUT = "src/norm/COMPARE.md"

doc = open(TMPL).read()
missing = []
for marker in sorted(set(re.findall(r"\bTABLE_[A-Z0-9_]+\b", doc))):
    path = os.path.join(TABLES, "t_" + marker[len("TABLE_"):].lower() + ".md")
    if not os.path.exists(path):
        missing.append((marker, path))
        continue
    doc = doc.replace(marker, open(path).read().rstrip("\n"))
if missing:
    for m, p in missing:
        print("missing", m, "->", p, file=sys.stderr)
    raise SystemExit(1)
left = re.findall(r"\bTABLE_[A-Z0-9_]+\b", doc)
assert not left, left
open(OUT, "w").write(doc)
print("wrote", OUT, len(doc), "bytes")
