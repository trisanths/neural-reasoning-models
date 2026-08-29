"""Can a gold plan reach the gold answer while the induced operator is wrong?

The paraphrase pass is where induction actually fails, so it is the only place
this question has any items to answer it with. For every item, the operator the
question needs is compared against gold by exact body text and by behaviour on
the arguments the executor really passed, and that is crossed with whether
oracle_plan came out correct.
"""
import json, sys
from collections import Counter
from src.opgraph.opdef import OpError, parse_operator, serialize_expr
from src.opgraph.plan import PlanError, answer_text, parse_plan, run_plan

def norm(s):
    return str(s).strip().strip(".").strip().lower()

d = json.load(open(sys.argv[1]))
tot = Counter()
per_depth = {}
for dep, rec in d["items"].items():
    st = Counter()
    for gp, gold, seed, syms, ok in zip(rec["gold_plans"], rec["gold"],
                                        rec["seeds"], rec["symbols"],
                                        rec["conds"]["oracle_plan"]["ok"]):
        w = d["worlds"][str(seed)]
        sym = syms[0]
        g = parse_operator(w["gold"][sym])
        i = w["induced"].get(sym)
        st["items"] += 1
        if i is None:
            st["induced_missing"] += 1
            st["induced_missing_and_CORRECT"] += bool(ok)
            continue
        i = parse_operator(i)
        exact = serialize_expr(i.body) == serialize_expr(g.body) and i.params == g.params
        st["body_exact" if exact else "body_wrong"] += 1
        if ok:
            st["CORRECT_body_exact" if exact else "CORRECT_body_wrong"] += 1
    per_depth[dep] = dict(st)
    tot.update(st)
out = {"per_depth": per_depth, "total": dict(tot)}
print(json.dumps(out, indent=1))
json.dump(out, open(sys.argv[2], "w"), indent=1)
