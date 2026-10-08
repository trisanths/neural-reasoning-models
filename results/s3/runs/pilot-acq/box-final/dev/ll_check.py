import json, sys, os
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")
from src.pilot.vllm_model import MODELS, VLLMModel
from src.pilot.popqa import pairs_of
items=[json.loads(l) for l in open("/mnt/nvme/pilot/items/popqa_fc.jsonl")][:6]
pairs=[p for it in items for p in pairs_of(it)]
m=VLLMModel(MODELS["lfm2.5-350m-base"], max_model_len=4096, gpu_memory_utilization=0.5)
a=m.loglik(pairs); b=m.loglik(pairs)
import torch
from transformers import AutoModelForCausalLM
hf=AutoModelForCausalLM.from_pretrained("LiquidAI/LFM2.5-350M-Base", dtype=torch.bfloat16).cuda().eval()
c=[]
for ctx,cont in pairs:
    ci=m.tok(ctx).input_ids; oi=m.tok(cont, add_special_tokens=False).input_ids
    x=torch.tensor([ci+oi]).cuda()
    with torch.no_grad(): lp=torch.log_softmax(hf(x).logits[0,:-1].float(),-1)
    t=x[0,1:]; s=-lp[len(ci)-1:, :].gather(1, t[len(ci)-1:].unsqueeze(1)).sum().item()
    c.append((s,len(oi)))
for x,y,z in zip(a,b,c): print(round(x[0],3), round(y[0],3), round(z[0],3), x[1], z[1])
sys.stdout.flush(); os._exit(0)
