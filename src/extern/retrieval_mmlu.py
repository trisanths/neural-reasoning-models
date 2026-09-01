"""MMLU with retrieved pages in context, and the contamination split.

This builds cells 2 and 4 of the comparison. Cell 4 puts retrieved pages into
an external model's context and rescores with the calibrated settings. Cell 2
is the same pages in front of this project's own reader.

The contamination label is per question and is the whole point of the split.
A page that states the answer turns the question into a lookup, and an
accuracy that pools lookups with the rest is not evidence about reasoning:

    verbatim   the retrieved text contains the question stem itself
    answer     it contains the gold answer string but not the stem
    neither    it contains neither

Accuracy is reported once for each label and never pooled. "Correct with
neither retrieved" is the cell that speaks to the thesis.

Retrieval goes through `src/retrieval_web/exa.py`. With no api key the module
refuses to construct a live client, and `--retriever mock` runs the offline
MockExa so the whole path can be exercised without the network. A mock run is
labelled as such in its output and is never a substitute for a measured cell.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.extern.bench import LETTERS, TASKS, mmlu_block

WORD = re.compile(r"[a-z0-9]+")


def norm(s):
    return " ".join(WORD.findall(str(s).lower()))


def query_for(row):
    """One search query per question: the stem, trimmed to a searchable length."""
    q = " ".join(str(row["question"]).split())
    return q[:300]


def label_contamination(pages_text, row):
    """verbatim / answer / neither, decided on normalised word sequences."""
    hay = norm(pages_text)
    stem = norm(row["question"])
    gold = norm(row["choices"][row["gold"]])
    stem_key = " ".join(stem.split()[:12])
    if stem_key and stem_key in hay:
        return "verbatim"
    if gold and gold in hay:
        return "answer"
    return "neither"


class Cache:
    """Searches are cached on disk keyed by query so a rerun costs nothing."""

    def __init__(self, path):
        self.path = path
        os.makedirs(path, exist_ok=True)

    def _p(self, q):
        return os.path.join(self.path,
                            hashlib.sha256(q.encode()).hexdigest()[:32] + ".json")

    def get(self, q):
        p = self._p(q)
        return json.load(open(p)) if os.path.exists(p) else None

    def put(self, q, v):
        json.dump(v, open(self._p(q), "w"))


def make_retriever(kind, num_results):
    if kind == "mock":
        from src.retrieval_web.exa import MockExa
        return MockExa(), "mock"
    from src.retrieval_web.exa import ExaClient
    return ExaClient(), "exa"


def search(client, cache, q, num_results, budget):
    hit = cache.get(q)
    if hit is not None:
        return hit, False
    if budget["spent"] >= budget["max"]:
        raise RuntimeError(f"search budget of {budget['max']} calls exhausted")
    budget["spent"] += 1
    # Both ExaClient and MockExa return the ranked result list directly.
    res = client.search(q, num_results=num_results, text=True)
    out = []
    for r in (res or []):
        out.append({"url": r.get("url", ""), "title": r.get("title", ""),
                    "text": (r.get("text") or "")})
    cache.put(q, out)
    return out, True


def context_block(pages, max_chars):
    """The retrieved pages as they are put in front of a model."""
    parts, used = [], 0
    for p in pages:
        t = " ".join((p["text"] or "").split())
        if not t:
            continue
        room = max_chars - used
        if room <= 0:
            break
        parts.append(f"[{p['title'] or p['url']}] {t[:room]}")
        used += min(len(t), room)
    return "\n\n".join(parts)


@torch.no_grad()
def score_letters(model, tok, ctx, n_choices, bos):
    ids = tok(ctx, add_special_tokens=False)["input_ids"]
    if bos and tok.bos_token_id is not None:
        ids = [tok.bos_token_id] + ids
    logits = model(input_ids=torch.tensor([ids])).logits.float()
    lp = torch.log_softmax(logits[0, -1], dim=-1)
    out = []
    for i in range(n_choices):
        t = tok(" " + LETTERS[i], add_special_tokens=False)["input_ids"]
        out.append(float(lp[t[0]]) if len(t) == 1 else float("-inf"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--out", required=True)
    ap.add_argument("--retriever", default="exa", choices=("exa", "mock"))
    ap.add_argument("--num-results", type=int, default=5)
    ap.add_argument("--max-context-chars", type=int, default=6000)
    ap.add_argument("--cache", default="results/extern/exa_cache")
    ap.add_argument("--budget", type=int, default=600)
    ap.add_argument("--bos", action="store_true")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dtype", default="float32")
    a = ap.parse_args()

    rows = TASKS["mmlu"](a.root, a.n, a.seed)
    client, kind = make_retriever(a.retriever, a.num_results)
    # The cache is namespaced by retriever. A mock run writes empty results
    # under the same query keys a live run uses, and a later live run would
    # then take those empties as cache hits and score the question with no
    # retrieved text at all. Keeping the two apart makes that impossible.
    cache = Cache(a.cache if kind == "exa" else os.path.join(a.cache, kind))
    budget = {"spent": 0, "max": a.budget}

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=getattr(torch, a.dtype)).to(a.device).eval()

    recs, t0 = [], time.time()
    for k, row in enumerate(rows):
        q = query_for(row)
        pages, live = search(client, cache, q, a.num_results, budget)
        block = context_block(pages, a.max_context_chars)
        lab = label_contamination(block, row)
        head = ("The following are multiple choice questions (with answers) "
                f"about {row['subject'].replace('_', ' ')}.\n\n")
        shots = "".join(mmlu_block(s["question"], list(s["choices"]),
                                   int(s["answer"])) for s in row["shots"])
        body = mmlu_block(row["question"], row["choices"])
        ctx = (("Reference material:\n" + block + "\n\n") if block else "") \
            + head + shots + body
        lp = score_letters(model, tok, ctx, len(row["choices"]), a.bos)
        recs.append({"id": row["id"], "subject": row["subject"],
                     "gold": row["gold"], "n_choices": len(row["choices"]),
                     "pred": int(max(range(len(lp)), key=lambda i: lp[i])),
                     "contamination": lab, "n_pages": len(pages),
                     "context_chars": len(block), "query": q,
                     "urls": [p["url"] for p in pages][:5]})
        if (k + 1) % 20 == 0:
            el = time.time() - t0
            print(f"{k+1}/{len(rows)} {el:.0f}s "
                  f"eta {el/(k+1)*(len(rows)-k-1):.0f}s "
                  f"live_searches={budget['spent']}", flush=True)

    def cell(sub):
        if not sub:
            return None
        return {"n": len(sub),
                "acc": round(sum(r["pred"] == r["gold"]
                                 for r in sub) / len(sub), 4),
                "floor": round(sum(1.0 / r["n_choices"]
                                   for r in sub) / len(sub), 4)}

    res = {"model": a.model, "task": "mmlu", "condition": "retrieval",
           "retriever": kind, "live_searches": budget["spent"],
           "n": len(recs), "seed": a.seed, "bos": a.bos,
           "num_results": a.num_results,
           "max_context_chars": a.max_context_chars,
           "mean_context_chars": round(sum(r["context_chars"]
                                           for r in recs) / len(recs), 1),
           "mean_pages": round(sum(r["n_pages"] for r in recs) / len(recs), 2),
           "pages_empty": sum(1 for r in recs if r["n_pages"] == 0),
           "all": cell(recs),
           "by_contamination": {
               lab: cell([r for r in recs if r["contamination"] == lab])
               for lab in ("verbatim", "answer", "neither")},
           "seconds": round(time.time() - t0, 1), "records": recs}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "records"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
