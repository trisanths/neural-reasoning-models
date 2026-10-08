"""One lever at a time, scored by whether the answer reaches the model.

A condition is a query formulation, a result count, a search type, an
optional domain restriction and whether highlights were requested. Each
condition is fetched once, cached, and then scored offline as many times
as we like, so packing and rank cutoffs cost nothing to re-examine.

The cache is namespaced by the whole request, not by the query string. A
run with different options writes to a different key and can never be
served an entry fetched under other options, which is the failure that
once put empty results under live query keys. Every entry records how
many results came back and how many carried text; an entry with no
results is counted as an empty search and is never scored as if the
search had returned pages.

The metric is the answer present rate: does the text that actually
reaches the model state the gold answer. It is reported with the token
detector (whole token match) and the soft detector (gold content words
in one window) and never as a single pooled number with accuracy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.getcwd())

from src.extern.bench import TASKS
from src.extern.retpack import (contains_answer, contains_answer_chars,
                                contains_answer_soft, degenerate_gold, norm,
                                pack, stem_key)
from src.extern.retquery import formulate

DETECTORS = {"chars": contains_answer_chars, "token": contains_answer,
             "soft": contains_answer_soft}

# Sites that host copies of exam items. A page from one of these can carry
# the question and its lettered answer together, which makes the answer
# present rate go up without any fact having been retrieved. They are
# excluded in one condition so the leak can be measured rather than assumed.
LEAK_DOMAINS = [
    "quizlet.com", "coursehero.com", "studocu.com", "brainly.com",
    "brainly.in", "chegg.com", "scribd.com", "docsity.com", "studyres.com",
    "quizizz.com", "numerade.com", "gauthmath.com", "cram.com",
    "studystack.com", "proprofs.com", "answers.com", "vaia.com",
    "studysmarter.co.uk", "coursesidekick.com", "quiz-maker.com",
    "testbank.com", "slideshare.net", "questionai.com", "studypool.com",
    "homework.study.com", "transtutors.com", "sparknotes.com",
    "coursehero.co.uk", "quizgecko.com", "knowunity.com", "studyx.ai",
    "examveda.com", "sanfoundry.com", "indiabix.com", "mcqmate.com",
    "careerride.com", "gkseries.com", "quizwiz.io", "flashcardmachine.com",
    "memorang.com", "anki.tools", "studyhippo.com", "studymoose.com",
]

REFERENCE_DOMAINS = [
    "en.wikipedia.org", "britannica.com", "ncbi.nlm.nih.gov",
    "plato.stanford.edu", "khanacademy.org", "byjus.com", "toppr.com",
    "study.com", "quizlet.com", "chem.libretexts.org", "bio.libretexts.org",
    "med.libretexts.org", "math.libretexts.org", "socratic.org",
    "mayoclinic.org", "investopedia.com", "law.cornell.edu",
]


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - h) / d, 3), round((c + h) / d, 3)]


def subset(rows, n, seed):
    if n >= len(rows):
        return rows
    idx = sorted(random.Random(seed).sample(range(len(rows)), n))
    return [rows[i] for i in idx]


class SweepCache:
    def __init__(self, path):
        self.path = path
        os.makedirs(path, exist_ok=True)
        self.lock = threading.Lock()

    def key(self, query, cfg):
        blob = json.dumps({"query": query, "cfg": cfg}, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:40]

    def get(self, query, cfg):
        p = os.path.join(self.path, self.key(query, cfg) + ".json")
        if not os.path.exists(p):
            return None
        try:
            rec = json.load(open(p))
        except ValueError:
            return None
        # An entry that does not carry the request it was fetched under, or
        # that carries no results list, is not a usable hit.
        if rec.get("cfg") != cfg or not isinstance(rec.get("results"), list):
            return None
        return rec

    def put(self, query, cfg, rec):
        p = os.path.join(self.path, self.key(query, cfg) + ".json")
        tmp = p + ".tmp"
        with open(tmp, "w") as f:
            json.dump(rec, f)
        os.replace(tmp, p)


def merge_results(recs):
    """Round robin over the ranked lists, first occurrence of a url wins."""
    out, seen = [], set()
    lists = [r["results"] for r in recs]
    for i in range(max((len(x) for x in lists), default=0)):
        for lst in lists:
            if i < len(lst) and lst[i]["url"] not in seen:
                seen.add(lst[i]["url"])
                out.append(lst[i])
    return out


def fetch_one(client, cache, row, cfg, gen_path, budget, lock):
    # A formulation written as "a+b" issues both queries and merges the two
    # ranked lists. It costs two searches per item and is scored as one
    # condition, so its spend is stated wherever its hit rate is.
    if "+" in cfg["formulation"]:
        parts, live_any = [], False
        for f in cfg["formulation"].split("+"):
            sub = dict(cfg, formulation=f)
            rec, live = fetch_one(client, cache, row, sub, gen_path, budget,
                                  lock)
            if rec is None:
                return None, live_any
            parts.append(rec)
            live_any = live_any or live
        merged = merge_results(parts)
        return {"query": " || ".join(p["query"] for p in parts), "cfg": cfg,
                "n_results": len(merged),
                "n_with_text": sum(1 for r in merged if r["text"].strip()),
                "results": merged}, live_any
    q = formulate(cfg["formulation"], row, gen_path)
    rec = cache.get(q, cfg)
    if rec is not None:
        return rec, False
    if client is None:
        return None, False
    with lock:
        if budget["spent"] >= budget["max"]:
            raise RuntimeError(f"search budget {budget['max']} exhausted")
        budget["spent"] += 1
    # The highlight query is the question and its options, whatever the
    # search query was. Highlights are content extraction, so asking for
    # the spans that match the whole item is the fair test of them, and
    # every option is in that query so none is favoured.
    hl = ({"query": formulate(cfg["hl_query"], row, gen_path),
           "numSentences": 5, "highlightsPerUrl": 3}
          if cfg["highlights"] else None)
    data = client.search_ex(
        q, num_results=cfg["num_results"], search_type=cfg["type"],
        text=True, max_characters=cfg["max_characters"], highlights=hl,
        include_domains=(cfg["domains"] or None),
        exclude_domains=(cfg.get("exclude_domains") or None))
    results = []
    for r in (data.get("results") or []):
        results.append({"url": r.get("url", ""), "title": r.get("title", ""),
                        "text": r.get("text") or "",
                        "highlights": list(r.get("highlights") or []),
                        "score": r.get("score")})
    rec = {"query": q, "cfg": cfg, "ts": time.time(),
           "n_results": len(results),
           "n_with_text": sum(1 for r in results if r["text"].strip()),
           "results": results}
    cache.put(q, cfg, rec)
    return rec, True


def pack_highlights(results, max_chars):
    parts, used = [], 0
    for r in results:
        for h in r.get("highlights") or []:
            h = " ".join(h.split())
            if not h:
                continue
            room = max_chars - used
            if room <= 0:
                return "\n\n".join(parts)
            parts.append(f"[{r.get('title') or r.get('url')}] {h[:room]}")
            used += min(len(h), room)
    return "\n\n".join(parts)


def flags(text, question, gold, distractors):
    hay = norm(text)
    sk = stem_key(question)
    out = {d: fn(hay, gold) for d, fn in DETECTORS.items()}
    out["stem"] = bool(sk) and sk in hay
    out["n_distractors"] = sum(1 for c in distractors if contains_answer(hay, c))
    out["chars"] = len(text)
    return out


def evaluate(items, max_chars, keep_list, packers):
    """items: list of (row, rec). Returns the summary dict."""
    per_item = []
    for row, rec in items:
        gold = row["choices"][row["gold"]]
        others = [c for i, c in enumerate(row["choices"]) if i != row["gold"]]
        res = rec["results"]
        page_flags = [flags(r["text"], row["question"], gold, others)
                      for r in res]
        ctx = {}
        for keep in keep_list:
            sub = res[:keep]
            for pk in packers:
                if pk == "highlights":
                    block = pack_highlights(sub, max_chars)
                else:
                    block = pack(pk, sub, max_chars, query=row["question"],
                                 options=row["choices"])
                ctx[f"{pk}@{keep}"] = flags(block, row["question"], gold, others)
        per_item.append({"id": row["id"], "subject": row["subject"],
                         "query": rec["query"], "n_results": rec["n_results"],
                         "n_with_text": rec["n_with_text"],
                         "degenerate_gold": degenerate_gold(gold),
                         "page_flags": page_flags, "ctx": ctx})
    n = len(per_item)

    def frac(pred):
        k = sum(1 for r in per_item if pred(r))
        return {"k": k, "n": n, "rate": round(k / n, 4) if n else None,
                "ci": wilson(k, n)}

    maxk = max((len(r["page_flags"]) for r in per_item), default=0)
    ks = [k for k in (1, 3, 5, 10, 20, 25, 30) if k <= max(maxk, 1)]
    if maxk and maxk not in ks:
        ks.append(maxk)
    recall = {}
    for det in ("token", "soft"):
        for k in ks:
            recall[f"{det}@{k}"] = frac(
                lambda r, k=k, d=det: any(p[d] for p in r["page_flags"][:k]))
    ctx_keys = sorted({k for r in per_item for k in r["ctx"]})
    ctx_summary = {}
    for ck in ctx_keys:
        ctx_summary[ck] = {
            "token": frac(lambda r, c=ck: r["ctx"][c]["token"]),
            "soft": frac(lambda r, c=ck: r["ctx"][c]["soft"]),
            "stem": frac(lambda r, c=ck: r["ctx"][c]["stem"]),
            "all_distractors_too": frac(
                lambda r, c=ck: r["ctx"][c]["token"]
                and r["ctx"][c]["n_distractors"] >= 3),
            "mean_chars": round(sum(r["ctx"][ck]["chars"]
                                    for r in per_item) / max(1, n), 1)}
    return {"n": n,
            "empty_searches": sum(1 for r in per_item if r["n_results"] == 0),
            "no_text_searches": sum(1 for r in per_item
                                    if r["n_with_text"] == 0),
            "mean_results": round(sum(r["n_results"] for r in per_item)
                                  / max(1, n), 2),
            "mean_page_chars": round(
                sum(p["chars"] for r in per_item for p in r["page_flags"])
                / max(1, sum(len(r["page_flags"]) for r in per_item)), 1),
            "recall_full_text": recall, "context_hit": ctx_summary}, per_item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--formulation", default="question")
    ap.add_argument("--num-results", type=int, default=20)
    ap.add_argument("--type", default="neural")
    ap.add_argument("--domains", default="")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--highlights", action="store_true")
    ap.add_argument("--max-characters", type=int, default=50000)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--subset-n", type=int, default=50)
    ap.add_argument("--subset-seed", type=int, default=20260831)
    ap.add_argument("--gen-queries", default="data/extern/gen_queries.json")
    ap.add_argument("--cache", default="results/extern/exa_sweep_cache")
    ap.add_argument("--max-context-chars", type=int, default=6000)
    ap.add_argument("--keep", default="1,3,5,10,20")
    ap.add_argument("--packers",
                    default="sequential,even,passages,passages_q,highlights")
    ap.add_argument("--budget", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--outdir", default="results/extern/retsweep")
    a = ap.parse_args()

    cfg = {"formulation": a.formulation, "num_results": a.num_results,
           "type": a.type,
           "domains": ([d.strip() for d in a.domains.split(",") if d.strip()]
                       if a.domains != "reference" else REFERENCE_DOMAINS),
           "highlights": bool(a.highlights),
           "hl_query": "question_options",
           "max_characters": a.max_characters}
    # Added only when used, so the cache keys written before this option
    # existed still match and no earlier condition has to be refetched.
    exclude = (LEAK_DOMAINS if a.exclude == "leak"
               else [d.strip() for d in a.exclude.split(",") if d.strip()])
    if exclude:
        cfg["exclude_domains"] = exclude
    rows = subset(TASKS["mmlu"](a.root, a.n, a.seed), a.subset_n, a.subset_seed)
    cache = SweepCache(a.cache)
    budget = {"spent": 0, "max": a.budget}
    lock = threading.Lock()
    client = None
    if a.budget > 0:
        from src.extern.retexa import ExaSearch
        client = ExaSearch()

    t0 = time.time()
    items, misses = [], 0

    def work(row):
        return row, fetch_one(client, cache, row, cfg, a.gen_queries,
                              budget, lock)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for row, (rec, live) in ex.map(work, rows):
            if rec is None:
                misses += 1
                continue
            items.append((row, rec))
    if misses:
        print(f"WARNING {misses} items had no cache entry and no budget",
              flush=True)
    keep_list = [int(x) for x in a.keep.split(",") if int(x) <= a.num_results]
    if a.num_results not in keep_list:
        keep_list.append(a.num_results)
    packers = [p for p in a.packers.split(",") if p]
    if not cfg["highlights"] and "highlights" in packers:
        packers.remove("highlights")
    summary, per_item = evaluate(items, a.max_context_chars, keep_list, packers)
    summary = {"name": a.name, "cfg": cfg, "subset_n": a.subset_n,
               "subset_seed": a.subset_seed, "items_scored": len(items),
               "items_unfetched": misses,
               "live_searches": budget["spent"], "budget": a.budget,
               "max_context_chars": a.max_context_chars,
               "seconds": round(time.time() - t0, 1)} | summary
    os.makedirs(a.outdir, exist_ok=True)
    out = os.path.join(a.outdir, a.name + ".json")
    json.dump({"summary": summary, "records": per_item}, open(out, "w"),
              indent=1)
    brief = {k: summary[k] for k in ("name", "items_scored", "live_searches",
                                     "empty_searches", "no_text_searches",
                                     "mean_results", "mean_page_chars")}
    brief["recall_token"] = {k: v["rate"] for k, v in
                             summary["recall_full_text"].items()
                             if k.startswith("token@")}
    brief["ctx_token"] = {k: v["token"]["rate"]
                          for k, v in summary["context_hit"].items()}
    print(json.dumps(brief), flush=True)
    print("wrote " + out, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
