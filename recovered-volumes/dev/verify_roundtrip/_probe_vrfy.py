"""Is rerender an independent check, or is it entailed by identical?"""
import itertools, json, random
from src.norm.gen import make_for
from src.norm.render import render, classify, SHAPES, frames
from src.norm.parse import parse
from src.norm.interp import run
from src.norm.lang import Program, Step, Ref

fr, bank = frames()
fids = [f.fid for f in fr]

# 1. render determinism: same (p, fid, preamble) -> same bytes, twice
det = 0; n = 0
for i, shape in enumerate(SHAPES):
    for j in range(6):
        fid = fids[(i*7+j*53) % len(fids)]
        p = make_for(fid, shape, 1000+i*13+j)
        a = render(p, fid, preamble_level=3)["text"]
        b = render(p, fid, preamble_level=3)["text"]
        n += 1; det += int(a == b)
print("render determinism:", det, "/", n)

# 2. does rerender ever add information over identical, in the shipped records?
# logically: identical => q == p => render(q) == render(p) => rerender True.
# so rerender can only be < identical, never >. Check the shipped file.
import gzip
same_pat = 0; tot = 0
for line in gzip.open("results/norm/roundtrip/records.jsonl.gz", "rt"):
    r = json.loads(line); tot += 1
    if r["identical"] and not r["rerender"]:
        same_pat += 1
print("items where identical=1 but rerender=0:", same_pat, "of", tot)

# 3. the documented guarantee: "a parser that guessed the plan from the shape
#    alone would fail rerender". Test it. Same defs, same inputs, same shape,
#    wrong wiring.
print()
hits = []
for shape in ("compose", "sum_chain", "precedence", "band_then_lookup",
              "lookup_then_band"):
    for j in range(40):
        fid = fids[(j*37) % len(fids)]
        p = make_for(fid, shape, 5000+j)
        if len(p.steps) < 2:
            continue
        # permute the wiring while keeping defs, inputs and answer name
        if shape == "compose":
            names = [s.args[0] for s in p.steps]
            rot = names[1:] + names[:1]
            steps = []
            prev = p.inputs[0][0]
            for i, nm in enumerate(rot, start=1):
                steps.append(Step(f"t{i}", "lookup", (nm, Ref(prev))))
                prev = f"t{i}"
            q = Program(p.defs, p.inputs, tuple(steps), p.answer)
        else:
            # swap the order of the first two steps outputs
            s = list(p.steps)
            s[0], s[1] = s[1], s[0]
            q = Program(p.defs, p.inputs, tuple(s), p.answer)
        if classify(q) != classify(p):
            continue
        try:
            t1 = render(p, fid, preamble_level=2)["text"]
            t2 = render(q, fid, preamble_level=2)["text"]
        except Exception as e:
            continue
        a, b = run(p), run(q)
        if t1 == t2 and q != p:
            hits.append((shape, fid, a.ok, b.ok, str(a.value), str(b.value),
                         a.value != b.value if (a.ok and b.ok) else None))
print("wrong-plan programs that re-render to the SAME bytes:", len(hits))
for h in hits[:8]:
    print("  ", h)
