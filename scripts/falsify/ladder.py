"""The headline, corrected one step at a time.

Each rung removes one way of scoring a point without reading the values on
the page, and nothing else changes: same checkpoint, same items, same
rollouts. The rungs are cumulative.

  1 published grader   contains the gold answer within six tokens of slack
  2 forced choice      the first candidate word the prediction names, so
                       naming both no longer scores
  3 no hedging         a prediction that names more than one candidate is
                       wrong outright rather than resolved by word order
  4 label balanced     the per-gold-label rates, averaged, so a constant
                       answer scores chance however the labels are skewed
  5 non-trivial only   items no value-blind page shortcut solves
  6 chance corrected   (score - chance) / (1 - chance), because two of the
                       three families offer exactly two answers
"""

from __future__ import annotations

import argparse
import json

from scripts.falsify.balanced import balanced, load


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--cond", default="textbook")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    preds = load(args.data, args.pred, args.cond)
    fams = sorted({p["meta"]["family"] for p in preds})
    rows, out = [], {"condition": args.cond, "n": len(preds), "families": {}}

    for f in fams:
        rf = [p for p in preds if p["meta"]["family"] == f]
        kept = [p for p in rf if not p["trivial"]]
        chance = sum(1.0 / len(set(p["cand_l"])) for p in rf) / len(rf)
        b = {
            "n": len(rf), "n_kept": len(kept),
            "chance": round(chance, 4),
            "hedge_rate": round(sum(p["hedged"] for p in rf) / len(rf), 4),
            "forced": balanced(rf, "forced")["raw"],
            "forced_bal": balanced(rf, "forced")["balanced"],
            "nonhedged_bal": balanced(rf, "nonhedged")["balanced"],
            "nonhedged_kept_bal": balanced(kept, "nonhedged")["balanced"],
            "forced_kept_bal": balanced(kept, "forced")["balanced"],
        }
        b["chance_corrected"] = round(
            (b["nonhedged_kept_bal"] - chance) / (1 - chance), 4)
        b["forced_chance_corrected"] = round(
            (b["forced_kept_bal"] - chance) / (1 - chance), 4)
        out["families"][f] = b
        rows.append(b)

    def macro(k):
        return round(sum(r[k] for r in rows) / len(rows), 4)

    out["macro"] = {k: macro(k) for k in
                    ("chance", "forced", "forced_bal", "nonhedged_bal",
                     "forced_kept_bal", "nonhedged_kept_bal",
                     "forced_chance_corrected", "chance_corrected")}

    print(f"=== {args.cond}  n={len(preds)}")
    hdr = (f"{'family':<20s}{'n':>6s}{'kept':>6s}{'chance':>8s}{'hedge':>8s}"
           f"{'forced':>9s}{'f.bal':>8s}{'nohedge':>9s}{'kept':>8s}{'corr':>8s}")
    print(hdr)
    for f in fams:
        b = out["families"][f]
        print(f"{f:<20s}{b['n']:>6d}{b['n_kept']:>6d}{b['chance']:>8.4f}"
              f"{b['hedge_rate']:>8.4f}{b['forced']:>9.4f}{b['forced_bal']:>8.4f}"
              f"{b['nonhedged_bal']:>9.4f}{b['nonhedged_kept_bal']:>8.4f}"
              f"{b['chance_corrected']:>8.4f}")
    m = out["macro"]
    print(f"{'MACRO':<20s}{'':>6s}{'':>6s}{m['chance']:>8.4f}{'':>8s}"
          f"{m['forced']:>9.4f}{m['forced_bal']:>8.4f}"
          f"{m['nonhedged_bal']:>9.4f}{m['nonhedged_kept_bal']:>8.4f}"
          f"{m['chance_corrected']:>8.4f}")

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
