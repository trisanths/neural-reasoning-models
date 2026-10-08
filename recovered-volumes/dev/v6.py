import gzip, json, sys, collections
sys.path.insert(0,'/home/ec2-user/decoupled-reasoner')
from src.norm import ndata
import numpy as np
iv, ov = ndata._vocab()
g=ndata.split_frames()
print({k:len(v) for k,v in g.items()})
tr=set(g['train'])
D='/home/ec2-user/decoupled-reasoner/results/norm/compare/'
items=[json.loads(l) for l in gzip.open(D+'items.jsonl.gz','rt')]
bad=[it for it in items if it['split']!='train' and it['fid'] in tr]
print('held-out items whose fid is actually a training fid:',len(bad))
# find a colliding qframe item and locate the training row
ins,outs,ioff,ooff=ndata.load_split('data/norm/train')
meta=None
idx={}
for i in range(len(ioff)-1):
    idx.setdefault(ins[ioff[i]:ioff[i+1]].astype('<u2').tobytes(), i)
ex=[it for it in items if it['split']=='qframe' and it['shape']=='exclusion'][0]
ids,slots,nu=iv.encode(ex['text'])
b=np.asarray(ids,dtype=np.uint16).tobytes()
j=idx.get(b)
print('example fid:',ex['fid'],'in train fids?',ex['fid'] in tr,'match row:',j)
m=ndata.load_meta('data/norm/train')
print('matching training row fid:',m[j]['fid'],'shape',m[j]['shape'])
print('same target too?', outs[ooff[j]:ooff[j+1]].astype('<u2').tobytes()==None)
print()
print('EVAL TEXT:'); print(ex['text'][:500])
print('EVAL slots:',slots[:10])
print('TRAIN row slots:', m[j]['slots'][:10])
