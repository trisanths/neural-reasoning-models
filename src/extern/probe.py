"""Download one checkpoint, count its parameters, print its chat template."""
import argparse, json, os, sys
import torch
from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--load", action="store_true")
a = ap.parse_args()

cfg = AutoConfig.from_pretrained(a.model, trust_remote_code=True)
print("ARCH", getattr(cfg, "architectures", None), "model_type", cfg.model_type)
print("CFG", json.dumps({k: v for k, v in cfg.to_dict().items()
                         if isinstance(v, (int, float, str, bool))}, indent=1)[:2000])

tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=True)
print("VOCAB", len(tok), "pad", tok.pad_token, tok.pad_token_id,
      "eos", tok.eos_token, tok.eos_token_id, "padding_side", tok.padding_side)
tmpl = tok.chat_template
print("HAS_CHAT_TEMPLATE", bool(tmpl))
print("----TEMPLATE----")
print(tmpl)
print("----RENDER plain----")
msgs = [{"role": "user", "content": "What is the capital of France?"}]
print(repr(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)))
try:
    print("----RENDER with system----")
    m2 = [{"role": "system", "content": "You are helpful."}] + msgs
    print(repr(tok.apply_chat_template(m2, tokenize=False, add_generation_prompt=True)))
except Exception as e:
    print("system role failed:", e)

if a.load:
    m = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16,
                                             trust_remote_code=True)
    tot = sum(p.numel() for p in m.parameters())
    emb = m.get_input_embeddings().weight.numel()
    tied = getattr(m.config, "tie_word_embeddings", None)
    print("PARAMS_TOTAL", tot)
    print("PARAMS_TOTAL_M", round(tot / 1e6, 2))
    print("EMBED_PARAMS", emb, "tie_word_embeddings", tied)
    print("PARAMS_NON_EMBED_M", round((tot - emb * (1 if tied else 2)) / 1e6, 2))
    print("DTYPE", next(m.parameters()).dtype)
