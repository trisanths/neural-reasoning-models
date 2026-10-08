"""Cell 4 again, with the retrieval configuration the sweep selected.

Everything about the scoring is held at what the published cell used:
the same 200 MMLU items at seed 1234, the same five shot completion
prompt with the reference material in front of it, the same log
likelihood over the letter continuations, bos prepended, float32 on cpu.
The only changes are which pages are fetched and which of their
characters reach the model.

The contamination split is computed under two detectors and both are
written out. `chars` is the raw substring test the published split used,
`token` is the whole token test. The cells are never pooled: an item
whose page carries the answer is a lookup and an item whose page does
not is the reasoning measurement, and one number over both would say
nothing about either.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.getcwd())

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.extern.bench import LETTERS, TASKS, mmlu_block
from src.extern.retpack import (contains_answer, contains_answer_chars,
                                contains_answer_soft, degenerate_gold, norm,
                                pack, stem_key)
from src.extern.retsweep import (LEAK_DOMAINS, REFERENCE_DOMAINS, SweepCache,
                                 fetch_one, pack_highlights, subset, wilson)


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


def cell(sub):
    if not sub:
        return {"n": 0}
    k = sum(r["pred"] == r["gold"] for r in sub)
    n = len(sub)
    return {"n": n, "correct": k, "acc": round(k / n, 4),
            "floor": round(sum(1.0 / r["n_choices"] for r in sub) / n, 4),
            "ci": wilson(k, n)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="LiquidAI/LFM2-350M")
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--subset-n", type=int, default=200)
    ap.add_argument("--subset-seed", type=int, default=20260831)
    ap.add_argument("--formulation", default="question_options")
    ap.add_argument("--type", default="neural")
    ap.add_argument("--num-results", type=int, default=20)
    ap.add_argument("--keep", type=int, default=20)
    ap.add_argument("--packer", default="passages")
    ap.add_argument("--domains", default="")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--highlights", action="store_true")
    ap.add_argument("--max-characters", type=int, default=50000)
    ap.add_argument("--max-context-chars", type=int, default=6000)
    ap.add_argument("--gen-queries", default="data/extern/gen_queries.json")
    ap.add_argument("--cache", default="results/extern/exa_sweep_cache")
    ap.add_argument("--budget", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--bos", action="store_true")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--fetch-only", action="store_true")
    a = ap.parse_args()

    cfg = {"formulation": a.formulation, "num_results": a.num_results,
           "type": a.type,
           "domains": (REFERENCE_DOMAINS if a.domains == "reference"
                       else [d.strip() for d in a.domains.split(",")
                             if d.strip()]),
           "highlights": bool(a.highlights),
           "hl_query": "question_options",
           "max_characters": a.max_characters}
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
    fetched = {}

    def work(row):
        return row["id"], fetch_one(client, cache, row, cfg, a.gen_queries,
                                    budget, lock)[0]

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for rid, rec in ex.map(work, rows):
            fetched[rid] = rec
    unfetched = [r["id"] for r in rows if fetched.get(r["id"]) is None]
    if unfetched:
        raise SystemExit(f"{len(unfetched)} items unfetched, budget "
                         f"{a.budget} spent {budget['spent']}: "
                         f"{unfetched[:3]}")
    empty = sum(1 for r in rows if fetched[r["id"]]["n_results"] == 0)
    no_text = sum(1 for r in rows if fetched[r["id"]]["n_with_text"] == 0)
    print(f"fetched {len(rows)} live={budget['spent']} empty={empty} "
          f"no_text={no_text} {time.time()-t0:.0f}s", flush=True)

    blocks = {}
    for row in rows:
        res = fetched[row["id"]]["results"][:a.keep]
        blocks[row["id"]] = (
            pack_highlights(res, a.max_context_chars) if a.packer == "highlights"
            else pack(a.packer, res, a.max_context_chars,
                      query=row["question"], options=row["choices"]))
    if a.fetch_only:
        summary = hit_summary(rows, blocks, fetched, cfg, a, budget, empty,
                              no_text, t0)
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        json.dump({"summary": summary}, open(a.out, "w"), indent=1)
        print(json.dumps(summary))
        return 0

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=getattr(torch, a.dtype)).to(a.device).eval()

    recs = []
    for k, row in enumerate(rows):
        block = blocks[row["id"]]
        gold = row["choices"][row["gold"]]
        others = [c for i, c in enumerate(row["choices"]) if i != row["gold"]]
        hay = norm(block)
        sk = stem_key(row["question"])
        f = {"stem": bool(sk) and sk in hay,
             "chars": contains_answer_chars(hay, gold),
             "token": contains_answer(hay, gold),
             "soft": contains_answer_soft(hay, gold),
             "n_distractors": sum(1 for c in others
                                  if contains_answer(hay, c))}
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
                     "flags": f, "degenerate_gold": degenerate_gold(gold),
                     "n_pages": len(fetched[row["id"]]["results"][:a.keep]),
                     "context_chars": len(block),
                     "query": fetched[row["id"]]["query"],
                     "urls": [x["url"] for x in
                              fetched[row["id"]]["results"][:5]]})
        if (k + 1) % 20 == 0:
            el = time.time() - t0
            print(f"{k+1}/{len(rows)} {el:.0f}s "
                  f"eta {el/(k+1)*(len(rows)-k-1):.0f}s", flush=True)

    def label(r, det):
        if r["flags"]["stem"]:
            return "verbatim"
        return "answer" if r["flags"][det] else "neither"

    res = {"model": a.model, "task": "mmlu", "condition": "retrieval",
           "cfg": cfg, "packer": a.packer, "keep": a.keep,
           "max_context_chars": a.max_context_chars,
           "n": len(recs), "seed": a.seed, "bos": a.bos,
           "live_searches": budget["spent"], "empty_searches": empty,
           "no_text_searches": no_text,
           "mean_context_chars": round(sum(r["context_chars"]
                                           for r in recs) / len(recs), 1),
           "mean_pages": round(sum(r["n_pages"] for r in recs) / len(recs), 2),
           "answer_present_token": round(sum(r["flags"]["token"]
                                             for r in recs) / len(recs), 4),
           "answer_present_chars": round(sum(r["flags"]["chars"]
                                             for r in recs) / len(recs), 4),
           "stem_present": round(sum(r["flags"]["stem"]
                                     for r in recs) / len(recs), 4),
           "all": cell(recs),
           "by_contamination_token": {
               lab: cell([r for r in recs if label(r, "token") == lab])
               for lab in ("verbatim", "answer", "neither")},
           "by_contamination_chars": {
               lab: cell([r for r in recs if label(r, "chars") == lab])
               for lab in ("verbatim", "answer", "neither")},
           "seconds": round(time.time() - t0, 1)}
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(res | {"records": recs}, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "records"}),
          flush=True)
    return 0


def hit_summary(rows, blocks, fetched, cfg, a, budget, empty, no_text, t0):
    n = len(rows)
    counts = {"token": 0, "chars": 0, "soft": 0, "stem": 0, "answer": 0,
              "clean": 0}
    for row in rows:
        gold = row["choices"][row["gold"]]
        others = [c for i, c in enumerate(row["choices"]) if i != row["gold"]]
        hay = norm(blocks[row["id"]])
        sk = stem_key(row["question"])
        st = bool(sk) and sk in hay
        tk = contains_answer(hay, gold)
        nd = sum(1 for c in others if contains_answer(hay, c))
        counts["token"] += tk
        counts["chars"] += contains_answer_chars(hay, gold)
        counts["soft"] += contains_answer_soft(hay, gold)
        counts["stem"] += st
        counts["answer"] += tk and not st
        counts["clean"] += tk and not st and nd < 3
    return {"cfg": cfg, "packer": a.packer, "keep": a.keep,
            "max_context_chars": a.max_context_chars, "n": n,
            "live_searches": budget["spent"], "empty_searches": empty,
            "no_text_searches": no_text,
            "mean_context_chars": round(sum(len(b) for b in blocks.values())
                                        / n, 1),
            "rates": {k: {"k": v, "n": n, "rate": round(v / n, 4),
                          "ci": wilson(v, n)} for k, v in counts.items()},
            "seconds": round(time.time() - t0, 1)}


if __name__ == "__main__":
    raise SystemExit(main())
