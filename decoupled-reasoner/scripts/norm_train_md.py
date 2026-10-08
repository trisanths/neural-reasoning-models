"""Build src/norm/TRAIN.md from its template and the generated tables.

The template holds the prose and four markers. Every table in the finished
document comes out of the summaries by way of `scripts/norm_md.py`,
`scripts/norm_ladder.py`, `scripts/norm_safety.py` and
`scripts/norm_attacks.py`, so no number in it was typed by hand.

    python scripts/norm_train_md.py xs s m l
"""

import subprocess
import sys

TAGS = sys.argv[1:] or ["xs", "s", "m", "l"]


def run(script, args):
    out = subprocess.run([sys.executable, script] + args,
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


subs = {
    "SPLIT_TABLES": run("scripts/norm_md.py", TAGS),
    "LADDER_TABLE": run("scripts/norm_ladder.py", []),
    "SAFETY_TABLE": run("scripts/norm_safety.py", TAGS),
    "ATTACK_TABLES": run("scripts/norm_attacks.py", TAGS),
}
doc = open("src/norm/TRAIN.tmpl.md").read()
for k, v in subs.items():
    assert k in doc, "missing marker " + k
    doc = doc.replace(k, v)
for k in subs:
    assert k not in doc
open("src/norm/TRAIN.md", "w").write(doc)
print("wrote src/norm/TRAIN.md", len(doc), "bytes, tags", TAGS)
