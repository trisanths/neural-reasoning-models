"""Is the model's answer a function of the question, or a constant?

Removing the items a shortcut solves filters on the gold label, so a model
that answers with the same word regardless of the question scores higher on
what remains than it did on the whole set. That is a property of the filter,
not of the model, and the first table here is what exposes it: accuracy split
by which label was gold.

Balanced accuracy is the honest summary. It averages the per-label rates, so
a constant answer scores exactly chance no matter how the labels are skewed,
and no subset selection can lift it.

Three graders, tightening:

  forced       the first candidate word the prediction names
  nonhedged    the same, except a prediction naming more than one candidate
               is wrong, because naming both is not an answer
  strictish    normalized exact match against gold
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict

WORD_RE = re.compile(r"[A-Za-z]+")
BLIND = ("random_nonce", "freq_nonce", "last_nonce", "nearest_nonce")
KS = (1, 4, 6)


def named(pred: str, cands: list) -> list:
    low = [c.lower() for c in cands]
    seen, out = set(), []
    for w in WORD_RE.findall(pred):
        wl = w.lower()
        if wl in low and wl not in seen:
            seen.add(wl)
            out.append(wl)
    return out


def wilson(k: int, n: int) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    z, p = 1.96, k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 4), round((c + h) / d, 4))


def load(data_dir: str, pred_dir: str, cond: str) -> list:
    metas = [json.loads(l) for l in open(f"{data_dir}/meta_{cond}.jsonl")]
    preds = [json.loads(l) for l in open(f"{pred_dir}/pred_{cond}.jsonl")]
    for p in preds:
        p["meta"] = metas[p["episode_index"]]
        cands = p["meta"]["candidates"]
        nm = named(p["model"][0], cands)
        p["named"] = nm
        p["first"] = nm[0] if nm else ""
        p["hedged"] = len(nm) > 1
        p["gold_l"] = p["gold"].lower()
        p["cand_l"] = [c.lower() for c in cands]
        p["forced"] = p["first"] == p["gold_l"]
        p["nonhedged"] = p["forced"] and not p["hedged"]
        hits = [f"{n}@{k}" for n in BLIND for k in KS
                if named(p["baseline"].get(f"{n}@{k}", ""), cands)[:1]
                == [p["gold_l"]]]
        p["trivial"] = bool(hits) or bool(
            re.search(rf"(?<![\w.]){re.escape(p['gold'])}(?![\w.])",
                      p["question"], re.I))
    return preds


def balanced(rows: list, key: str) -> dict:
    """Macro-average of the per-gold-label accuracies.

    A label here is the candidate's index in the episode's own answer set, so
    'label 0' means the same role across episodes even though the invented
    word differs every time.
    """
    per = defaultdict(lambda: [0, 0])
    for p in rows:
        try:
            lab = p["cand_l"].index(p["gold_l"])
        except ValueError:
            lab = -1
        per[lab][0] += 1
        per[lab][1] += bool(p[key])
    if not per:
        return {"n": 0}
    rates = {lab: v[1] / v[0] for lab, v in per.items()}
    return {
        "n": len(rows),
        "raw": round(sum(p[key] for p in rows) / len(rows), 4),
        "balanced": round(sum(rates.values()) / len(rates), 4),
        "per_label": {str(k): {"n": per[k][0], "acc": round(rates[k], 4)}
                      for k in sorted(per)},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--conds", default="textbook")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    report = {}
    for cond in args.conds.split(","):
        preds = load(args.data, args.pred, cond)
        entry = {"n": len(preds), "families": {}}
        print(f"\n================ {cond}  n={len(preds)}")
        fams = sorted({p["meta"]["family"] for p in preds})
        for f in fams:
            rows = [p for p in preds if p["meta"]["family"] == f]
            kept = [p for p in rows if not p["trivial"]]
            fe = {
                "hedge_rate": round(sum(p["hedged"] for p in rows) / len(rows), 4),
                "forced": balanced(rows, "forced"),
                "nonhedged": balanced(rows, "nonhedged"),
                "forced_kept": balanced(kept, "forced"),
            }
            # What does the model actually say? If one word dominates
            # regardless of the question, the raw score is a label prior.
            pos = Counter()
            for p in rows:
                pos[p["cand_l"].index(p["first"]) if p["first"] in p["cand_l"]
                    else -1] += 1
            fe["first_word_slot"] = {str(k): round(v / len(rows), 4)
                                     for k, v in sorted(pos.items())}
            gold_pos = Counter(p["cand_l"].index(p["gold_l"]) for p in rows)
            fe["gold_slot"] = {str(k): round(v / len(rows), 4)
                               for k, v in sorted(gold_pos.items())}
            entry["families"][f] = fe
            print(f"-- {f}  n={len(rows)}  hedge_rate {fe['hedge_rate']:.4f}")
            print(f"   forced      raw {fe['forced']['raw']:.4f}  "
                  f"balanced {fe['forced']['balanced']:.4f}  "
                  f"per_label {json.dumps(fe['forced']['per_label'])}")
            print(f"   nonhedged   raw {fe['nonhedged']['raw']:.4f}  "
                  f"balanced {fe['nonhedged']['balanced']:.4f}")
            print(f"   forced kept raw {fe['forced_kept']['raw']:.4f}  "
                  f"balanced {fe['forced_kept']['balanced']:.4f}  "
                  f"n={fe['forced_kept']['n']}")
            print(f"   model first word lands in slot {fe['first_word_slot']}")
            print(f"   gold lands in slot             {fe['gold_slot']}")

        macro = {g: round(sum(entry["families"][f][g]["balanced"] for f in fams)
                          / len(fams), 4)
                 for g in ("forced", "nonhedged", "forced_kept")}
        entry["macro_over_families"] = macro
        print(f"== macro over families: {json.dumps(macro)}")
        report[cond] = entry

    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
