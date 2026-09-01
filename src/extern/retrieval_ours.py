"""Cell 2: this project's reader on MMLU with its own retrieval loop.

The model is not handed pages. It is given the world header and the question
in the training trace layout and it has to emit `<|retrieve|>` and write its
own queries; `src/evals/interactive.py:generate_with_retrieval` serves what it
asks for out of the live web through `src/retrieval_web/tier.py`, using the
same BM25 ranking the training oracle scored with. Both passes run over the
same items: `web` with a serving surface and `none` without, so the control is
the same model on the same questions with retrieval unavailable.

This reader was trained on this project's own corpus grammar and has never
seen an MMLU question, so it is expected to do badly. An accuracy alone would
not say why, and there are four different failures behind one flat number:

    issued_query      did it emit <|retrieve|> at all
    query_returned    did the query come back with any chunk
    context_entered   were served chunk tokens actually spliced into the trace
    read_it           conditional on the three above, did the answer change

Every one is recorded per question so the negative can be located rather than
asserted. The contamination label is taken from the chunks actually served,
not from a separate search, so it describes the text the model really saw.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

from src.extern.bench import LETTERS, TASKS
from src.extern.retrieval_mmlu import label_contamination, norm
from src.norm.cmpwork.grade import forced

WORLD_PREAMBLE = "domain: corporate"


class CachedExa:
    """The ExaClient search surface, cached on disk and hard budgeted.

    The cache is shared with cell 4 so one manifest covers the whole run and a
    replay costs nothing. The budget is counted in live calls only.
    """

    def __init__(self, client, cache_dir, budget):
        self.client = client
        self.dir = cache_dir
        self.budget = int(budget)
        self.live = 0
        self.hits = 0
        os.makedirs(cache_dir, exist_ok=True)

    def _p(self, q):
        h = hashlib.sha256(q.encode()).hexdigest()[:32]
        return os.path.join(self.dir, h + ".json")

    def search(self, query, num_results=10, text=True):
        p = self._p(query)
        if os.path.exists(p):
            self.hits += 1
            return json.load(open(p))
        if self.live >= self.budget:
            raise RuntimeError(f"exa budget of {self.budget} live calls spent")
        self.live += 1
        res = self.client.search(query, num_results=num_results, text=text)
        out = [{"url": r.get("url", ""), "title": r.get("title", ""),
                "text": r.get("text") or ""} for r in (res or [])]
        json.dump(out, open(p, "w"))
        return out


def question_text(row):
    s = row["question"].strip() + "\n"
    for i, c in enumerate(row["choices"]):
        s += f"{LETTERS[i]}. {c}\n"
    return s.strip()


def grade(answer, row):
    """Forced choice over the option strings, with a bare letter honoured."""
    opts = [str(c) for c in row["choices"]]
    gold = opts[row["gold"]]
    a = (answer or "").strip()
    head = a.split()[0].rstrip(".):").upper() if a.split() else ""
    if head in LETTERS[:len(opts)]:
        pick = LETTERS.index(head)
        return {"strict_correct": int(pick == row["gold"]),
                "lenient_correct": int(pick == row["gold"]),
                "named_none": 0, "hedged": 0, "via": "letter"}
    f = forced(a, opts, gold)
    f["via"] = "text"
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="/home/ec2-user/retrain/corpus-v1-8k.pt")
    ap.add_argument("--tag", default="corpus-v1-8k")
    ap.add_argument("--tokenizer",
                    default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default="results/extern/exa_cache")
    ap.add_argument("--budget", type=int, default=600)
    ap.add_argument("--max-rounds", type=int, default=3)
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--chunk-tokens", type=int, default=512)
    ap.add_argument("--num-results", type=int, default=5)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--retriever", default="exa", choices=("exa", "mock"))
    ap.add_argument("--passes", default="web,none")
    a = ap.parse_args()

    from src.evals.interactive import generate_with_retrieval, \
        make_checkpoint_step_fn
    from src.retrieval_web.tier import WebRetrievalTier, WebTierIndex
    from src.train.tokenizer import load_tokenizer

    if a.retriever == "mock":
        from src.retrieval_web.exa import MockExa
        base = MockExa()
    else:
        from src.retrieval_web.exa import ExaClient
        base = ExaClient()
    # Namespaced for the same reason as cell 4: a mock run must never leave
    # empty results where a live run will read them as hits.
    client = CachedExa(base, a.cache if a.retriever == "exa"
                       else os.path.join(a.cache, a.retriever), a.budget)

    tok = load_tokenizer(a.tokenizer)
    sid = tok.special_ids
    step_fn, model, state = make_checkpoint_step_fn(a.ckpt, a.device)
    n_params = sum(p.numel() for p in model.parameters())

    rows = TASKS["mmlu"](a.root, a.n, a.seed)
    passes = [p for p in a.passes.split(",") if p]
    recs, t0 = [], time.time()
    budget_hit = False

    for k, row in enumerate(rows):
        qt = question_text(row)
        prompt = [sid["<|world|>"], *tok.encode(WORLD_PREAMBLE),
                  sid["<|q|>"], *tok.encode(qt)]
        rec = {"id": row["id"], "subject": row["subject"],
               "gold": row["gold"], "n_choices": len(row["choices"])}
        for mode in passes:
            idx = None
            if mode == "web":
                if budget_hit:
                    continue
                tier = WebRetrievalTier(client, tok,
                                        max_chunk_tokens=a.chunk_tokens,
                                        num_results=a.num_results)
                idx = WebTierIndex(tier)
            try:
                out = generate_with_retrieval(
                    step_fn, tok, [], prompt, max_rounds=a.max_rounds,
                    max_new_tokens=a.max_new_tokens, seed=0, index=idx)
            except RuntimeError as e:
                if "budget" in str(e):
                    budget_hit = True
                    continue
                raise
            except Exception as e:
                rec[mode] = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
                continue
            served = " ".join(r.get("chunk", "") or "" for r in out["rounds"])
            g = grade(out.get("answer_text", ""), row)
            rec[mode] = {
                "answer": (out.get("answer_text") or "")[:300],
                "stop_reason": out.get("stop_reason"),
                "n_rounds": out.get("n_rounds", 0),
                "n_generated": out.get("n_generated", 0),
                "queries": [r.get("query", "")[:120] for r in out["rounds"]],
                "chunk_tokens": [r.get("n_chunk_tokens", 0)
                                 for r in out["rounds"]],
                "served_chars": len(served),
                "issued_query": int(out.get("n_rounds", 0) > 0
                                    or out.get("stop_reason") == "max_rounds"),
                "query_returned": int(out.get("n_rounds", 0) > 0),
                "context_entered": int(sum(r.get("n_chunk_tokens", 0)
                                           for r in out["rounds"]) > 0),
                "strict": g["strict_correct"], "lenient": g["lenient_correct"],
                "named_none": g["named_none"], "hedged": g["hedged"],
                "via": g["via"],
                "contamination": label_contamination(served, row)
                if mode == "web" else "n/a",
            }
        recs.append(rec)
        if (k + 1) % 10 == 0:
            el = time.time() - t0
            print(f"{k+1}/{len(rows)} {el:.0f}s "
                  f"eta {el/(k+1)*(len(rows)-k-1):.0f}s "
                  f"live={client.live} cached={client.hits}", flush=True)

    def cell(sub, mode):
        sub = [r[mode] for r in sub if mode in r and "error" not in r[mode]]
        if not sub:
            return None
        n = len(sub)
        return {"n": n,
                "strict": round(sum(r["strict"] for r in sub) / n, 4),
                "lenient": round(sum(r["lenient"] for r in sub) / n, 4),
                "named_none": round(sum(r["named_none"] for r in sub) / n, 4),
                "issued_query": round(sum(r["issued_query"]
                                          for r in sub) / n, 4),
                "query_returned": round(sum(r["query_returned"]
                                            for r in sub) / n, 4),
                "context_entered": round(sum(r["context_entered"]
                                             for r in sub) / n, 4),
                "mean_rounds": round(sum(r["n_rounds"] for r in sub) / n, 2),
                "mean_served_chars": round(sum(r["served_chars"]
                                               for r in sub) / n, 1)}

    res = {"model": f"ours:{a.tag}", "cell": "2", "task": "mmlu",
           "params_total": n_params, "n": len(recs), "seed": a.seed,
           "retriever": a.retriever, "live_searches": client.live,
           "cache_hits": client.hits, "budget": a.budget,
           "max_rounds": a.max_rounds, "max_new_tokens": a.max_new_tokens,
           "world_preamble": WORLD_PREAMBLE, "budget_hit": budget_hit,
           "floor": round(sum(1.0 / r["n_choices"] for r in recs) / len(recs), 4),
           "web": cell(recs, "web"), "none": cell(recs, "none"),
           "by_contamination": {
               lab: cell([r for r in recs
                          if r.get("web", {}).get("contamination") == lab],
                         "web")
               for lab in ("verbatim", "answer", "neither")},
           "seconds": round(time.time() - t0, 1), "records": recs}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "records"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
