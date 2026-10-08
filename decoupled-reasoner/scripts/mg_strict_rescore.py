"""Regrade dumped rollouts under a forced-choice rule and report the floors.

The shipped environment grader in `src/rl/env.py` accepts any prediction that
CONTAINS the gold string with six tokens of slack. One rule family on this
project reached 0.985 under that rule by naming both candidates, and fell to
0.009 once naming more than one counted as wrong. So every accuracy here is
reported twice, and the hedge rate is reported beside it.

    acc_shipped   the environment grader, as recorded in the rollout row
    acc_forced    the named candidate set equals the gold set exactly
    acc_first     the first |gold| distinct candidates named are the gold set
    hedge_rate    more distinct candidates named than the answer has
    none_rate     no candidate named at all

Candidates come from the item, never from the prediction. A mathgen exercise
answers with an object name, a comma separated list of object names, or a
count, so its candidate alphabet is the carrier of its own universe plus the
counts zero to the carrier size. A skillacq problem's alphabet is the family's
answer set, which `src.falsify.probe.candidates` already defines.

Chance is the item's own guessing floor: the mathgen answer key records
`necessity.guess_space` per exercise, and a skillacq item's floor is one over
its own alphabet. A cell's floor is the mean of its items' floors.

Two chance corrections are reported wherever cells are averaged, because they
differ and have been conflated on this project once already:

    corrected_of_macro   (mean_acc - mean_chance) / (1 - mean_chance)
    macro_of_corrected   mean over cells of (acc_c - chance_c) / (1 - chance_c)

Nothing is ever grouped across `answer_source`.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from collections import defaultdict

# ------------------------------------------------------------------ graders


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def named(answer: str, cands: list[str]) -> list[str]:
    """Distinct candidates named by the answer, in order of first appearance.

    Whole token match, so `korrvex` does not match inside `korrvexes` and the
    count `1` does not match inside `12`.
    """
    a = _norm(answer)
    hits = []
    for c in cands:
        c = c.lower()
        m = re.search(rf"(?<![a-z0-9]){re.escape(c)}(?![a-z0-9])", a)
        if m:
            hits.append((m.start(), c))
    hits.sort()
    seen, out = set(), []
    for _, c in hits:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def grade(prediction: str, gold: str, cands: list[str]) -> dict:
    gold_named = named(gold, cands)
    gold_set = set(gold_named)
    pred_named = named(prediction, cands)
    n_gold = max(1, len(gold_set))
    return {
        "n_candidates": len(cands),
        "n_gold_named": len(gold_set),
        "n_pred_named": len(pred_named),
        "forced": bool(gold_set) and set(pred_named) == gold_set,
        "first": bool(gold_set) and set(pred_named[:n_gold]) == gold_set,
        "hedge": len(pred_named) > n_gold,
        "none_named": len(pred_named) == 0,
    }


# --------------------------------------------------------------- alphabets


def mathgen_alphabets(universe_root: str, seeds: list[int]) -> dict:
    """seed -> {"cands": [...], "guess": {qid: 1/guess_space}, "kind": {...}}."""
    from src.mathgen import theory as th_mod

    out = {}
    for seed in seeds:
        udir = os.path.join(universe_root, f"u{seed:04d}")
        with open(os.path.join(udir, "answer_key.json"), encoding="utf-8") as fh:
            key = json.load(fh)
        elements = list(th_mod.build(seed).structure.elements)
        counts = [str(i) for i in range(len(elements) + 1)]
        guess, kind = {}, {}
        for ex in key["exercises"]:
            space = int(ex["necessity"]["guess_space"])
            guess[ex["exercise_id"]] = 1.0 / space if space else float("nan")
            kind[ex["exercise_id"]] = ex["answer_kind"]
        out[seed] = {"elements": elements, "counts": counts,
                     "guess": guess, "kind": kind}
    return out


def gate_alphabets(episodes_dir: str, families: list[str]) -> dict:
    """(family, episode line) -> candidate list, via the family's own answer set."""
    import random

    from src.falsify.probe import candidates as cand_of
    from src.skillacq.systems import _all_families

    pool = _all_families()
    out = {}
    for fam in families:
        path = os.path.join(episodes_dir, f"ep_{fam}.jsonl")
        with open(path, encoding="utf-8") as fh:
            for line_no, line in enumerate(fh):
                if not line.strip():
                    continue
                seed = json.loads(line)["seed"]
                sysobj = pool[fam](random.Random(seed))
                out[(fam, line_no)] = [str(c) for c in cand_of(sysobj)]
    return out


# ------------------------------------------------------------------- cells


def cell(rows: list[dict]) -> dict:
    by_q = defaultdict(list)
    for r in rows:
        by_q[(r["condition"], r["episode_index"], r["qid"])].append(r)
    n_q, n_r = len(by_q), len(rows)

    def mean(field):
        return sum(float(r[field]) for r in rows) / n_r if n_r else float("nan")

    def anyq(field):
        return (sum(1 for v in by_q.values() if any(x[field] for x in v))
                / n_q) if n_q else float("nan")

    floors = {}
    for r in rows:
        floors[(r["condition"], r["episode_index"], r["qid"])] = r["chance"]
    finite = [v for v in floors.values() if not math.isnan(v)]
    ch = sum(finite) / len(finite) if finite else float("nan")

    def corrected(acc):
        if math.isnan(ch) or ch >= 1.0:
            return float("nan")
        return (acc - ch) / (1.0 - ch)

    acc_forced = mean("forced")
    acc_shipped = mean("correct")
    return {
        "n_questions": n_q,
        "n_rollouts": n_r,
        "samples_per_question": min(len(v) for v in by_q.values()) if by_q else 0,
        "chance": ch,
        "mean_candidates": mean("n_candidates"),
        "acc_shipped": acc_shipped,
        "acc_forced": acc_forced,
        "acc_first": mean("first"),
        "acc_strict_em": mean("strict_em"),
        "acc_shipped_at_k": anyq("correct"),
        "acc_forced_at_k": anyq("forced"),
        "corrected_shipped": corrected(acc_shipped),
        "corrected_forced": corrected(acc_forced),
        "hedge_rate": mean("hedge"),
        "none_named_rate": mean("none_named"),
        "mean_pred_named": mean("n_pred_named"),
        "mean_rounds": mean("n_rounds"),
        "any_retrieval": mean("any_retrieval"),
        "well_formed": mean("well_formed"),
        "degenerate_query_rate": (sum(1 for r in rows
                                      if r["degenerate_queries"] > 0) / n_r)
        if n_r else float("nan"),
        "answer_in_retrieved": mean("answer_in_retrieved"),
        "answer_in_library": mean("answer_in_library"),
        "empty_answer_rate": sum(1 for r in rows
                                 if not (r["prediction"] or "").strip()) / n_r,
        "stop_reasons": {s: sum(1 for r in rows if r["stop_reason"] == s)
                         for s in sorted({r["stop_reason"] for r in rows})},
    }


def macro(cells: dict, keys: list[str], field: str) -> dict:
    """Both aggregation orders, with the formulas they came from."""
    accs = [cells[k][field] for k in keys]
    chs = [cells[k]["chance"] for k in keys]
    good = [(a, c) for a, c in zip(accs, chs)
            if not (math.isnan(a) or math.isnan(c) or c >= 1.0)]
    if not good:
        return {}
    ma = sum(a for a, _ in good) / len(good)
    mc = sum(c for _, c in good) / len(good)
    return {
        "cells": len(good),
        "macro_accuracy": ma,
        "macro_chance": mc,
        "corrected_of_macro": (ma - mc) / (1.0 - mc),
        "macro_of_corrected": sum((a - c) / (1.0 - c) for a, c in good) / len(good),
        "formula_corrected_of_macro": "(mean_acc - mean_chance)/(1 - mean_chance)",
        "formula_macro_of_corrected": "mean_c[(acc_c - chance_c)/(1 - chance_c)]",
    }


# -------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollouts", nargs="+", required=True)
    ap.add_argument("--suite", choices=["gate", "mathgen"], required=True)
    ap.add_argument("--episodes-dir", required=True)
    ap.add_argument("--universes", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--graded-out", default="", help="per-rollout graded jsonl")
    args = ap.parse_args()

    rows = []
    for path in args.rollouts:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    rows.append(json.loads(line))
    if not rows:
        print("no rollouts")
        return 1

    if args.suite == "gate":
        fams = sorted({r["condition"] for r in rows})
        alpha = gate_alphabets(args.episodes_dir, fams)
        for r in rows:
            cands = alpha[(r["condition"], r["episode_index"])]
            r.update(grade(r["prediction"], r["gold"], cands))
            r["chance"] = 1.0 / len(cands) if cands else float("nan")
    else:
        seeds = sorted({int(r["seed"]) for r in rows if r.get("seed") is not None})
        alpha = mathgen_alphabets(args.universes, seeds)
        for r in rows:
            a = alpha[int(r["seed"])]
            kind = r.get("answer_kind") or a["kind"].get(r["qid"], "object")
            cands = a["counts"] if kind == "count" else a["elements"]
            r.update(grade(r["prediction"], r["gold"], cands))
            r["chance"] = a["guess"].get(r["qid"], float("nan"))

    if args.graded_out:
        with open(args.graded_out, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps({k: r[k] for k in (
                    "suite", "condition", "decode", "sample_index", "seed",
                    "episode_index", "qid", "level", "answer_source",
                    "answer_kind", "gold", "prediction", "correct", "forced",
                    "first", "hedge", "none_named", "chance", "n_candidates",
                    "n_rounds", "any_retrieval", "well_formed",
                    "degenerate_queries", "answer_in_retrieved",
                    "answer_in_library", "stop_reason")}) + "\n")

    groups: dict = defaultdict(list)
    for r in rows:
        base = (r["suite"], r["condition"], r["decode"])
        if args.suite == "mathgen":
            src = r.get("answer_source") or "unlabelled"
            groups[base + (src, "all")].append(r)
            groups[base + (src, f"level{r.get('level')}")].append(r)
            groups[base + (src, f"kind:{r.get('answer_kind')}")].append(r)
        else:
            groups[base + ("n/a", "all")].append(r)

    cells = {"|".join(str(k) for k in key): cell(groups[key])
             for key in sorted(groups)}

    report = {"cells": cells, "macro": {}}
    if args.suite == "mathgen":
        for cond in sorted({r["condition"] for r in rows}):
            for dec in sorted({r["decode"] for r in rows}):
                for src in sorted({r.get("answer_source") or "unlabelled"
                                   for r in rows}):
                    keys = [k for k in cells
                            if k.startswith(f"mathgen|{cond}|{dec}|{src}|level")]
                    if keys:
                        report["macro"][f"{cond}|{dec}|{src}|over_levels"] = {
                            "shipped": macro(cells, keys, "acc_shipped"),
                            "forced": macro(cells, keys, "acc_forced")}

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

    width = max(len(k) for k in cells)
    print(f"{'cell'.ljust(width)}  {'nQ':>5} {'nR':>6} {'floor':>6} "
          f"{'ship':>6} {'forced':>6} {'first':>6} {'c_ship':>7} {'c_frc':>7} "
          f"{'hedge':>6} {'none':>6} {'rnds':>5} {'anyret':>6} {'wf':>6} "
          f"{'degen':>6}")
    for k, c in cells.items():
        print(f"{k.ljust(width)}  {c['n_questions']:>5} {c['n_rollouts']:>6} "
              f"{c['chance']:>6.3f} {c['acc_shipped']:>6.3f} "
              f"{c['acc_forced']:>6.3f} {c['acc_first']:>6.3f} "
              f"{c['corrected_shipped']:>7.3f} {c['corrected_forced']:>7.3f} "
              f"{c['hedge_rate']:>6.3f} {c['none_named_rate']:>6.3f} "
              f"{c['mean_rounds']:>5.2f} {c['any_retrieval']:>6.3f} "
              f"{c['well_formed']:>6.3f} {c['degenerate_query_rate']:>6.3f}")
    for k, m in report["macro"].items():
        for which, v in m.items():
            if v:
                print(f"macro {k} {which}: cells {v['cells']} "
                      f"acc {v['macro_accuracy']:.4f} floor {v['macro_chance']:.4f} "
                      f"corrected_of_macro {v['corrected_of_macro']:.4f} "
                      f"macro_of_corrected {v['macro_of_corrected']:.4f}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
