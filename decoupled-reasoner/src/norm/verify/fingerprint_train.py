import numpy as np, gzip, json, hashlib, collections, sys
z=np.load("data/norm/train.npz")
outs=z["outs"]; ooff=z["ooff"]; ins=z["ins"]; ioff=z["ioff"]
n=len(ooff)-1
print("train n",n)
tgt=set(); pair=set(); inp=set()
ob=outs.tobytes(); ib=ins.tobytes()
for i in range(n):
    t=ob[2*ooff[i]:2*ooff[i+1]]
    x=ib[2*ioff[i]:2*ioff[i+1]]
    ht=hashlib.blake2b(t,digest_size=16).digest()
    hx=hashlib.blake2b(x,digest_size=16).digest()
    tgt.add(ht); inp.add(hx); pair.add(ht+hx)
print("uniq targets",len(tgt),"uniq inputs",len(inp),"uniq pairs",len(pair))
json.dump({"n":n,"uniq_t":len(tgt),"uniq_i":len(inp),"uniq_p":len(pair)},open("/tmp/leak_train.json","w"))
import pickle
pickle.dump((tgt,inp,pair),open("/tmp/leak_sets.pkl","wb"),protocol=4)
