import gzip, json, collections, sys
sys.path.insert(0,'/home/ec2-user/decoupled-reasoner')
from src.norm.cmpwork.grade import forced

D='/home/ec2-user/decoupled-reasoner/results/norm/compare/'
def load(n): return [json.loads(l) for l in gzip.open(D+n+'.jsonl.gz','rt')]

b=load('b'); cl=load('c_l'); cxs=load('c_xs')
print('n', len(b), len(cl), len(cxs))
by=lambda rs:{r['id']:r for r in rs}
B,CL,CXS=by(b),by(cl),by(cxs)
ids=list(B)

cell=collections.defaultdict(lambda: collections.defaultdict(list))
for i in ids:
    rb,rl,rx=B[i],CL[i],CXS[i]
    k=(rb['split'],rb['shape'])
    g,o=rb['gold'],rb['options']
    cell[k]['b_oracle'].append(forced(rb['b_oracle']['answer'],o,g)['strict_correct'])
    cell[k]['b_train'].append(forced(rb['b_train']['answer'],o,g)['strict_correct'])
    cell[k]['cl_g'].append(forced(rl['greedy']['answer'],o,g)['strict_correct'])
    cell[k]['cl_s'].append(forced(rl['sampled']['answer'],o,g)['strict_correct'])
    cell[k]['cxs_g'].append(forced(rx['greedy']['answer'],o,g)['strict_correct'])
    cell[k]['cxs_s'].append(forced(rx['sampled']['answer'],o,g)['strict_correct'])
    cell[k]['cl_g_exact'].append(rl['greedy'].get('exact',0))
    cell[k]['cl_s_exact'].append(rl['sampled'].get('exact',0))
    cell[k]['cxs_g_exact'].append(rx['greedy'].get('exact',0))
    cell[k]['cxs_s_exact'].append(rx['sampled'].get('exact',0))

m=lambda v: sum(v)/len(v)
# 1. B oracle total
tot=[x for k in cell for x in cell[k]['b_oracle']]
print('B oracle strict total: %d/%d = %.4f'%(sum(tot),len(tot),m(tot)))
print('B oracle cells at 1.0:', sum(1 for k in cell if m(cell[k]['b_oracle'])==1.0), 'of', len(cell))

# 2. 36-cell claim
held=[k for k in cell if k[0] in ('lexicon','mode','mixed')]
print('held cells', len(held))
bad=[]
for k in sorted(held):
    bt=m(cell[k]['b_train'])
    for col in ('cl_g','cl_s','cxs_g','cxs_s'):
        if m(cell[k][col])<=bt: bad.append((k,col,round(m(cell[k][col]),4),round(bt,4)))
print('cells where C does NOT beat b_train:')
for x in bad: print('  ',x)

# 3. C exact 1.0 cells
for col in ('cl_g_exact','cl_s_exact','cxs_g_exact','cxs_s_exact'):
    ones=[k for k in cell if m(cell[k][col])==1.0]
    print(col,'cells at exact 1.0000:',len(ones),'of',len(cell))
    print('   e.g.',sorted(ones)[:8])
# also accuracy 1.0 cells
for col in ('cl_g','cl_s','cxs_g','cxs_s'):
    ones=[k for k in cell if m(cell[k][col])==1.0]
    print(col,'cells at accuracy 1.0000:',len(ones),'of',len(cell))
