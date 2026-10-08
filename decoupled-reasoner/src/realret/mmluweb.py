"""MMLU with live web pages, for this project's checkpoints.

`src/extern/retrieval_mmlu.py` builds this for the external models. This
builds the other side of the same table, and it does so by importing that
module rather than restating it: the item sample, the search query, the
page cache, the context block and the contamination label all come from
there, so the two sides of a row differ in the model and in nothing else.

Run this after the external cell with `--budget 0`. Every search then has
to be a cache hit, and a miss is an error rather than a second, different
set of pages. That is what makes "given the same pages" checkable instead
of asserted.

Three conditions, reported separately and never pooled.

  matched   the pages are prepended to the same five-shot completion string
            the external model is scored on, and the four letters are scored
            by log likelihood. This is the cell that is comparable to the
            external one, because the string and the scoring rule are the
            same.

  native    the pages arrive as `<|doc|>` blocks after the world header, the
            question and its choices follow, and the four choice texts are
            scored after `<|a|>`. This is the format the checkpoint was
            trained in. A model that reads pages only in its own layout
            shows up as native above matched.

  agentic   the model drives its own retrieval: it is given the world header
            and the question, and when it emits `<|retrieve|>` the query it
            writes goes to the web tier and the pages come back through
            `<|result|>`. Nothing is put in its context that it did not ask
            for. This is the condition the training is actually about, and
            the one whose failures decompose.

Chance floor is one over the number of choices on every cell, and it is
carried in the output next to every accuracy.
"""

from __future__ import annotations

import argparse
import json
import os
import time

import torch

from src.extern.bench import LETTERS, TASKS, mmlu_block
from src.extern.retrieval_mmlu import (Cache, context_block, label_contamination,
                                       make_retriever, query_for, search)


class CachedSearch:
    """The Exa client behind the same on-disk cache the scored cells use.

    A model that drives its own retrieval writes its own queries, so a run
    can spend one search per round per item. Caching means a rerun of the
    same checkpoint costs nothing and a second checkpoint asking the same
    question gets the same pages, which is the only way two agentic cells
    are comparable at all.
    """

    def __init__(self, client, cache, budget: int):
        self.client = client
        self.cache = cache
        self.budget = {"spent": 0, "max": budget}

    def search(self, query: str, num_results: int = 10, text: bool = True):
        key = f"agentic:{num_results}:{query}"
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        if self.budget["spent"] >= self.budget["max"]:
            raise RuntimeError("search budget exhausted")
        self.budget["spent"] += 1
        res = self.client.search(query, num_results=num_results, text=text)
        out = [{"url": r.get("url", ""), "title": r.get("title", ""),
                "text": (r.get("text") or "")} for r in (res or [])]
        self.cache.put(key, out)
        return out


@torch.no_grad()
def letters_ours(model, tok, ctx: str, n_choices: int, device, max_seq: int,
                 prefix=()):
    """Log probability of " A" .. " D" as the next token after ctx.

    Returns the scores and how long the context was before cropping. The
    crop keeps the tail, and the retrieved pages sit at the head, so an
    overflow silently deletes the evidence the cell is supposed to measure.
    The length is recorded per item and the overflow count is reported, so a
    cell that measured a cropped prompt cannot be read as a cell that
    measured the pages.
    """
    ids = list(prefix) + tok.encode(ctx)
    full = len(ids)
    ids = ids[-max_seq:]
    x = torch.tensor([ids], dtype=torch.long, device=device)
    lp = torch.log_softmax(model(x)[0].float()[0, -1], dim=-1)
    out = []
    for i in range(n_choices):
        t = tok.encode(" " + LETTERS[i])
        out.append(float(lp[t[0]]) if len(t) == 1 else float("-inf"))
    return out, full


def native_context(row, pages, tok, chunk_tokens: int, max_chunks: int):
    """World header, retrieved chunks as documents, question, answer marker."""
    from src.retrieval_web.tier import chunk_text
    from src.train.data import render_world_preamble

    sid = tok.special_ids
    ids = [sid["<|world|>"]]
    ids.extend(tok.encode(render_world_preamble({"domain": "web"})))
    n = 0
    for p in pages:
        for c in chunk_text(p.get("text") or "", tok, chunk_tokens):
            if n >= max_chunks:
                break
            ids.append(sid["<|doc|>"])
            ids.extend(tok.encode(c))
            n += 1
        if n >= max_chunks:
            break
    body = mmlu_block(row["question"], row["choices"])
    ids.append(sid["<|q|>"])
    ids.extend(tok.encode(body))
    ids.append(sid["<|a|>"])
    return ids, n


def cell(sub):
    if not sub:
        return None
    return {"n": len(sub),
            "acc": round(sum(r["pred"] == r["gold"] for r in sub) / len(sub), 4),
            "floor": round(sum(1.0 / r["n_choices"] for r in sub) / len(sub), 4)}


def summarise(recs, key="pred"):
    def c(sub):
        if not sub:
            return None
        return {"n": len(sub),
                "acc": round(sum(r[key] == r["gold"] for r in sub) / len(sub), 4),
                "floor": round(sum(1.0 / r["n_choices"]
                                   for r in sub) / len(sub), 4)}
    return {"all": c(recs),
            "by_contamination": {
                lab: c([r for r in recs if r["contamination"] == lab])
                for lab in ("verbatim", "answer", "neither")}}


def cmd_score(args) -> int:
    from src.evals.mc import load_checkpoint_model, score_mc
    from src.train.tokenizer import load_tokenizer

    rows = TASKS["mmlu"](args.root, args.n, args.seed)
    client, kind = make_retriever(args.retriever, args.num_results)
    cache = Cache(args.cache)
    budget = {"spent": 0, "max": args.budget}

    tok = load_tokenizer(args.tokenizer)
    device = args.device
    model, state = load_checkpoint_model(args.ckpt, device)
    max_seq = model.cfg.max_seq_len
    prefix = (tok.token_id("<|eot|>"),) if args.eot_prefix else ()

    recs, t0 = [], time.time()
    for k, row in enumerate(rows):
        q = query_for(row)
        pages, _ = search(client, cache, q, args.num_results, budget)
        block = context_block(pages, args.max_context_chars)
        lab = label_contamination(block, row)
        head = ("The following are multiple choice questions (with answers) "
                f"about {row['subject'].replace('_', ' ')}.\n\n")
        shots = "".join(mmlu_block(s["question"], list(s["choices"]),
                                   int(s["answer"])) for s in row["shots"])
        body = mmlu_block(row["question"], row["choices"])

        closed = (head + shots + body)
        opened = (("Reference material:\n" + block + "\n\n") if block else "") \
            + head + shots + body
        lp_closed, len_closed = letters_ours(
            model, tok, closed, len(row["choices"]), device, max_seq, prefix)
        lp_open, len_open = letters_ours(
            model, tok, opened, len(row["choices"]), device, max_seq, prefix)

        ids, n_chunks = native_context(row, pages, tok, args.chunk_tokens,
                                       args.max_chunks)
        ids = ids[-max_seq:]
        best, nlls = score_mc(model, tok, ids, list(row["choices"]), device)

        recs.append({
            "id": row["id"], "subject": row["subject"], "gold": row["gold"],
            "n_choices": len(row["choices"]), "contamination": lab,
            "n_pages": len(pages), "context_chars": len(block),
            "n_native_chunks": n_chunks, "query": q,
            "ctx_tokens_closed": len_closed, "ctx_tokens_open": len_open,
            "cropped": bool(len_open > max_seq),
            "urls": [p["url"] for p in pages][:5],
            "pred_closed": int(max(range(len(lp_closed)),
                                   key=lambda i: lp_closed[i])),
            "pred": int(max(range(len(lp_open)), key=lambda i: lp_open[i])),
            "pred_native": int(best),
            "logp_closed": [round(v, 4) for v in lp_closed],
            "logp_open": [round(v, 4) for v in lp_open],
            "nll_native": [round(v, 4) for v in nlls],
        })
        if (k + 1) % 25 == 0:
            el = time.time() - t0
            print(f"{k+1}/{len(rows)} {el:.0f}s "
                  f"eta {el/(k+1)*(len(rows)-k-1):.0f}s "
                  f"live={budget['spent']}", flush=True)

    res = {"model": f"ours:{args.tag}", "ckpt": os.path.abspath(args.ckpt),
           "task": "mmlu", "condition": "retrieval", "retriever": kind,
           "live_searches": budget["spent"], "n": len(recs),
           "seed": args.seed, "shots": 5, "eot_prefix": args.eot_prefix,
           "num_results": args.num_results,
           "max_context_chars": args.max_context_chars,
           "params_total": sum(p.numel() for p in model.parameters()),
           "mean_context_chars": round(sum(r["context_chars"]
                                           for r in recs) / len(recs), 1),
           "mean_pages": round(sum(r["n_pages"] for r in recs) / len(recs), 2),
           "pages_empty": sum(1 for r in recs if r["n_pages"] == 0),
           "max_seq_len": max_seq,
           "mean_ctx_tokens_open": round(sum(r["ctx_tokens_open"]
                                             for r in recs) / len(recs), 1),
           "max_ctx_tokens_open": max(r["ctx_tokens_open"] for r in recs),
           "prompts_cropped": sum(1 for r in recs if r["cropped"]),
           "matched_uncropped": summarise(
               [r for r in recs if not r["cropped"]], "pred"),
           "closed_book": summarise(recs, "pred_closed"),
           "matched": summarise(recs, "pred"),
           "native": summarise(recs, "pred_native"),
           "seconds": round(time.time() - t0, 1), "records": recs}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(res, open(args.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "records"},
                     indent=1))
    return 0


# ----------------------------------------------------------------- agentic

def cmd_agentic(args) -> int:
    """The model asks for its own pages and writes an answer."""
    from src.evals.interactive import (generate_with_retrieval,
                                       make_checkpoint_step_fn)
    from src.extern.bench import mmlu_block
    from src.retrieval_web.exa import ExaClient, MockExa
    from src.retrieval_web.tier import WebRetrievalTier, WebTierIndex
    from src.train.data import render_world_preamble
    from src.train.tokenizer import load_tokenizer

    rows = TASKS["mmlu"](args.root, args.n, args.seed)
    tok = load_tokenizer(args.tokenizer)
    step_fn, model, _ = make_checkpoint_step_fn(args.ckpt, args.device)
    sid = tok.special_ids
    client = CachedSearch(MockExa() if args.retriever == "mock" else ExaClient(),
                          Cache(args.cache), args.budget)

    recs, t0 = [], time.time()
    for k, row in enumerate(rows):
        tier = WebRetrievalTier(client, tok, num_results=args.num_results,
                                max_chunk_tokens=args.chunk_tokens)
        index = WebTierIndex(tier)
        body = mmlu_block(row["question"], row["choices"])
        prompt = [sid["<|world|>"]]
        prompt.extend(tok.encode(render_world_preamble({"domain": "web"})))
        prompt.append(sid["<|q|>"])
        prompt.extend(tok.encode(body))
        try:
            out = generate_with_retrieval(
                step_fn, tok, [], prompt, max_rounds=args.max_rounds,
                max_new_tokens=args.max_new_tokens, index=index,
                query_max_tokens=args.query_max_tokens)
            err = ""
        except Exception as exc:  # a live retriever can fail on one item
            out = {"rounds": [], "n_rounds": 0, "answer_text": "",
                   "stop_reason": "error", "n_generated": 0, "tokens": prompt}
            err = f"{type(exc).__name__}: {exc}"
        answer = out["answer_text"]
        pred = None
        low = answer.strip().lower()
        for i, ch in enumerate(row["choices"][:len(LETTERS)]):
            if low.startswith(LETTERS[i].lower() + ".") or low == LETTERS[i].lower():
                pred = i
        if pred is None:
            for i, ch in enumerate(row["choices"]):
                if ch.strip() and ch.strip().lower() in low:
                    pred = i
                    break
        served = " ".join(r["chunk"] for r in out["rounds"])
        recs.append({
            "id": row["id"], "subject": row["subject"], "gold": row["gold"],
            "n_choices": len(row["choices"]),
            "queries": [r["query"] for r in out["rounds"]],
            "n_rounds": out["n_rounds"],
            "served_chars": len(served),
            "contamination": label_contamination(served, row),
            "answer_text": answer, "pred": pred if pred is not None else -1,
            "stop_reason": out["stop_reason"],
            "n_generated": out.get("n_generated", 0),
            "error": err,
        })
        if (k + 1) % 10 == 0:
            el = time.time() - t0
            print(f"{k+1}/{len(rows)} {el:.0f}s "
                  f"eta {el/(k+1)*(len(rows)-k-1):.0f}s", flush=True)

    n = len(recs)
    res = {"model": f"ours:{args.tag}", "ckpt": os.path.abspath(args.ckpt),
           "task": "mmlu", "condition": "agentic_web", "n": n,
           "seed": args.seed,
           "issued_query": round(sum(r["n_rounds"] >= 1 for r in recs) / n, 4),
           "mean_rounds": round(sum(r["n_rounds"] for r in recs) / n, 3),
           "pages_entered_context": round(
               sum(r["served_chars"] > 0 for r in recs) / n, 4),
           "named_a_choice": round(sum(r["pred"] >= 0 for r in recs) / n, 4),
           "errors": sum(1 for r in recs if r["error"]),
           "live_searches": client.budget["spent"],
           "stop_reasons": {s: sum(1 for r in recs if r["stop_reason"] == s)
                            for s in {r["stop_reason"] for r in recs}},
           "acc": round(sum(r["pred"] == r["gold"] for r in recs) / n, 4),
           "floor": round(sum(1.0 / r["n_choices"] for r in recs) / n, 4),
           "by_contamination": {
               lab: cell([r for r in recs if r["contamination"] == lab])
               for lab in ("verbatim", "answer", "neither")},
           "seconds": round(time.time() - t0, 1), "records": recs}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(res, open(args.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "records"},
                     indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("score", cmd_score), ("agentic", cmd_agentic)):
        p = sub.add_parser(name)
        p.add_argument("--ckpt", required=True)
        p.add_argument("--tag", required=True)
        p.add_argument("--out", required=True)
        p.add_argument("--n", type=int, default=500)
        p.add_argument("--seed", type=int, default=1234)
        p.add_argument("--root", default="data/extern")
        p.add_argument("--tokenizer",
                       default="/home/ec2-user/data/tokenizer_v2.json")
        p.add_argument("--retriever", default="exa", choices=("exa", "mock"))
        p.add_argument("--num-results", type=int, default=5)
        p.add_argument("--chunk-tokens", type=int, default=128)
        p.add_argument("--device", default="cuda")
        p.set_defaults(fn=fn)
        if name == "score":
            p.add_argument("--max-context-chars", type=int, default=6000)
            p.add_argument("--max-chunks", type=int, default=8)
            p.add_argument("--cache", default="results/extern/exa_cache")
            p.add_argument("--budget", type=int, default=0)
            p.add_argument("--eot-prefix", action="store_true")
        else:
            p.add_argument("--max-rounds", type=int, default=4)
            p.add_argument("--max-new-tokens", type=int, default=192)
            p.add_argument("--query-max-tokens", type=int, default=24)
            p.add_argument("--cache", default="/home/ec2-user/realret/exa_cache")
            p.add_argument("--budget", type=int, default=800)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
