"""The gate rerun with a deliberately wrong reader, to price each check.

The reader is the real parser with one thing broken: it returns a program whose
plan is right but whose answer slot points at the wrong step. Nothing about the
rendered text depends on the answer slot, so this is a reader that "guessed the
plan from the shape alone" in the sense CORE section 6 says rerender catches.
"""
import random, json
from collections import Counter, defaultdict
from src.norm.gen import make_for
from src.norm.render import render, SHAPES, frames
from src.norm.parse import parse
from src.norm.interp import run
from src.norm.lang import Program

fr, bank = frames()
rng = random.Random(20260830)
tot = Counter(); per = defaultdict(Counter)
for fi, f in enumerate(fr):
    for si, shape in enumerate(SHAPES):
        seed = 20260830 + fi * 1000 + si * 37
        pre = rng.randrange(0, 13)
        p = make_for(f.fid, shape, seed)
        if len(p.steps) < 2:
            continue
        text = render(p, f.fid, preamble_level=pre)["text"]
        got = parse(text, f.fid)
        if not got.ok:
            tot["unparsed"] += 1
            continue
        q0 = got.program
        others = [s.out for s in q0.steps if s.out != q0.answer]
        if not others:
            continue
        q = Program(q0.defs, q0.inputs, q0.steps, others[-1])
        text2 = render(q, f.fid, preamble_level=pre)["text"]
        a, b = run(p), run(q)
        rec = {
            "parsed": True,
            "identical": q == p,
            "rerender": text2 == text,
            "executes": bool(a.ok and b.ok and a.value == b.value),
        }
        for k, v in rec.items():
            tot[k] += int(v); per[shape][k] += int(v)
        tot["n"] += 1; per[shape]["n"] += 1

n = tot["n"]
print("items with a plan of two or more steps:", n)
for k in ("parsed", "identical", "rerender", "executes"):
    print(f"  {k:10s} {tot[k]/n:.4f}  ({tot[k]}/{n})")
print()
for s in sorted(per):
    c = per[s]
    print(f"  {s:18s} n={c[n]:4d}  identical={c[identical]/c[n]:.3f}"
          f"  rerender={c[rerender]/c[n]:.3f}"
          f"  executes={c[executes]/c[n]:.3f}")
