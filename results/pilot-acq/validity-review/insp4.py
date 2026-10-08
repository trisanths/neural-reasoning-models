import json,sys,os,tempfile,shutil,time
sys.path.insert(0,'/home/ec2-user/decoupled-reasoner')
from src.pilot import report
from src.pilot.items import file_sha, CONDITIONS
d=tempfile.mkdtemp(dir='/mnt/nvme/pilot/dev')
shutil.copy('/mnt/nvme/pilot/items/items.jsonl', d+'/items.jsonl')
shutil.copy('/mnt/nvme/pilot/items/popqa_fc.jsonl', d+'/popqa.jsonl')
time.sleep(1.1)
items=[json.loads(l) for l in open(d+'/items.jsonl')]
sha=file_sha(d+'/items.jsonl')
rec=d+'/records'; os.makedirs(rec)
# only the three configs the decision checks; everything wrong
for m in ['lfm2.5-350m-base','qwen3-0.6b-base','qwen3-1.7b-base']:
    with open(f'{rec}/gen__{m}__think0.jsonl','w') as fh:
        for it in items:
            for c in CONDITIONS:
                fh.write(json.dumps({'model':m,'thinking':False,'condition':c,'item_id':it['item_id'],'family':it['family'],'level':it['level'],'floor':it['floor'],'prompt_hash':it['prompt_hashes'][c],'items_sha':sha,'correct':False,'hedge':False,'correct_lenient':False,'answer_found':True,'think_truncated':False,'n_think_tokens':0, 'text':'Answer: '+str(it['answer'])})+'\n')
time.sleep(1.1)
r=report.build(d+"/items.jsonl", None, rec)
print("FAILS", [(f["model"],f["cell"],f["condition"],f["n"],f["k"],round(f["wilson_hi"],4),round(f["floor"],4)) for f in r["decision"]["validity"]["failures"]])
report.VALIDITY_SLACK=1.0
r=report.build(d+"/items.jsonl", None, rec)
print('NO POPQA, 3 configs only:', r['decision']['verdict'])
print('validity cells checked', r['decision']['validity']['cells_checked'])
# partial popqa: 10 items for each model, no full set
pq=[json.loads(l) for l in open(d+'/popqa.jsonl')][:10]
psha=file_sha(d+'/popqa.jsonl')
for m in ['lfm2.5-350m-base','qwen3-0.6b-base','qwen3-1.7b-base']:
    with open(f'{rec}/popqa__{m}.jsonl','w') as fh:
        for it in pq:
            fh.write(json.dumps({'model':m,'item_id':it['item_id'],'quartile':it['quartile'],'popqa_sha':psha,'correct':True,'correct_summed_nll':True})+'\n')
time.sleep(1.1)
r=report.build(d+"/items.jsonl", d+"/popqa.jsonl", rec)
print('PARTIAL POPQA (10/1000):', r['decision']['verdict'], [ (m,g['popqa_ok'],g['complete']) for m,g in r['decision']['go'].items()])
shutil.rmtree(d)
