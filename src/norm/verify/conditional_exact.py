import numpy as np, gzip, json, hashlib, pickle, collections
tgt,inp,pair=pickle.load(open("/tmp/leak_sets.pkl","rb"))
sp="train_frames_eval"
z=np.load(f"data/norm/{sp}.npz"); ins=z["ins"]; ioff=z["ioff"]; ib=ins.tobytes()
meta=[json.loads(l) for l in gzip.open(f"data/norm/{sp}.meta.jsonl.gz","rt")]
N=2800
seen=[]
for i in range(N):
    x=ib[2*ioff[i]:2*ioff[i+1]]
    seen.append(hashlib.blake2b(x,digest_size=16).digest() in inp)
for size in ["xs","l","m"]:
    recs=[json.loads(l) for l in gzip.open(f"results/norm/eval/{size}/records_{sp}_greedy.jsonl.gz","rt")]
    assert len(recs)==N, len(recs)
    bad=sum(1 for i in range(N) if recs[i]["shape"]!=meta[i]["shape"] or recs[i]["fid"]!=meta[i]["fid"])
    per=collections.defaultdict(lambda: collections.Counter())
    for i in range(N):
        sh=recs[i]["shape"]; c=per[sh]
        k="seen" if seen[i] else "unseen"
        c[k+"_n"]+=1; c[k+"_ex"]+=int(recs[i]["exact"])
    print("====",size,"alignment mismatches:",bad)
    tot=collections.Counter()
    for sh in sorted(per):
        c=per[sh]; tot+=c
        sn,se,un,ue=c["seen_n"],c["seen_ex"],c["unseen_n"],c["unseen_ex"]
        print("  %-18s seen %3d/%3d %s   unseen %3d/%3d %s" % (sh,se,sn,("%.3f"%(se/sn)) if sn else "  -  ",ue,un,("%.3f"%(ue/un)) if un else "  -  "))
    print("  POOLED seen %d/%d %.4f   unseen %d/%d %.4f" % (tot["seen_ex"],tot["seen_n"],tot["seen_ex"]/tot["seen_n"],tot["unseen_ex"],tot["unseen_n"],tot["unseen_ex"]/tot["unseen_n"]))
