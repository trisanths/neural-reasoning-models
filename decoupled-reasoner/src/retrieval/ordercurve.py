"""The depth curve with the page order permuted, and nothing else moved.

R0 is the depth-d question exactly as generated, against the minimal page set:
the preamble, then one routing table per office in chain order. The order is
what `minimal_pages` chose and it has never been varied, so the published curve
cannot say whether a zero at depth two is composition failing or the table the
second step needs sitting behind the table the first step needs.

This driver varies that one thing. The question text is untouched, which
matters: a control on this lane that appended a sentence asking for nothing
collapsed retrieval rounds from 0.98 to 0.01, so anything that works by adding
words to the question is untestable on this checkpoint.

Arms, all with the preamble held at position zero:

  chain      the order on record, table i at position i+1;
  reverse    the tables reversed, so the last step's table sits at position 1;
  goldfirst  only the table holding the final answer moved to position 1, the
             rest left in chain order, which is R1o's manipulation applied to
             R0 instead of to a re-keyed sub-question;
  randN      the tables shuffled by seed N.

Every arm runs the same questions, the same sampler seed and the same grader,
so a difference between arms is page order and nothing else. The tie break is
pinned per run and recorded in the report, because a position-blind tie break
would move these arms too and the two effects must not be measured together.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter

from src.disc.minrepro import classify, hits_target
from src.disc.rekey import load_problems, named_tokens
from src.retrieval.rankdiag import diagnose, summarise, wilson
from src.train.retrieval import BM25Index


def permute(docs: list[dict], order: str) -> list[dict]:
    """Reorder the tables, holding the preamble at position zero."""
    head, tables = docs[0], list(docs[1:])
    if order == "chain":
        pass
    elif order == "reverse":
        tables = tables[::-1]
    elif order == "goldfirst":
        tables = [tables[-1]] + tables[:-1]
    elif order.startswith("rand"):
        random.Random(int(order[4:])).shuffle(tables)
    else:
        raise SystemExit(f"unknown order {order!r}")
    return [head] + tables


def gold_positions(docs: list[dict], permuted: list[dict]) -> list[int]:
    """Where each chain table landed, in chain order."""
    pos = {id(d): i for i, d in enumerate(permuted)}
    return [pos[id(d)] for d in docs[1:]]


def run_cell(model, tok, device, problems, order, *, samples, temperature,
             batch, max_len, max_rounds, max_new_tokens, seed,
             max_prompt_tokens):
    from src.rl.env import EnvConfig, EpisodeEnv, Task, build_prompt
    from src.rl.sampler import CachedPolicy

    env = EpisodeEnv(tok, EnvConfig(max_rounds=max_rounds,
                                    max_new_tokens=max_new_tokens,
                                    max_len=max_len))
    depth = problems[0]["depth"]
    tasks, metas = [], []
    dropped = 0
    for p in problems:
        docs = permute(p["docs"], order)
        positions = gold_positions(p["docs"], docs)
        episode = {"world": p["world"], "documents": docs, "n_context": 0}
        prompt = build_prompt(episode, {"text": p["text"]}, tok)
        if len(prompt) > max_prompt_tokens:
            dropped += 1
            continue
        t = Task(episode_index=p["episode_index"], qid=p["qid"],
                 question=p["text"], gold=p["answer"], prompt=prompt,
                 documents=docs, domain=p["world"].get("domain", "unknown"),
                 hops=depth)
        for s in range(samples):
            tasks.append(t)
            metas.append((p, positions, s))

    policy = CachedPolicy(model, device, max_len=max_len,
                          temperature=temperature, seed=seed)
    rolls = []
    for i in range(0, len(tasks), batch):
        rolls.extend(env.rollout(policy, tasks[i:i + batch]))

    n = len(rolls)
    ok_n = strict_n = hedged_n = 0
    rounds_total = 0
    any_ret = 0
    served_by_step = Counter()
    served_preamble = 0
    kinds = Counter()
    by_q, by_q_f = {}, {}
    diags = []
    rows = []
    final_page_served = [0, 0]
    for (p, positions, sample), t, r in zip(metas, tasks, rolls):
        ok = hits_target(r.answer_text, p["answer"])
        named = named_tokens(r.answer_text, p["alphabet"])
        strict = len(named) == 1 and named[0] == p["answer"]
        ok_n += int(ok)
        strict_n += int(strict)
        hedged_n += int(len(named) > 1)
        kinds[classify(r.answer_text, p, p["alphabet"])] += 1
        rounds_total += len(r.rounds)
        any_ret += int(bool(r.rounds))
        served = [x["doc_index"] for x in r.rounds]
        for s in served:
            if s == 0:
                served_preamble += 1
            elif s in positions:
                served_by_step[positions.index(s)] += 1
        gp = positions[-1]
        final_page_served[0] += int(gp in served)
        final_page_served[1] += int(gp in served and ok)
        key = (p["episode_index"], p["qid"])
        by_q.setdefault(key, []).append(ok)
        by_q_f.setdefault(key, []).append(strict)
        index = BM25Index([d["text"] for d in t.documents])
        per_round = []
        seen = []
        for x in r.rounds:
            per_round.append(diagnose(index, x["query"], {gp},
                                      exclude=set(seen)))
            seen.append(x["doc_index"])
        if per_round:
            diags.append(per_round[0])
        rows.append({
            "order": order, "depth": depth, "qid": p["qid"],
            "episode_index": p["episode_index"], "sample": sample,
            "gold": p["answer"], "final_page": gp,
            "table_positions": positions, "answer": r.answer_text,
            "hits_target": ok, "forced": strict, "hedged": len(named) > 1,
            "n_rounds": len(r.rounds), "stop": r.stop_reason,
            "queries": [x["query"] for x in r.rounds], "served": served,
            "diag": per_round,
        })
    alpha = len(problems[0]["alphabet"])
    lo, hi = wilson(ok_n, max(1, n))
    lof, hif = wilson(strict_n, max(1, n))
    return {
        "order": order, "depth": depth, "n_rollouts": n,
        "n_questions": len(by_q), "samples": samples,
        "dropped_long_prompts": dropped,
        "pass_at_1": ok_n / max(1, n),
        "pass_at_1_ci95": [round(lo, 4), round(hi, 4)],
        "pass_at_1_forced": strict_n / max(1, n),
        "pass_at_1_forced_ci95": [round(lof, 4), round(hif, 4)],
        "hedge_rate": hedged_n / max(1, n),
        "pass_at_k": sum(any(v) for v in by_q.values()) / max(1, len(by_q)),
        "pass_at_k_forced": sum(any(v) for v in by_q_f.values())
        / max(1, len(by_q_f)),
        "chance_per_step": 1.0 / max(1, alpha),
        "chance_per_chain": (1.0 / max(1, alpha)) ** depth,
        "mean_rounds": rounds_total / max(1, n),
        "any_retrieval": any_ret / max(1, n),
        "served_preamble": served_preamble / max(1, n),
        "served_table_by_chain_step": {str(k): v / max(1, n)
                                       for k, v in sorted(served_by_step.items())},
        "served_final_table": final_page_served[0] / max(1, n),
        "acc_given_final_table": final_page_served[1]
        / max(1, final_page_served[0]),
        "n_given_final_table": final_page_served[0],
        "answer_classes": {k: v / max(1, n) for k, v in kinds.items()},
        "first_round_ranking_final_table": summarise(diags),
    }, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", required=True, help="comma separated")
    ap.add_argument("--orders", default="chain,reverse,goldfirst")
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--tokenizer", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows-out", default="")
    ap.add_argument("--tie-break", default="first")
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--max-prompt-tokens", type=int, default=800)
    ap.add_argument("--max-rounds", type=int, default=6)
    ap.add_argument("--max-new-tokens", type=int, default=96)
    ap.add_argument("--seed", type=int, default=99)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    from src.train import retrieval as retrieval_mod
    retrieval_mod.RETRIEVAL_TIE_BREAK = args.tie_break
    from src.disc.minrepro import load_policy_parts
    model, tok, device = load_policy_parts(args.checkpoint, args.tokenizer)

    report = {"tie_break": args.tie_break, "orders": args.orders.split(","),
              "cells": [], "config": {"samples": args.samples,
                                      "seed": args.seed,
                                      "temperature": args.temperature,
                                      "max_rounds": args.max_rounds}}
    rows_fh = open(args.rows_out, "w") if args.rows_out else None
    for path in args.episodes.split(","):
        problems = load_problems(path)
        if args.limit:
            problems = problems[: args.limit]
        for order in args.orders.split(","):
            cell, rows = run_cell(model, tok, device, problems, order,
                                  samples=args.samples,
                                  temperature=args.temperature,
                                  batch=args.batch, max_len=args.max_len,
                                  max_rounds=args.max_rounds,
                                  max_new_tokens=args.max_new_tokens,
                                  seed=args.seed,
                                  max_prompt_tokens=args.max_prompt_tokens)
            cell["episodes_path"] = path
            cell["tie_break"] = args.tie_break
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
