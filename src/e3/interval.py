"""Wilson score intervals and a floor test, so no accuracy is reported bare.

Every accuracy in src/e3 carries n, its chance floor, and a 95 percent
interval. The floor test is the exact binomial tail against the floor, which
is what decides whether a number is distinguishable from guessing.
"""
from __future__ import annotations

import math

Z95 = 1.959963984540054


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """95 percent Wilson score interval for k successes in n trials."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p). Exact, summed in log space."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    total = 0.0
    logp = math.log(p) if p > 0 else float("-inf")
    log1p_ = math.log1p(-p) if p < 1 else float("-inf")
    for i in range(k, n + 1):
        term = (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                + i * logp + (n - i) * log1p_)
        total += math.exp(term)
    return min(1.0, total)


def summarise(k: int, n: int, floor: float) -> dict:
    """One accuracy with everything needed to read it honestly."""
    lo, hi = wilson(k, n)
    return {
        "k": int(k),
        "n": int(n),
        "acc": round(k / n, 4) if n else None,
        "floor": round(floor, 4),
        "ci95": [round(lo, 4), round(hi, 4)],
        "ci_contains_floor": bool(lo <= floor <= hi),
        "p_vs_floor": round(binom_sf(k, n, floor), 5),
        "above_floor": bool(lo > floor),
    }
