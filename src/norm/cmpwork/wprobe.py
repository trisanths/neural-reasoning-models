import random, collections, numpy as np, torch
from src.norm import gen, ndata, neval, nmodel, render
from src.norm.interp import run
from src.norm.ntok import deserialize
from src.norm.cmpwork.wdepth import case
from src.norm.neval import candidates

iv, ov = ndata._vocab()
ck = torch.load("results/norm/train/ckpt_l.pt", map_location="cpu", weights_only=False)
m = nmodel.build(ck["size"], len(iv), len(ov)).cuda(); m.load_state_dict(ck["state"]); m.eval()
fids = sorted(ndata.split_frames()["train"])

for (w, d) in ((14, 12), (12, 2), (10, 2)):
    items, encs = [], []
    for s in range(40):
        fid = fids[s % len(fids)]
        p = case(fid, 30011 + s * 7919 + w * 101 + d, d, w)
        doc = render.render(p, fid, s % 5)
        r = run(p)
        cs = candidates(p)
        if not r.ok or cs is None or r.text not in cs: continue
        ids, slots, unk = iv.encode(doc["text"])
        items.append((p, r.text)); encs.append({"ids": np.asarray(ids, dtype=np.int64), "slots": slots})
    em = neval.emit(m, [{"ids": e["ids"]} for e in encs], ov, "cuda", "greedy", batch=32, max_len=320)
    stat = collections.Counter()
    for (p, gold), e, en in zip(items, em, encs):
        try:
            g = deserialize(ov.decode(e), en["slots"])
        except Exception:
            stat["malformed"] += 1; continue
        rr = run(g)
        same_defs = g.defs == p.defs
        same_steps = len(g.steps) == len(p.steps)
        same_in = g.inputs == p.inputs
        right = rr.ok and rr.text == gold
        stat[(("defs" if same_defs else "DEFS"), ("nsteps" if same_steps else f"NSTEPS{len(g.steps)}"),
              ("in" if same_in else "IN"), "right" if right else "wrong")] += 1
    print(f"width {w} depth {d}:", stat.most_common(6))
