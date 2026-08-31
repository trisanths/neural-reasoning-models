import gzip, json, torch
from src.norm import ndata, nmodel, neval
from src.norm.interp import run
from src.norm.lang import pretty, program_load
from src.norm.ntok import deserialize
from src.norm.parse import parse

iv, ov = ndata._vocab()
ck = torch.load("results/norm/train/ckpt_l.pt", map_location="cpu", weights_only=False)
m = nmodel.build(ck["size"], len(iv), len(ov)).cuda(); m.load_state_dict(ck["state"]); m.eval()

items = [json.loads(l) for l in gzip.open("results/norm/compare/d_items.jsonl.gz", "rt")]
sel = []
for d in (1, 2, 3, 4, 10):
    sel += [it for it in items if it["split"] == "train" and it["depth"] == d][:2]
enc = []
for it in sel:
    ids, slots, unk = iv.encode(it["text"])
    enc.append({"ids": __import__("numpy").asarray(ids, dtype="int64"), "slots": slots})
em = neval.emit(m, enc, ov, "cuda", "greedy", batch=16, max_len=320)
for it, e, en in zip(sel, em, enc):
    gold = program_load(it["prog"])
    try:
        got = deserialize(ov.decode(e), en["slots"])
        r = run(got)
        gs = f"steps={len(got.steps)} ans={r.text if r.ok else '(refused)'}"
    except Exception as exc:
        got, gs = None, f"malformed {type(exc).__name__}"
    print(f"--- depth {it['depth']} gold_steps={len(gold.steps)} gold_ans={it['gold']} opts={len(it['options'])}")
    print("    Q:", it["question"])
    print("    got:", gs)
    if got is not None and len(got.steps) < 30:
        print("    got plan:", [(s.out, s.op, s.args) for s in got.steps][:6], "...")
        print("    gold plan:", [(s.out, s.op, s.args) for s in gold.steps][:6], "...")
        print("    defs equal:", got.defs == gold.defs, "inputs", got.inputs, gold.inputs)
