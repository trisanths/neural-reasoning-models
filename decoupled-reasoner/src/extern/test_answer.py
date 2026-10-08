"""The grader dry run: synthetic generations whose correct grade is known.

Each case states what the answer span must come out as and what the strict
rule must say about it, so a change to either the extraction or the strict
rule fails here rather than silently moving a benchmark number.
"""
from src.extern.answer import answer_span
from src.norm.cmpwork.grade import forced

OPTS = ["lummel", "thoxxanth"]
GOLD = "lummel"

CASES = [
    # (name, raw, expect_state, expect_span_contains, strict, lenient, hedged)
    ("bare word", "lummel", "ok", "lummel", 1, 1, 0),
    ("bare wrong", "thoxxanth", "ok", "thoxxanth", 0, 0, 0),
    ("answer marker", "Let me think.\nAnswer: lummel", "ok", "lummel", 1, 1, 0),
    ("marker after prose",
     "The Zuntquil reading is thoxxanth and the Nevipyr reading is drifrik, "
     "so they differ.\nAnswer: lummel", "ok", "lummel", 1, 1, 0),
    ("hedge in span", "It is either lummel or thoxxanth.", "ok", "lummel",
     0, 1, 1),
    ("reasoning names both, answer one",
     "<think>could be lummel, could be thoxxanth, they differ so "
     "lummel</think>\nAnswer: lummel", "ok", "lummel", 1, 1, 0),
    ("unterminated reasoning",
     "<think>the Zuntquil reading is thoxxanth and I need to check",
     "unterminated_reasoning", "", 0, 0, 0),
    ("closing tag with no opener",
     "reasoning text mentioning thoxxanth</think>lummel", "ok", "lummel",
     1, 1, 0),
    ("empty", "   \n ", "empty", "", 0, 0, 0),
    ("prefix must not count", "thox", "ok", "thox", 0, 0, 0),
    ("last line wins",
     "Step 1: read thoxxanth.\nStep 2: they differ.\nlummel", "ok",
     "lummel", 1, 1, 0),
    ("final answer marker", "blah\nFinal Answer: lummel", "ok", "lummel",
     1, 1, 0),
    ("newline after marker", "reasoning\nAnswer:\nlummel", "ok", "lummel",
     1, 1, 0),
    ("blank lines after marker", "Answer:\n\n  lummel  \nnote", "ok",
     "lummel", 1, 1, 0),
    ("marker with nothing after", "text\nAnswer:\n", "ok", "", 0, 0, 0),
]

fails = 0
for name, raw, st, contains, strict, lenient, hedged in CASES:
    sp = answer_span(raw)
    f = forced(sp["span"], OPTS, GOLD)
    bad = []
    if sp["state"] != st:
        bad.append(f"state {sp['state']!r} != {st!r}")
    if contains and contains not in sp["span"]:
        bad.append(f"span {sp['span']!r} lacks {contains!r}")
    if f["strict_correct"] != strict:
        bad.append(f"strict {f['strict_correct']} != {strict}")
    if f["lenient_correct"] != lenient:
        bad.append(f"lenient {f['lenient_correct']} != {lenient}")
    if f["hedged"] != hedged:
        bad.append(f"hedged {f['hedged']} != {hedged}")
    if bad:
        fails += 1
        print(f"FAIL {name}: {'; '.join(bad)}")
    else:
        print(f"ok   {name}")
print("FAILS", fails)
raise SystemExit(1 if fails else 0)
