"""Aggregate real-document rollouts, and decompose what went wrong.

Input is a rollouts jsonl written by `src/corpus/evalrun.py gen`, one line
per rollout, kept on disk. Aggregation is this separate pass, so a number
can be recomputed from a file that outlived the run that made it.

Accuracy is reported three ways on every cell, because they disagree and
the disagreement is informative.

  ship    the environment's own grader: normalised exact match, then a
          bounded contains fallback. This is what training optimised.
  strict  normalised exact match only. No credit for an answer that merely
          contains the gold somewhere.
  f1      token overlap with the gold, which shows a near miss.

Nothing is pooled across sources. Each source gets its own line with its
own denominator. The chance floor for a free-text answer is zero and is
stated as zero rather than omitted; for the yes/no subset of HotpotQA it is
one half and that subset is reported apart, because pooling a coin flip
with an open-ended span would flatter both.

The decomposition answers, for each rollout that got the answer wrong,
which of four things failed:

  no_query        it never emitted a retrieval round
  bad_pages       it retrieved, but no served page carries the gold answer
  truncated       a page was served and the rollout hit its length cap, so
                  the evidence may not have survived into the context
  did_not_read    a served page carries the gold answer, the rollout was not
                  truncated, and the answer is still wrong

Only the last of those is a claim about the model rather than about the
retriever or the budget.
"""

from __future__ import annotations

import argparse
import json
import math
import re

from src.evals.naturalized import contains_answer, exact_match, normalize

CONTAINS_SLACK = 6


def gold_on_page(chunk: str, gold: str) -> bool:
    if not gold:
        return False
    return re.search(rf"(?<![A-Za-z0-9]){re.escape(gold)}(?![A-Za-z0-9])",
                     chunk, re.I) is not None


def ship_correct(pred: str, gold: str) -> bool:
    """The environment's grader, restated so aggregation does not import a
    training object to grade with."""
    if exact_match(pred, gold):
        return True
    gt = normalize(gold).split()
    if len(gt) == 1 and gt[0] in ("yes", "no"):
        return False
    pt = normalize(pred).split()
    if not pt or len(pt) > len(gt) + CONTAINS_SLACK:
        return False
    return contains_answer(pred, gold)


def token_f1(pred: str, gold: str) -> float:
    p = normalize(pred).split()
    g = normalize(gold).split()
    if not p or not g:
        return 0.0
    counts: dict = {}
    for t in g:
        counts[t] = counts.get(t, 0) + 1
    hits = 0
    for t in p:
        if counts.get(t, 0) > 0:
            counts[t] -= 1
            hits += 1
    if not hits:
        return 0.0
    prec, rec = hits / len(p), hits / len(g)
    return 2 * prec * rec / (prec + rec)


def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - s) / d, 4), round((c + s) / d, 4))


def cell(rolls: list[dict], floor: float) -> dict:
    n = len(rolls)
    if not n:
        return {}
    ship = sum(r["_ship"] for r in rolls)
    strict = sum(r["_strict"] for r in rolls)
    served = sum(r["_gold_served"] for r in rolls)
    issued = sum(r["n_rounds"] >= 1 for r in rolls)
    trunc = sum(r["stop_reason"] in ("max_len", "max_new_tokens")
                for r in rolls)
    wrong = [r for r in rolls if not r["_ship"]]
    decomp = {"no_query": 0, "bad_pages": 0, "truncated": 0, "did_not_read": 0}
    for r in wrong:
        if r["n_rounds"] == 0:
            decomp["no_query"] += 1
        elif not r["_gold_served"]:
            decomp["bad_pages"] += 1
        elif r["stop_reason"] in ("max_len", "max_new_tokens"):
            decomp["truncated"] += 1
        else:
            decomp["did_not_read"] += 1
    read_given_served = [r for r in rolls if r["_gold_served"]]
    return {
        "n": n, "floor": floor,
        "ship": round(ship / n, 4), "ship_ci": wilson(ship, n),
        "strict": round(strict / n, 4), "strict_ci": wilson(strict, n),
        "f1": round(sum(r["_f1"] for r in rolls) / n, 4),
        "issued_query": round(issued / n, 4),
        "mean_rounds": round(sum(r["n_rounds"] for r in rolls) / n, 3),
        "gold_page_served": round(served / n, 4),
        "hit_a_cap": round(trunc / n, 4),
        "ship_given_gold_served": (
            round(sum(r["_ship"] for r in read_given_served)
                  / len(read_given_served), 4) if read_given_served else None),
        "n_gold_served": len(read_given_served),
        "well_formed": round(sum(bool(r.get("well_formed"))
                                 for r in rolls) / n, 4),
        "empty_answer": round(sum(not str(r.get("answer", "")).strip()
                                  for r in rolls) / n, 4),
        "wrong": len(wrong), "decomposition": decomp,
        "stop_reasons": {s: sum(1 for r in rolls if r["stop_reason"] == s)
                         for s in sorted({r["stop_reason"] for r in rolls})},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollouts", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--episodes", nargs="*", default=[],
                    help="episode files, to recover the per-rollout source")
    a = ap.parse_args()

    src_of: dict = {}
    yes_no: dict = {}
    for path in a.episodes:
        with open(path) as fh:
            for line in fh:
                ep = json.loads(line)
                for q in ep.get("questions", []):
                    src_of[q.get("qid")] = ep.get("source", "?")
                    yes_no[q.get("qid")] = bool(ep.get("yesno"))

    rolls: list[dict] = []
    for path in a.rollouts:
        with open(path) as fh:
            for line in fh:
                r = json.loads(line)
                gold = str(r.get("gold", ""))
                pred = str(r.get("answer", ""))
                chunks = r.get("chunks") or []
                r["_ship"] = ship_correct(pred, gold)
                r["_strict"] = bool(exact_match(pred, gold))
                r["_f1"] = token_f1(pred, gold)
                r["_gold_served"] = any(gold_on_page(c, gold) for c in chunks)
                r["_source"] = src_of.get(r.get("qid"), r.get("source", "?"))
                r["_yesno"] = yes_no.get(r.get("qid"), False)
                r["_file"] = path
                rolls.append(r)

    out: dict = {"rollout_files": a.rollouts, "n_rollouts": len(rolls),
                 "cells": {}}
    decodes = sorted({r.get("decode", "greedy") for r in rolls})
    sources = sorted({r["_source"] for r in rolls})
    for dec in decodes:
        for src in sources:
            sel = [r for r in rolls
                   if r.get("decode", "greedy") == dec and r["_source"] == src]
            if not sel:
                continue
            open_ended = [r for r in sel if not r["_yesno"]]
            binary = [r for r in sel if r["_yesno"]]
            if open_ended:
                out["cells"][f"{src}|{dec}|open"] = cell(open_ended, 0.0)
            if binary:
                out["cells"][f"{src}|{dec}|yesno"] = cell(binary, 0.5)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out, indent=1)[:9000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
