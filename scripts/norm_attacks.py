"""The page edit attack tables for src/norm/TRAIN.md."""
import json, os, sys
tags = sys.argv[1:]
def load(t):
    p = f"results/norm/nattack/ckpt_{t}.pt.json"
    return json.load(open(p)) if os.path.exists(p) else None
ds = [(t, load(t)) for t in tags]
ds = [(t, d) for t, d in ds if d]

print("Edits that change what the page says, with the reference parser as the")
print("oracle for what it now says. `silently_original` is the network emitting")
print("the pre-edit structure anyway.\n")
print("| size | attack | edits scored | network changed its output | followed the edit exactly | silently_original | malformed |")
print("|---|---|---|---|---|---|---|")
for name in ("value", "delete"):
    for t, d in ds:
        c = d["attacks"][name]
        n = c.get("structure_edit", 0)
        print("| %s | `%s` | %d | %d | %d | %d | %d |"
              % (t, name, n, c.get("changed", 0),
                 c.get("followed_edit_exactly", 0),
                 c.get("silently_original", 0), c.get("malformed", 0)))
print("\nEdits that leave no structure to emit, where the only right answer is")
print("silence.\n")
print("| size | attack | items | refused or malformed | answered anyway |")
print("|---|---|---|---|---|")
for name in ("truncate", "strip"):
    for t, d in ds:
        c = d["attacks"][name]
        print("| %s | `%s` | %d | %d | %d |"
              % (t, name, c.get("n", 0), c.get("refused_or_malformed", 0),
                 c.get("answered_anyway", 0)))
