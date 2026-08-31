import numpy as np, gzip, json, hashlib, collections
z=np.load("data/norm/train.npz"); ins=z["ins"]; ioff=z["ioff"]; ib=ins.tobytes()
per=collections.defaultdict(set); cnt=collections.Counter()
i=0
for line in gzip.open("data/norm/train.meta.jsonl.gz","rt"):
    sh=json.loads(line)["shape"]
    per[sh].add(hashlib.blake2b(ib[2*ioff[i]:2*ioff[i+1]],digest_size=16).digest())
    cnt[sh]+=1; i+=1
out={sh:{"n":cnt[sh],"uniq":len(per[sh])} for sh in cnt}
json.dump(out,open("/tmp/space.json","w"),indent=1)
for sh in sorted(out,key=lambda s:out[s]["uniq"]):
    print("%-18s n=%7d uniq_inputs=%7d  dup_factor=%.2f" % (sh,out[sh]["n"],out[sh]["uniq"],out[sh]["n"]/out[sh]["uniq"]))
