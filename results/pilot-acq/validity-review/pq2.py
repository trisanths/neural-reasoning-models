import json, collections, random
from datasets import load_dataset
rows=[dict(r) for r in load_dataset("akariasai/PopQA", split="test")]
items=[json.loads(l) for l in open("/mnt/nvme/pilot/items/popqa_fc.jsonl")]
objfreq=collections.defaultdict(collections.Counter)
for r in rows: objfreq[r["prop"]][r["obj"].strip()]+=1
for trial in range(3):
    rng=random.Random(trial); acc=0; accq=collections.Counter(); nq=collections.Counter(); pp=collections.defaultdict(lambda:[0,0])
    for it in items:
        f=[objfreq[it["prop"]][o] - (1 if k==it["gold_index"] else 0) for k,o in enumerate(it["options"])]
        m=max(f); best=[k for k,v in enumerate(f) if v==m]
        c = rng.choice(best)==it["gold_index"]
        acc+=c; nq[it["quartile"]]+=1; accq[it["quartile"]]+=c; pp[it["prop"]][0]+=c; pp[it["prop"]][1]+=1
    print("LOO freq-prior acc", acc/len(items), {q:round(accq[q]/nq[q],3) for q in sorted(nq)})
print({k:(v[1],round(v[0]/v[1],2)) for k,v in pp.items()})
ex=[it for it in items if it["prop"] in ("occupation","sport","country","genre")][:8]
for it in ex: print(it["question"],"|",it["options"],"gold",it["gold"])
