"""Read the condition JSONs and print the two tables the experiment is for.

    python scripts/latentret_report.py results/latentret

Table one is retrieval and the gate. Table two is whether anything reached the
output. Chance rates are printed on the same rows as the numbers they qualify,
because every one of these metrics has a different one and reading hit_gate
against 0.5 or acc_vs_foil against 1/6 would be a mistake that costs nothing to
prevent here.
"""

from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.latentret.vocab import get_vocab  # noqa: E402

ORDER = ["latent", "decoded", "question", "uniform", "latent_notask",
         "latent_easy", "latent_lm"]


def load(directory: str) -> list[dict]:
    rows = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        with open(path) as fh:
            blob = json.load(fh)
        blob["_name"] = os.path.basename(path).rsplit(".", 1)[0]
        rows.append(blob)
    key = lambda r: (ORDER.index(r["config"]["name"])
                     if r["config"]["name"] in ORDER else 99, r["_name"])
    return sorted(rows, key=key)


def main() -> None:
    directory = sys.argv[1] if len(sys.argv) > 1 else "results/latentret"
    rows = load(directory)
    if not rows:
        print(f"no result files in {directory}")
        return

    chance = rows[0]["final"]["chance_hit_one"]
    print(f"\nRETRIEVAL AND THE GATE   (hit chance {chance:.3f}, auc chance 0.500)\n")
    head = f"{'run':<24}{'hit_gate':>9}{'hit_last':>9}{'p_gold':>8}"
    head += f"{'gate_auc':>10}{'gate_gap':>10}{'g|need':>8}{'g|ctx':>8}"
    print(head)
    print("-" * len(head))
    for r in rows:
        f = r["final"]
        print(f"{r['_name']:<24}{f['hit_gate']:>9.3f}{f['hit_last']:>9.3f}"
              f"{f['p_gold_mean']:>8.3f}{f['gate_auc']:>10.3f}"
              f"{f['gate_gap']:>+10.3f}{f['gate_max_need']:>8.3f}"
              f"{f['gate_max_in_context']:>8.3f}")

    print(f"\nDID THE PAGE REACH THE OUTPUT   "
          f"(acc chance 1/{len(get_vocab())}, foil chance 0.500)\n")
    head = f"{'run':<24}{'acc':>7}{'acc|need':>10}{'acc|ctx':>9}"
    head += f"{'foil':>7}{'foil|need':>11}{'foil-corrupt':>14}{'acc-noinj':>11}"
    print(head)
    print("-" * len(head))
    for r in rows:
        f = r["final"]
        print(f"{r['_name']:<24}{f['acc_final']:>7.3f}{f['acc_need']:>10.3f}"
              f"{f['acc_in_context']:>9.3f}{f['acc_vs_foil']:>7.3f}"
              f"{f['acc_vs_foil_need']:>11.3f}"
              f"{f['acc_vs_foil_corrupted']:>14.3f}"
              f"{f['acc_no_injection']:>11.3f}")

    print("\nPER FAMILY, main run\n")
    main_row = next((r for r in rows if r["config"]["name"] == "latent"), rows[0])
    head = f"{'family':<20}{'n':>6}{'hit_gate':>10}{'gate_auc':>10}{'acc':>7}{'foil':>7}"
    print(head)
    print("-" * len(head))
    for family, v in main_row["final"]["by_family"].items():
        print(f"{family:<20}{v['n']:>6}{v['hit_gate']:>10.3f}"
              f"{v['gate_auc']:>10.3f}{v['acc_final']:>7.3f}{v['acc_vs_foil']:>7.3f}")

    print("\nTHE CURVE, main run   (step: hit_gate / gate_auc / foil)\n")
    for point in main_row["curve"]:
        print(f"  {point['step']:>5}  {point['hit_gate']:.3f}  "
              f"{point['gate_auc']:.3f}  {point['acc_vs_foil']:.3f}")

    print("\nBY ITERATION, main run\n")
    it = main_row["per_iteration"]
    for label in ("hit_by_iter", "p_gold_by_iter", "gate_need_by_iter",
                  "gate_in_context_by_iter"):
        print(f"  {label:<24}" + " ".join(f"{v:.3f}" for v in it[label]))
    print()


if __name__ == "__main__":
    main()
