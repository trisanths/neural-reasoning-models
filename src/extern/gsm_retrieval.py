"""GSM8K with method retrieval: pages that carry procedure, not answers.

Retrieving on the problem text finds the problem, and a page with the answer
on it turns a reasoning benchmark into a lookup. So the query is built from
the problem's method rather than its wording: the quantities and names are
stripped out and what is left is the operation being asked for, which is what
a worked example would be indexed under.

Three conditions, reported separately and never pooled:

    closed      the standard 8 shot chain of thought prompt
    method      the same, with retrieved procedure pages prepended
    problem     the same, retrieving on the raw problem text, which is the
                contaminated control that shows what lookup would buy

Every retrieved set is labelled for whether it contains the gold numeric
answer, so a correct answer sitting next to its own number is never counted
as reasoning. Subset sizes are printed beside every subset accuracy.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.extern.bench_gsm import build_prompt, extract, gold_of, load
from src.extern.retrieval_ours import CachedExa

NUM = re.compile(r"\d[\d,]*\.?\d*")
NAME = re.compile(r"\b[A-Z][a-z]+\b")


def method_query(question):
    """The problem with its numbers and proper names removed.

    What survives is the shape of the task, which is what a worked example is
    written about. The gold number cannot be in this query, so a page found by
    it was not found by carrying the answer.
    """
    q = NUM.sub("", question)
    q = NAME.sub("", q)
    q = " ".join(q.split())
    return ("worked example step by step method: " + q[:220]).strip()


def contains_answer(text, gold):
    if gold is None:
        return False
    g = f"{gold:g}"
    return g in (text or "").replace(",", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--shots", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default="results/extern/exa_cache")
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--conditions", default="closed,method")
    ap.add_argument("--num-results", type=int, default=4)
    ap.add_argument("--max-context-chars", type=int, default=4000)
    ap.add_argument("--max-new", type=int, default=320)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--bos", action="store_true")
    ap.add_argument("--retriever", default="exa", choices=("exa", "mock"))
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dtype", default="float32")
    a = ap.parse_args()

    if a.retriever == "mock":
        from src.retrieval_web.exa import MockExa
        base = MockExa()
    else:
        from src.retrieval_web.exa import ExaClient
        base = ExaClient()
    cdir = a.cache if a.retriever == "exa" else os.path.join(a.cache,
                                                             a.retriever)
    client = CachedExa(base, cdir, a.budget)

    test = load(a.root, a.n, a.seed, "test")
    shots = load(a.root, a.shots, 7, "train")[:a.shots]
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=getattr(torch, a.dtype)).to(a.device).eval()

    conds = [c for c in a.conditions.split(",") if c]
    out = {}
    t0 = time.time()
    for cond in conds:
        recs = []
        for i, r in enumerate(test):
            gold = gold_of(r["answer"])
            block = ""
            if cond != "closed":
                q = (method_query(r["question"]) if cond == "method"
                     else " ".join(r["question"].split())[:250])
                try:
                    pages = client.search(q, num_results=a.num_results,
                                          text=True)
                except RuntimeError:
                    pages = []
                parts, used = [], 0
                for p in pages:
                    t = " ".join((p.get("text") or "").split())
                    if not t:
                        continue
                    room = a.max_context_chars - used
                    if room <= 0:
                        break
                    parts.append(t[:room])
                    used += min(len(t), room)
                block = "\n\n".join(parts)
            prompt = build_prompt(shots, r["question"], "completion", tok)
            if block:
                prompt = ("Reference material:\n" + block + "\n\n") + prompt
            ids = tok(prompt, add_special_tokens=False)["input_ids"]
            if a.bos and tok.bos_token_id is not None:
                ids = [tok.bos_token_id] + ids
            with torch.no_grad():
                g = model.generate(
                    input_ids=torch.tensor([ids]).to(a.device),
                    max_new_tokens=a.max_new, do_sample=False,
                    temperature=None, top_p=None, top_k=None,
                    pad_token_id=tok.pad_token_id)
            raw = tok.decode(g[0, len(ids):], skip_special_tokens=True)
            s, f = extract(raw)
            recs.append({"id": f"gsm/{i}", "gold": gold, "strict": s,
                         "flexible": f, "answer_on_page":
                         bool(block) and contains_answer(block, gold),
                         "context_chars": len(block), "raw": raw[:800]})
            if (i + 1) % 10 == 0:
                el = time.time() - t0
                print(f"{cond} {i+1}/{len(test)} {el:.0f}s "
                      f"live={client.live}", flush=True)
        n = len(recs)

        def sub(rows):
            if not rows:
                return None
            return {"n": len(rows),
                    "strict": round(sum(1 for r in rows if r["gold"] is not None
                                        and r["strict"] == r["gold"])
                                    / len(rows), 4),
                    "flexible": round(sum(1 for r in rows
                                          if r["gold"] is not None
                                          and r["flexible"] == r["gold"])
                                      / len(rows), 4)}
        out[cond] = {
            "all": sub(recs),
            "answer_on_page": sub([r for r in recs if r["answer_on_page"]]),
            "answer_not_on_page": sub([r for r in recs
                                       if not r["answer_on_page"]]),
            "mean_context_chars": round(sum(r["context_chars"]
                                            for r in recs) / n, 1),
            "records": recs}
    res = {"model": a.model, "task": "gsm8k", "shots": a.shots, "seed": a.seed,
           "n": len(test), "live_searches": client.live,
           "cache_hits": client.hits, "conditions": conds,
           "seconds": round(time.time() - t0, 1), "results": out}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: (v if k != "results" else
                          {c: {kk: vv for kk, vv in d.items()
                               if kk != "records"} for c, d in v.items()})
                      for k, v in res.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
