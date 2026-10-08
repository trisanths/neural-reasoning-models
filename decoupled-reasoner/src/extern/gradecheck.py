"""Does the cell 2 grader recognise a correct answer when it is handed one.

An accuracy of 0.01 against a 0.25 floor is the shape a broken grader makes,
so the grader is exercised on constructed answers before the number is
reported. Every form the model could plausibly produce is checked against the
same rows the run scored.
"""
import json
from src.extern.bench import LETTERS, TASKS
from src.extern.retrieval_ours import grade

rows = TASKS["mmlu"]("data/extern", 400, 1234)
forms = {
    "bare gold letter": lambda r: LETTERS[r["gold"]],
    "gold letter with period": lambda r: LETTERS[r["gold"]] + ".",
    "gold option text": lambda r: str(r["choices"][r["gold"]]),
    "sentence naming gold text": lambda r: "The answer is " + str(r["choices"][r["gold"]]) + ".",
    "wrong letter": lambda r: LETTERS[(r["gold"] + 1) % len(r["choices"])],
    "wrong option text": lambda r: str(r["choices"][(r["gold"] + 1) % len(r["choices"])]),
    "empty": lambda r: "",
    "nonsense": lambda r: " bashovi",
}
out = {}
for name, f in forms.items():
    k = n = nn = 0
    for r in rows:
        g = grade(f(r), r)
        k += g["strict_correct"]; nn += g["named_none"]; n += 1
    out[name] = {"n": n, "strict": round(k / n, 4), "named_none": round(nn / n, 4)}
print(json.dumps(out, indent=1))
