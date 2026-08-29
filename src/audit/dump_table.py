import json, sys
d = json.load(open(sys.argv[1]))
kind = sys.argv[2] if len(sys.argv) > 2 else "sequential"
print("conditions:", [k for k in d if k != "config"])
print()
for name in d:
    if name == "config" or name.startswith("induction"):
        continue
    row = d[name].get(kind, {})
    if not row:
        continue
    cells = " ".join("%s:%.3f" % (k, row[k]["acc"]) for k in sorted(row, key=int))
    print("%-30s %s" % (name, cells))
print()
for k in d:
    if k.startswith("induction"):
        print(k, json.dumps(d[k]))
print()
print("config:", json.dumps(d.get("config", {})))
