import gzip, json, collections, sys
sys.path.insert(0,'/home/ec2-user/decoupled-reasoner')
from src.norm import ndata
import numpy as np
iv, ov = ndata._vocab()
D='/home/ec2-user/decoupled-reasoner/results/norm/compare/'
items=[json.loads(l) for l in gzip.open(D+'items.jsonl.gz','rt')]
ins,outs,ioff,ooff=ndata.load_split('data/norm/train')
tri=set()
for i in range(len(ioff)-1):
    tri.add(ins[ioff[i]:ioff[i+1]].astype('<u2').tobytes())
per=collections.defaultdict(lambda:[0,0])
pershape=collections.defaultdict(lambda:[0,0])
for it in items:
    ids,slots,nu=iv.encode(it['text'])
    b=np.asarray(ids,dtype=np.uint16).tobytes()
    per[it['split']][1]+=1; per[it['split']][0]+= (b in tri)
    pershape[(it['split'],it['shape'])][1]+=1; pershape[(it['split'],it['shape'])][0]+=(b in tri)
print('eval input verbatim in training, by split:')
for k,(h,t) in sorted(per.items()): print('  %-8s %d/%d = %.4f'%(k,h,t,h/t))
print('nonzero held-out cells:')
for k,(h,t) in sorted(pershape.items()):
    if k[0]!='train' and h: print('  ',k,h,'/',t)
