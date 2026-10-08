import json
rs=[json.loads(l) for l in open('/mnt/nvme/pilot/smoke/records/gen__qwen3-0.6b__think1.jsonl')]
print('double close', sum(r['raw'].count('</think>')>=2 for r in rs), 'of', len(rs))
print('raw starts with <think>', sum(r['raw'].lstrip().startswith('<think>') for r in rs))
for r in rs:
    if not r['answer_found']:
        print('NOANS trunc=',r['think_truncated'],'ntok',r['n_answer_tokens'], repr(r['text'][-200:]))
for r in rs:
    if r['think_truncated']:
        print('TRUNC text', repr(r['text'][:150])); break
rs0=[json.loads(l) for l in open('/mnt/nvme/pilot/smoke/records/gen__qwen3-0.6b__think0.jsonl')]
print('think0 ans tokens max', max(r['n_answer_tokens'] for r in rs0))
import collections
for f in ['lfm2.5-350m-base']:
    rb=[json.loads(l) for l in open(f'/mnt/nvme/pilot/smoke/records/gen__{f}__think0.jsonl')]
    print('base first-line samples', [r['answer_line'][:40] for r in rb if r['family']!='refuniverse'][:15])
