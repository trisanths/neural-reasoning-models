"""Rank diagnostics for the BM25 retrieval gate.

The gate is `BM25Index.top` in `src/train/retrieval.py`, reached from
`RetrievalService.top` in `src/rl/env.py`. It returns one document per round.
This module takes the same index and asks, for a query and a labelled set of
needed pages, three things that the single returned index cannot answer:

  what rank the needed page actually got,
  whether the document that beat it beat it on score or only on position,
  how large the exactly-tied group at the top is.

Nothing here changes retrieval. It only reads the index.
"""

from __future__ import annotations

from src.train.retrieval import BM25Index

# Two BM25 scores count as an exact tie when they agree to this relative
# tolerance. The ties this gate produces are exact in IEEE double because the
# tied documents have identical term counts and identical lengths, so the
# tolerance only guards against reordering of the same additions.
TIE_REL = 1e-12


def score_vector(index: BM25Index, query: str) -> list[float]:
    return [index.score(query, i) for i in range(index.n_docs)]


def _tied(a: float, b: float) -> bool:
    return abs(a - b) <= TIE_REL * max(1.0, abs(a), abs(b))


def ranking(scores: list[float], exclude=()) -> list[int]:
    """Document indices best first, ties broken toward the lower index, which
    is the order `BM25Index.top` walks."""
    excluded = set(exclude)
    live = [i for i in range(len(scores)) if i not in excluded]
    return sorted(live, key=lambda i: (-scores[i], i))


def diagnose(index: BM25Index, query: str, gold: set[int], exclude=()) -> dict:
    """One query against one index, with the needed pages labelled.

    verdict is the whole point:

      hit          the gate returns a needed page;
      tie_loss     a needed page is exactly tied with the served page and lost
                   on document index alone, which is an artifact of page order;
      score_loss   every needed page scores strictly below the served page.

    gold_rank counts from 1 under the gate's own ordering. tie_group is the
    number of documents exactly tied with the served page, and gold_in_tie is
    how many of those are needed pages.
    """
    scores = score_vector(index, query)
    order = ranking(scores, exclude)
    if not order:
        return {"verdict": "empty", "gold_rank": None}
    served = order[0]
    top = scores[served]
    tie_group = [i for i in order if _tied(scores[i], top)]
    gold_live = [i for i in order if i in gold]
    gold_rank = None
    gold_score = None
    for r, i in enumerate(order, start=1):
        if i in gold:
            gold_rank, gold_score = r, scores[i]
            break
    if served in gold:
        verdict = "hit"
    elif gold_score is not None and _tied(gold_score, top):
        verdict = "tie_loss"
    elif gold_score is None:
        verdict = "absent"
    else:
        verdict = "score_loss"
    return {
        "verdict": verdict,
        "served": served,
        "served_score": top,
        "gold_rank": gold_rank,
        "gold_score": gold_score,
        "gold_indices": sorted(gold_live),
        "n_docs": index.n_docs,
        "tie_group": len(tie_group),
        "gold_in_tie": sum(1 for i in tie_group if i in gold),
        "margin": (top - gold_score) if gold_score is not None else None,
    }


def summarise(rows: list[dict]) -> dict:
    """Fold diagnose rows into the counts a cell is reported with.

    tie_share is the fraction of misses that a needed page lost on document
    index rather than on score, which is the quantity that separates a page
    order artifact from a retriever that genuinely ranks the page low.
    """
    n = len(rows)
    if n == 0:
        return {"n": 0}
    counts = {"hit": 0, "tie_loss": 0, "score_loss": 0, "absent": 0, "empty": 0}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    misses = counts["tie_loss"] + counts["score_loss"]
    ranks = [r["gold_rank"] for r in rows if r.get("gold_rank")]
    ties = [r["tie_group"] for r in rows if r.get("tie_group")]
    out = {
        "n": n,
        "hit_at_1": counts["hit"] / n,
        "tie_loss": counts["tie_loss"] / n,
        "score_loss": counts["score_loss"] / n,
        "absent": counts["absent"] / n,
        "tie_share_of_misses": (counts["tie_loss"] / misses) if misses else 0.0,
        "mean_gold_rank": sum(ranks) / len(ranks) if ranks else None,
        "mean_tie_group": sum(ties) / len(ties) if ties else None,
    }
    for k in (1, 2, 3):
        out[f"hit_at_{k}"] = sum(
            1 for r in rows if r.get("gold_rank") and r["gold_rank"] <= k) / n
    # What the same queries would serve if the tie were broken without
    # reference to document order: a needed page in a group of k tied
    # documents is served one time in k instead of always or never.
    expected = 0.0
    for r in rows:
        if r.get("verdict") == "hit" and r.get("tie_group") == 1:
            expected += 1.0
        elif r.get("tie_group", 0) > 1 and r.get("gold_in_tie"):
            expected += r["gold_in_tie"] / r["tie_group"]
    out["expected_served_position_blind"] = expected / n
    return out


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95 percent Wilson interval, so no proportion is reported bare."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)
