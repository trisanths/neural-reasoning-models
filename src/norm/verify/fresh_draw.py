import random, hashlib, pickle, json, collections
import numpy as np
from src.norm import ndata
tgt,inp,pair=pickle.load(open("/tmp/leak_sets.pkl","rb"))
groups=ndata.split_frames(); fids=groups["train"]
rng=random.Random(987654321)
shapes=["lookup_general","exclusion","inverse","precedence","pair","lookup","priority","iterate","classify","compose","sum_chain","apply_n"]
res={}
for sh in shapes:
    hit=0; n=0; uniq=set()
    while n<1500:
        fid=rng.choice(fids)
        e=ndata.build_example(fid, sh, rng.randrange(1<<60), rng.randrange(0,9))
        if e is None: continue
        b=np.asarray(e["in"],dtype=np.uint16).tobytes()
        h=hashlib.blake2b(b,digest_size=16).digest()
        uniq.add(h); hit+=int(h in inp); n+=1
    res[sh]={"n":n,"already_in_training":hit,"rate":round(hit/n,4),"uniq_drawn":len(uniq)}
    print("%-18s fresh draws=%d already in training set=%d (%.4f)  distinct drawn=%d" % (sh,n,hit,hit/n,len(uniq)))
json.dump(res,open("/tmp/fresh.json","w"),indent=1)
