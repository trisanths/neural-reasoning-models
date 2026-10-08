"""The chat template and the bos token, verified before anything is scored.

Three things are checked and written to `results/role/lfm2/control.json`:
the rendered prompt string and its first token ids, so it is on record that
`<|startoftext|>` is present; free answers to control questions the model
should get right, so a template that renders but does not work would be
visible; and the same questions with the bos token stripped, which is the
fault that voided earlier numbers on this project.
"""
from __future__ import annotations

import hashlib
import json
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "LiquidAI/LFM2-350M"
Q = ["What is the capital of France?",
     "What is 12 plus 30?",
     "Name the largest planet in our solar system.",
     "Who wrote the play Hamlet?",
     "What colour is the sky on a clear day?"]

tok = AutoTokenizer.from_pretrained(MODEL)
tok.padding_side = "left"
if tok.pad_token_id is None:
    tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(
    MODEL, dtype=torch.bfloat16).to("cuda").eval()

rendered = [tok.apply_chat_template([{"role": "user", "content": q}],
                                    tokenize=False, add_generation_prompt=True)
            for q in Q]
ids0 = tok(rendered[0], add_special_tokens=False)["input_ids"]
bos = tok.bos_token_id
out = {"model": MODEL,
       "params_total": sum(p.numel() for p in model.parameters()),
       "bos_token": tok.bos_token, "bos_token_id": bos,
       "eos_token": tok.eos_token, "eos_token_id": tok.eos_token_id,
       "pad_token": tok.pad_token,
       "chat_template_sha256": hashlib.sha256(
           (tok.chat_template or "").encode()).hexdigest(),
       "rendered_example": rendered[0],
       "first_ids_with_template": ids0[:8],
       "first_ids_decoded": [tok.decode([i]) for i in ids0[:8]],
       "bos_present_from_template": bool(ids0[0] == bos),
       "add_special_tokens_true_would_give": tok(
           rendered[0], add_special_tokens=True)["input_ids"][:4],
       "generation_config": model.generation_config.to_diff_dict()}


def answers(prompts):
    enc = tok(prompts, return_tensors="pt", padding=True,
              add_special_tokens=False).to("cuda")
    with torch.no_grad():
        g = model.generate(**enc, max_new_tokens=128, do_sample=False,
                           temperature=None, top_p=None, top_k=None,
                           pad_token_id=tok.pad_token_id)
    new = g[:, enc["input_ids"].shape[1]:]
    return [tok.decode(x, skip_special_tokens=True).strip() for x in new]


out["control_answers"] = dict(zip(Q, answers(rendered)))
stripped = [r[len(tok.bos_token):] if r.startswith(tok.bos_token) else r
            for r in rendered]
out["bos_stripped_first_ids"] = tok(
    stripped[0], add_special_tokens=False)["input_ids"][:8]
out["control_answers_no_bos"] = dict(zip(Q, answers(stripped)))

os.makedirs("results/role/lfm2", exist_ok=True)
with open("results/role/lfm2/control.json", "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps({k: v for k, v in out.items()
                  if k != "chat_template_sha256"}, indent=1)[:4000])
