"""Cross-condition consistency checks over the shipped results file.

Two supporting claims are tested arithmetically:

  plan_execute == oracle_ops to three decimals at every depth
  oracle_plan diverges from oracle_both, which is what is offered as proof
  that oracle_plan runs model-induced operators
"""

from __future__ import annotations

import json
import sys
from math import sqrt

KINDS = ["sequential", "breadth", "novel", "sequential_paren",
         "same_page_pair", "units"]


def cells(d, name, kind):
    return d.get(name, {}).get(kind, {})


def main() -> int:
    d = json.load(open(sys.argv[1]))
    print("== plan_execute vs oracle_ops ==")
    worst = 0.0
    diffs = []
    for kind in KINDS:
        a, b = cells(d, "plan_execute", kind), cells(d, "oracle_ops", kind)
        for k in sorted(set(a) & set(b), key=int):
            x, y = a[k]["acc"], b[k]["acc"]
            worst = max(worst, abs(x - y))
            flag = "" if abs(x - y) < 0.0005 else "   <-- DIFFERS"
            if flag:
                diffs.append((kind, k, x, y))
            print(f"  {kind:18s} d={k:2s} plan_execute={x:.3f} oracle_ops={y:.3f}{flag}")
    print(f"  max |plan_execute - oracle_ops| = {worst:.3f} over "
          f"{sum(len(set(cells(d,'plan_execute',k)) & set(cells(d,'oracle_ops',k))) for k in KINDS)} cells; "
          f"{len(diffs)} cells differ at three decimals")
    print()
    print("== oracle_plan vs oracle_both ==")
    for kind in KINDS:
        a, b = cells(d, "oracle_plan", kind), cells(d, "oracle_both", kind)
        for k in sorted(set(a) & set(b), key=int):
            x, y = a[k]["acc"], b[k]["acc"]
            tagd = "  diverges" if abs(x - y) > 0.0005 else ""
            print(f"  {kind:18s} d={k:2s} oracle_plan={x:.3f} oracle_both={y:.3f}{tagd}")
    print()
    print("== base_untrained_direct ==")
    for kind in KINDS:
        a = cells(d, "base_untrained_direct", kind)
        if a:
            print(f"  {kind:18s}", " ".join(f"{k}:{a[k]['acc']:.3f}"
                                            for k in sorted(a, key=int)))
    return 0


def chi2_2x2(a, b, c, dd):
    n = a + b + c + dd
    r1, r2, c1, c2 = a + b, c + dd, a + c, b + dd
    if min(r1, r2, c1, c2) == 0:
        return 0.0, 0.0
    exp = [r1 * c1 / n, r1 * c2 / n, r2 * c1 / n, r2 * c2 / n]
    obs = [a, b, c, dd]
    x2 = sum((o - e) ** 2 / e for o, e in zip(obs, exp))
    phi = (a * dd - b * c) / sqrt(r1 * r2 * c1 * c2)
    return x2, phi


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "chi2":
        vals = [int(x) for x in sys.argv[3:7]]
        x2, phi = chi2_2x2(*vals)
        print(f"chi2={x2:.4f} phi={phi:.4f}")
        raise SystemExit(0)
    raise SystemExit(main())
