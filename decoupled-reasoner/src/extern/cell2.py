"""Cell 2 at a real n: this project's reader on MMLU driving its own retrieval.

The headline is the rate at which the policy emits `<|retrieve|>`, not the
accuracy. Two earlier passes disagreed about that rate, 0.05 against 0.255, and
the disagreement was a measurement artefact rather than a fact about the model,
so this runner records the emission directly and symmetrically across passes.

`src/extern/retrieval_ours.py` scored `issued_query` as
`n_rounds > 0 or stop_reason == "max_rounds"`. Those two conditions mean
different things depending on whether a serving surface is attached:

    no index   `<|retrieve|>` short circuits at the index-is-None guard before
               a single query token is written, so stop_reason is max_rounds
               and every emission is counted.
    web index  the loop keeps decoding to collect the query text. If the
               new-token budget runs out mid query the loop breaks with
               stop_reason still max_new_tokens and no round recorded, so the
               emission is counted as zero.

`emitted_retrieve` below is true whenever the model wrote `<|retrieve|>` at
all, in either pass, and it is what the rate is quoted from. The legacy
counter is kept beside it so the two published numbers can be reconciled
rather than quietly replaced.

The prompt comes from `src/rl/env.py:build_prompt`, the same function the RL
rollouts use, with the world header present. Without the header this
checkpoint emits no retrieval rounds at all, so the header is asserted into
the token stream rather than assumed.

Greedy decoding is reported beside temperature sampling. Greedy reads one
point of the policy and can return a false zero for a behaviour the policy
holds at moderate probability; the sampled arms estimate the rate under the
distribution the policy actually defines.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

import numpy as np

from src.extern.bench import LETTERS, TASKS
from src.extern.retrieval_mmlu import label_contamination
from src.extern.retrieval_ours import CachedExa, grade, question_text

WORLD = {"domain": "corporate"}


class QueryLog:
    """Per item record of every query the policy actually sent to the web.

    An empty query never reaches the API. This policy emits `<|retrieve|>`
    followed immediately by `<|result|>` often enough that letting the request
    through ends the run on an HTTP 400, and an empty query is a degenerate
    query rather than a search that failed. It is recorded as one and the
    decode loop is told nothing could be served, which is the same path an
    exhausted index takes.

    A live API failure returns nothing and is never written to the cache, so a
    transient error cannot leave an empty page list under a real query key for
    a later run to score against. Failures are counted and reported rather
    than swallowed: a run whose retrieval quietly stopped working would look
    exactly like a policy that never retrieves.
    """

    def __init__(self, cached):
        self.c = cached
        self.item = []
        self.empty = 0
        self.api_errors = []
        self.suspect_hits = []

    @property
    def live(self):
        return self.c.live

    @property
    def hits(self):
        return self.c.hits

    def reset(self):
        self.item = []

    def search(self, query, num_results=10, text=True):
        q = (query or "").strip()
        if not q:
            self.empty += 1
            self.item.append({"query": query[:160], "outcome": "empty"})
            return []
        before = self.c.live
        try:
            res = self.c.search(query, num_results=num_results, text=text)
        except RuntimeError as e:
            if "budget" in str(e):
                raise
            self.api_errors.append({"query": q[:160], "error": str(e)[:200]})
            self.item.append({"query": q[:160], "outcome": "api_error"})
            return []
        chars = sum(len((r.get("text") or "")) for r in res)
        outcome = "live" if self.c.live > before else "cached"
        if outcome == "cached" and chars == 0:
            self.suspect_hits.append(q[:160])
        self.item.append({"query": q[:160], "outcome": outcome,
                          "n_pages": len(res), "n_text_chars": chars})
        return res


def build_prompt_for(row, tok):
    """The RL prompt builder, with the header, plus a token level check.

    `src/rl/env.py:build_prompt` renders `<|world|> preamble <|q|> question`
    for an episode carrying no in-context documents, which is what cell 2 is.
    The assertion pins the layout: if the header ever stopped being emitted
    this raises here instead of producing a silent zero-retrieval run.
    """
    from src.rl.env import build_prompt
    qt = question_text(row)
    ids = build_prompt({"world": WORLD, "documents": [], "n_context": 0},
                       {"text": qt}, tok)
    sid = tok.special_ids
    expect = [sid["<|world|>"], *tok.encode("domain: corporate"),
              sid["<|q|>"], *tok.encode(qt)]
    assert ids == expect, "world header missing from the built prompt"
    assert ids[0] == sid["<|world|>"]
    assert sid["<|q|>"] in ids
    return ids, qt


def sampling_step(step_fn, temperature, top_p, seed):
    """Wrap a scores callable so the decode loop samples instead of argmaxing.

    The loop takes an argmax over whatever the step function returns, so a
    one-hot vector at the sampled index makes it sample without touching
    `src/evals/interactive.py`. The generator is seeded per item, so a
    sampled arm replays exactly.
    """
    rng = np.random.default_rng(seed)

    def f(tokens):
        logits = np.asarray(step_fn(tokens), dtype=np.float64).reshape(-1)
        z = logits / max(temperature, 1e-6)
        z -= z.max()
        p = np.exp(z)
        p /= p.sum()
        if top_p < 1.0:
            order = np.argsort(-p)
            c = np.cumsum(p[order])
            keep = order[:max(1, int(np.searchsorted(c, top_p) + 1))]
            mask = np.zeros_like(p)
            mask[keep] = p[keep]
            p = mask / mask.sum()
        pick = int(rng.choice(len(p), p=p))
        out = np.zeros_like(p)
        out[pick] = 1.0
        return out

    return f


def run_pass(rows, tok, step_fn, sid, client, mode, decode, a,
             max_new_tokens, log_every=10):
    """One arm: every item, one decode setting, with or without a web index."""
    from src.evals.interactive import generate_with_retrieval
    from src.retrieval_web.tier import WebRetrievalTier, WebTierIndex

    retrieve_id = sid["<|retrieve|>"]
    recs = []
    t0 = time.time()
    budget_hit = False
    for k, row in enumerate(rows):
        prompt, _ = build_prompt_for(row, tok)
        idx = None
        client.reset()
        if mode == "web":
            tier = WebRetrievalTier(client, tok,
                                    max_chunk_tokens=a.chunk_tokens,
                                    num_results=a.num_results)
            idx = WebTierIndex(tier)
        fn = step_fn
        if decode["kind"] == "sampled":
            fn = sampling_step(step_fn, decode["temperature"],
                               decode["top_p"], decode["seed"] + k)
        err = None
        try:
            out = generate_with_retrieval(
                fn, tok, [], prompt, max_rounds=a.max_rounds,
                max_new_tokens=max_new_tokens, seed=decode.get("seed", 0),
                index=idx)
        except RuntimeError as e:
            if "budget" in str(e):
                budget_hit = True
                break
            raise
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {str(e)[:160]}"
            out = None
        if out is None:
            recs.append({"id": row["id"], "subject": row["subject"],
                         "gold": row["gold"],
                         "n_choices": len(row["choices"]), "error": err,
                         "sent_queries": list(client.item)})
            continue
        served = " ".join(r.get("chunk", "") or "" for r in out["rounds"])
        g = grade(out.get("answer_text", ""), row)
        stop = out.get("stop_reason")
        n_rounds = out.get("n_rounds", 0)
        recs.append({
            "id": row["id"], "subject": row["subject"], "gold": row["gold"],
            "n_choices": len(row["choices"]),
            "answer": (out.get("answer_text") or "")[:300],
            "stop_reason": stop, "n_rounds": n_rounds,
            "n_generated": out.get("n_generated", 0),
            "queries": [r.get("query", "")[:160] for r in out["rounds"]],
            "chunk_tokens": [r.get("n_chunk_tokens", 0)
                             for r in out["rounds"]],
            "served_chars": len(served),
            "sent_queries": list(client.item),
            "n_queries_sent": len(client.item),
            "empty_query": int(any(q["outcome"] == "empty"
                                   for q in client.item)),
            "api_error_query": int(any(q["outcome"] == "api_error"
                                       for q in client.item)),
            # The symmetric counter. True whenever <|retrieve|> was written,
            # whether or not a query completed and whether or not it served.
            "emitted_retrieve": int(retrieve_id in out["generated"]
                                    or stop == "max_rounds"),
            # The counter the published passes used, kept for reconciliation.
            "issued_query_legacy": int(n_rounds > 0 or stop == "max_rounds"),
            "query_returned": int(n_rounds > 0),
            "context_entered": int(sum(r.get("n_chunk_tokens", 0)
                                       for r in out["rounds"]) > 0),
            "strict": g["strict_correct"], "lenient": g["lenient_correct"],
            "named_none": g["named_none"], "hedged": g["hedged"],
            "via": g["via"],
            "contamination": (label_contamination(served, row)
                              if mode == "web" else "n/a"),
        })
        if (k + 1) % log_every == 0:
            el = time.time() - t0
            print(f"  {mode}/{decode['name']} {k+1}/{len(rows)} {el:.0f}s "
                  f"eta {el/(k+1)*(len(rows)-k-1):.0f}s "
                  f"live={client.live} cached={client.hits} "
                  f"emit={sum(r.get('emitted_retrieve', 0) for r in recs)}",
                  flush=True)
    return recs, budget_hit, round(time.time() - t0, 1)


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
    ap.add_argument("--budget", type=int, default=400)
    ap.add_argument("--max-rounds", type=int, default=3)
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--truncated-max-new-tokens", type=int, default=64)
    ap.add_argument("--chunk-tokens", type=int, default=512)
    ap.add_argument("--num-results", type=int, default=5)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--retriever", default="exa", choices=("exa", "mock"))
    ap.add_argument("--arms", default="web_greedy,none_greedy,none_t10,"
                                      "none_t08,web_greedy_trunc64")
    a = ap.parse_args()

    from src.evals.interactive import make_checkpoint_step_fn
    from src.train.tokenizer import load_tokenizer

    if a.retriever == "mock":
        from src.retrieval_web.exa import MockExa
        base = MockExa()
    else:
        from src.retrieval_web.exa import ExaClient
        base = ExaClient()
    cdir = a.cache if a.retriever == "exa" else os.path.join(a.cache,
                                                             a.retriever)
    client = QueryLog(CachedExa(base, cdir, a.budget))

    tok = load_tokenizer(a.tokenizer)
    sid = tok.special_ids
    step_fn, model, state = make_checkpoint_step_fn(a.ckpt, a.device)
    n_params = sum(p.numel() for p in model.parameters())
    rows = TASKS["mmlu"](a.root, a.n, a.seed)

    ARMS = {
        "web_greedy": ("web", {"kind": "greedy", "name": "greedy"},
                       a.max_new_tokens),
        "none_greedy": ("none", {"kind": "greedy", "name": "greedy"},
                        a.max_new_tokens),
        "none_t10": ("none", {"kind": "sampled", "name": "T=1.0",
                              "temperature": 1.0, "top_p": 1.0,
                              "seed": 7000}, a.max_new_tokens),
        "none_t08": ("none", {"kind": "sampled", "name": "T=0.8,p=0.95",
                              "temperature": 0.8, "top_p": 0.95,
                              "seed": 8000}, a.max_new_tokens),
        "web_greedy_trunc64": ("web", {"kind": "greedy",
                                       "name": "greedy,trunc"},
                               a.truncated_max_new_tokens),
    }

    arms = {}
    t0 = time.time()
    for name in [s for s in a.arms.split(",") if s]:
        mode, decode, mnt = ARMS[name]
        print(f"== arm {name}: mode={mode} decode={decode['name']} "
              f"max_new_tokens={mnt}", flush=True)
        recs, bh, secs = run_pass(rows, tok, step_fn, sid, client, mode,
                                  decode, a, mnt)
        arms[name] = {"mode": mode, "decode": decode, "max_new_tokens": mnt,
                      "budget_hit": bh, "seconds": secs, "records": recs}
        print(f"== arm {name} done in {secs}s, live={client.live} "
              f"cached={client.hits}", flush=True)

    res = {"model": f"ours:{a.tag}", "cell": "2", "task": "mmlu",
           "ckpt": os.path.abspath(a.ckpt), "params_total": n_params,
           "n_items": len(rows), "seed": a.seed, "device": a.device,
           "retriever": a.retriever, "live_searches": client.live,
           "cache_hits": client.hits, "budget": a.budget,
           "empty_queries": client.empty,
           "api_errors": client.api_errors[:40],
           "n_api_errors": len(client.api_errors),
           "suspect_cache_hits": client.suspect_hits[:40],
           "n_suspect_cache_hits": len(client.suspect_hits),
           "max_rounds": a.max_rounds, "num_results": a.num_results,
           "chunk_tokens": a.chunk_tokens,
           "world_preamble": "domain: corporate",
           "prompt_builder": "src.rl.env.build_prompt",
           "floor": round(sum(1.0 / len(r["choices"]) for r in rows)
                          / len(rows), 4),
           "seconds": round(time.time() - t0, 1), "arms": arms}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "arms"}))
    for k, v in arms.items():
        rs = [r for r in v["records"] if "error" not in r]
        n = len(rs)
        if not n:
            continue
        print(k, "n", n,
              "emit", round(sum(r["emitted_retrieve"] for r in rs) / n, 4),
              "legacy", round(sum(r["issued_query_legacy"] for r in rs) / n, 4),
              "served", round(sum(r["query_returned"] for r in rs) / n, 4),
              "acc", round(sum(r["strict"] for r in rs) / n, 4), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
