import random
from src.norm import gen, ndata, render
from src.norm.lang import Table, pretty
from src.norm.shapes import assemble
from src.norm.interp import run
from src.norm.parse import parse
from src.norm.ntok import serialize
from src.corpus.lexicon import Lexicon

sp = ndata.split_frames()
fid = sorted(sp["train"])[0]
iv, ov = ndata._vocab()

for n in (1, 4, 8, 16, 48, 96):
    rng = random.Random(11)
    lex = gen.lexicon_for(fid, rng)
    width = 8
    name = lex.name(); ring = lex.words(width); rng.shuffle(ring)
    t = Table(name, tuple((ring[i], ring[(i+1) % width]) for i in range(width)))
    p = assemble("iterate", tables=[t], inputs=(("x", ring[0]),), n=n)
    d = render.render(p, fid, 1)
    r = run(p)
    ids, slots, unk = iv.encode(d["text"])
    toks = serialize(p, slots)
    pr = parse(d["text"], fid)
    print(f"n={n:3d} steps={len(p.steps):3d} ok={r.ok} ans={r.text} "
          f"in_tok={len(ids)} out_tok={len(toks)+2} unk={unk} "
          f"parse_ok={pr.ok} parse_same={pr.ok and pr.program==p} qlen={len(d['question'])}")
print()
print("Q:", render.render(assemble("iterate", tables=[t], inputs=(("x", ring[0]),), n=48), fid, 1)["question"])

# pair transposition
p = gen.make_for(fid, "pair", 7)
print()
print(pretty(p))
d = render.render(p, fid, 1)
print("PAGE:", d["pages"][0][:500].replace("\n", " | "))
print("Q:", d["question"])
