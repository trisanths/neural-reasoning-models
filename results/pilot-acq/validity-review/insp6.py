import json,collections
for m in ['lfm2.5-350m-base']:
    rb=[json.loads(l) for l in open(f'/mnt/nvme/pilot/smoke/records/gen__{m}__think0.jsonl')]
    print(m,'answer_found',sum(r['answer_found'] for r in rb),'n_named==0',sum(r['n_named']==0 for r in rb),'of',len(rb))
