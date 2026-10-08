"""The floor a plan capped at three steps reaches on a chain of d operators.

Training never showed a plan longer than three steps, and at depth four and
above the audited checkpoint writes a three step plan for every single item. A
three step plan consumes four operands out of the d + 1 the question carries, so
whatever it lands on was reachable without composing the rest of the chain. This
measures how often that number is the right one anyway, before looking at any
model output, so the comparison is not circular.

Strategies, all folded with the associativity the page states and again with the
opposite one, because the planner's fold direction is not a function of the page:

  prefix        v0 v1 v2 v3, the first four operands
  prefix_last   v0 v1 v2 vd, the first three operands and the last
  any_fourth    the best over every choice of the fourth operand and both fold
                directions, an upper bound on any three step plan that starts
                at the left end of the chain
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.expanduser("~/opg"))

from src.audit.refprose import RefWorld, _rem  # noqa: E402
from src.opgraph.data import eval_worlds, make_item  # noqa: E402


def fold(vals, b, assoc):
    if assoc == "left":
        acc = vals[0]
        for v in vals[1:]:
            acc = _rem(b.raw(acc, v), b.modulus, False)
    else:
        acc = vals[-1]
        for v in reversed(vals[:-1]):
            acc = _rem(b.raw(v, acc), b.modulus, False)
    return str(acc)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--depths", default="1,2,3,4,5,6,7,8")
    ap.add_argument("--out", default="results/audit_floor3.json")
    args = ap.parse_args()

    worlds = eval_worlds("sequential", args.n, breadth=3)
    readers = {w.seed: RefWorld.read([p.text for p in w.shuffled_pages()])
               for w in worlds}
    out = {}
    for d in [int(x) for x in args.depths.split(",")]:
        items = [make_item("sequential", w, d, i) for i, w in enumerate(worlds)]
        hits = defaultdict(int)
        n = 0
        for it in items:
            g = it.symbols[0]
            b = readers[it.world.seed].binops[g]
            m = re.match(r"^Evaluate\s+(.*?)\.$", it.text)
            vals = [int(v) for v in m.group(1).split()[0::2]]
            n += 1
            if len(vals) <= 4:
                # a three step plan is long enough here; no truncation to test
                hits["not_applicable"] += 1
                continue
            for assoc in ("left", "right"):
                if fold(vals[:4], b, assoc) == it.gold:
                    hits[f"prefix_{assoc}"] += 1
                if fold(vals[:3] + [vals[-1]], b, assoc) == it.gold:
                    hits[f"prefix_last_{assoc}"] += 1
            page = b.assoc
            if fold(vals[:4], b, page) == it.gold:
                hits["prefix_page_assoc"] += 1
            if fold(vals[:3] + [vals[-1]], b, page) == it.gold:
                hits["prefix_last_page_assoc"] += 1
            best = False
            for j in range(3, len(vals)):
                for assoc in ("left", "right"):
                    if fold(vals[:3] + [vals[j]], b, assoc) == it.gold:
                        best = True
            if best:
                hits["any_fourth"] += 1
        out[str(d)] = {"n": n, **{k: v for k, v in sorted(hits.items())},
                       **{"rate_" + k: round(v / n, 4)
                          for k, v in sorted(hits.items())}}
        print(f"d{d} n={n} " + " ".join(
            f"{k}={v}({v/n:.4f})" for k, v in sorted(hits.items())))
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"[written] {args.out}")


if __name__ == "__main__":
    main()
