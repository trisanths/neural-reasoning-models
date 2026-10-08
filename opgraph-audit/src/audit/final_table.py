"""The consolidated floor table and the chance corrected curve.

Four floors are combined into one per depth, and the depth curve is corrected
against it. Both macro orders are printed, because they are different numbers
and the difference has already been reported wrongly once in this project:

  correction of the macro   (mean_d acc_d - mean_d p0_d) / (1 - mean_d p0_d)
  mean of the corrections   mean_d (acc_d - p0_d) / (1 - p0_d)
"""

from __future__ import annotations

import argparse
import json

DEPTHS = [1, 2, 3, 4, 8]

AUDITED = {
    "direct": {1: .480, 2: .227, 3: .127, 4: .020, 8: .013},
    "trace": {1: .827, 2: .493, 3: .260, 4: .007, 8: .000},
    "plan_execute": {1: 1.000, 2: .480, 3: .500, 4: .020, 8: .013},
    "oracle_ops": {1: 1.000, 2: .480, 3: .507, 4: .020, 8: .013},
    "oracle_plan": {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 8: 1.0},
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floors", default="results/audit_floors.json")
    ap.add_argument("--floor3", default="results/audit_floor3.json")
    ap.add_argument("--out", default="results/audit_chance.json")
    args = ap.parse_args()
    f = json.load(open(args.floors))
    f3 = json.load(open(args.floor3))

    rows = {}
    print(f"{'d':>2} {'uniform':>8} {'constant':>9} {'trunc_k*':>9} "
          f"{'3step_pfx':>10} {'3step_last':>11} {'any_4th':>8} {'p0':>7}")
    for d in DEPTHS:
        c = f[str(d)]
        parts = {"uniform": c["floor_uniform"],
                 "constant": c["floor_constant"],
                 "truncate_best_k": c["floor_truncate_best_k"]}
        g = f3.get(str(d), {})
        if "rate_prefix_page_assoc" in g:
            parts["three_step_prefix"] = g["rate_prefix_page_assoc"]
            parts["three_step_prefix_last"] = g["rate_prefix_last_page_assoc"]
            parts["any_fourth_upper_bound"] = g["rate_any_fourth"]
        p0 = max(v for k, v in parts.items() if k != "any_fourth_upper_bound")
        rows[d] = {"parts": parts, "p0": p0}
        print(f"{d:>2} {parts['uniform']:>8.4f} {parts['constant']:>9.4f} "
              f"{parts['truncate_best_k']:>9.4f} "
              f"{parts.get('three_step_prefix', float('nan')):>10.4f} "
              f"{parts.get('three_step_prefix_last', float('nan')):>11.4f} "
              f"{parts.get('any_fourth_upper_bound', float('nan')):>8.4f} "
              f"{p0:>7.4f}")

    print(f"\n{'condition':<14} " + " ".join(f"{'d'+str(d):>8}" for d in DEPTHS)
          + f" {'macro_acc':>10} {'corr_of_macro':>14} {'mean_of_corr':>13}")
    table = {}
    for cond, accs in AUDITED.items():
        ks = []
        for d in DEPTHS:
            p0 = rows[d]["p0"]
            ks.append((accs[d] - p0) / (1 - p0))
        macro = sum(accs[d] for d in DEPTHS) / len(DEPTHS)
        p0m = sum(rows[d]["p0"] for d in DEPTHS) / len(DEPTHS)
        com = (macro - p0m) / (1 - p0m)
        moc = sum(ks) / len(ks)
        table[cond] = {"corrected": {str(d): round(k, 4)
                                     for d, k in zip(DEPTHS, ks)},
                       "macro_acc": round(macro, 4),
                       "mean_floor": round(p0m, 4),
                       "correction_of_macro": round(com, 4),
                       "mean_of_corrections": round(moc, 4)}
        print(f"{cond:<14} " + " ".join(f"{k:>8.3f}" for k in ks)
              + f" {macro:>10.3f} {com:>14.3f} {moc:>13.3f}")

    with open(args.out, "w") as fh:
        json.dump({"floors": {str(d): rows[d] for d in DEPTHS},
                   "audited_accuracy": AUDITED, "corrected": table}, fh, indent=1)
    print(f"\n[written] {args.out}")


if __name__ == "__main__":
    main()
