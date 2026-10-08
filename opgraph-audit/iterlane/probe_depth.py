"""How far can the grid actually go: item generation, executor, and each head's codec."""
import json, sys, traceback
from src.opgraph.data import eval_worlds, make_item
from src.opgraph.planheads import FLAT, GRAPH, encode_plan, SlotError, N_NODES, INT_MAX
from src.opgraph.plan import run_plan, serialize_plan

DEPTHS = [1,2,3,4,5,6,8,12,16,32]
out = {}
for kind in ["sequential", "breadth", "novel"]:
    for d in DEPTHS:
        if kind == "breadth" and d > 6: continue
        if kind == "novel" and d > 6: continue
        breadth = d if kind == "breadth" else 3
        try:
            ws = eval_worlds(kind, 8, breadth=breadth, style=0)
        except Exception as e:
            out[f"{kind}/{d}"] = {"worlds_error": f"{type(e).__name__}: {e}"}
            continue
        rec = {"n": 0, "gen_err": None, "steps_min": 99, "steps_max": 0,
               "flat_ok": 0, "graph_ok": 0, "flat_err": None, "graph_err": None,
               "exec_ok": 0, "max_int": 0, "answer_kinds": {}}
        for i, w in enumerate(ws):
            try:
                it = make_item(kind, w, d, i)
            except Exception as e:
                rec["gen_err"] = f"{type(e).__name__}: {e}"
                break
            rec["n"] += 1
            ns = len(it.plan.steps)
            rec["steps_min"] = min(rec["steps_min"], ns)
            rec["steps_max"] = max(rec["steps_max"], ns)
            try:
                v = run_plan(it.plan, w.ops)
                rec["exec_ok"] += 1
            except Exception as e:
                rec.setdefault("exec_err", f"{type(e).__name__}: {e}")
            for st in it.plan.steps:
                for a in st.args:
                    if isinstance(a, int) and not isinstance(a, bool):
                        rec["max_int"] = max(rec["max_int"], abs(a))
            try:
                encode_plan(it.plan, w.ops, FLAT); rec["flat_ok"] += 1
            except Exception as e:
                if rec["flat_err"] is None: rec["flat_err"] = f"{type(e).__name__}: {e}"
            try:
                encode_plan(it.plan, w.ops, GRAPH); rec["graph_ok"] += 1
            except Exception as e:
                if rec["graph_err"] is None: rec["graph_err"] = f"{type(e).__name__}: {e}"
        out[f"{kind}/{d}"] = rec
print(json.dumps(out, indent=1))
