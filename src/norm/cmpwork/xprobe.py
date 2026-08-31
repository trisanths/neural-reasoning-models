import gzip, json, collections, random, numpy as np, torch
from src.norm import gen, ndata, nmodel, neval, render
from src.norm.interp import run
from src.norm.lang import Table, program_json
from src.norm.neval import candidates
from src.norm.ntok import deserialize
from src.norm.shapes import assemble

R = {json.loads(l)["id"]: json.loads(l) for l in gzip.open("results/norm/compare/x_c_l.jsonl.gz","rt")}
c = collections.Counter((r["greedy"]["state"], r["greedy"].get("reason","")[:60]) for r in R.values())
print("C_l states on x_items:", c.most_common(6))

iv, ov = ndata._vocab()
ck = torch.load("results/norm/train/ckpt_l.pt", map_location="cpu", weights_only=False)
m = nmodel.build(ck["size"], len(iv), len(ov)).cuda(); m.load_state_dict(ck["state"]); m.eval()
sp = ndata.split_frames(); fid = sorted(sp["train"])[0]

def grid(seed, overlap):
    rng = random.Random(seed)
    lex = gen.lexicon_for(fid, rng)
    pool = lex.words(6 - overlap)
    rows = pool[:3]
    cols = pool[3-overlap:6-overlap]
    cells = lex.words(9)
    name = lex.name()
    ent, t = [], 0
    for a in rows:
        for b in cols:
            ent.append(((a, b), cells[t])); t += 1
    tbl = Table(name, tuple(ent))
    return assemble("pair", tables=[tbl], inputs=(("x", rows[0]), ("y", cols[1])))

for overlap in (0, 1, 2, 3):
    progs, encs = [], []
    for s in range(40):
        p = grid(1000 + s, overlap)
        d = render.render(p, fid, 1)
        ids, slots, unk = iv.encode(d["text"])
        progs.append(p); encs.append({"ids": np.asarray(ids, dtype="int64"), "slots": slots})
    em = neval.emit(m, encs, ov, "cuda", "greedy", batch=40, max_len=320)
    ok = ex = 0
    reasons = collections.Counter()
    for p, e, en in zip(progs, em, encs):
        try:
            g = deserialize(ov.decode(e), en["slots"])
        except Exception as exc:
            reasons[f"malformed {type(exc).__name__}"] += 1; continue
        ex += int(g == p)
        r = run(g)
        if r.ok and r.text == run(p).text: ok += 1
        elif not r.ok: reasons[f"refused {r.reason[:40]}"] += 1
    print(f"overlap={overlap} rows/cols share {overlap} symbols: answer_ok={ok}/40 exact={ex}/40 {reasons.most_common(3)}")
