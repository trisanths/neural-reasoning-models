import json, collections, random
from datasets import load_dataset
rows=[dict(r) for r in load_dataset("akariasai/PopQA", split="test")]
items=[json.loads(l) for l in open("/mnt/nvme/pilot/items/popqa_fc.jsonl")]
print("n",len(items), "gold idx", collections.Counter(i["gold_index"] for i in items))
objfreq=collections.defaultdict(collections.Counter)
for r in rows: objfreq[r["prop"]][r["obj"].strip()]+=1
byid={r["id"]:r for r in rows}
# frequency prior baseline
acc=0; ties=0; accq=collections.Counter(); nq=collections.Counter()
rng=random.Random(0)
for it in items:
    f=[objfreq[it["prop"]][o] for o in it["options"]]
    m=max(f); best=[k for k,v in enumerate(f) if v==m]
    pick=rng.choice(best)
    c = pick==it["gold_index"]
    acc+=c; nq[it["quartile"]]+=1; accq[it["quartile"]]+=c
print("freq-prior baseline acc", acc/len(items), {q:round(accq[q]/nq[q],3) for q in sorted(nq)})
# per prop
pp=collections.defaultdict(lambda:[0,0])
for it in items:
    f=[objfreq[it["prop"]][o] for o in it["options"]]
    pp[it["prop"]][0]+= (f.index(max(f))==it["gold_index"]); pp[it["prop"]][1]+=1
print({k:(v[1],round(v[0]/v[1],2)) for k,v in pp.items()})
# lengths
gl=[len(it["gold"]) for it in items]; dl=[len(o) for it in items for k,o in enumerate(it["options"]) if k!=it["gold_index"]]
print("mean chars gold",sum(gl)/len(gl),"distractor",sum(dl)/len(dl))
longest=sum(1 for it in items if max(range(4),key=lambda k:len(it["options"][k]))==it["gold_index"])
shortest=sum(1 for it in items if min(range(4),key=lambda k:len(it["options"][k]))==it["gold_index"])
print("gold is longest",longest/len(items),"gold is shortest",shortest/len(items))
# distractor also correct: another row with same subj+prop has that obj, or distractor in aliases of same-subject rows
subjprop=collections.defaultdict(set)
for r in rows:
    s=set([r["obj"].strip().lower()])
    for key in ("possible_answers","o_aliases"):
        v=r.get(key)
        if isinstance(v,str):
            try: v=json.loads(v)
            except Exception: v=[v]
        for a in v or []:
            if isinstance(a,str): s.add(a.strip().lower())
    subjprop[(r["subj"],r["prop"])]|=s
multi=0; ex=[]
for it in items:
    r=byid[int(it["item_id"].split("-")[1])]
    ok=subjprop[(r["subj"],r["prop"])]
    for k,o in enumerate(it["options"]):
        if k!=it["gold_index"] and o.lower() in ok:
            multi+=1; ex.append((it["question"],it["gold"],o)); break
print("items with a distractor that is also a gold for the same subject+relation", multi, ex[:5])
# distractor in question, alias in question
dq=sum(1 for it in items if any(o.lower() in it["question"].lower() for k,o in enumerate(it["options"]) if k!=it["gold_index"]))
print("distractor string in question",dq)
aq=0
for it in items:
    r=byid[int(it["item_id"].split("-")[1])]
    al=[a.lower() for a in json.loads(r["possible_answers"]) if len(a)>2]
    if any(a in it["question"].lower() for a in al): aq+=1
print("gold alias in question",aq)
# substring overlap: distractor is prefix/substring of gold or vice versa
sub=sum(1 for it in items if any((o.lower() in it["gold"].lower() or it["gold"].lower() in o.lower()) for k,o in enumerate(it["options"]) if k!=it["gold_index"]))
print("distractor substring of gold or vice versa",sub)
# frequency of gold rank in pool
print("props",collections.Counter(it["prop"] for it in items).most_common(16))
