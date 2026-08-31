import gzip, json, collections, numpy as np, torch
from src.norm import ndata, neval, nmodel
from src.norm.interp import run
from src.norm.lang import program_load, pretty
from src.norm.ntok import deserialize

iv, ov = ndata._vocab()
ck = torch.load("results/norm/compare/ft_xs_k1024.pt", map_location="cpu", weights_only=False)
m = nmodel.build(ck["size"], len(iv), len(ov)).cuda(); m.load_state_dict(ck["state"]); m.eval()
items = [json.loads(l) for l in gzip.open("results/norm/compare/x_items.jsonl.gz", "rt")]
items = [it for it in items if it["split"] == "train"][:60]
enc = []
for it in items:
    ids, slots, unk = iv.encode(it["text"])
    enc.append({"ids": np.asarray(ids, dtype=np.int64), "slots": slots})
em = neval.emit(m, [{"ids": e["ids"]} for e in enc], ov, "cuda", "greedy", batch=32, max_len=320)
cnt = collections.Counter(); shown = 0
for it, e, en in zip(items, em, enc):
    gold = program_load(it["prog"])
    try:
        got = deserialize(ov.decode(e), en["slots"])
    except Exception as ex:
        cnt["malformed"] += 1; continue
    r = run(got)
    right = r.ok and r.text == it["gold"]
    if got == gold:
        cnt["exact"] += 1; continue
    gd, dd = gold.defs[0], got.defs[0]
    same_name = gd.name == dd.name
    same_keys = [k for k, _ in gd.entries] == [k for k, _ in dd.entries]
    same_vals = [v for _, v in gd.entries] == [v for _, v in dd.entries]
    cnt[(f"name={same_name}", f"keyorder={same_keys}", f"vals={same_vals}",
         f"inputs={got.inputs == gold.inputs}", "right" if right else "wrong")] += 1
    if shown < 2 and right:
        shown += 1
        print("--- an item answered right whose structure is not exact")
        print("  gold entries:", gd.entries)
        print("  got  entries:", dd.entries)
        print("  gold inputs:", gold.inputs, " got inputs:", got.inputs)
print(cnt.most_common(8))
