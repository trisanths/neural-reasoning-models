"""Check 3 on the real outputs, and check 2 restricted to what the model wrote.

The pair is a question and the same question against a page whose only edit is
the sentence saying which way a run of the operator associates. At depth one
that edit changes nothing, so depth one says whether the pair machinery is
sound. At depth two and above the pair has two different right answers.

Three things come out of it.

How often the two members of a pair are graded correct together, which is the
double credit the rule-family audit found elsewhere. How often the plan written
for one member is byte identical to the plan written for the other, which is
what double credit would need. And what the plan actually computed: the chain
folded left, the chain folded right, or neither.

Check 2 is then repeated against the plans themselves. A plan with fewer steps
than the question has operators did not compose the question; when such a plan
is graded correct, the number it landed on was already reachable without the
rest of the chain.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq", default="results/audit_seq_items.json")
    ap.add_argument("--gold", default="results/audit_gold_items.json")
    ap.add_argument("--out", default="results/audit_pairs.json")
    args = ap.parse_args()

    rows = json.load(open(args.seq))
    lazy = {}
    for r in json.load(open(args.gold)):
        if r["kind"] == "sequential" and r["style"] == 0:
            lazy[(r["depth"], r["seed"])] = r

    out = {}
    for d in sorted({r["depth"] for r in rows}):
        rs = [r for r in rows if r["depth"] == d]
        n = len(rs)
        pe = [r["plan_execute"] for r in rs]
        tw = [r["twin_plan_execute"] for r in rs]
        oo = [r["oracle_ops"] for r in rs]
        too = [r["twin_oracle_ops"] for r in rs]

        differs = [r for r in rs if r["twin_differs"]]
        both = sum(1 for r in rs
                   if r["twin_differs"] and r["plan_execute"]["ok"]
                   and r["twin_plan_execute"]["ok"])
        one = sum(1 for r in rs
                  if r["twin_differs"] and (r["plan_execute"]["ok"]
                                            ^ r["twin_plan_execute"]["ok"]))
        neither = sum(1 for r in rs
                      if r["twin_differs"] and not r["plan_execute"]["ok"]
                      and not r["twin_plan_execute"]["ok"])
        same_text = sum(1 for r in rs
                        if r["plan_execute"]["plan"] == r["twin_plan_execute"]["plan"])
        same_text_differs = sum(1 for r in rs if r["twin_differs"]
                                and r["plan_execute"]["plan"]
                                == r["twin_plan_execute"]["plan"])
        dbl_same_text = sum(1 for r in rs if r["twin_differs"]
                            and r["plan_execute"]["plan"]
                            == r["twin_plan_execute"]["plan"]
                            and r["plan_execute"]["ok"]
                            and r["twin_plan_execute"]["ok"])

        # What did the written plan compute?
        what = Counter()
        for r in rs:
            v = r["plan_execute"]["value"]
            if v is None:
                what["no_value"] += 1
            elif v == r["left_answer"] and v == r["right_answer"]:
                what["both_folds_agree"] += 1
            elif v == r["left_answer"]:
                what["left_fold"] += 1
            elif v == r["right_answer"]:
                what["right_fold"] += 1
            else:
                what["neither_fold"] += 1

        # Associativity: what the page says, what induction produced, whether
        # accuracy splits on it.
        ind_ok = sum(1 for r in rs if r["induced_assoc"] == r["assoc"])
        by_assoc = defaultdict(lambda: [0, 0])
        for r in rs:
            b = by_assoc[r["assoc"]]
            b[0] += 1
            b[1] += int(r["plan_execute"]["ok"])
        by_ind = defaultdict(lambda: [0, 0])
        for r in rs:
            b = by_ind[str(r["induced_assoc"])]
            b[0] += 1
            b[1] += int(r["plan_execute"]["ok"])

        # Check 2 against what was written: a plan with fewer steps than the
        # question has operators cannot have composed the question.
        steps = Counter(r["plan_execute"]["steps"] for r in rs)
        short_ok = sum(1 for r in rs
                       if r["plan_execute"]["ok"]
                       and (r["plan_execute"]["steps"] or 0) < d)
        full_n = sum(1 for r in rs if (r["plan_execute"]["steps"] or 0) == d)
        full_ok = sum(1 for r in rs
                      if r["plan_execute"]["ok"]
                      and (r["plan_execute"]["steps"] or 0) == d)
        # collision-free subset: answer not reachable by truncating the chain,
        # not equal to an intermediate, not equal to an operand.
        cf, cf_ok = 0, 0
        col, col_ok = 0, 0
        for r in rs:
            g = lazy.get((d, r["seed"]))
            if g is None:
                continue
            hit = (r["gold"] in g["truncations"] or r["gold"] in g["intermediates"]
                   or r["gold"] in g["operands"])
            if hit:
                col += 1
                col_ok += int(r["plan_execute"]["ok"])
            else:
                cf += 1
                cf_ok += int(r["plan_execute"]["ok"])

        out[str(d)] = {
            "n": n,
            "plan_execute": round(sum(x["ok"] for x in pe) / n, 4),
            "oracle_ops": round(sum(x["ok"] for x in oo) / n, 4),
            "twin_plan_execute": round(sum(x["ok"] for x in tw) / n, 4),
            "twin_oracle_ops": round(sum(x["ok"] for x in too) / n, 4),
            "pair_sum": round((sum(x["ok"] for x in pe)
                               + sum(x["ok"] for x in tw)) / n, 4),
            "pairs_with_different_gold": len(differs),
            "pair_both_correct": both,
            "pair_exactly_one_correct": one,
            "pair_neither_correct": neither,
            "pair_identical_plan_text": same_text,
            "pair_identical_plan_text_and_different_gold": same_text_differs,
            "double_credited_identical_text": dbl_same_text,
            "what_the_plan_computed": dict(what),
            "induced_assoc_matches_page": round(ind_ok / n, 4),
            "acc_by_page_assoc": {k: [v[0], v[1], round(v[1] / max(1, v[0]), 4)]
                                  for k, v in by_assoc.items()},
            "acc_by_induced_assoc": {k: [v[0], v[1], round(v[1] / max(1, v[0]), 4)]
                                     for k, v in by_ind.items()},
            "plan_step_counts": {str(k): v for k, v in sorted(
                steps.items(), key=lambda kv: (kv[0] is None, kv[0]))},
            "correct_with_short_plan": short_ok,
            "n_full_length_plan": full_n,
            "correct_with_full_length_plan": full_ok,
            "collision_items": col, "collision_items_correct": col_ok,
            "collision_free_items": cf, "collision_free_correct": cf_ok,
            "acc_collision_free": round(cf_ok / max(1, cf), 4),
        }
        o = out[str(d)]
        print(f"d{d}: pe={o['plan_execute']} twin={o['twin_plan_execute']} "
              f"sum={o['pair_sum']} both={both} one={one} neither={neither} "
              f"identical_text={same_text} dbl={dbl_same_text}")
        print(f"     computed {dict(what)}")
        print(f"     induced_assoc_ok={o['induced_assoc_matches_page']} "
              f"acc_by_page_assoc={o['acc_by_page_assoc']}")
        print(f"     steps={o['plan_step_counts']} short_ok={short_ok} "
              f"full_n={full_n} full_ok={full_ok}")
        print(f"     collision_free {cf_ok}/{cf} = {o['acc_collision_free']} | "
              f"collision {col_ok}/{col}")

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"\n[written] {args.out}")


if __name__ == "__main__":
    main()
