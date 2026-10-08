import random, collections, numpy as np, torch
from src.norm import gen, ndata, nmodel, neval, render
from src.norm.interp import run
from src.norm.lang import Table
from src.norm.ntok import deserialize, serialize
from src.norm.parse import parse
from src.norm.shapes import assemble

iv, ov = ndata._vocab()
sp = ndata.split_frames(); fid = sorted(sp["train"])[0]


def grid(seed, overlap):
    rng = random.Random(seed)
    lex = gen.lexicon_for(fid, rng)
    pool = lex.words(6 - overlap)
    rows = pool[:3]
    cols = pool[3 - overlap:6 - overlap]
    cells = lex.words(9)
    name = lex.name()
    ent, t = [], 0
    for a in rows:
        for b in cols:
            ent.append(((a, b), cells[t])); t += 1
    return assemble("pair", tables=[Table(name, tuple(ent))],
                    inputs=(("x", rows[0]), ("y", cols[1])))


print("gold round trip through the seam and through the parser:")
for overlap in (0, 1, 2, 3):
    okser = okpar = 0
    err = collections.Counter()
    for s in range(20):
        p = grid(2000 + s, overlap)
        d = render.render(p, fid, 1)
        ids, slots, unk = iv.encode(d["text"])
        try:
            toks = serialize(p, slots)
            back = deserialize(toks, slots)
            okser += int(back == p)
        except Exception as exc:
            err[f"seam {type(exc).__name__}: {exc}"[:90]] += 1
        pr = parse(d["text"], fid)
        okpar += int(pr.ok and pr.program == p)
    print(f" overlap={overlap} seam_roundtrip={okser}/20 parser_exact={okpar}/20 {err.most_common(2)}")

ck = torch.load("results/norm/train/ckpt_l.pt", map_location="cpu", weights_only=False)
m = nmodel.build(ck["size"], len(iv), len(ov)).cuda(); m.load_state_dict(ck["state"]); m.eval()
print()
print("what the network writes when the two key columns share a symbol:")
for overlap in (1, 3):
    progs, encs = [], []
    for s in range(8):
        p = grid(2000 + s, overlap)
        d = render.render(p, fid, 1)
        ids, slots, unk = iv.encode(d["text"])
        progs.append(p); encs.append({"ids": np.asarray(ids, dtype="int64"), "slots": slots})
    em = neval.emit(m, encs, ov, "cuda", "greedy", batch=8, max_len=320)
    for k, (p, e, en) in enumerate(zip(progs, em, encs)):
        toks = ov.decode(e)
        try:
            deserialize(toks, en["slots"])
            msg = "ok"
        except Exception as exc:
            msg = f"{type(exc).__name__}: {exc}"
        if k < 3:
            print(f" overlap={overlap} #{k}: {msg}")
            print("   gold toks:", " ".join(serialize(p, en["slots"]))[:200])
            print("   got  toks:", " ".join(toks)[:200])
