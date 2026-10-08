"""Run one external model over the acquisition items and write its generations.

Every model is prompted through its own chat template with
`tokenizer.apply_chat_template`, so a model card's header is applied by the
card's own jinja rather than by anything written here. The rendered string of
the first item is stored in the meta file so the header that was actually used
is on record.

Decoding follows the checkpoint's own `generation_config` unless a flag
overrides it, and the settings that were in force are written to the meta file.

Nothing here scores anything. Grading is `src/extern/score.py`, which calls
`src/norm/cmpwork/grade.py` so the external models are graded by the same
function as the project's own systems.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.extern import prompts


def load_items(path, conds, families, pages, limit, stride):
    rows = [json.loads(l) for l in gzip.open(path, "rt")]
    if conds:
        rows = [r for r in rows if r["cond"] in conds]
    if families:
        rows = [r for r in rows if r["family"] in families]
    if pages:
        rows = [r for r in rows if r["n_pages"] in pages]
    rows.sort(key=lambda r: r["id"])
    if stride > 1:
        rows = rows[::stride]
    if limit:
        rows = rows[:limit]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--variant", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--items", default="results/norm/oneshot/items.jsonl.gz")
    ap.add_argument("--conds", default="acq")
    ap.add_argument("--families", default="")
    ap.add_argument("--pages", default="1")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--max-new", type=int, default=512)
    ap.add_argument("--greedy", action="store_true")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--top-k", type=int, default=0)
    ap.add_argument("--top-p", type=float, default=0.0)
    ap.add_argument("--rep-penalty", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--load-4bit", action="store_true")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--max-batch-tokens", type=int, default=0)
    a = ap.parse_args()

    conds = [c for c in a.conds.split(",") if c]
    fams = [f for f in a.families.split(",") if f]
    pages = [int(p) for p in a.pages.split(",") if p]
    items = load_items(a.items, conds, fams, pages, a.limit, a.stride)
    print(f"items {len(items)}", flush=True)

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    kw = {"dtype": getattr(torch, a.dtype)}
    quant = None
    if a.load_4bit:
        from transformers import BitsAndBytesConfig
        kw = {"quantization_config": BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True)}
        quant = "bnb-nf4-double"
    model = AutoModelForCausalLM.from_pretrained(a.model, **kw)
    if not a.load_4bit:
        model = model.to(a.device)
    model.eval()

    n_params = sum(p.numel() for p in model.parameters())
    emb = model.get_input_embeddings().weight.numel()
    tied = bool(getattr(model.config, "tie_word_embeddings", False))
    gc = model.generation_config
    gkw = {"max_new_tokens": a.max_new, "pad_token_id": tok.pad_token_id}
    if a.greedy:
        gkw.update(do_sample=False, temperature=None, top_p=None, top_k=None)
    else:
        # The model card's own recommended sampling settings, passed in by the
        # driver, so the decode is the one the publisher asks for.
        gkw.update(do_sample=True, temperature=a.temperature)
        if a.top_k:
            gkw["top_k"] = a.top_k
        if a.top_p:
            gkw["top_p"] = a.top_p
        if a.rep_penalty:
            gkw["repetition_penalty"] = a.rep_penalty
        torch.manual_seed(a.seed)
    print("gen_config", gc.to_diff_dict(), flush=True)

    pre = prompts.prefill(a.variant)
    rendered = [tok.apply_chat_template(prompts.build(a.variant, it),
                                        tokenize=False,
                                        add_generation_prompt=True) + pre
                for it in items]
    order = sorted(range(len(items)), key=lambda i: -len(rendered[i]))
    out = [None] * len(items)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    t0 = time.time()
    done = 0
    b = 0
    while b < len(order):
        idx = order[b:b + a.batch]
        if a.max_batch_tokens:
            # A long-prompt batch is trimmed so peak memory stays flat across
            # the run rather than spiking on the longest items.
            while len(idx) > 1 and \
                    len(idx) * len(rendered[idx[0]]) // 4 > a.max_batch_tokens:
                idx = idx[:len(idx) // 2]
        b += len(idx)
        enc = tok([rendered[i] for i in idx], return_tensors="pt",
                  padding=True, add_special_tokens=False).to(a.device)
        with torch.no_grad():
            gen = model.generate(**enc, **gkw)
        new = gen[:, enc["input_ids"].shape[1]:]
        for k, i in enumerate(idx):
            out[i] = {"raw": tok.decode(new[k], skip_special_tokens=True),
                      "n_new": int((new[k] != tok.pad_token_id).sum()),
                      "n_prompt": int(enc["attention_mask"][k].sum())}
        done += len(idx)
        if done % (a.batch * 4) < a.batch:
            el = time.time() - t0
            print(f"{done}/{len(items)} {el:.0f}s "
                  f"eta {el / done * (len(items) - done):.0f}s", flush=True)

    with gzip.open(a.out, "wt") as fh:
        for it, o in zip(items, out):
            fh.write(json.dumps({
                "id": it["id"], "cond": it["cond"], "family": it["family"],
                "split": it["split"], "fid": it["fid"], "gold": it["gold"],
                "options": it["options"], "floor": it["floor"],
                "n_pages": it["n_pages"], "item_key": it["item_key"],
                "raw": o["raw"], "n_new": o["n_new"],
                "n_prompt": o["n_prompt"]}) + "\n")
    meta = {
        "model": a.model, "variant": a.variant,
        "options_shown": prompts.options_shown(a.variant),
        "params_total": n_params, "params_embedding": emb,
        "params_non_embedding": n_params - emb * (1 if tied else 2),
        "tie_word_embeddings": tied,
        "architectures": model.config.architectures,
        "model_type": model.config.model_type,
        "quantization": quant, "dtype": a.dtype,
        "n_items": len(items), "conds": conds, "families": fams,
        "pages": pages, "stride": a.stride, "limit": a.limit,
        "batch": a.batch, "max_new_tokens": a.max_new,
        "greedy": a.greedy, "device": a.device, "gen_kwargs": {k: v for k, v in gkw.items()
                                          if k != "pad_token_id"},
        "seed": a.seed,
        "generation_config": gc.to_diff_dict(),
        "chat_template_sha": hash(tok.chat_template or "") & 0xffffffff,
        "rendered_example": rendered[0], "prefill": pre,
        "max_prompt_tokens": max(o["n_prompt"] for o in out),
        "mean_new_tokens": round(sum(o["n_new"] for o in out) / len(out), 1),
        "seconds": round(time.time() - t0, 1),
        "out": os.path.abspath(a.out),
    }
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps({k: v for k, v in meta.items()
                      if k != "rendered_example"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
