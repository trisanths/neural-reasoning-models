import random
from src.norm import gen, ndata, render
from src.norm.lang import Table, pretty
from src.norm.shapes import assemble
from src.norm.interp import run
from src.norm.parse import parse
from src.norm.ntok import serialize
from src.norm.neval import candidates

sp = ndata.split_frames()
fid = sorted(sp["train"])[0]
iv, ov = ndata._vocab()

rng = random.Random(3)
lex = gen.lexicon_for(fid, rng)
syms = lex.words(3)
cells = lex.words(9)
name = lex.name()
ent, t = [], 0
for a in syms:
    for b in syms:
        ent.append(((a, b), cells[t])); t += 1
tbl = Table(name, tuple(ent))
p = assemble("pair", tables=[tbl], inputs=(("x", syms[0]), ("y", syms[1])))
d = render.render(p, fid, 1)
print("PAGE:", d["pages"][0].replace("\n", " | "))
print("Q:", d["question"])
print("ans:", run(p).text, "cands:", sorted(candidates(p)))
pr = parse(d["text"], fid)
print("parse ok", pr.ok, "same", pr.ok and pr.program == p)
ids, slots, unk = iv.encode(d["text"]); print("in_tok", len(ids), "unk", unk, "out_tok", len(serialize(p, slots)) + 2)

tp = Table(name, tuple(((b, a), v) for (a, b), v in tbl.entries))
p2 = assemble("pair", tables=[tp], inputs=(("x", syms[0]), ("y", syms[1])))
d2 = render.render(p2, fid, 1)
print()
print("TPAGE:", d2["pages"][0].replace("\n", " | "))
print("Tans:", run(p2).text)
pr2 = parse(d2["text"], fid)
print("parse ok", pr2.ok, "same", pr2.ok and pr2.program == p2)
