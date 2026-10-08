"""How load-bearing is the frame id the parser is handed?

The gate calls parse(text, fid). Nothing in the text says which frame wrote it.
Ask: does the text alone pick out the structure, or does the hint do work?
"""
import random, sys, time, json
from collections import Counter
from src.norm.gen import make_for
from src.norm.render import render, SHAPES, frames
from src.norm.parse import parse

fr, bank = frames()
fids = [f.fid for f in fr]
rng = random.Random(4242)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 150

items = []
for i in range(N):
    fid = fids[rng.randrange(len(fids))]
    shape = SHAPES[i % len(SHAPES)]
    seed = 700000 + i
    pre = rng.randrange(0, 13)
    p = make_for(fid, shape, seed)
    items.append((fid, shape, p, render(p, fid, preamble_level=pre)["text"]))

t0 = time.time()
uniq = 0; recovered = 0; nmatch = Counter(); wrong_but_ok = 0
for fid, shape, p, text in items:
    hits = []
    for g in fids:
        try:
            r = parse(text, g)
        except Exception:
            continue
        if r.ok:
            hits.append((g, r.program))
    nmatch[len(hits)] += 1
    if len(hits) == 1:
        uniq += 1
        recovered += int(hits[0][1] == p)
    else:
        # a frame-blind reader has to choose; count how often the wrong frames
        # that also parse give the right program anyway
        good = sum(1 for g, q in hits if q == p)
        if good == len(hits) and hits:
            wrong_but_ok += 1
print("items:", N, "seconds:", round(time.time() - t0, 1))
print("frames that parse, histogram:", dict(sorted(nmatch.items())))
print("unique frame:", uniq, " and program recovered there:", recovered)
print("multi-frame items where every parsing frame gives the same right program:",
      wrong_but_ok)
