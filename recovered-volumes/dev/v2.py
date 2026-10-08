import gzip, json, collections, sys
sys.path.insert(0,'/home/ec2-user/decoupled-reasoner')
from src.norm import ndata
from src.norm.ntok import serialize, TokenizeError
from src.norm.lang import program_load

iv, ov = ndata._vocab()
D='/home/ec2-user/decoupled-reasoner/results/norm/compare/'
items=[json.loads(l) for l in gzip.open(D+'items.jsonl.gz','rt')]
print('items',len(items))

per_shape=collections.defaultdict(collections.Counter)
per_cell=collections.defaultdict(collections.Counter)
inp_shape=collections.defaultdict(collections.Counter)
bad=0
for it in items:
    try:
        ids,slots,nu=iv.encode(it['text'])
        p=program_load(it['prog'])
        toks=tuple(serialize(p,slots))
    except Exception as e:
        bad+=1; continue
    per_shape[it['shape']][toks]+=1
    per_cell[(it['split'],it['shape'])][toks]+=1
    # delexicalised input: keep slot ids and digits/punct, blank English
    delex=tuple('S' if i>=iv.slot0 else 'E' for i in ids)
    inp_shape[it['shape']][delex]+=1
print('bad',bad)
print()
print('%-18s %6s %8s %8s %8s' % ('shape','n','distinct','modal','top1frac'))
for sh,c in sorted(per_shape.items()):
    n=sum(c.values()); mode=c.most_common(1)[0][1]
    print('%-18s %6d %8d %8d %8.3f'%(sh,n,len(c),mode,mode/n))
print()
print('distinct targets per (split,shape), 250 items each shape / 50 per cell:')
for k in sorted(per_cell):
    c=per_cell[k]; n=sum(c.values())
    print('  %-8s %-18s n=%d distinct=%d modal=%d'%(k[0],k[1],n,len(c),c.most_common(1)[0][1]))
