"""What the tie break does to a page set, for any minimal-repro episodes file.

The E0 ladder's wide condition and the depth curve's six-page condition are
built by different code paths and only one of them orders its pages. This tool
takes either and reports, per question:

  the size of the group BM25 leaves exactly level at the top,
  where the needed page sits in that group,
  what a position-blind tie break would serve instead.

Queries come from a rows file written by `src/retrieval/rungeval.py`, so they
are queries this checkpoint actually wrote on this family and surface form.
They are transferred across page sets, which is sound only because the policy's
queries carry almost no information about the question; each transferred query
is applied to every page set and the result is a distribution, not a per
question claim.
"""

from __future__ import annotations

import argparse
import json
import random
import re

from src.retrieval.rankdiag import diagnose, summarise
from src.train.retrieval import BM25Index

TABLE_HEAD = re.compile(r"^The (\w+) routing table\.")


def gold_pages(docs: list[dict], offices: list[str]) -> set[int]:
    """Indices of the tables the chain needs, wherever they were shuffled to."""
    want = set(offices)
    out = set()
    for i, d in enumerate(docs):
        m = TABLE_HEAD.match(d["text"])
        if m and m.group(1) in want:
            out.add(i)
    return out


def load_queries(rows_path: str, limit: int) -> list[str]:
    qs = []
    with open(rows_path) as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("queries"):
                qs.append(r["queries"][0])
    random.Random(0).shuffle(qs)
    return qs[:limit]


def run(path: str, queries: list[str], final_only: bool) -> dict:
    rows = []
    tie_sizes = []
    n_pages = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            ep = json.loads(line)
            docs = ep["documents"]
            index = BM25Index([d["text"] for d in docs],
                              reliabilities=[float(d.get("reliability", 1.0))
                                             for d in docs])
            n_pages.append(len(docs))
            for q in ep["questions"]:
                chain = q["chain"]
                offices = [chain[-1]] if final_only else chain
                gold = gold_pages(docs, offices)
                if not gold:
                    continue
                for query in queries:
                    d = diagnose(index, query, gold)
                    rows.append(d)
                    tie_sizes.append(d["tie_group"])
    expected = 0.0
    for d in rows:
        if d["verdict"] == "hit" and d["tie_group"] == 1:
            expected += 1.0
        elif d["tie_group"] > 1 and d["gold_in_tie"]:
            expected += d["gold_in_tie"] / d["tie_group"]
    summary = summarise(rows)
    summary["expected_served_position_blind"] = expected / max(1, len(rows))
    summary["mean_pages"] = sum(n_pages) / max(1, len(n_pages))
    summary["mean_tie_group_all"] = sum(tie_sizes) / max(1, len(tie_sizes))
    summary["tied_at_all"] = sum(1 for t in tie_sizes if t > 1) / max(1, len(tie_sizes))
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", required=True, help="comma separated")
    ap.add_argument("--rows", required=True, help="rungeval rows file")
    ap.add_argument("--n-queries", type=int, default=40)
    ap.add_argument("--final-only", action="store_true")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    queries = load_queries(args.rows, args.n_queries)
    res = {"n_queries": len(queries), "final_only": args.final_only,
           "files": {}}
    print(f"{'file':34s} {'pgs':>4s} {'hit@1':>6s} {'tieL':>6s} {'scoreL':>7s} "
          f"{'tieshr':>7s} {'rank':>5s} {'grp':>5s} {'tied':>6s} {'pred':>6s}")
    for path in args.episodes.split(","):
        s = run(path, queries, args.final_only)
        res["files"][path] = s
        print(f"{path.split('/')[-1]:34s} {s['mean_pages']:4.1f} "
              f"{s['hit_at_1']:6.3f} {s['tie_loss']:6.3f} "
              f"{s['score_loss']:7.3f} {s['tie_share_of_misses']:7.3f} "
              f"{(s['mean_gold_rank'] or 0):5.2f} {s['mean_tie_group_all']:5.2f} "
              f"{s['tied_at_all']:6.3f} "
              f"{s['expected_served_position_blind']:6.3f}")
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
