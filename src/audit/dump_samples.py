import json, sys
d = json.load(open("results/opgraph.json"))
for name in ("plan_execute", "oracle_ops", "oracle_plan"):
    for kind in ("sequential",):
        row = d[name][kind]
        for dep in sorted(row, key=int):
            c = row[dep]
            print("---", name, kind, "d=" + dep, "acc=%.3f" % c["acc"], c.get("reasons"))
            for s in c.get("samples", [])[:3]:
                print("    ", s[:200])
