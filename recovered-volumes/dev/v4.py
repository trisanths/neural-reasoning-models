import gzip, json, collections, sys
sys.path.insert(0,'/home/ec2-user/decoupled-reasoner')
from src.norm import ndata
from src.norm.ntok import serialize
from src.norm.lang import program_load
from src.norm.cmpwork.grade import forced
import numpy as np

iv, ov = ndata._vocab()
D='/home/ec2-user/decoupled-reasoner/results/norm/compare/'
items={json.loads(l)['id']:json.loads(l) for l in gzip.open(D+'items.jsonl.gz','rt')}
cl={json.loads(l)['id']:json.loads(l) for l in gzip.open(D+'c_l.jsonl.gz','rt')}
cxs={json.loads(l)['id']:json.loads(l) for l in gzip.open(D+'c_xs.jsonl.gz','rt')}

ins,outs,ioff,ooff=ndata.load_split('data/norm/train')
tr=set()
for i in range(len(ooff)-1):
    tr.add(outs[ooff[i]:ooff[i+1]].astype('<u2').tobytes())
# also the exact INPUT streams
tri=set()
for i in range(len(ioff)-1):
    tri.add(ins[ioff[i]:ioff[i+1]].astype('<u2').tobytes())
print('distinct training inputs', len(tri))

rows=[]
for iid,it in items.items():
    ids,slots,nu=iv.encode(it['text'])
    t=serialize(program_load(it['prog']),slots)
    tb=np.asarray([ov.bos]+ov.encode(list(t))+[ov.eos],dtype=np.uint16).tobytes()
    ib=np.asarray(ids,dtype=np.uint16).tobytes()
    rows.append((it['split'],it['shape'],tb in tr, ib in tri,
                 cl[iid]['greedy'].get('exact',0), cxs[iid]['greedy'].get('exact',0)))
print('eval INPUTS appearing verbatim in training:', sum(r[3] for r in rows),'/',len(rows))

held=[r for r in rows if r[0] in ('lexicon','mode','mixed')]
for name,sub in (('ALL 3000',rows),('held-out frames only',held)):
    for memo in (True,False):
        s=[r for r in sub if r[2]==memo]
        if not s: continue
        print('%-22s target seen in training=%-5s n=%4d  C45.5M exact=%.4f  C0.40M exact=%.4f'%(
            name,memo,len(s),sum(r[4] for r in s)/len(s),sum(r[5] for r in s)/len(s)))
print()
print('per shape, held-out frames only:')
byshape=collections.defaultdict(list)
for r in held: byshape[r[1]].append(r)
for sh in sorted(byshape):
    s=byshape[sh]
    mem=sum(r[2] for r in s)/len(s)
    print('  %-18s memorizable_target=%.3f  C45.5M exact=%.4f  C0.40M exact=%.4f'%(
        sh,mem,sum(r[4] for r in s)/len(s),sum(r[5] for r in s)/len(s)))
