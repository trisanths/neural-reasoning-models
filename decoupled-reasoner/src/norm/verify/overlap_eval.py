import numpy as np, gzip, json, hashlib, pickle, collections
tgt,inp,pair=pickle.load(open("/tmp/leak_sets.pkl","rb"))
print("train uniq t/i",len(tgt),len(inp))
out={}
for sp in ["train_frames_eval","qframe","lexicon","mode","mixed"]:
    z=np.load(f"data/norm/{sp}.npz")
    outs=z["outs"];ooff=z["ooff"];ins=z["ins"];ioff=z["ioff"]
    meta=[json.loads(l) for l in gzip.open(f"data/norm/{sp}.meta.jsonl.gz","rt")]
    ob=outs.tobytes(); ib=ins.tobytes()
    N=2800
    per=collections.defaultdict(lambda: collections.Counter())
    for i in range(N):
        sh=meta[i]["shape"]
        t=ob[2*ooff[i]:2*ooff[i+1]]; x=ib[2*ioff[i]:2*ioff[i+1]]
        ht=hashlib.blake2b(t,digest_size=16).digest()
        hx=hashlib.blake2b(x,digest_size=16).digest()
        c=per[sh]; c["n"]+=1
        c["t_seen"]+=int(ht in tgt); c["i_seen"]+=int(hx in inp); c["p_seen"]+=int((ht+hx) in pair)
    tot=collections.Counter()
    for sh in per: tot+=per[sh]
    out[sp]={"per_shape":{k:dict(v) for k,v in per.items()},"pooled":dict(tot)}
    print(sp,"pooled n",tot["n"],"input seen in train",tot["i_seen"],round(tot["i_seen"]/tot["n"],4),
          "target seen",round(tot["t_seen"]/tot["n"],4))
json.dump(out,open("/tmp/leak_eval.json","w"),indent=1)
