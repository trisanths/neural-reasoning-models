"""Probe: does the machinery already handle breadth beyond three?"""
import json, random
from src.opgraph.invent import make_world, breadth_item
from src.opgraph.opdef import serialize_all, parse_operators
from src.opgraph.plan import serialize_plan, parse_plan, run_plan, MAX_STEPS, Plan, Step
from src.opgraph.data import induce_prompt, plan_prompt, eval_worlds, make_item
from src.train.tokenizer import load_tokenizer

tok = load_tokenizer("/home/ec2-user/data/tokenizer_v2.json")
print("MAX_STEPS", MAX_STEPS)

# blocker check: a 40 and a 48 step plan
for n in (32, 40, 48):
    p = Plan(tuple(Step(f"t{i+1}", "@", (1, 2)) for i in range(n)), f"t{n}")
    try:
        q = parse_plan(serialize_plan(p))
        print(f"plan len {n}: parse ok, steps={len(q.steps)}")
    except Exception as e:
        print(f"plan len {n}: FAIL {e}")

print("--- worlds by breadth ---")
for b in range(1, 9):
    ws = eval_worlds("breadth", 3, breadth=b, style=0)
    w = ws[0]
    page = w.page_of("score")
    tgt = serialize_all(page.ops)
    pr = induce_prompt(page.text)
    it = make_item("breadth", w, b, 0)
    pp = plan_prompt(w.ops, it.text)
    gp = serialize_plan(it.plan)
    ntgt = len(tok.encode(" " + tgt))
    npr = len(tok.encode(pr))
    # round trip
    rt = [o.symbol for o in parse_operators(tgt)]
    sc = w.ops["score"]
    print(json.dumps({"breadth": b, "flags": len(page.flags), "score_arity": sc.arity,
                      "induce_prompt_tok": npr, "induce_target_tok": ntgt,
                      "plan_prompt_tok": len(tok.encode(pp)),
                      "plan_target_tok": len(tok.encode(" " + gp)),
                      "rt_syms": rt, "gold": it.gold,
                      "answer_run": str(run_plan(parse_plan(gp), w.ops))}))
print("--- style1 breadth 8 target ---")
w = eval_worlds("breadth", 1, breadth=8, style=1)[0]
print(serialize_all(w.page_of("score").ops)[:600])
