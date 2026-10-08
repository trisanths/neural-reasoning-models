"""Static rank diagnosis of the retrieval gate on the E0 rescue page sets.

No model runs here. The page sets are rebuilt exactly as `src/disc/rekey.py`
builds them, the index is built exactly as `src/rl/env.make_service` builds it,
and every query is one the harness itself can issue without sampling:

  subq      the sub-question text the rung hands the model, which is also the
            query the `keyword_nearest` baseline on record issues;
  shared    a query drawn only from vocabulary every page of the set holds,
            which is the limiting case the recorded traces sit near;
  goldterm  each term unique to the needed page, one at a time, which measures
            whether the page is reachable at all.

Writes one json of per-cell rows and prints a summary.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from src.disc.rekey import SUB_Q, WIDE_PAGES, load_problems
from src.retrieval.rankdiag import diagnose, score_vector, summarise, wilson
from src.train.retrieval import BM25Index, norm_terms


def pages_for(problem: dict, rung: str, step: int) -> tuple[list[dict], int]:
    """The page set one sub-question sees and the index of the needed page.

    Mirrors `src/disc/rekey._pages_for`. Returned alongside it is the position
    the needed table lands at, which is the quantity R1o moves.
    """
    docs = problem["docs"]
    if rung == "r1o":
        return ([docs[0], docs[step + 1]]
                + [docs[j + 1] for j in range(len(problem["chain"]))
                   if j != step], 1)
    if rung in WIDE_PAGES:
        return docs, step + 1
    return [docs[0], docs[step + 1]], 1


def make_index(docs: list[dict]) -> BM25Index:
    """Index a page set the way the environment does."""
    return BM25Index([d["text"] for d in docs],
                     reliabilities=[float(d.get("reliability", 1.0))
                                    for d in docs])


def shared_vocab(docs: list[dict]) -> list[str]:
    """Normalized terms every page in the set holds."""
    sets = [set(norm_terms(d["text"])) for d in docs]
    common = set.intersection(*sets) if sets else set()
    return sorted(common)


def unique_terms(docs: list[dict], gold: int) -> list[str]:
    """Normalized terms the needed page holds and no other page holds."""
    mine = set(norm_terms(docs[gold]["text"]))
    for i, d in enumerate(docs):
        if i != gold:
            mine -= set(norm_terms(d["text"]))
    return sorted(mine)


def run(path: str, rungs: list[str], out_path: str) -> dict:
    problems = load_problems(path)
    cells: dict[str, dict] = {}
    examples: list[dict] = []
    for rung in rungs:
        depth = problems[0]["depth"]
        for step in range(depth):
            rows_subq: list[dict] = []
            rows_shared: list[dict] = []
            reach = Counter()
            positions = Counter()
            for p in problems:
                docs, gold = pages_for(p, rung, step)
                index = make_index(docs)
                positions[gold] += 1
                key = p["stages"][step]
                qtext = SUB_Q.format(key=key, office=p["chain"][step])
                rows_subq.append(diagnose(index, qtext, {gold}))
                common = shared_vocab(docs)
                rows_shared.append(
                    diagnose(index, " ".join(common), {gold}))
                for term in unique_terms(docs, gold):
                    d = diagnose(index, term, {gold})
                    reach["hit" if d["verdict"] == "hit" else "miss"] += 1
                if len(examples) < 3 and step == depth - 1:
                    sv = score_vector(index, qtext)
                    examples.append({
                        "rung": rung, "step": step, "qid": p["qid"],
                        "query": qtext, "gold_index": gold,
                        "scores": [round(s, 6) for s in sv],
                        "doc_heads": [d["text"][:44] for d in docs],
                    })
            cell = f"{rung}:step{step}"
            n = len(rows_subq)
            hits = sum(1 for r in rows_subq if r["verdict"] == "hit")
            lo, hi = wilson(hits, n)
            cells[cell] = {
                "rung": rung, "step": step, "n_questions": n,
                "gold_position": dict(positions),
                "subq": summarise(rows_subq),
                "subq_hit_ci95": [round(lo, 4), round(hi, 4)],
                "shared_only_query": summarise(rows_shared),
                "unique_term_reach": {
                    "n": sum(reach.values()),
                    "hit": reach["hit"] / max(1, sum(reach.values())),
                },
            }
    result = {"episodes_path": path, "rungs": rungs, "cells": cells,
              "examples": examples}
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=1)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", required=True)
    ap.add_argument("--rungs", default="r1,r1w,r1o")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    res = run(args.episodes, args.rungs.split(","), args.out)
    print(f"{'cell':14s} {'n':>4s} {'goldpos':>10s} {'subq@1':>7s} "
          f"{'tie':>6s} {'score':>6s} {'tieshr':>7s} {'rank':>5s} "
          f"{'tiegrp':>6s} {'shared@1':>8s} {'uniqreach':>9s}")
    for name, c in res["cells"].items():
        s, sh = c["subq"], c["shared_only_query"]
        pos = ",".join(f"{k}x{v}" for k, v in sorted(c["gold_position"].items()))
        print(f"{name:14s} {c['n_questions']:4d} {pos:>10s} "
              f"{s['hit_at_1']:7.3f} {s['tie_loss']:6.3f} "
              f"{s['score_loss']:6.3f} {s['tie_share_of_misses']:7.3f} "
              f"{(s['mean_gold_rank'] or 0):5.2f} "
              f"{(s['mean_tie_group'] or 0):6.2f} {sh['hit_at_1']:8.3f} "
              f"{c['unique_term_reach']['hit']:9.3f}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
