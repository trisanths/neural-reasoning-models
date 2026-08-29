"""Read a rungeval rows file and report the ranking behind each served page.

Three things the cell summary cannot show.

How much of the miss is the tie break. A first round is a tie loss when the
needed page holds the same score as the page that was served, to the last bit,
and lost on document index. That fraction times one minus one over the tie
group size is what a position-blind tie break can return.

What the tie break costs where it currently helps. On a step whose needed page
sits early, the gate wins its ties by position today. Those wins become coin
flips, so the cell is expected to give some back.

Whether the queries repeat. A tie broken by hashing the query is a function of
the query, so it averages over a tie group only if the queries differ. If one
query dominates a cell, the hash is a fixed choice and not a fair share.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from src.retrieval.rankdiag import wilson


def load(path: str) -> list[dict]:
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def cell_stats(rows: list[dict]) -> dict:
    first = [r["diag"][0] for r in rows if r["diag"]]
    n = len(rows)
    queries = Counter(r["queries"][0] for r in rows if r["queries"])
    tie_loss = [d for d in first if d["verdict"] == "tie_loss"]
    hits = [d for d in first if d["verdict"] == "hit"]
    tied_wins = [d for d in hits if d["tie_group"] > 1]
    # expected served rate under a position-blind tie break, holding the
    # queries the policy actually wrote fixed
    expected = 0.0
    for d in first:
        if d["verdict"] == "hit" and d["tie_group"] == 1:
            expected += 1.0
        elif d["tie_group"] > 1 and d["gold_in_tie"]:
            expected += d["gold_in_tie"] / d["tie_group"]
    lo, hi = wilson(len(hits), max(1, len(first)))
    return {
        "n_rollouts": n,
        "n_with_a_round": len(first),
        "served_gold_first_round": len(hits) / max(1, len(first)),
        "served_gold_ci95": [round(lo, 4), round(hi, 4)],
        "tie_loss": len(tie_loss) / max(1, len(first)),
        "tie_won_on_position": len(tied_wins) / max(1, len(first)),
        "mean_tie_group_when_tied": (
            sum(d["tie_group"] for d in first if d["tie_group"] > 1)
            / max(1, sum(1 for d in first if d["tie_group"] > 1))),
        "expected_served_position_blind": expected / max(1, len(first)),
        "n_distinct_first_queries": len(queries),
        "top_query_share": (queries.most_common(1)[0][1] / max(1, sum(queries.values()))
                            if queries else 0.0),
        "hedge_rate": sum(r["hedged"] for r in rows) / max(1, n),
        "accuracy": sum(r["hits_target"] for r in rows) / max(1, n),
        "accuracy_forced": sum(r["forced"] for r in rows) / max(1, n),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    rows = load(args.rows)
    by_cell: dict[tuple, list[dict]] = {}
    for r in rows:
        by_cell.setdefault((r["rung"], r["step"]), []).append(r)
    out = {}
    print(f"{'cell':12s} {'n':>4s} {'servd':>6s} {'tieL':>6s} {'tieW':>6s} "
          f"{'grp':>5s} {'pred':>6s} {'nq':>5s} {'topq':>6s} {'acc':>6s} "
          f"{'accF':>6s} {'hedge':>6s}")
    for key in sorted(by_cell):
        s = cell_stats(by_cell[key])
        out[f"{key[0]}:step{key[1]}"] = s
        print(f"{key[0]+':'+str(key[1]):12s} {s['n_rollouts']:4d} "
              f"{s['served_gold_first_round']:6.3f} {s['tie_loss']:6.3f} "
              f"{s['tie_won_on_position']:6.3f} "
              f"{s['mean_tie_group_when_tied']:5.2f} "
              f"{s['expected_served_position_blind']:6.3f} "
              f"{s['n_distinct_first_queries']:5d} {s['top_query_share']:6.3f} "
              f"{s['accuracy']:6.3f} {s['accuracy_forced']:6.3f} "
              f"{s['hedge_rate']:6.3f}")
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=1)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
