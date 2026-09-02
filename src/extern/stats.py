"""Interval and paired-test helpers shared by the cell 2 and GSM8K reports.

Wilson is the interval used everywhere in this lane, so a 0.275 against a 0.25
floor reads as "cannot distinguish" rather than as a result. McNemar is exact
and two sided, computed from the discordant pairs alone, which is the only
test that separates a treatment from item selection when the same model is
run on the same items under two conditions.
"""
from __future__ import annotations

import math


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))


def ci(k, n):
    if not n:
        return "-"
    lo, hi = wilson(k, n)
    return f"{k / n:.4f} [{lo:.3f}, {hi:.3f}]"


def mcnemar(b, c):
    """Exact two sided p for b wins against c losses among discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def paired(a_flags, b_flags):
    """(n, a_only, b_only, both, neither, p) for two aligned 0/1 lists."""
    assert len(a_flags) == len(b_flags)
    a_only = sum(1 for x, y in zip(a_flags, b_flags) if x and not y)
    b_only = sum(1 for x, y in zip(a_flags, b_flags) if y and not x)
    both = sum(1 for x, y in zip(a_flags, b_flags) if x and y)
    neither = sum(1 for x, y in zip(a_flags, b_flags) if not x and not y)
    return {"n": len(a_flags), "a_only": a_only, "b_only": b_only,
            "both": both, "neither": neither,
            "p": round(mcnemar(a_only, b_only), 4)}


def tbl(head, rows):
    w = [len(str(h)) for h in head]
    for r in rows:
        for i, c in enumerate(r):
            w[i] = max(w[i], len(str(c)))
    o = ["| " + " | ".join(str(h).ljust(w[i]) for i, h in enumerate(head)) + " |",
         "| " + " | ".join("-" * w[i] for i in range(len(head))) + " |"]
    for r in rows:
        o.append("| " + " | ".join(str(c).ljust(w[i])
                                   for i, c in enumerate(r)) + " |")
    return "\n".join(o)
