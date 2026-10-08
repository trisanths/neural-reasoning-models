import json,sys,os
sys.path.insert(0,'/home/ec2-user/decoupled-reasoner')
from transformers import AutoTokenizer
from src.pilot.vllm_model import MODELS, VLLMModel, THINK_BUDGET, ANSWER_BUDGET_INSTRUCT
items=[json.loads(l) for l in open('/mnt/nvme/pilot/items/items.jsonl')]
prompts=[i['prompts'][c] for i in items for c in i['prompts']]
for name in ['lfm2.5-350m-base','lfm2.5-350m','qwen3-0.6b-base','qwen3-0.6b']:
    spec=MODELS[name]
    m=VLLMModel.__new__(VLLMModel); m.spec=spec; m.tok=AutoTokenizer.from_pretrained(spec.hf_id); m.thinking=False
    print('=====',name,'bos',m.tok.bos_token, 'has enable_thinking', 'enable_thinking' in (m.tok.chat_template or ''))
    for th in ([False,True] if True in spec.thinking_modes else [False]):
        m.thinking=th
        ids=m.encode(prompts[0])
        print(' think',th,'head',repr(m.tok.decode(ids[:4])),'tail',repr(m.tok.decode(ids[-12:])))
    m.thinking=False
    L=[len(m.encode(p)) for p in prompts]
    lim=24576-THINK_BUDGET-ANSWER_BUDGET_INSTRUCT
    print(' max tokens',max(L),'n over limit',sum(x>lim for x in L))
    if name=='qwen3-0.6b':
        print(' </think> id', m.tok.convert_tokens_to_ids('</think>'), 'special?', '</think>' in m.tok.all_special_tokens)
        print(' close ids', m.tok("\n</think>\n\n", add_special_tokens=False).input_ids)
