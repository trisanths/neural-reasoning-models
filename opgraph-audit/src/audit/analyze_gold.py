"""Floors, entropies and collision rates for the sequential depth curve.

Reads the per item dump written by src/audit/goldcheck.py and turns it into the
numbers checks 2 and 4 ask for. No model, no GPU.

Four floors are reported, and they are different things:

  uniform    one over the modulus the page states, averaged over items. What a
             guess uniform on the stated range would score.
  constant   the frequency of the single most common answer in the cell. What
             the best fixed reply would score.
  truncate_k the frequency with which the answer to the full chain equals the
             answer to the same chain cut off after k operators. What a plan
             that stops early scores without composing the rest.
  wrong_way  the frequency with which folding the chain the other way round
             lands on the same number, so associativity could be ignored.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict


def entropy(c, n):
    return -sum((v / n) * math.log2(v / n) for v in c.values() if v)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="results/audit_gold_items.json")
    ap.add_argument("--kind", default="sequential")
    ap.add_argument("--style", type=int, default=0)
    ap.add_argument("--out", default="results/audit_floors.json")
    args = ap.parse_args()

    rows = [r for r in json.load(open(args.items))
            if r["kind"] == args.kind and r["style"] == args.style]
    by_depth = defaultdict(list)
    for r in rows:
        by_depth[r["depth"]].append(r)

    out = {}
    print(f"{'d':>2} {'n':>4} {'right%':>7} {'supp':>5} {'H':>6} {'unif':>7} "
          f"{'const':>7} {'trunc*':>7} {'wrongway':>9} {'inter':>6} {'oper':>5}")
    for d in sorted(by_depth):
        rs = by_depth[d]
        n = len(rs)
        golds = Counter(r["gold"] for r in rs)
        unif = sum(1.0 / r["modulus"] for r in rs) / n
        const = max(golds.values()) / n
        right = sum(1 for r in rs if r["assoc"] == "right") / n
        wrong_way = sum(1 for r in rs if r.get("wrong_assoc_answer") == r["gold"]) / n
        inter = sum(1 for r in rs if r["gold"] in r["intermediates"]) / n
        oper = sum(1 for r in rs if r["gold"] in r["operands"]) / n
        tr = {}
        maxk = max((len(r["truncations"]) for r in rs), default=0)
        for k in range(maxk):
            hits = sum(1 for r in rs
                       if len(r["truncations"]) > k and r["truncations"][k] == r["gold"])
            tr[k + 1] = hits / n
        any_tr = sum(1 for r in rs if r["gold"] in r["truncations"]) / n
        best_tr = max(tr.values()) if tr else 0.0
        mods = Counter(r["modulus"] for r in rs)
        forms = Counter(r["form"] for r in rs)
        out[str(d)] = {
            "n": n, "support": len(golds), "entropy_bits": round(entropy(golds, n), 4),
            "right_assoc_rate": round(right, 4),
            "floor_uniform": round(unif, 5),
            "floor_constant": round(const, 4),
            "floor_constant_value": golds.most_common(1)[0][0],
            "floor_truncate_best_k": round(best_tr, 4),
            "floor_truncate_by_k": {k: round(v, 4) for k, v in tr.items()},
            "truncate_any_k": round(any_tr, 4),
            "wrong_way_same": round(wrong_way, 4),
            "intermediate_equals_answer": round(inter, 4),
            "operand_equals_answer": round(oper, 4),
            "modulus": dict(mods), "forms": dict(forms),
        }
        print(f"{d:>2} {n:>4} {right*100:>6.1f}% {len(golds):>5} "
              f"{entropy(golds, n):>6.3f} {unif:>7.4f} {const:>7.4f} "
              f"{best_tr:>7.4f} {wrong_way:>9.4f} {inter:>6.4f} {oper:>5.4f}")

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"\n[written] {args.out}")

    # ------------------------------------------------ chance corrected table
    audited = {"direct": {1: .480, 2: .227, 3: .127, 4: .020, 8: .013},
               "trace": {1: .827, 2: .493, 3: .260, 4: .007, 8: .000},
               "plan_execute": {1: 1.000, 2: .480, 3: .500, 4: .020, 8: .013},
               "oracle_ops": {1: 1.000, 2: .480, 3: .500, 4: .020, 8: .013},
               "oracle_plan": {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 8: 1.0}}
    for floor_name in ("floor_uniform", "floor_constant", "floor_truncate_best_k"):
        print(f"\n=== chance corrected with {floor_name} ===")
        print(f"{'condition':<14} " + " ".join(f"d{d:<6}" for d in (1, 2, 3, 4, 8))
              + "  macro(acc)  corr_of_macro  mean_of_corr")
        for cond, accs in audited.items():
            ks, corr = [], []
            for d in (1, 2, 3, 4, 8):
                p0 = out[str(d)][floor_name]
                k = (accs[d] - p0) / (1 - p0) if p0 < 1 else float("nan")
                corr.append(k)
                ks.append(f"{k:>7.3f}")
            macro = sum(accs.values()) / len(accs)
            p0m = sum(out[str(d)][floor_name] for d in (1, 2, 3, 4, 8)) / 5
            print(f"{cond:<14} " + " ".join(ks)
                  + f"  {macro:>9.3f}  {(macro - p0m)/(1 - p0m):>12.3f}"
                  + f"  {sum(corr)/len(corr):>12.3f}")


if __name__ == "__main__":
    main()
