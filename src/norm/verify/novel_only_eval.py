import json,gzip,hashlib,pickle,collections,os
import numpy as np, torch
from src.norm import ndata, neval, nmodel
tgt,inp,pair=pickle.load(open("/tmp/leak_sets.pkl","rb"))
sp="train_frames_eval"; N=7000
z=np.load(f"data/norm/{sp}.npz"); ins=z["ins"]; ioff=z["ioff"]; ib=ins.tobytes()
seen=[hashlib.blake2b(ib[2*ioff[i]:2*ioff[i+1]],digest_size=16).digest() in inp for i in range(N)]
print("full 7000 seen rate", round(sum(seen)/N,4), flush=True)
iv,ov=ndata._vocab()
items=neval.load_eval(f"data/norm/{sp}", N)
out={}
for size in ["xs","l"]:
    ck=torch.load(f"results/norm/train/ckpt_{size}.pt",map_location="cpu",weights_only=False)
    model=nmodel.build(ck["size"],len(iv),len(ov)).to("cuda"); model.load_state_dict(ck["state"])
    em=neval.emit(model,items,ov,"cuda","greedy",batch=64)
    ex=[]
    for it,e in zip(items,em):
        r=neval.classify_emission(ov.decode(e), it["slots"], it["prog"])
        ex.append(bool(r["exact"]))
    print(size,"params",ck["params"]["total"],"repro first2800 pooled exact",round(sum(ex[:2800])/2800,4),"full7000",round(sum(ex)/N,4),flush=True)
    per=collections.defaultdict(lambda: collections.Counter())
    for i,it in enumerate(items):
        c=per[it["shape"]]; k="seen" if seen[i] else "unseen"
        c[k+"_n"]+=1; c[k+"_ex"]+=int(ex[i])
    rows={}
    tot=collections.Counter()
    for sh in sorted(per):
        c=per[sh]; tot+=c
        rows[sh]={k:c[k] for k in c}
        sn,se,un,ue=c["seen_n"],c["seen_ex"],c["unseen_n"],c["unseen_ex"]
        print("   %-18s seen %4d/%4d %s  NOVEL %4d/%4d %s" % (sh,se,sn,("%.4f"%(se/sn)) if sn else " -- ",ue,un,("%.4f"%(ue/un)) if un else " -- "),flush=True)
    print("   POOLED seen %.4f (n=%d)  NOVEL %.4f (n=%d)" % (tot["seen_ex"]/tot["seen_n"],tot["seen_n"],tot["unseen_ex"]/tot["unseen_n"],tot["unseen_n"]),flush=True)
    out[size]={"rows":rows,"pooled_first2800":sum(ex[:2800])/2800,"pooled_7000":sum(ex)/N,
               "seen_n":tot["seen_n"],"seen_ex":tot["seen_ex"],"unseen_n":tot["unseen_n"],"unseen_ex":tot["unseen_ex"]}
    del model; torch.cuda.empty_cache()
json.dump(out,open("/tmp/novel.json","w"),indent=1)
print("done")
