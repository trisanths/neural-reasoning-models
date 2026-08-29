"""Are the model plans under plan_execute and oracle_ops the same strings?

plan_execute shows the scheduler an ops line built from induced operators.
oracle_ops shows the same line built from gold operators, which differs only
by the associativity field. If the two conditions produce identical plan text,
the scheduler is not reading that field.
"""
import json, sys
d = json.load(open(sys.argv[1]))
tot = same = 0
print("depth  n   identical  plan_execute_acc  oracle_ops_acc")
for k in sorted(d["items"], key=int):
    a = d["items"][k]["conds"]["plan_execute"]
    b = d["items"][k]["conds"]["oracle_ops"]
    s = sum(1 for x, y in zip(a["plans"], b["plans"]) if x == y)
    tot += len(a["plans"]); same += s
    print("%5s %4d %6d      %.3f            %.3f"
          % (k, len(a["plans"]), s, a["acc"], b["acc"]))
print("total %d/%d = %.4f identical" % (same, tot, same / tot))
