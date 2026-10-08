import json, random
from src.norm import ndata, gen, render
from src.norm.interp import run
from src.norm.neval import candidates
from src.frames.generate import FRAMES as FFRAMES

sp = ndata.split_frames()
print("split sizes:", {k: len(v) for k, v in sp.items()})
for k, v in sp.items():
    print(k, "sample", sorted(v)[:2])

nf = render.frames()
print("render frames n:", len(nf))
ids = sorted(render._BY_ID.keys()) if render._BY_ID else []
print("render frame id sample:", ids[:3])
print("frames.generate FRAMES n:", len(FFRAMES))
fk = sorted(FFRAMES.keys())
print("frames.generate id sample:", fk[:3])
print("same id set:", set(ids) == set(fk))

# closed candidate sets per shape
rng = random.Random(0)
fid = sorted(sp["train"])[0]
print("fid:", fid)
for sh in render.SHAPES:
    try:
        p = gen.make_for(fid, sh, 7)
    except Exception as e:
        print(sh, "GEN FAIL", type(e).__name__, e); continue
    try:
        d = render.render(p, fid, 1)
    except Exception as e:
        print(sh, "RENDER FAIL", type(e).__name__, e); continue
    c = candidates(p)
    r = run(p)
    print(f"{sh:18s} cand={'None' if c is None else len(c)} ok={r.ok} ans={r.text!r} pages={len(d['pages'])} chars={len(d['text'])}")
