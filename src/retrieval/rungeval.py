"""Instrumented re-run of the E0 gold-key rungs, for retrieval measurement.

`src/disc/rekey.py` reports one served-page histogram per cell. That is not
enough to tell a page the retriever ranked low from a page it ranked joint
first and dropped on document index. This driver rolls the same rungs out the
same way and keeps every query, so the ranking behind each served page can be
recomputed afterwards.

It reproduces `rekey.run_rung` for the gold-key rungs by reusing that module's
own page sets, prompts, seeds and graders. The reproduction is checked against
the recorded cells rather than assumed: run it once before any retrieval change
and the pass@1 must match `rescue_full.json` and `rescue_order.json`.

Both graders travel together on every row. hits_target is the rule the
environment trains against, which accepts an answer containing the gold. forced
is the single-choice rule: the answer names exactly one token of the episode's
universe and that token is the gold one. The hedge rate is the fraction naming
more than one, which is the only thing that can separate them.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from src.disc.minrepro import hits_target
from src.disc.rekey import (RUNGS, SUB_Q, _pages_for, _task, extract_token,
                            load_problems, named_tokens)
from src.retrieval.rankdiag import diagnose, summarise, wilson
from src.train.retrieval import BM25Index

GOLD_KEY_RUNGS = ("r1", "r1w", "r1o")


def gold_page_index(rung: str, step: int) -> int:
    """Where the table this step needs sits in the page set the step sees."""
    return step + 1 if rung == "r1w" else 1


def _index_for(docs: list[dict]) -> BM25Index:
    return BM25Index([d["text"] for d in docs],
                     reliabilities=[float(d.get("reliability", 1.0))
                                    for d in docs])


def run_rung(model, tok, device, problems, rung, *, samples, temperature,
             batch, max_len, max_rounds, max_new_tokens, seed,
             max_prompt_tokens):
    from src.rl.env import EnvConfig, EpisodeEnv
    from src.rl.sampler import CachedPolicy

    if rung not in GOLD_KEY_RUNGS:
        raise SystemExit(f"{rung} is not a gold-key rung")
    env = EpisodeEnv(tok, EnvConfig(max_rounds=max_rounds,
                                    max_new_tokens=max_new_tokens,
                                    max_len=max_len))
    depth = problems[0]["depth"]
    chains = [(p, s) for p in problems for s in range(samples)]
    step_ok = [[] for _ in chains]
    step_strict = [[] for _ in chains]
    per_step = []
    rows = []

    for step in range(depth):
        tasks, golds, live = [], [], []
        for ci, (p, sample) in enumerate(chains):
            key = p["stages"][step]
            qtext = SUB_Q.format(key=key, office=p["chain"][step])
            gold = p["stages"][step + 1]
            docs = _pages_for(p, rung, step)
            t = _task(p, qtext, gold, docs, tok)
            if len(t.prompt) > max_prompt_tokens:
                continue
            tasks.append(t)
            golds.append(gold)
            live.append(ci)

        policy = CachedPolicy(model, device, max_len=max_len,
                              temperature=temperature,
                              seed=seed + 1009 * step + 7 * RUNGS.index(rung))
        rolls = []
        for i in range(0, len(tasks), batch):
            rolls.extend(env.rollout(policy, tasks[i:i + batch]))

        gp = gold_page_index(rung, step)
        served_hist = Counter()
        diags = []
        ok_n = strict_n = hedged_n = 0
        with_gold = [0, 0]
        without_gold = [0, 0]
        for ci, t, r, gold in zip(live, tasks, rolls, golds):
            p = chains[ci][0]
            ok = hits_target(r.answer_text, gold)
            named = named_tokens(r.answer_text, p["alphabet"])
            strict = len(named) == 1 and named[0] == gold
            hedged = len(named) > 1
            ok_n += int(ok)
            strict_n += int(strict)
            hedged_n += int(hedged)
            step_ok[ci].append(ok)
            step_strict[ci].append(strict)
            served = [x["doc_index"] for x in r.rounds]
            for s in served:
                served_hist[s] += 1
            bucket = with_gold if gp in served else without_gold
            bucket[0] += 1
            bucket[1] += int(ok)

            index = _index_for(t.documents)
            seen: list[int] = []
            per_round = []
            for x in r.rounds:
                d = diagnose(index, x["query"], {gp}, exclude=set(seen))
                d["round"] = len(per_round)
                per_round.append(d)
                seen.append(x["doc_index"])
            if per_round:
                diags.append(per_round[0])
            rows.append({
                "rung": rung, "step": step, "qid": p["qid"],
                "episode_index": p["episode_index"], "sample": chains[ci][1],
                "gold": gold, "gold_page": gp, "n_docs": len(t.documents),
                "answer": r.answer_text, "hits_target": ok, "forced": strict,
                "hedged": hedged, "n_rounds": len(r.rounds),
                "stop": r.stop_reason,
                "queries": [x["query"] for x in r.rounds],
                "served": served,
                "diag": per_round,
            })

        n = len(rolls)
        hits = sum(1 for d in diags if d["verdict"] == "hit")
        lo, hi = wilson(hits, max(1, len(diags)))
        per_step.append({
            "step": step, "n": n, "gold_page": gp,
            "step_accuracy": ok_n / max(1, n),
            "step_accuracy_forced": strict_n / max(1, n),
            "hedge_rate": hedged_n / max(1, n),
            "served_pages": dict(served_hist),
            "served_gold_page": with_gold[0] / max(1, n),
            "acc_given_gold_page": with_gold[1] / max(1, with_gold[0]),
            "n_given_gold_page": with_gold[0],
            "acc_without_gold_page": without_gold[1] / max(1, without_gold[0]),
            "n_without_gold_page": without_gold[0],
            "first_round_ranking": summarise(diags),
            "first_round_hit_ci95": [round(lo, 4), round(hi, 4)],
        })

    n_roll = len(chains)
    chain_ok = [len(v) == depth and all(v) for v in step_ok]
    chain_f = [len(v) == depth and all(v) for v in step_strict]
    by_q, by_q_f = {}, {}
    for (p, _), c, cf in zip(chains, chain_ok, chain_f):
        by_q.setdefault((p["episode_index"], p["qid"]), []).append(c)
        by_q_f.setdefault((p["episode_index"], p["qid"]), []).append(cf)
    alpha = len(chains[0][0]["alphabet"])
    lo, hi = wilson(sum(chain_ok), n_roll)
    lof, hif = wilson(sum(chain_f), n_roll)
    return {
        "rung": rung, "depth": depth, "n_chains": n_roll,
        "n_questions": len(by_q), "samples": samples,
        "chain_pass_at_1": sum(chain_ok) / max(1, n_roll),
        "chain_pass_at_1_ci95": [round(lo, 4), round(hi, 4)],
        "chain_pass_at_k": sum(any(v) for v in by_q.values()) / max(1, len(by_q)),
        "chain_pass_at_1_forced": sum(chain_f) / max(1, n_roll),
        "chain_pass_at_1_forced_ci95": [round(lof, 4), round(hif, 4)],
        "chain_pass_at_k_forced": sum(any(v) for v in by_q_f.values())
        / max(1, len(by_q_f)),
        "chance_per_step": 1.0 / max(1, alpha),
        "chance_per_chain": (1.0 / max(1, alpha)) ** depth,
        "per_step": per_step,
    }, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", required=True)
    ap.add_argument("--rungs", default="r1w,r1o,r1")
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--tokenizer", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows-out", default="")
    ap.add_argument("--tag", default="before")
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--max-prompt-tokens", type=int, default=800)
    ap.add_argument("--max-rounds", type=int, default=6)
    ap.add_argument("--max-new-tokens", type=int, default=96)
    ap.add_argument("--seed", type=int, default=99)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tie-break", default="",
                    help="override src.rl.env.RETRIEVAL_TIE_BREAK for this run")
    args = ap.parse_args()

    problems = load_problems(args.episodes)
    if args.limit:
        problems = problems[: args.limit]
    from src.train import retrieval as retrieval_mod
    if args.tie_break:
        retrieval_mod.RETRIEVAL_TIE_BREAK = args.tie_break
    from src.disc.minrepro import load_policy_parts
    model, tok, device = load_policy_parts(args.checkpoint, args.tokenizer)

    report = {"tag": args.tag, "episodes_path": args.episodes,
              "tie_break": retrieval_mod.RETRIEVAL_TIE_BREAK, "cells": [],
              "config": {"samples": args.samples, "seed": args.seed,
                         "temperature": args.temperature,
                         "max_rounds": args.max_rounds,
                         "max_new_tokens": args.max_new_tokens}}
    rows_fh = open(args.rows_out, "w") if args.rows_out else None
    for rung in args.rungs.split(","):
        cell, rows = run_rung(model, tok, device, problems, rung,
                              samples=args.samples,
                              temperature=args.temperature, batch=args.batch,
                              max_len=args.max_len,
                              max_rounds=args.max_rounds,
                              max_new_tokens=args.max_new_tokens,
                              seed=args.seed,
                              max_prompt_tokens=args.max_prompt_tokens)
        cell["episodes_path"] = args.episodes
        cell["tie_break"] = retrieval_mod.RETRIEVAL_TIE_BREAK
        report["cells"].append(cell)
        print(json.dumps(cell), flush=True)
        if rows_fh:
            for r in rows:
                rows_fh.write(json.dumps(r) + "\n")
            rows_fh.flush()
        with open(args.out, "w") as fh:
            json.dump(report, fh, indent=1)
    if rows_fh:
        rows_fh.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
