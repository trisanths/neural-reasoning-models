import json,collections,glob
for f in sorted(glob.glob('/mnt/nvme/pilot/smoke/records/gen__*.jsonl')):
    rs=[json.loads(l) for l in open(f)]
    print(f.split('/')[-1], len(rs))
    print('  finish', collections.Counter(r['finish_reason'] for r in rs))
    print('  answer_found', sum(r['answer_found'] for r in rs), 'hedge', sum(r['hedge'] for r in rs), 'correct', sum(r['correct'] for r in rs), 'lenient', sum(r['correct_lenient'] for r in rs))
    print('  max prompt tok', max(r['n_prompt_tokens'] for r in rs), 'trunc', sum(r['think_truncated'] for r in rs))
    print('  keys', sorted(rs[0].keys()))
    for r in rs[:6]:
        print('   ', r['condition'], r['family'], r['level'], 'ans=',r['answer'], '| line=',repr(r['answer_line'][:80]), '| text=',repr(r['text'][:120]))
