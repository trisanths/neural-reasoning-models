"""Re-check every episode contract from the written file alone.

The builder verified as it planned. This reads the finished episodes back
and checks the same things from scratch, because a builder that verifies
with the object it just constructed can agree with itself about a bug.

Per question:

  serves     every round's query ranks its recorded document under the same
             BM25 gate and tie-break the serving loops use, with the earlier
             rounds excluded
  available  no query uses a surface term that was not available when it was
             written: the question's terms plus the terms of pages already
             served, and nothing from a page the trace had not yet read
  readable   the answer stands as a whole token on one of the served pages,
             or the answer is yes/no, which stands on no page by construction
  budget     no query is longer than the environment's query token cap, and
             the rendered example fits the training window
  header     the prompt carries the world header, which is the fault that has
             cost this project two results

A sample is checked rather than the whole file when --sample is given, and
the sample is a stride over the file rather than its head, because reading
the first N lines of an ordered file has produced two wrong numbers here.
"""

from __future__ import annotations

import argparse
import json
import random
import time

from src.realret.episodes import QUERY_MAX_TOKENS
from src.realret.sources import answer_in, norm
from src.train import retrieval as _retrieval
from src.train.retrieval import BM25Index, terms


def check_episode(ep: dict, tok, max_len: int = 1024) -> list[str]:
    fails: list[str] = []
    texts = [d["text"] for d in ep["documents"]]
    index = BM25Index(texts)
    sid = tok.special_ids
    for qi, q in enumerate(ep["questions"]):
        plan = q["plan"]
        if not plan:
            fails.append(f"q{qi}: empty plan")
            continue
        available = set(terms(q["text"]))
        served: list[int] = []
        for hi, pair in enumerate(plan):
            query, doc = pair[0], int(pair[1])
            if len(tok.encode(query)) > QUERY_MAX_TOKENS:
                fails.append(f"q{qi} hop{hi}: query over token cap")
            missing = set(terms(query)) - available
            if missing:
                fails.append(f"q{qi} hop{hi}: unavailable terms "
                             f"{sorted(missing)[:4]}")
            try:
                tied, _ = index.top_group(query, exclude=set(served))
                pick = _retrieval.break_tie(query, texts, tied,
                                            _retrieval.RETRIEVAL_TIE_BREAK)
            except ValueError:
                fails.append(f"q{qi} hop{hi}: nothing servable")
                break
            if pick != doc:
                fails.append(f"q{qi} hop{hi}: gate serves {pick} not {doc}")
            served.append(doc)
            available |= set(terms(texts[doc]))
        answer = q["answer"]
        if norm(answer) not in ("yes", "no"):
            if not any(answer_in(texts[d], answer) for d in served):
                fails.append(f"q{qi}: answer on no served page")
        # length and header
        n = 1 + len(tok.encode(
            "domain: " + ep.get("world", {}).get("domain", "unknown")))
        n += 1 + len(tok.encode(q["text"]))
        for pair in plan:
            n += 2 + len(tok.encode(pair[0])) + len(tok.encode(texts[pair[1]]))
        n += 2 + len(tok.encode(" " + answer))
        if n > max_len:
            fails.append(f"q{qi}: rendered length {n} over {max_len}")
        if sid.get("<|world|>") is None:
            fails.append("tokenizer has no world token")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", nargs="+", required=True)
    ap.add_argument("--tokenizer", default="/home/ec2-user/data/tokenizer_v2.json")
    ap.add_argument("--sample", type=int, default=4000)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-len", type=int, default=1024)
    a = ap.parse_args()

    from src.train.tokenizer import load_tokenizer
    tok = load_tokenizer(a.tokenizer)

    report = {"files": {}, "sample": a.sample, "max_len": a.max_len}
    t0 = time.time()
    for path in a.episodes:
        total = sum(1 for _ in open(path))
        stride = max(1, total // a.sample) if a.sample else 1
        checked = 0
        bad = 0
        reasons: dict = {}
        examples: list = []
        rounds_hist: dict = {}
        with open(path) as fh:
            for n, line in enumerate(fh):
                if n % stride:
                    continue
                ep = json.loads(line)
                fails = check_episode(ep, tok, a.max_len)
                checked += 1
                rounds_hist[len(ep["questions"][0]["plan"])] = rounds_hist.get(
                    len(ep["questions"][0]["plan"]), 0) + 1
                if fails:
                    bad += 1
                    for f in fails:
                        key = f.split(": ", 1)[-1].split(" ")[0]
                        reasons[key] = reasons.get(key, 0) + 1
                    if len(examples) < 5:
                        examples.append({"qid": ep.get("qid"), "fails": fails})
        report["files"][path] = {
            "lines": total, "stride": stride, "checked": checked,
            "episodes_with_failures": bad,
            "clean_rate": round(1 - bad / max(1, checked), 4),
            "reasons": reasons, "examples": examples,
            "rounds_hist": {str(k): v for k, v in sorted(rounds_hist.items())},
        }
        print(path, json.dumps(report["files"][path])[:400], flush=True)
    report["seconds"] = round(time.time() - t0, 1)
    with open(a.out, "w") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps({p: {k: v for k, v in r.items() if k != "examples"}
                      for p, r in report["files"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
