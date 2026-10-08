"""Flag plan records whose question determines their target.

`src/corpus/plans.py:render_tree` writes a binary infix expression for any
node with two or more children, so a symbol of arity three or more loses every
operand past the second. `score/4` is such a symbol and it is callable in every
world. An item that uses it has a question from which no reader, model or
program, can recover the gold plan. The flag is set by running the
question-only parser and comparing with the gold target, so it is a property
of the item and not of an assumption about which symbols are lossy.
"""
import json, sys, collections
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")
from src.corpus.planparser import expression_of, parse_expression, plan_text, QUESTION

for path in ("/home/ec2-user/retrain/plan/heldout_whole_sample.jsonl",
             "/home/ec2-user/retrain/plan/extrap_whole.jsonl"):
    rows = [json.loads(l) for l in open(path)]
    by_len = collections.Counter(); det_by_len = collections.Counter()
    for r in rows:
        m = QUESTION.search(r["prompt"])
        try:
            got = plan_text(parse_expression(expression_of(m.group(1), r["qframe"])))
        except Exception:
            got = ""
        r["determinate"] = got.strip() == r["target"].strip()
        by_len[r["n_steps"]] += 1
        det_by_len[r["n_steps"]] += int(r["determinate"])
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    n = len(rows); d = sum(r["determinate"] for r in rows)
    print(path.split("/")[-1], "n", n, "determinate", d, "=", round(d / n, 3))
    print("  by length:", {k: f"{det_by_len[k]}/{by_len[k]}" for k in sorted(by_len)})

# incidence over the corpus files themselves, so the report can state it
for path in ("/home/ec2-user/corpus/v1/plan_train_whole.jsonl",
             "/home/ec2-user/corpus/v1/plan_heldout_whole.jsonl"):
    n = d = 0
    for line in open(path):
        r = json.loads(line)
        m = QUESTION.search(r["prompt"])
        try:
            got = plan_text(parse_expression(expression_of(m.group(1), r["qframe"])))
        except Exception:
            got = ""
        n += 1
        d += int(got.strip() == r["target"].strip())
    print(path.split("/")[-1], "n", n, "determinate", d, "=", round(d / n, 3))
