"""Real-web retrieval demo: trained checkpoints answer real factual
questions by searching the live web through the Exa tier.

The experiment wires src/evals/interactive.py's decode loop to the web
tier's WebTierIndex through the loop's injected-index parameter. Each
question renders as a training-format trace prompt, world preamble then
question, with no documents in context. The model must emit
<|retrieve|> and write its own queries; Exa results are chunked to a
token budget and served through the same BM25 ranking the training
oracle scores with. A control pass runs the same prompts with no index,
so any <|retrieve|> stops the loop unserved and the model answers, or
fails to, from its weights alone.

Two subcommands. run evaluates one checkpoint over the question file,
both passes, appending one JSON line per (pass, question) to
<out-dir>/rows-<model>.jsonl; finished rows are skipped on restart, so
the run is resumable. report merges every rows file in the directory
into a single results json with per-model accuracy, round and query
statistics, and verbatim transcripts.

The Exa api key comes from the EXA_API_KEY environment variable and is
never logged. Searches are cached on disk keyed by query, shared across
models and passes, and a hard budget on live api calls aborts the run
before the experiment can overspend.
"""

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

# The preamble uses a training domain name on purpose. A variant probe
# (scripts/diag_webdemo.py) showed the out-of-vocabulary "domain: world"
# suppresses query emission entirely for the regime E checkpoint, while a
# training-style header lets the trained retrieve habit fire; the choice
# is recorded in the results config block.
WORLD_PREAMBLE = "domain: corporate"
DEFAULT_MAX_ROUNDS = 3
DEFAULT_CHUNK_TOKENS = 512
DEFAULT_NUM_RESULTS = 5
DEFAULT_MAX_NEW_TOKENS = 160
DEFAULT_API_BUDGET = 590
CHUNK_PREVIEW_CHARS = 240


class ExaBudgetExhausted(RuntimeError):
    """Raised before a live api call would exceed the run's search budget."""


class CachingExa:
    """Disk-cached wrapper around ExaClient's search surface.

    Cache entries are keyed by (num_results, query) and shared by every
    model and round in the experiment, so a repeated query costs one live
    call total. api_calls counts only live calls; the budget is enforced
    against api_calls plus prior_calls, the live total recorded by
    earlier invocations against the same cache directory.
    """

    def __init__(self, client, cache_path: Path, budget: int,
                 prior_calls: int = 0):
        self.client = client
        self.cache_path = Path(cache_path)
        self.budget = int(budget)
        self.prior_calls = int(prior_calls)
        self.api_calls = 0
        self.cache_hits = 0
        self.cache: dict[str, list] = {}
        if self.cache_path.exists():
            with open(self.cache_path) as fh:
                self.cache = json.load(fh)

    def _save(self) -> None:
        tmp = self.cache_path.with_suffix(".tmp")
        with open(tmp, "w") as fh:
            json.dump(self.cache, fh)
        os.replace(tmp, self.cache_path)

    def search(self, query: str, num_results: int = 10,
               text: bool = True) -> list[dict]:
        key = f"{num_results}|{query}"
        if key in self.cache:
            self.cache_hits += 1
            return json.loads(json.dumps(self.cache[key]))
        if self.prior_calls + self.api_calls >= self.budget:
            raise ExaBudgetExhausted(
                f"live Exa call budget ({self.budget}) exhausted")
        results = self.client.search(query, num_results=num_results,
                                     text=text)
        self.api_calls += 1
        self.cache[key] = results
        self._save()
        return json.loads(json.dumps(results))


def load_questions(path: str) -> list[dict]:
    with open(path) as fh:
        questions = json.load(fh)
    for q in questions:
        assert q["id"] and q["question"] and q["golds"], q
    return questions


def prior_live_calls(usage_path: Path) -> int:
    total = 0
    if usage_path.exists():
        with open(usage_path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    total += json.loads(line).get("api_calls", 0)
    return total


def build_prompt(tokenizer, question: str) -> list[int]:
    sid = tokenizer.special_ids
    return [sid["<|world|>"], *tokenizer.encode(WORLD_PREAMBLE),
            sid["<|q|>"], *tokenizer.encode(question)]


def run_one(step_fn, tokenizer, question: dict, args, web_index) -> dict:
    """One (pass, question) evaluation. web_index None means the control
    pass: no serving surface, so retrieval attempts stop the loop."""
    from src.evals.interactive import generate_with_retrieval
    from src.evals.naturalized import contains_answer

    prompt = build_prompt(tokenizer, question["question"])
    start = time.monotonic()
    out = generate_with_retrieval(
        step_fn, tokenizer, [], prompt,
        max_rounds=args.max_rounds,
        max_new_tokens=args.max_new_tokens,
        seed=0,
        index=web_index)
    seconds = time.monotonic() - start

    rounds = []
    for r in out["rounds"]:
        meta = {}
        if web_index is not None:
            meta = web_index.doc_meta[r["doc_index"]]
        rounds.append({
            "query": r["query"],
            "n_query_tokens": len(tokenizer.encode(r["query"])),
            "n_query_words": len(r["query"].split()),
            "doc_index": r["doc_index"],
            "n_chunk_tokens": r["n_chunk_tokens"],
            "url": meta.get("url", ""),
            "title": meta.get("title", ""),
            "chunk": r["chunk"],
        })
    answer = out["answer_text"]
    correct = any(contains_answer(answer, g) for g in question["golds"])
    attempted = (web_index is None and out["stop_reason"] == "max_rounds")
    return {
        "qid": question["id"],
        "category": question.get("category", ""),
        "question": question["question"],
        "golds": question["golds"],
        "answer": answer,
        "correct": bool(correct),
        "stop_reason": out["stop_reason"],
        "attempted_retrieval_unserved": bool(attempted),
        "n_rounds": out["n_rounds"],
        "rounds": rounds,
        "n_generated": out["n_generated"],
        "seconds": round(seconds, 3),
    }


def cmd_run(args) -> int:
    import torch  # noqa: F401  (fails fast when the env lacks the gpu stack)

    from src.evals.interactive import make_checkpoint_step_fn
    from src.retrieval_web.exa import ExaClient
    from src.retrieval_web.tier import WebRetrievalTier, WebTierIndex
    from src.train.tokenizer import load_tokenizer

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / f"rows-{args.model_name}.jsonl"
    usage_path = out_dir / "exa-usage.jsonl"

    questions = load_questions(args.questions)
    tokenizer = load_tokenizer(args.tokenizer)

    done = set()
    if rows_path.exists():
        with open(rows_path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    row = json.loads(line)
                    done.add((row["pass"], row["qid"]))

    client = CachingExa(
        ExaClient(),
        out_dir / "exa-cache.json",
        budget=args.api_budget,
        prior_calls=prior_live_calls(usage_path),
    )

    print(f"[{args.model_name}] loading checkpoint {args.checkpoint}",
          flush=True)
    t0 = time.monotonic()
    step_fn, model, state = make_checkpoint_step_fn(args.checkpoint,
                                                    args.device)
    load_seconds = time.monotonic() - t0
    step = state.get("step")
    print(f"[{args.model_name}] step {step}, load {load_seconds:.1f}s",
          flush=True)

    budget_hit = False
    with open(rows_path, "a") as sink:
        for mode in ("none", "web"):
            for question in questions:
                if (mode, question["id"]) in done:
                    continue
                if mode == "web":
                    if budget_hit:
                        break
                    tier = WebRetrievalTier(
                        client, tokenizer,
                        max_chunk_tokens=args.chunk_tokens,
                        num_results=args.num_results)
                    web_index = WebTierIndex(tier)
                else:
                    web_index = None
                try:
                    row = run_one(step_fn, tokenizer, question, args,
                                  web_index)
                except ExaBudgetExhausted as err:
                    print(f"[{args.model_name}] {err}", flush=True)
                    budget_hit = True
                    break
                except Exception as err:  # sanitized by the client
                    row = {
                        "qid": question["id"],
                        "question": question["question"],
                        "golds": question["golds"],
                        "answer": "",
                        "correct": False,
                        "error": f"{type(err).__name__}: {err}",
                        "n_rounds": 0,
                        "rounds": [],
                        "seconds": 0.0,
                    }
                row["model"] = args.model_name
                row["pass"] = mode
                row["checkpoint_step"] = step
                sink.write(json.dumps(row) + "\n")
                sink.flush()
                mark = "+" if row["correct"] else " "
                print(f"[{args.model_name}] {mode:4s} {question['id']:8s} "
                      f"[{mark}] rounds={row['n_rounds']} "
                      f"ans={row['answer'][:48]!r}", flush=True)

    with open(usage_path, "a") as fh:
        fh.write(json.dumps({
            "model": args.model_name,
            "api_calls": client.api_calls,
            "cache_hits": client.cache_hits,
            "load_seconds": round(load_seconds, 1),
        }) + "\n")
    print(f"[{args.model_name}] live exa calls this invocation: "
          f"{client.api_calls}, cache hits: {client.cache_hits}", flush=True)
    return 1 if budget_hit else 0


def _mean(values) -> float:
    values = list(values)
    return round(statistics.fmean(values), 4) if values else 0.0


def _transcripts(web_rows: list[dict], none_by_qid: dict, limit: int = 10):
    """First successes and first failures in question order, half each,
    padded from the other side when one side runs short."""
    correct = [r for r in web_rows if r["correct"]]
    wrong = [r for r in web_rows if not r["correct"]]
    half = limit // 2
    picked = correct[:half] + wrong[:limit - len(correct[:half])]
    if len(picked) < limit:
        seen = {r["qid"] for r in picked}
        picked += [r for r in correct if r["qid"] not in seen][
            :limit - len(picked)]
    out = []
    for row in picked[:limit]:
        control = none_by_qid.get(row["qid"], {})
        out.append({
            "qid": row["qid"],
            "question": row["question"],
            "golds": row["golds"],
            "queries": [r["query"] for r in row["rounds"]],
            "served": [{
                "url": r["url"],
                "title": r["title"],
                "chunk_preview": " ".join(r["chunk"].split())[
                    :CHUNK_PREVIEW_CHARS],
            } for r in row["rounds"]],
            "answer": row["answer"],
            "correct": row["correct"],
            "stop_reason": row.get("stop_reason", ""),
            "control_answer": control.get("answer", ""),
            "control_correct": control.get("correct", False),
        })
    return out


def cmd_report(args) -> int:
    runs_dir = Path(args.runs_dir)
    models = {}
    for rows_path in sorted(runs_dir.glob("rows-*.jsonl")):
        name = rows_path.stem[len("rows-"):]
        rows = []
        with open(rows_path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        web = [r for r in rows if r["pass"] == "web"]
        none = [r for r in rows if r["pass"] == "none"]
        none_by_qid = {r["qid"]: r for r in none}
        all_rounds = [rd for r in web for rd in r["rounds"]]
        models[name] = {
            "checkpoint_step": rows[0].get("checkpoint_step") if rows else None,
            "n_questions": {"web": len(web), "none": len(none)},
            "accuracy": {
                "with_search": _mean(r["correct"] for r in web),
                "without_search": _mean(r["correct"] for r in none),
            },
            "n_correct": {
                "with_search": sum(r["correct"] for r in web),
                "without_search": sum(r["correct"] for r in none),
            },
            "mean_rounds_web": _mean(r["n_rounds"] for r in web),
            "share_web_with_any_round": _mean(
                r["n_rounds"] > 0 for r in web),
            "mean_query_tokens": _mean(
                r["n_query_tokens"] for r in all_rounds),
            "mean_query_words": _mean(
                r["n_query_words"] for r in all_rounds),
            "control_attempted_retrieval": _mean(
                r.get("attempted_retrieval_unserved", False) for r in none),
            "stop_reasons": {
                "web": _hist(r.get("stop_reason", "error") for r in web),
                "none": _hist(r.get("stop_reason", "error") for r in none),
            },
            "errors": sum(1 for r in rows if "error" in r),
            "mean_seconds": {
                "web": _mean(r["seconds"] for r in web),
                "none": _mean(r["seconds"] for r in none),
            },
            "transcripts": _transcripts(web, none_by_qid),
        }

    usage = {"api_calls": 0, "cache_hits": 0}
    usage_path = runs_dir / "exa-usage.jsonl"
    if usage_path.exists():
        with open(usage_path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    usage["api_calls"] += rec.get("api_calls", 0)
                    usage["cache_hits"] += rec.get("cache_hits", 0)

    report = {
        "experiment": "web-demo-1",
        "description": "first real-web retrieval pass: trained checkpoints "
                       "answer real factual questions through the Exa tier",
        "config": {
            "world_preamble": WORLD_PREAMBLE,
            "max_rounds": args.max_rounds,
            "chunk_tokens": args.chunk_tokens,
            "num_results": args.num_results,
            "max_new_tokens": args.max_new_tokens,
            "scoring": "contains-answer (normalized, any gold form)",
            "decode": "greedy",
        },
        "exa_usage": usage,
        "models": models,
    }
    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1)
    print(f"wrote {args.out}")
    for name, m in models.items():
        print(f"{name}: web {m['accuracy']['with_search']:.3f} "
              f"none {m['accuracy']['without_search']:.3f} "
              f"rounds {m['mean_rounds_web']:.2f}")
    return 0


def _hist(values) -> dict:
    out: dict[str, int] = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items()))


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.web_qa_demo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="evaluate one checkpoint")
    p_run.add_argument("--checkpoint", required=True)
    p_run.add_argument("--model-name", required=True)
    p_run.add_argument("--questions", required=True)
    p_run.add_argument("--out-dir", required=True)
    p_run.add_argument("--tokenizer", default=os.path.expanduser(
        "~/runs/tokenizer_v2/tokenizer_v2.json"))
    p_run.add_argument("--device", default="cuda")
    p_run.add_argument("--max-rounds", type=int, default=DEFAULT_MAX_ROUNDS)
    p_run.add_argument("--chunk-tokens", type=int,
                       default=DEFAULT_CHUNK_TOKENS)
    p_run.add_argument("--num-results", type=int,
                       default=DEFAULT_NUM_RESULTS)
    p_run.add_argument("--max-new-tokens", type=int,
                       default=DEFAULT_MAX_NEW_TOKENS)
    p_run.add_argument("--api-budget", type=int, default=DEFAULT_API_BUDGET)
    p_run.add_argument("--limit", type=int, default=0,
                       help="evaluate only the first N questions")

    p_rep = sub.add_parser("report", help="merge rows into results json")
    p_rep.add_argument("--runs-dir", required=True)
    p_rep.add_argument("--out", required=True)
    p_rep.add_argument("--max-rounds", type=int, default=DEFAULT_MAX_ROUNDS)
    p_rep.add_argument("--chunk-tokens", type=int,
                       default=DEFAULT_CHUNK_TOKENS)
    p_rep.add_argument("--num-results", type=int,
                       default=DEFAULT_NUM_RESULTS)
    p_rep.add_argument("--max-new-tokens", type=int,
                       default=DEFAULT_MAX_NEW_TOKENS)

    args = parser.parse_args()
    if args.cmd == "run":
        if args.limit:
            questions = load_questions(args.questions)[:args.limit]
            limited = Path(args.out_dir) / "questions-limited.json"
            Path(args.out_dir).mkdir(parents=True, exist_ok=True)
            with open(limited, "w") as fh:
                json.dump(questions, fh)
            args.questions = str(limited)
        return cmd_run(args)
    return cmd_report(args)


if __name__ == "__main__":
    sys.exit(main())
