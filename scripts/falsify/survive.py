"""How much of the headline survives once the grader is fixed and the
trivially derivable items are removed.

Two corrections are applied in sequence, and each is reported on its own so
the reader can see which one does the damage.

  grader     The environment marks a prediction correct when it contains the
             gold answer within six tokens of slack, so naming both candidate
             words scores as well as naming the right one. Forced choice reads
             the first candidate word a prediction names and compares that.

  triviality An item is trivial when a program that never reads the values on
             the page can still produce its gold answer: the answer sits in
             the question, or a generic page shortcut lands on it. The
             shortcuts are the value blind ones only. rule_parser knows the
             three families by shape and would remove every item, and
             hedge_all_nonce is a grader exploit rather than a shortcut, so
             neither is allowed to mark an item trivial.

The chance floor matters as much as either correction. Two of the three
families admit exactly two answers, so guessing among the words the page
offers scores 0.5 there, and the headline has to be read against 0.402 rather
than against the 0.002 wrong-page control.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict

WORD_RE = re.compile(r"[A-Za-z]+")

# Shortcuts that never look at which value the rule assigns. rule_parser and
# hedge_all_nonce are excluded, for the reasons in the module docstring.
BLIND = ("random_nonce", "freq_nonce", "last_nonce", "nearest_nonce")
KS = (1, 4, 6)


def first_candidate(pred: str, cands: list) -> str:
    low = [c.lower() for c in cands]
    for w in WORD_RE.findall(pred):
        if w.lower() in low:
            return w.lower()
    return ""


def forced(pred: str, gold: str, cands: list) -> bool:
    return first_candidate(pred, cands) == gold.lower()


def wilson(k: int, n: int) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    z, p = 1.96, k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 4), round((c + h) / d, 4))


def gold_in_question(gold: str, question: str) -> bool:
    return bool(re.search(rf"(?<![\w.]){re.escape(gold)}(?![\w.])", question, re.I))


def audit(preds: list) -> list:
    """Tag every item with why it might be trivial."""
    for p in preds:
        gold, cands = p["gold"], p["meta"]["candidates"]
        hits = [f"{n}@{k}" for n in BLIND for k in KS
                if forced(p["baseline"].get(f"{n}@{k}", ""), gold, cands)]
        p["shortcut_hits"] = hits
        p["in_question"] = gold_in_question(gold, p["question"])
        p["n_cands"] = len(set(c.lower() for c in cands))
        p["trivial"] = bool(hits) or p["in_question"]
        p["forced_ok"] = forced(p["model"][0], gold, cands)
    return preds


def block(rows: list, label: str) -> dict:
    if not rows:
        return {"label": label, "n": 0}
    n = len(rows)
    k = sum(r["forced_ok"] for r in rows)
    chance = sum(1.0 / r["n_cands"] for r in rows) / n
    acc = k / n
    lo, hi = wilson(k, n)
    return {
        "label": label, "n": n, "forced": round(acc, 4),
        "forced_ci": [lo, hi], "chance": round(chance, 4),
        "above_chance": round(acc - chance, 4),
        "chance_corrected": round((acc - chance) / (1 - chance), 4)
        if chance < 1 else None,
    }


def show(b: dict) -> None:
    if not b["n"]:
        print(f"  {b['label']:<34s} n=0")
        return
    print(f"  {b['label']:<34s} n={b['n']:<5d} forced {b['forced']:.4f} "
          f"ci [{b['forced_ci'][0]:.3f},{b['forced_ci'][1]:.3f}] "
          f"chance {b['chance']:.4f}  corrected {b['chance_corrected']:+.4f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--cond", default="textbook")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    metas = [json.loads(l) for l in open(f"{args.data}/meta_{args.cond}.jsonl")]
    preds = [json.loads(l) for l in open(f"{args.pred}/pred_{args.cond}.jsonl")]
    for p in preds:
        p["meta"] = metas[p["episode_index"]]
    preds = audit(preds)

    report = {"condition": args.cond, "n_items": len(preds), "blocks": [],
              "per_family": {}, "shortcut_coverage": {}}

    print(f"=== {args.cond}: n={len(preds)}")
    print(f"gold appears in the question: "
          f"{sum(p['in_question'] for p in preds) / len(preds):.4f}")
    cov = {}
    for name in BLIND:
        for k in KS:
            key = f"{name}@{k}"
            cov[key] = round(sum(key in p["shortcut_hits"] for p in preds)
                             / len(preds), 4)
    cov["any_blind_shortcut"] = round(
        sum(bool(p["shortcut_hits"]) for p in preds) / len(preds), 4)
    cov["trivial_any_reason"] = round(
        sum(p["trivial"] for p in preds) / len(preds), 4)
    report["shortcut_coverage"] = cov
    print("shortcut coverage (fraction of items a value-blind program gets):")
    for key, v in cov.items():
        print(f"  {key:<24s} {v:.4f}")

    print("\nforced-choice accuracy, whole set and after each cut:")
    blocks = [
        block(preds, "all items"),
        block([p for p in preds if not p["in_question"]],
              "minus gold-in-question"),
        block([p for p in preds if not p["trivial"]],
              "minus every trivial item"),
        block([p for p in preds if p["trivial"]],
              "the trivial items alone"),
    ]
    for b in blocks:
        show(b)
    report["blocks"] = blocks

    print("\nper family, after removing every trivial item:")
    fams = sorted({p["meta"]["family"] for p in preds})
    for f in fams:
        rows = [p for p in preds if p["meta"]["family"] == f]
        kept = [p for p in rows if not p["trivial"]]
        ba, bk = block(rows, f"{f} all"), block(kept, f"{f} kept")
        show(ba)
        show(bk)
        report["per_family"][f] = {"all": ba, "kept": bk}

    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
