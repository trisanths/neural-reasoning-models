"""vLLM prompt logprobs against a plain transformers forward pass, on PopQA FC.

usage: ll_check2.py MODEL_NAME N_ITEMS POPQA_FILE
Prints one JSON line: pick agreement under the pilot's scoring rule, both
accuracies, and the per-option summed-NLL differences.
"""
import json
import os
import sys

sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")

from src.pilot.popqa import pairs_of, score_item  # noqa: E402
from src.pilot.vllm_model import MODELS, VLLMModel  # noqa: E402

name, n, path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
items = [json.loads(line) for line in open(path)][:n]
pairs = [p for it in items for p in pairs_of(it)]
m = VLLMModel(MODELS[name], max_model_len=24576, gpu_memory_utilization=0.45)
a = m.loglik(pairs)

import torch  # noqa: E402
from transformers import AutoModelForCausalLM  # noqa: E402

hf = AutoModelForCausalLM.from_pretrained(MODELS[name].hf_id,
                                          dtype=torch.bfloat16).cuda().eval()
c = []
with torch.no_grad():
    for ctx, cont in pairs:
        ci = m.tok(ctx).input_ids
        oi = m.tok(cont, add_special_tokens=False).input_ids
        x = torch.tensor([ci + oi]).cuda()
        lp = torch.log_softmax(hf(x).logits[0, :-1].float(), -1)
        t = x[0, 1:]
        s = -lp[len(ci) - 1:].gather(1, t[len(ci) - 1:].unsqueeze(1)).sum().item()
        c.append((s, len(oi)))

agree = acc_v = acc_h = 0
diffs = []
for k, it in enumerate(items):
    sa = score_item(it, a[4 * k:4 * k + 4])
    sc = score_item(it, c[4 * k:4 * k + 4])
    agree += sa["pick"] == sc["pick"]
    acc_v += sa["correct"]
    acc_h += sc["correct"]
    diffs += [abs(x[0] - y[0]) for x, y in zip(a[4 * k:4 * k + 4], c[4 * k:4 * k + 4])]
diffs.sort()
print(json.dumps({"model": name, "items": n, "options": len(diffs),
                  "pick_agreement": agree / n, "acc_vllm": acc_v / n,
                  "acc_hf": acc_h / n, "max_abs_nll_diff": round(diffs[-1], 3),
                  "median_abs_nll_diff": round(diffs[len(diffs) // 2], 4),
                  "p95_abs_nll_diff": round(diffs[int(0.95 * len(diffs))], 3)}),
      flush=True)
sys.stdout.flush()
os._exit(0)
