import json,collections
items=[json.loads(l) for l in open('/mnt/nvme/pilot/items/items.jsonl')]
it=[i for i in items if i['family']=='refuniverse' and i['level']==3][0]
print(it['prompts']['oracle'][-2500:])
print('=====SIBLING tail')
print(it['prompts']['sibling'][-1200:])
print('=====BLANK')
print(it['prompts']['blank'][-1500:])
print('=====CLOSED')
print(it['prompts']['closed_book'])
print('answer',it['answer'],'sib',it['sibling_answer'],'mod',it['modulus'])
for fam in ['algebra','binary_op','threshold_rule']:
    it=[i for i in items if i['family']==fam][0]
    print('=====',fam, it['answer'], it.get('candidates'), it['floor'])
    print(it['prompts']['closed_book'][-900:])
# prompt length in chars
L=[len(i['prompts'][c]) for i in items for c in i['prompts']]
print('max chars',max(L))
# floors and answer kinds
print(collections.Counter((i['family'],i['answer_kind']) for i in items))
# check sibling answer == gold count
print('sib==gold',sum(str(i['sibling_answer'])==str(i['answer']) for i in items))
# glyphs used in refuniverse questions containing $ or *
print('q with $ or *', sum(('$' in i['question'] or '*' in i['question']) for i in items))
