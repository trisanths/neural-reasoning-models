import gzip, json, collections, sys
sys.path.insert(0,'/home/ec2-user/decoupled-reasoner')
from src.norm import ndata
from src.norm.ntok import serialize
from src.norm.lang import program_load
import numpy as np, os

iv, ov = ndata._vocab()
D='/home/ec2-user/decoupled-reasoner/results/norm/compare/'
items=[json.loads(l) for l in gzip.open(D+'items.jsonl.gz','rt')]

# show modal streams for the degenerate shapes
seen=collections.defaultdict(collections.Counter)
tgt={}
for it in items:
    ids,slots,nu=iv.encode(it['text'])
    toks=tuple(serialize(program_load(it['prog']),slots))
    seen[it['shape']][toks]+=1
    tgt[it['id']]=toks
for sh in ('lookup_general','exclusion','lookup','pair'):
    print('---',sh)
    for t,c in seen[sh].most_common(3):
        print('  n=%d  %s'%(c,' '.join(t)[:220]))

print()
print('train npz present:', os.path.exists('data/norm/train.npz'))
if os.path.exists('data/norm/train.npz'):
    ins,outs,ioff,ooff=ndata.load_split('data/norm/train')
    n=len(ooff)-1
    print('train examples',n)
    tr=set()
    for i in range(n):
        tr.add(bytes(outs[ooff[i]:ooff[i+1]].astype('<u2').tobytes()))
    print('distinct training target streams:',len(tr))
    hit=0; tot=0
    for it in items:
        t=tgt[it['id']]
        enc=[ov.bos]+ov.encode(list(t))+[ov.eos]
        b=np.asarray(enc,dtype=np.uint16).tobytes()
        tot+=1; hit+= (b in tr)
    print('eval targets that appear verbatim in the training set: %d / %d = %.4f'%(hit,tot,hit/tot))
    # per split
    per=collections.defaultdict(lambda:[0,0])
    for it in items:
        t=tgt[it['id']]
        b=np.asarray([ov.bos]+ov.encode(list(t))+[ov.eos],dtype=np.uint16).tobytes()
        per[it['split']][1]+=1; per[it['split']][0]+= (b in tr)
    for k,(h,t2) in sorted(per.items()): print('   %-8s %d/%d = %.4f'%(k,h,t2,h/t2))
    per=collections.defaultdict(lambda:[0,0])
    for it in items:
        t=tgt[it['id']]
        b=np.asarray([ov.bos]+ov.encode(list(t))+[ov.eos],dtype=np.uint16).tobytes()
        per[it['shape']][1]+=1; per[it['shape']][0]+= (b in tr)
    for k,(h,t2) in sorted(per.items()): print('   %-18s %d/%d = %.4f'%(k,h,t2,h/t2))
