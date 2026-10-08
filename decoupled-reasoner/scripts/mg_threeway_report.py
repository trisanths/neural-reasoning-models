"""Aggregate a per-rollout jsonl into cells. Nothing is ever pooled over answer source.

pass@1 is the mean over every rollout in the cell. pass@k is the fraction of
questions with at least one correct rollout among their k samples. Greedy is
one rollout per question, so its pass@1 is the greedy accuracy and its pass@k
is the same number.

Retrieval behaviour is reported beside accuracy in every cell, because on this
project the retrieval signal has repeatedly explained an accuracy number.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

GUESS_SPACE = {
    "object": lambda size: size,
    "count": lambda size: size,
    "object_list": lambda size: (2 ** size) - 1,
}


def chance(rows: list[dict]) -> float:
    """Analytic guessing floor, averaged over the questions in the cell."""
    per = {}
    for r in rows:
        size = r.get("carrier_size")
        kind = r.get("answer_kind")
        if not size or kind not in GUESS_SPACE:
            continue
        space = GUESS_SPACE[kind](int(size))
        per[(r["episode_index"], r["qid"])] = 1.0 / space if space else 0.0
    if not per:
        return float("nan")
    return sum(per.values()) / len(per)


def cell(rows: list[dict]) -> dict:
    by_q = defaultdict(list)
    for r in rows:
        by_q[(r["episode_index"], r["qid"])].append(r)
    n_q = len(by_q)
    n_r = len(rows)
    k = min(len(v) for v in by_q.values()) if by_q else 0

    def mean(field):
        return sum(float(r[field]) for r in rows) / n_r if n_r else float("nan")

    return {
        "n_questions": n_q,
        "n_rollouts": n_r,
        "samples_per_question": k,
        "pass_at_1": mean("correct"),
        "pass_at_k": (sum(1 for v in by_q.values() if any(x["correct"] for x in v))
                      / n_q) if n_q else float("nan"),
        "strict_em_pass_at_1": mean("strict_em"),
        "strict_em_pass_at_k": (sum(1 for v in by_q.values()
                                    if any(x["strict_em"] for x in v))
                                / n_q) if n_q else float("nan"),
        "mean_rounds": mean("n_rounds"),
        "any_retrieval": mean("any_retrieval"),
        "well_formed": mean("well_formed"),
        "degenerate_query_rate": (sum(1 for r in rows if r["degenerate_queries"] > 0)
                                  / n_r) if n_r else float("nan"),
        "mean_degenerate_queries": mean("degenerate_queries"),
        "mean_query_len": mean("mean_query_len"),
        "retrieved_required_chapter": mean("retrieved_required_chapter"),
        "answer_in_retrieved": mean("answer_in_retrieved"),
        "answer_in_library": mean("answer_in_library"),
        "empty_answer_rate": sum(1 for r in rows if not r["prediction"].strip()) / n_r,
        "mean_pred_tokens": mean("pred_tokens"),
        "mean_gold_tokens": mean("gold_tokens"),
        "hedge_rate": (sum(1 for r in rows
                           if r["pred_tokens"] > r["gold_tokens"]) / n_r)
        if n_r else float("nan"),
        "chance": chance(rows),
        "stop_reasons": {s: sum(1 for r in rows if r["stop_reason"] == s)
                         for s in sorted({r["stop_reason"] for r in rows})},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollouts", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--split-answer-source", action="store_true")
    args = ap.parse_args()

    rows = []
    for path in args.rollouts:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    rows.append(json.loads(line))

    groups: dict = defaultdict(list)
    for r in rows:
        base = (r["suite"], r["condition"], r["decode"])
        if args.split_answer_source:
            src = r.get("answer_source") or "unlabelled"
            groups[base + (src, "all")].append(r)
            groups[base + (src, f"level{r.get('level')}")].append(r)
        else:
            groups[base + ("n/a", "all")].append(r)

    out = {}
    for key in sorted(groups):
        out["|".join(str(k) for k in key)] = cell(groups[key])
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")

    width = max(len(k) for k in out)
    print(f"{'cell'.ljust(width)}  {'nQ':>5} {'nR':>6} {'pass@1':>7} "
          f"{'pass@k':>7} {'EMonly':>7} {'rounds':>6} {'anyret':>6} "
          f"{'wf':>6} {'degen':>6} {'reqch':>6} {'ansret':>6} {'chance':>6}")
    for key, c in out.items():
        print(f"{key.ljust(width)}  {c['n_questions']:>5} {c['n_rollouts']:>6} "
              f"{c['pass_at_1']:>7.4f} {c['pass_at_k']:>7.4f} "
              f"{c['strict_em_pass_at_1']:>7.4f} {c['mean_rounds']:>6.2f} "
              f"{c['any_retrieval']:>6.3f} {c['well_formed']:>6.3f} "
              f"{c['degenerate_query_rate']:>6.3f} "
              f"{c['retrieved_required_chapter']:>6.3f} "
              f"{c['answer_in_retrieved']:>6.3f} {c['chance']:>6.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
