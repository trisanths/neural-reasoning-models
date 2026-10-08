"""Static rank diagnosis of the retrieval gate on the skillacq families.

A skillacq episode holds one invented system's textbook pages plus a second
system's pages as distractors, shuffled together. With n_context zero the
pages arrive only through the gate, so a problem is answerable only once a
page of its own family is served.

Needed pages here are every page of the episode's own family, recovered by
replaying the generator's random stream up to the point the pages were built.
That is the lenient labelling: it counts a hit whenever the family's textbook
is reached at all, not whenever the one page carrying the needed rule is
reached, so the miss rates below are lower bounds on the miss rate for a
specific rule.

Queries, none of which need the model:

  problem   the problem text, which is the query a keyword baseline issues;
  shared    vocabulary every page of the episode holds, the limiting case a
            content-free query approaches.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter

from src.retrieval.rankdiag import diagnose, summarise, wilson
from src.skillacq.systems import _all_families, generate_episode
from src.train.retrieval import BM25Index, norm_terms


def own_pages(seed: int, family: str) -> list[str]:
    """The pages the episode's own system wrote, replayed from the seed.

    `generate_episode` draws the family, builds the system, and calls
    describe() before it touches anything else, so replaying those three
    draws reproduces the family's pages exactly.
    """
    rng = random.Random(seed)
    pool = _all_families()
    fam = family or rng.choice(sorted(pool))
    system = pool[fam](rng)
    return list(system.describe())


def index_for(pages: list[str]) -> BM25Index:
    return BM25Index(pages)


def shared_query(pages: list[str]) -> str:
    sets = [set(norm_terms(p)) for p in pages]
    return " ".join(sorted(set.intersection(*sets))) if sets else ""


def run_family(family: str, seeds: list[int]) -> dict:
    rows_prob: list[dict] = []
    rows_shared: list[dict] = []
    page_counts = Counter()
    gold_counts = Counter()
    n_problems = 0
    for seed in seeds:
        ep = generate_episode(seed, family=family)
        pages = list(ep.textbook)
        mine = set(own_pages(seed, family))
        gold = {i for i, p in enumerate(pages) if p in mine}
        if not gold or len(gold) == len(pages):
            continue
        page_counts[len(pages)] += 1
        gold_counts[len(gold)] += 1
        index = index_for(pages)
        rows_shared.append(diagnose(index, shared_query(pages), gold))
        for prob in ep.problems:
            n_problems += 1
            rows_prob.append(diagnose(index, prob["text"], gold))
    n = len(rows_prob)
    hits = sum(1 for r in rows_prob if r["verdict"] == "hit")
    lo, hi = wilson(hits, max(1, n))
    return {
        "family": family,
        "n_episodes": sum(page_counts.values()),
        "n_problems": n_problems,
        "pages_per_episode": dict(page_counts),
        "gold_pages_per_episode": dict(gold_counts),
        "problem_query": summarise(rows_prob),
        "problem_hit_ci95": [round(lo, 4), round(hi, 4)],
        "shared_only_query": summarise(rows_shared),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default="units,procedure,binary_op,"
                                          "threshold_rule,substitution_rule,"
                                          "exception_rule")
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--seed0", type=int, default=90000)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    seeds = list(range(args.seed0, args.seed0 + args.seeds))
    res = {"seed0": args.seed0, "n_seeds": args.seeds, "families": []}
    print(f"{'family':20s} {'eps':>4s} {'probs':>6s} {'hit@1':>6s} "
          f"{'hit@2':>6s} {'tie':>6s} {'score':>6s} {'tieshr':>7s} "
          f"{'rank':>5s} {'blind':>6s} {'shrd@1':>7s} {'shrdblind':>9s}")
    for fam in args.families.split(","):
        cell = run_family(fam, seeds)
        res["families"].append(cell)
        p, s = cell["problem_query"], cell["shared_only_query"]
        print(f"{fam:20s} {cell['n_episodes']:4d} {cell['n_problems']:6d} "
              f"{p['hit_at_1']:6.3f} {p['hit_at_2']:6.3f} {p['tie_loss']:6.3f} "
              f"{p['score_loss']:6.3f} {p['tie_share_of_misses']:7.3f} "
              f"{(p['mean_gold_rank'] or 0):5.2f} "
              f"{p['expected_served_position_blind']:6.3f} "
              f"{s['hit_at_1']:7.3f} "
              f"{s['expected_served_position_blind']:9.3f}")
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
