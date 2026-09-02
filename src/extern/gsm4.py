"""GSM8K with method retrieval, four conditions, one query builder.

The design is `src/extern/gsm_retrieval.py`: retrieve method rather than
answers, with the query stripped of numbers and proper names so the gold
number cannot appear in it, and the raw problem text kept beside it as the
contaminated control. This module runs that design over both models so the
retrieved material is identical between them by construction: the query is
built by the same function from the same item list in the same order, and the
page cache is keyed on the query, so the second model reads the bytes the
first one read. Every context block is hashed and the hash is stored per item,
so "the same material" is checkable after the fact rather than asserted.

Both readers are scored:

    LFM2-350M          8 shot chain of thought completion, the format its
                       published 30.1 is quoted from
    ours corpus-v1-8k  its own trace layout, `<|world|> preamble [<|doc|>
                       page] <|q|> problem`, built by `src/rl/env.py`

Those two prompts are not the same prompt, and the rows are never pooled or
subtracted. Neither format is available to both models: this checkpoint has
no chain of thought convention and no 8 shot format in its training traces,
and LFM2 has no `<|doc|>` channel. The `shots` prompt style runs the 8 shot
text through our reader as well, so the objection that it was never shown the
format is answered rather than argued.

Scoring keeps lm-eval's two conventions apart, strict on the `#### ` marker
and flexible on the last number anywhere, and counts generations carrying no
number at all separately. A model that never produced a number failed
differently from one that produced a wrong number, and reporting "solves 12
percent perfectly" as "scores 12 percent on GSM8K" would be a different
claim from the one the published table makes.

Contamination is labelled three ways per item on the pages actually placed in
the context, not on a separate search: verbatim problem, gold answer, or
neither. Correct with the answer on the page is a lookup. Correct with
neither is the reasoning result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time

from src.extern.bench_gsm import build_prompt, extract, gold_of, load
from src.extern.gsm_retrieval import method_query
from src.extern.retrieval_ours import CachedExa

WORD = re.compile(r"[a-z0-9]+")


def norm(s):
    return " ".join(WORD.findall(str(s).lower()))


def label_contamination(block, question, gold):
    """verbatim / answer / neither, on the text actually put in the context.

    The verbatim test is the first twelve normalised words of the problem,
    which is the same key `src/extern/retrieval_mmlu.py` uses on MMLU stems,
    so the two tasks report the same label under the same rule. The answer
    test is the gold number as a bare token, with thousands separators
    removed on both sides.
    """
    if not block:
        return "none"
    hay = norm(block)
    stem_key = " ".join(norm(question).split()[:12])
    if stem_key and stem_key in hay:
        return "verbatim"
    if gold is not None:
        g = f"{gold:g}"
        flat = (block or "").replace(",", "")
        if re.search(r"(?<![\d.])" + re.escape(g) + r"(?![\d.])", flat):
            return "answer"
    return "neither"


def fetch_block(client, cond, row, num_results, max_chars):
    """The retrieved context for one item, and the query that produced it."""
    if cond == "closed":
        return "", "", []
    q = (method_query(row["question"]) if cond == "method"
         else " ".join(row["question"].split())[:250])
    try:
        pages = client.search(q, num_results=num_results, text=True)
    except RuntimeError as e:
        if "budget" in str(e):
            raise
        return "", q, [{"error": str(e)[:200]}]
    parts, used, meta = [], 0, []
    for p in pages:
        t = " ".join((p.get("text") or "").split())
        if not t:
            continue
        room = max_chars - used
        if room <= 0:
            break
        parts.append(t[:room])
        used += min(len(t), room)
        meta.append({"url": p.get("url", ""), "chars": min(len(t), room)})
    return "\n\n".join(parts), q, meta


# --------------------------------------------------------------- readers

class HFReader:
    """LFM2 style causal LM, 8 shot completion, greedy or sampled."""

    name = "hf"

    def __init__(self, a):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(a.model)
        self.tok.padding_side = "left"
        if self.tok.pad_token_id is None:
            self.tok.pad_token = self.tok.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            a.model, dtype=getattr(torch, a.dtype)).to(a.device).eval()
        self.a = a
        self.shots = load(a.root, a.shots, 7, "train")[:a.shots]

    def run(self, question, block, decode):
        prompt = build_prompt(self.shots, question, "completion", self.tok)
        if block:
            prompt = "Reference material:\n" + block + "\n\n" + prompt
        ids = self.tok(prompt, add_special_tokens=False)["input_ids"]
        if self.a.bos and self.tok.bos_token_id is not None:
            ids = [self.tok.bos_token_id] + ids
        kw = dict(max_new_tokens=self.a.max_new,
                  pad_token_id=self.tok.pad_token_id)
        if decode["kind"] == "greedy":
            kw.update(do_sample=False, temperature=None, top_p=None,
                      top_k=None)
        else:
            kw.update(do_sample=True, temperature=decode["temperature"],
                      top_p=decode["top_p"], top_k=0)
            self.torch.manual_seed(decode["seed"])
        with self.torch.no_grad():
            g = self.model.generate(
                input_ids=self.torch.tensor([ids]).to(self.a.device), **kw)
        raw = self.tok.decode(g[0, len(ids):], skip_special_tokens=True)
        return {"raw": raw, "prompt_tokens": len(ids), "emitted_a": 1}


class OursReader:
    """This project's checkpoint in its own trace layout.

    Retrieved pages go in through the `<|doc|>` channel the training traces
    use, which is the only in-context document channel this model has ever
    seen. Decoding runs the same interactive loop the RL rollouts use, with
    no serving surface attached, so an emitted `<|retrieve|>` ends the
    trajectory and is recorded rather than served.
    """

    name = "ours"

    def __init__(self, a):
        import numpy as np
        from src.evals.interactive import make_checkpoint_step_fn
        from src.train.tokenizer import load_tokenizer
        self.np = np
        self.tok = load_tokenizer(a.tokenizer)
        self.step_fn, self.model, self.state = make_checkpoint_step_fn(
            a.ckpt, a.device)
        self.a = a
        self.shots = load(a.root, a.shots, 7, "train")[:a.shots]

    def _prompt(self, question, block):
        from src.rl.env import build_prompt as rl_build_prompt
        text = question
        if self.a.ours_prompt == "shots":
            head = ""
            for s in self.shots:
                head += f"Question: {s['question']}\nAnswer: {s['answer']}\n\n"
            text = head + f"Question: {question}\nAnswer:"
        ep = {"world": {"domain": "corporate"},
              "documents": ([{"text": block}] if block else []),
              "n_context": 1 if block else 0}
        ids = rl_build_prompt(ep, {"text": text}, self.tok)
        sid = self.tok.special_ids
        assert ids[0] == sid["<|world|>"], "world header missing"
        assert sid["<|q|>"] in ids
        if block:
            assert sid["<|doc|>"] in ids, "document channel missing"
        return ids

    def run(self, question, block, decode):
        from src.evals.interactive import generate_with_retrieval
        from src.extern.cell2 import sampling_step
        sid = self.tok.special_ids
        ids = self._prompt(question, block)
        fn = self.step_fn
        if decode["kind"] == "sampled":
            fn = sampling_step(self.step_fn, decode["temperature"],
                               decode["top_p"],
                               decode["seed"] + (len(ids) % 997))
        o = generate_with_retrieval(
            fn, self.tok, [], ids, max_rounds=self.a.max_rounds,
            max_new_tokens=self.a.max_new, seed=decode.get("seed", 0),
            index=None)
        # The whole generation is what gets parsed. Scoring only the span
        # after <|a|> would silently drop every trajectory that never opened
        # an answer span, which is the failure mode most worth counting here.
        full = self.tok.decode(o["generated"])
        return {"raw": full,
                "answer_span": o.get("answer_text", ""),
                "prompt_tokens": len(ids),
                "emitted_a": int(o.get("answer_start") is not None),
                "emitted_retrieve": int(
                    sid["<|retrieve|>"] in o["generated"]
                    or o.get("stop_reason") == "max_rounds"),
                "stop_reason": o.get("stop_reason", ""),
                "n_generated": o.get("n_generated", 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reader", required=True, choices=("hf", "ours"))
    ap.add_argument("--model", default="LiquidAI/LFM2-350M")
    ap.add_argument("--ckpt", default="/home/ec2-user/retrain/corpus-v1-8k.pt")
    ap.add_argument("--tag", default="corpus-v1-8k")
    ap.add_argument("--tokenizer",
                    default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--ours-prompt", default="native",
                    choices=("native", "shots"))
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--shots", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default="results/extern/exa_cache")
    ap.add_argument("--budget", type=int, default=500)
    ap.add_argument("--conditions", default="closed,method,problem")
    ap.add_argument("--decodes", default="greedy,sampled")
    ap.add_argument("--num-results", type=int, default=4)
    ap.add_argument("--max-context-chars", type=int, default=4000)
    ap.add_argument("--max-new", type=int, default=320)
    ap.add_argument("--max-rounds", type=int, default=3)
    ap.add_argument("--bos", action="store_true")
    ap.add_argument("--retriever", default="exa", choices=("exa", "mock"))
    ap.add_argument("--device", default="cuda")
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
    reader = HFReader(a) if a.reader == "hf" else OursReader(a)

    DECODES = {"greedy": {"kind": "greedy", "name": "greedy"},
               "sampled": {"kind": "sampled", "name": "T=0.8,p=0.95",
                           "temperature": 0.8, "top_p": 0.95, "seed": 4242}}
    conds = [c for c in a.conditions.split(",") if c]
    decodes = [DECODES[d] for d in a.decodes.split(",") if d]

    # The retrieved material is fetched once per condition and reused across
    # decodes, so a greedy row and a sampled row read identical pages.
    blocks = {}
    t0 = time.time()
    for cond in conds:
        blocks[cond] = []
        for i, r in enumerate(test):
            block, q, meta = fetch_block(client, cond, r, a.num_results,
                                         a.max_context_chars)
            blocks[cond].append({"block": block, "query": q, "pages": meta})
            if (i + 1) % 25 == 0:
                print(f"fetch {cond} {i+1}/{len(test)} live={client.live} "
                      f"cached={client.hits} {time.time()-t0:.0f}s",
                      flush=True)
    print(f"fetch done live={client.live} cached={client.hits}", flush=True)

    out = {}
    for cond in conds:
        for dec in decodes:
            key = f"{cond}/{dec['name']}"
            recs = []
            for i, r in enumerate(test):
                gold = gold_of(r["answer"])
                b = blocks[cond][i]
                block = b["block"]
                g = reader.run(r["question"], block, dec)
                raw = g["raw"]
                s, f = extract(raw)
                span = g.get("answer_span", "")
                ss, sf = extract(span) if span else (None, None)
                recs.append({
                    "id": f"gsm/{i}", "gold": gold,
                    "strict": s, "flexible": f,
                    "strict_correct": int(gold is not None and s == gold),
                    "flexible_correct": int(gold is not None and f == gold),
                    "unparseable": int(f is None),
                    "answer_span": span[:600],
                    "span_strict_correct": int(gold is not None
                                               and ss == gold),
                    "span_flexible_correct": int(gold is not None
                                                 and sf == gold),
                    "contamination": label_contamination(block, r["question"],
                                                         gold),
                    "context_chars": len(block),
                    "context_sha256": (hashlib.sha256(block.encode()).hexdigest()
                                       if block else ""),
                    "query": b["query"], "n_pages": len(b["pages"]),
                    "prompt_tokens": g.get("prompt_tokens", 0),
                    "emitted_a": g.get("emitted_a", 0),
                    "emitted_retrieve": g.get("emitted_retrieve", 0),
                    "stop_reason": g.get("stop_reason", ""),
                    "n_generated": g.get("n_generated", 0),
                    "raw": raw[:1200]})
                if (i + 1) % 20 == 0:
                    el = time.time() - t0
                    ok = sum(x["flexible_correct"] for x in recs)
                    print(f"{key} {i+1}/{len(test)} {el:.0f}s flex={ok}",
                          flush=True)
            out[key] = {"condition": cond, "decode": dec, "records": recs}
            n = len(recs)
            print(f"== {key} n={n} "
                  f"strict={sum(x['strict_correct'] for x in recs)/n:.4f} "
                  f"flex={sum(x['flexible_correct'] for x in recs)/n:.4f} "
                  f"unparseable={sum(x['unparseable'] for x in recs)/n:.4f}",
                  flush=True)

    res = {"reader": a.reader,
           "model": a.model if a.reader == "hf" else f"ours:{a.tag}",
           "ours_prompt": a.ours_prompt if a.reader == "ours" else None,
           "task": "gsm8k", "n": len(test), "shots": a.shots, "seed": a.seed,
           "device": a.device, "dtype": a.dtype, "bos": a.bos,
           "num_results": a.num_results,
           "max_context_chars": a.max_context_chars, "max_new": a.max_new,
           "retriever": a.retriever, "live_searches": client.live,
           "cache_hits": client.hits, "budget": a.budget,
           "floor": 0.0, "seconds": round(time.time() - t0, 1),
           "arms": out}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "arms"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
