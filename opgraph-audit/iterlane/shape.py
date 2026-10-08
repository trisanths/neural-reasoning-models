"""Fit the shape of the depth curve and say which shape the data actually has.

Two one dimensional families are fitted to the same points by the same grid
search over sum of squares, so their residuals are comparable:

  exponential   acc(d) = A * exp(-lam * (d - 1))
                smooth per step attrition; lam is the per step survival cost
  logistic      acc(d) = A / (1 + exp((d - d50) / w))
                a plateau that ends; d50 is where the cliff sits and w is how
                wide it is. A small w is a cliff, a large w is a slow slide

Reporting only one of them would decide the plateau against decay question by
assumption. Reporting both residuals lets the data decide, and the answer is
stated with the margin rather than as a verdict.

Threshold crossings are read off the measured points, not off a fit, and are
given as the bracket between the two grid depths the crossing falls between,
because the grid is not dense enough to name a single depth.
"""

from __future__ import annotations

import json
import math


def _sse(points, f):
    return sum((a - f(d)) ** 2 for d, a in points)


def fit_exponential(points):
    best = None
    for ai in range(0, 41):
        A = ai / 40
        for li in range(0, 401):
            lam = li / 100
            s = _sse(points, lambda d, A=A, lam=lam: A * math.exp(-lam * (d - 1)))
            if best is None or s < best[0]:
                best = (s, A, lam)
    s, A, lam = best
    return {"sse": round(s, 5), "A": round(A, 4), "lambda": round(lam, 4),
            "half_life_steps": (round(math.log(2) / lam, 3) if lam > 0 else None)}


def fit_logistic(points):
    best = None
    for ai in range(0, 41):
        A = ai / 40
        for di in range(2, 141):
            d50 = di / 4
            for wi in range(1, 81):
                w = wi / 8
                s = _sse(points, lambda d, A=A, d50=d50, w=w:
                         A / (1 + math.exp(min(60.0, max(-60.0, (d - d50) / w)))))
                if best is None or s < best[0]:
                    best = (s, A, d50, w)
    s, A, d50, w = best
    return {"sse": round(s, 5), "A": round(A, 4), "d50": round(d50, 3),
            "width": round(w, 4)}


def crossings(points, levels=(0.5, 0.1)):
    """Where the measured curve falls below each level, as a grid bracket."""
    pts = sorted(points)
    out = {}
    for lev in levels:
        hit = None
        for i, (d, a) in enumerate(pts):
            if a < lev:
                prev = pts[i - 1][0] if i else None
                hit = {"first_depth_below": d, "previous_depth": prev,
                       "previous_acc": round(pts[i - 1][1], 4) if i else None}
                break
        out[str(lev)] = hit or {"first_depth_below": None,
                                "previous_depth": pts[-1][0],
                                "previous_acc": round(pts[-1][1], 4)}
    return out


def shape(points) -> dict:
    """Both fits, the crossings, and which family the residuals prefer."""
    pts = sorted(points)
    if len(pts) < 3:
        return {"n_points": len(pts), "note": "too few points to fit"}
    e = fit_exponential(pts)
    g = fit_logistic(pts)
    margin = e["sse"] - g["sse"]
    if abs(margin) < 1e-3:
        verdict = "the two fits are within 0.001 sse, so the data does not separate them"
    elif margin > 0:
        verdict = "logistic fits better, which is the plateau then cliff shape"
    else:
        verdict = "exponential fits better, which is the smooth per step decay shape"
    return {"n_points": len(pts), "points": [[d, round(a, 4)] for d, a in pts],
            "exponential": e, "logistic": g,
            "sse_margin_exp_minus_logistic": round(margin, 5),
            "verdict": verdict, "crossings": crossings(pts)}


def se(p: float, n: int) -> float:
    return round(math.sqrt(max(p * (1 - p), 0.0) / n), 4) if n else 0.0


def curve_from(block, kind="sequential", max_depth=None):
    out = []
    for d, row in block.get(kind, {}).items():
        if max_depth is not None and int(d) > max_depth:
            continue
        out.append((int(d), row["acc"]))
    return sorted(out)


if __name__ == "__main__":
    import sys
    print(json.dumps(shape(json.load(open(sys.argv[1]))), indent=1))
