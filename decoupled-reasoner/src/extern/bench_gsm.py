"""GSM8K, which is generated rather than ranked, and scored two ways.

The multiple choice benchmarks are decided by comparing log likelihoods, so a
model never has to produce a format. GSM8K is not like that: the model has to
write a chain of reasoning and land on a number, so the answer has to be
parsed out, and how it is parsed changes the number.

Both conventions are reported and never pooled:

    strict     the answer is what follows the "#### " marker the few shot
               examples demonstrate, which is what lm-eval's strict-match
               scores
    flexible   the last number anywhere in the generation, which is what
               lm-eval's flexible-extract scores and which forgives a model
               that reasoned correctly and formatted badly

`unparseable` counts generations with no number at all, and is reported apart
from wrong answers, because a model that never produced a number has failed
differently from one that produced the wrong one.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time

import pyarrow.parquet as pq
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

NUM = re.compile(r"-?\$?\d[\d,]*\.?\d*")
HASH = re.compile(r"####\s*(-?\$?[\d,]*\.?\d+)")


def clean_num(s):
    s = s.replace(",", "").replace("$", "").rstrip(".")
    try:
        return float(s)
    except ValueError:
        return None


def gold_of(answer):
    m = HASH.search(answer)
    return clean_num(m.group(1)) if m else None


def extract(text):
    """(strict, flexible) numbers parsed out of one generation."""
    body = text.split("Question:")[0]
    m = HASH.search(body)
    strict = clean_num(m.group(1)) if m else None
    nums = NUM.findall(body)
    flexible = clean_num(nums[-1]) if nums else None
    return strict, flexible


def load(root, n, seed, split):
    t = pq.read_table(f"{root}/gsm8k/main/{split}-00000-of-00001.parquet")
    rows = t.to_pylist()
    import random
    rng = random.Random(seed)
    rng.shuffle(rows)
    return rows[:n] if n else rows


def build_prompt(shots, q, fmt, tok):
    head = ""
    for s in shots:
        head += f"Question: {s['question']}\nAnswer: {s['answer']}\n\n"
    body = f"Question: {q}\nAnswer:"
    if fmt == "chat":
        return tok.apply_chat_template(
            [{"role": "user",
              "content": (head + f"Question: {q}\n\nSolve it. End with the "
                          "final numeric answer after '#### '.")}],
            tokenize=False, add_generation_prompt=True)
    return head + body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--fmt", default="completion", choices=("completion", "chat"))
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--shots", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--max-new", type=int, default=320)
    ap.add_argument("--batch", type=int, default=8)
    a = ap.parse_args()

    test = load(a.root, a.n, a.seed, "test")
    shots = load(a.root, a.shots, 7, "train")[:a.shots]

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=getattr(torch, a.dtype)).to(a.device).eval()

    prompts = [build_prompt(shots, r["question"], a.fmt, tok) for r in test]
    recs = []
    t0 = time.time()
    for i in range(0, len(prompts), a.batch):
        chunk = prompts[i:i + a.batch]
        enc = tok(chunk, return_tensors="pt", padding=True,
                  add_special_tokens=False).to(a.device)
        with torch.no_grad():
            g = model.generate(**enc, max_new_tokens=a.max_new,
                               do_sample=False, temperature=None,
                               top_p=None, top_k=None,
                               pad_token_id=tok.pad_token_id)
        new = g[:, enc["input_ids"].shape[1]:]
        for j in range(len(chunk)):
            raw = tok.decode(new[j], skip_special_tokens=True)
            s, f = extract(raw)
            r = test[i + j]
            recs.append({"id": f"gsm/{i+j}", "gold": gold_of(r["answer"]),
                         "strict": s, "flexible": f, "raw": raw[:1500]})
        el = time.time() - t0
        print(f"{len(recs)}/{len(prompts)} {el:.0f}s "
              f"eta {el/len(recs)*(len(prompts)-len(recs)):.0f}s", flush=True)

    n = len(recs)
    ok_s = sum(1 for r in recs if r["gold"] is not None
               and r["strict"] == r["gold"])
    ok_f = sum(1 for r in recs if r["gold"] is not None
               and r["flexible"] == r["gold"])
    res = {"model": a.model, "task": "gsm8k", "fmt": a.fmt, "n": n,
           "shots": a.shots, "seed": a.seed, "max_new_tokens": a.max_new,
           "strict_match": round(ok_s / n, 4),
           "flexible_extract": round(ok_f / n, 4),
           "unparseable": round(sum(1 for r in recs
                                    if r["flexible"] is None) / n, 4),
           "floor": 0.0, "seconds": round(time.time() - t0, 1),
           "records": recs}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "records"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
