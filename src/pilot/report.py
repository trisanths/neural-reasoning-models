"""The pilot report: per-cell tables from stored records, and the preregistered decision.

Nothing here touches a model. Every generation record is regraded from its
stored text with src/pilot/grade.py as it stands when the report is built, so
a grading change costs a rerun of this file and not of the GPU; how many
stored grades the regrade overturned is printed.

Freshness, after the rule FRAMES.md and RETRAIN.md enforce for the score
files (a report must never quote records it cannot vouch for). The builder
refuses, writes nothing and exits non-zero when:

  - any RUNNING*.lock is present in the records directory (the run loop or
    one model is still writing);
  - any records file is newer than the moment this build started, or
    changes while it is being read (records newer than the report);
  - a record's items_sha or prompt_hash disagrees with the current item
    file, or a PopQA record's popqa_sha with the current PopQA file
    (records from an earlier generation of the items);
  - one configuration's records were written at more than one git commit,
    unless --allow-mixed-commits says that was meant;
  - a key (model, thinking, item, condition) appears twice;
  - the hedging canary scores above zero under the strict grader.

A records file older than the item file it matches by hash is reported as a
warning, not refused: the hash already proves which items it scored.

A verdict other than "not reached" needs every configuration in
src/pilot/vllm_model.MODELS (each model with each of its thinking modes) to
have a record for every item and condition, and every model to have a PopQA
record for every PopQA item. Models whose child exited non-zero in
run_log.jsonl are listed.

Every accuracy is printed with its denominator, its Wilson interval, the
mean per-item floor of the cell in that condition, the best-constant rate
of the cell (the share of its commonest gold), the hedge rate, the lenient
score and the rate of replies naming any candidate. Nothing is pooled across
families. The decision follows the rules in PREREGISTERED.md, section
"Acquisition pilot", with rule 1 as amended there on 2026-10-06.

  python scripts/pilot_report.py --items .../items.jsonl \\
      --popqa .../popqa_fc.jsonl --records .../records --out .../report
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict

from src.extern.stats import mcnemar, wilson
from src.pilot.grade import canary_reply, grade
from src.pilot.items import file_sha, load_items

VALIDITY_SLACK = 0.03
VALIDITY_ALPHA = 0.05
GO_GAP = 0.20
GO_CELLS = 2
POPQA_MARGIN = 0.15
POPQA_FLOOR = 0.25
BASE_CANDIDATES = ("lfm2.5-350m-base", "qwen3-0.6b-base")
FALLBACK = "qwen3-1.7b-base"
RECORDED_LEVELS = (4, 5, 6, 7, 8)
# Cells a reader can clear by matching the question's key word against the
# page and copying the label printed beside it.
LOOKUP_CELLS = ("threshold_rule", "substitution_rule", "exception_rule")
GRADE_FIELDS = ("answer_line", "answer_found", "answered", "parsed", "n_named",
                "hedge", "correct", "correct_lenient")


class Refusal(Exception):
    pass


def expected_configs() -> list[tuple[str, bool]]:
    """Every (model, thinking) the plan runs: each model, each thinking mode."""
    from src.pilot.vllm_model import MODELS

    return [(s.name, t) for s in MODELS.values() for t in s.thinking_modes]


def expected_models() -> list[str]:
    from src.pilot.vllm_model import MODELS

    return list(MODELS)


def config_key(model: str, thinking: bool) -> str:
    return f"{model}|think{int(thinking)}"


# --------------------------------------------------------------------------
# loading, with the freshness rules
# --------------------------------------------------------------------------
def _read(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _locks(records_dir: str) -> list[str]:
    return sorted(n for n in os.listdir(records_dir)
                  if n.startswith("RUNNING") and n.endswith(".lock"))


def load_records(records_dir: str, items_path: str, popqa_path: str,
                 started: float, allow_mixed_commits: bool = False) -> dict:
    locks = _locks(records_dir)
    if locks:
        raise Refusal(f"{locks} present in {records_dir}: a run is still "
                      f"writing records")
    items = {it["item_id"]: it for it in load_items(items_path)}
    items_sha = file_sha(items_path)
    items_mtime = os.path.getmtime(items_path)
    popqa = {it["item_id"]: it for it in load_items(popqa_path)}
    popqa_sha = file_sha(popqa_path)
    popqa_mtime = os.path.getmtime(popqa_path)

    names = sorted(n for n in os.listdir(records_dir)
                   if n.endswith(".jsonl") and n.startswith(("gen__", "popqa__")))
    mtimes = {n: os.path.getmtime(os.path.join(records_dir, n)) for n in names}
    gen, pq, warnings = [], [], []
    regrade = Counter()
    for n in names:
        path = os.path.join(records_dir, n)
        if mtimes[n] > started:
            raise Refusal(f"{n} is newer than this report build "
                          f"({mtimes[n]:.0f} > {started:.0f})")
        is_pq = n.startswith("popqa__")
        source_mtime = popqa_mtime if is_pq else items_mtime
        if mtimes[n] < source_mtime:
            warnings.append(f"{n} is older than its item file; its records "
                            f"match the file by hash, so they are used")
        rows = _read(path)
        if is_pq:
            for r in rows:
                if r["popqa_sha"] != popqa_sha or r["item_id"] not in popqa:
                    raise Refusal(f"{n}: record {r['item_id']} is from another "
                                  f"PopQA item file")
            pq.extend(rows)
            continue
        for r in rows:
            it = items.get(r["item_id"])
            if (r["items_sha"] != items_sha or it is None or
                    it["prompt_hashes"][r["condition"]] != r["prompt_hash"]):
                raise Refusal(f"{n}: record {r['item_id']}/{r['condition']} "
                              f"is from another item file")
            g = grade(r["text"], it, completion=(r["kind"] == "base"))
            for f in ("correct", "hedge", "correct_lenient"):
                if f in r and bool(r[f]) != bool(g[f]):
                    regrade[f] += 1
            regrade["records"] += 1
            r.update({f: g[f] for f in GRADE_FIELDS})
            r["floor"] = (it.get("floors") or {}).get(r["condition"], it["floor"])
        gen.extend(rows)
    for n in names:
        if os.path.getmtime(os.path.join(records_dir, n)) != mtimes[n]:
            raise Refusal(f"{n} changed while the report was reading it")

    keys = Counter((r["model"], r["thinking"], r["item_id"], r["condition"])
                   for r in gen)
    dup = [k for k, v in keys.items() if v > 1]
    if dup:
        raise Refusal(f"{len(dup)} duplicated generation keys, e.g. {dup[0]}")
    pkeys = Counter((r["model"], r["item_id"]) for r in pq)
    pdup = [k for k, v in pkeys.items() if v > 1]
    if pdup:
        raise Refusal(f"{len(pdup)} duplicated PopQA keys, e.g. {pdup[0]}")

    commits = commit_spread(gen, pq)
    mixed = {k: v for k, v in commits.items() if len(v) > 1}
    if mixed and not allow_mixed_commits:
        raise Refusal(f"records of {sorted(mixed)} were written at more than "
                      f"one commit ({mixed}); rerun them or pass "
                      f"--allow-mixed-commits")

    return {"items": items, "popqa": popqa, "gen": gen, "pq": pq,
            "regrade": dict(regrade), "commits": commits,
            "freshness": {"started_utc": _utc(started),
                          "items": {"path": items_path, "sha256": items_sha,
                                    "mtime_utc": _utc(items_mtime)},
                          "popqa": {"path": popqa_path, "sha256": popqa_sha,
                                    "mtime_utc": _utc(popqa_mtime)},
                          "records": {n: _utc(t) for n, t in mtimes.items()},
                          "warnings": warnings}}


def commit_spread(gen: list[dict], pq: list[dict]) -> dict:
    out: dict = defaultdict(set)
    for r in gen:
        out[config_key(r["model"], r["thinking"])].add(r.get("git_head"))
    for r in pq:
        out[f"{r['model']}|popqa"].add(r.get("git_head"))
    return {k: sorted(v, key=str) for k, v in sorted(out.items())}


def _utc(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def canary_check(items: dict) -> dict:
    """Every item answered with every candidate at once must score zero."""
    n = hits = 0
    for it in items.values():
        g = grade(canary_reply(it), it)
        n += 1
        hits += g["correct"]
    if hits:
        raise Refusal(f"hedging canary scored {hits}/{n} under the strict grader")
    return {"n": n, "strict_correct": hits}


def run_log_failures(records_dir: str) -> dict:
    """The last run_log.jsonl entry of each model whose child exited non-zero."""
    path = os.path.join(records_dir, "run_log.jsonl")
    if not os.path.exists(path):
        return {}
    last = {}
    for r in _read(path):
        last[r["model"]] = r
    return {m: r for m, r in last.items() if r.get("exit") != 0}


# --------------------------------------------------------------------------
# the tail probabilities rule 1 uses
# --------------------------------------------------------------------------
def binom_upper_p(k: int, n: int, p: float) -> float:
    """P[X >= k] for X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i)
                                       for i in range(k))))


def poisson_binomial_upper(k: int, probs: list[float]) -> float:
    """P[X >= k] for X the number of successes of independent Bernoulli(p_i)."""
    if k <= 0:
        return 1.0
    dist = [1.0]
    for p in probs:
        p = min(1.0, max(0.0, p))
        nxt = [0.0] * (len(dist) + 1)
        for j, d in enumerate(dist):
            nxt[j] += d * (1 - p)
            nxt[j + 1] += d * p
        dist = nxt
    return max(0.0, min(1.0, sum(dist[k:])))


def holm(pvals: dict, alpha: float) -> set:
    """Keys Holm's step-down procedure rejects at family-wise level alpha."""
    order = sorted(pvals, key=lambda key: (pvals[key], str(key)))
    m = len(order)
    out = set()
    for j, key in enumerate(order):
        if pvals[key] <= alpha / (m - j):
            out.add(key)
        else:
            break
    return out


# --------------------------------------------------------------------------
# cells
# --------------------------------------------------------------------------
def cell_name(family: str, level) -> str:
    return family if level is None else f"{family}/L{level}"


def majority_rates(items: dict) -> dict:
    """The share of each cell's commonest gold: the best constant answer."""
    by: dict = defaultdict(Counter)
    for it in items.values():
        key = (it["family"], it["level"])
        if it["answer_kind"] == "names" and it["family"] != "algebra":
            by[key][it["candidates"].index(it["answer"])] += 1
        else:
            by[key][it["answer"].strip().lower()] += 1
    return {k: c.most_common(1)[0][1] / sum(c.values()) for k, c in by.items()}


def gen_cells(gen: list[dict], items: dict) -> dict:
    maj = majority_rates(items)
    acc: dict = defaultdict(list)
    for r in gen:
        acc[(r["model"], r["thinking"], r["family"], r["level"],
             r["condition"])].append(r)
    out = {}
    for key, rows in acc.items():
        model, thinking, fam, lv, cond = key
        n = len(rows)
        k = sum(r["correct"] for r in rows)
        lo, hi = wilson(k, n)
        floors = [r["floor"] for r in rows]
        floor = sum(floors) / n
        out[key] = {
            "model": model, "thinking": thinking, "family": fam, "level": lv,
            "cell": cell_name(fam, lv), "condition": cond, "n": n, "k": k,
            "acc": k / n, "wilson_lo": lo, "wilson_hi": hi, "floor": floor,
            "item_floors": floors,
            "majority": maj.get((fam, lv)),
            "hedge": sum(r["hedge"] for r in rows) / n,
            "lenient": sum(r["correct_lenient"] for r in rows) / n,
            "answer_found": sum(r["answer_found"] for r in rows) / n,
            "answered": sum(r["answered"] for r in rows) / n,
            "think_truncated": sum(r["think_truncated"] for r in rows) / n,
            "mean_think_tokens": sum(r["n_think_tokens"] for r in rows) / n,
            # P[count >= k] for a reader at each item's floor, no slack.
            "p_at_or_above_floor": poisson_binomial_upper(k, floors),
        }
    return out


def paired_gap(gen: list[dict], model, thinking, fam, lv, a: str, b: str) -> dict:
    """acc(a) - acc(b) on the items both conditions answered, with McNemar."""
    ra = {r["item_id"]: r["correct"] for r in gen
          if (r["model"], r["thinking"], r["family"], r["level"], r["condition"])
          == (model, thinking, fam, lv, a)}
    rb = {r["item_id"]: r["correct"] for r in gen
          if (r["model"], r["thinking"], r["family"], r["level"], r["condition"])
          == (model, thinking, fam, lv, b)}
    common = sorted(set(ra) & set(rb))
    if not common:
        return {"n": 0, "gap": None, "p": None}
    xa = [ra[i] for i in common]
    xb = [rb[i] for i in common]
    a_only = sum(1 for x, y in zip(xa, xb) if x and not y)
    b_only = sum(1 for x, y in zip(xa, xb) if y and not x)
    return {"n": len(common), "acc_a": sum(xa) / len(common),
            "acc_b": sum(xb) / len(common),
            "gap": (sum(xa) - sum(xb)) / len(common),
            "a_only": a_only, "b_only": b_only,
            "p": round(mcnemar(a_only, b_only), 4)}


def popqa_cells(pq: list[dict]) -> dict:
    by: dict = defaultdict(list)
    for r in pq:
        by[(r["model"], "all")].append(r)
        by[(r["model"], f"Q{r['quartile']}")].append(r)
    out = {}
    for (model, band), rows in by.items():
        n = len(rows)
        k = sum(r["correct"] for r in rows)
        lo, hi = wilson(k, n)
        masked = [r["correct_masked"] for r in rows if "correct_masked" in r]
        out[(model, band)] = {
            "model": model, "band": band, "n": n, "k": k, "acc": k / n,
            "wilson_lo": lo, "wilson_hi": hi, "floor": POPQA_FLOOR,
            "margin": k / n - POPQA_FLOOR,
            "acc_masked": (sum(masked) / len(masked)) if masked else None,
            "n_masked": len(masked),
            "acc_summed_nll": sum(r["correct_summed_nll"] for r in rows) / n}
    return out


# --------------------------------------------------------------------------
# the preregistered decision
# --------------------------------------------------------------------------
def completeness(gen: list[dict], items: dict, conditions) -> dict:
    """Every expected configuration, with the ones that have no records."""
    have: dict = defaultdict(set)
    for r in gen:
        have[(r["model"], r["thinking"])].add((r["item_id"], r["condition"]))
    want = {(i, c) for i in items for c in conditions}
    configs = list(expected_configs())
    configs += [k for k in sorted(have) if k not in configs]
    return {config_key(m, t): {"records": len(have.get((m, t), ())),
                               "expected": len(want),
                               "complete": have.get((m, t), set()) == want}
            for m, t in configs}


def popqa_completeness(pq: list[dict], popqa: dict) -> dict:
    have: dict = defaultdict(set)
    for r in pq:
        have[r["model"]].add(r["item_id"])
    want = set(popqa)
    models = expected_models() + sorted(m for m in have
                                        if m not in expected_models())
    return {m: {"records": len(have.get(m, ())), "expected": len(want),
                "complete": have.get(m, set()) == want} for m in models}


def rule_validity(cells: dict, slack: float | None = None,
                  alpha: float | None = None) -> dict:
    """Rule 1 as amended on 2026-10-06, and as first registered beside it.

    Amended (gating): in every closed-book and blank cell, the exact
    probability that readers at each item's floor plus the slack get at
    least the observed count; a cell fails when Holm's procedure across
    every closed-book and blank cell rejects it at family-wise alpha.

    As registered (printed, not gating): the Wilson upper bound of the
    cell's accuracy is at most its mean floor plus the slack.
    """
    slack = VALIDITY_SLACK if slack is None else slack
    alpha = VALIDITY_ALPHA if alpha is None else alpha
    checked = {key: c for key, c in cells.items()
               if c["condition"] in ("closed_book", "blank")}
    pvals = {key: poisson_binomial_upper(c["k"], [f + slack for f in
                                                  c["item_floors"]])
             for key, c in checked.items()}
    rejected = holm(pvals, alpha)
    fields = ("model", "thinking", "cell", "condition", "n", "k", "acc",
              "wilson_hi", "floor", "p_at_or_above_floor")
    fails = [{**{f: checked[key][f] for f in fields}, "p_amended": pvals[key]}
             for key in sorted(rejected, key=lambda k: (pvals[k], str(k)))]
    registered_fails = [
        {**{f: c[f] for f in fields}, "p_amended": pvals[key]}
        for key, c in sorted(checked.items(), key=lambda kv: str(kv[0]))
        if c["wilson_hi"] > c["floor"] + slack + 1e-12]
    smallest = min(pvals.values()) if pvals else None
    return {"rule": "(1) validity, amended 2026-10-06",
            "cells_checked": len(checked), "alpha": alpha, "slack": slack,
            "smallest_p": smallest,
            "passed": bool(checked) and not fails, "failures": fails,
            "as_registered": {"rule": "Wilson upper bound <= floor + slack",
                              "cells_failing": len(registered_fails),
                              "failures": registered_fails}}


def rule_go_for(model: str, cells: dict, gen: list[dict], pqc: dict,
                complete: dict, pq_complete: dict) -> dict:
    key = config_key(model, False)
    rows = []
    for c in cells.values():
        if (c["model"], c["thinking"], c["condition"]) != (model, False, "oracle"):
            continue
        g = paired_gap(gen, model, False, c["family"], c["level"],
                       "oracle", "sibling")
        if g["gap"] is None:
            continue
        rows.append({"cell": c["cell"], "family": c["family"], **g,
                     "qualifies": g["gap"] >= GO_GAP})
    rows.sort(key=lambda r: r["cell"])
    q = [r["cell"] for r in rows if r["qualifies"]]
    lookup_only = bool(q) and all(r["family"] in LOOKUP_CELLS
                                  for r in rows if r["qualifies"])
    pq = pqc.get((model, "all"))
    pq_full = pq_complete.get(model, {}).get("complete", False)
    pq_ok = pq_full and pq is not None and pq["margin"] >= POPQA_MARGIN
    have_all = complete.get(key, {}).get("complete", False) and pq_full
    return {"model": model, "complete": have_all, "cells": rows,
            "qualifying_cells": q, "cells_ok": len(q) >= GO_CELLS,
            "qualifying_cells_all_lookup": lookup_only,
            "popqa_acc": pq["acc"] if pq else None,
            "popqa_acc_masked": pq["acc_masked"] if pq else None,
            "popqa_margin": pq["margin"] if pq else None,
            "popqa_complete": pq_full,
            "popqa_ok": pq_ok,
            "passes": have_all and len(q) >= GO_CELLS and pq_ok}


def recorded_gains(gen: list[dict]) -> dict:
    """Thinking gain at 1.7B and the 1.7B to 8B gain, refuniverse L4-L8, oracle."""
    def gap(m_a, t_a, m_b, t_b):
        per = []
        for lv in RECORDED_LEVELS:
            a = {r["item_id"]: r["correct"] for r in gen
                 if (r["model"], r["thinking"], r["family"], r["level"],
                     r["condition"]) == (m_a, t_a, "refuniverse", lv, "oracle")}
            b = {r["item_id"]: r["correct"] for r in gen
                 if (r["model"], r["thinking"], r["family"], r["level"],
                     r["condition"]) == (m_b, t_b, "refuniverse", lv, "oracle")}
            common = sorted(set(a) & set(b))
            if not common:
                per.append({"level": lv, "n": 0, "gain": None})
                continue
            xa = [a[i] for i in common]
            xb = [b[i] for i in common]
            ao = sum(1 for x, y in zip(xa, xb) if x and not y)
            bo = sum(1 for x, y in zip(xa, xb) if y and not x)
            per.append({"level": lv, "n": len(common),
                        "acc_a": sum(xa) / len(common),
                        "acc_b": sum(xb) / len(common),
                        "gain": (sum(xa) - sum(xb)) / len(common),
                        "p": round(mcnemar(ao, bo), 4)})
        vals = [p["gain"] for p in per if p["gain"] is not None]
        return {"per_level": per,
                "macro_mean_of_level_gains": (sum(vals) / len(vals)
                                              if len(vals) == len(per) else None),
                "macro_formula": "mean over levels 4..8 of (acc_a - acc_b), "
                                 "each level on its own items"}
    return {
        "thinking_gain_1.7b": gap("qwen3-1.7b", True, "qwen3-1.7b", False),
        "scaling_gain_1.7b_to_8b_thinking_off": gap("qwen3-8b", False,
                                                    "qwen3-1.7b", False),
        "scaling_gain_1.7b_to_8b_thinking_on": gap("qwen3-8b", True,
                                                   "qwen3-1.7b", True),
        "gated": False,
    }


def decide(cells, gen, pqc, complete, pq_complete, failed_models=None) -> dict:
    validity = rule_validity(cells)
    go = {m: rule_go_for(m, cells, gen, pqc, complete, pq_complete)
          for m in BASE_CANDIDATES}
    fallback = rule_go_for(FALLBACK, cells, gen, pqc, complete, pq_complete)
    missing = [k for k, v in complete.items() if not v["complete"]]
    missing += [f"{m}|popqa" for m, v in pq_complete.items()
                if not v["complete"]]
    if missing:
        verdict = (f"not reached: rule 1 needs every configuration and rule 2 "
                   f"every PopQA record; incomplete: {missing}")
        if failed_models:
            verdict += f"; children that exited non-zero: {sorted(failed_models)}"
    elif not validity["passed"]:
        verdict = ("INVALID: rule (1) fails on "
                   f"{len(validity['failures'])} cells; the guard leaks. Fix it "
                   "and spend nothing else.")
    else:
        passing = [m for m in BASE_CANDIDATES if go[m]["passes"]]
        if len(passing) == 1:
            verdict = f"GO: {passing[0]} is the treatment base (rule 2)"
        elif len(passing) == 2:
            verdict = ("GO: both base candidates clear rule 2; the rule does not "
                       "choose between them, so the choice goes to the owner")
        elif fallback["passes"]:
            verdict = f"FALLBACK: {FALLBACK} is the treatment base (rule 3)"
        else:
            verdict = ("FAIL: nothing at 2B or below clears rule 2; the "
                       "small-reader premise fails on this instrument and the "
                       "paper becomes the size-ladder study (rule 3)")
        winners = passing or ([FALLBACK] if fallback["passes"] else [])
        for m in winners:
            g = go.get(m, fallback)
            verdict += f"; {m} qualifies on {g['qualifying_cells']}"
            if g["qualifying_cells_all_lookup"]:
                verdict += (" (every qualifying cell is a lookup rule family; "
                            "no refuniverse or algebra level qualifies)")
    return {"verdict": verdict, "validity": validity, "go": go,
            "fallback": fallback, "missing": missing}


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------
def _f(x, d=3):
    return "-" if x is None else f"{x:.{d}f}"


def _g(x):
    return "-" if x is None else f"{x:.2e}"


def render_md(rep: dict) -> str:
    from src.extern.stats import tbl

    fr = rep["freshness"]
    out = ["# Acquisition pilot report", "",
           f"Built {fr['started_utc']} from items "
           f"`{fr['items']['sha256'][:16]}` and PopQA "
           f"`{fr['popqa']['sha256'][:16]}`.", "",
           f"Decision: {rep['decision']['verdict']}", ""]
    for w in fr.get("warnings", []):
        out.append(f"Warning: {w}")
    rg = rep["regrade"]
    out += [f"Regraded {rg.get('records', 0)} generation records from their "
            f"stored text; the stored grade disagreed on correct "
            f"{rg.get('correct', 0)}, hedge {rg.get('hedge', 0)} and lenient "
            f"{rg.get('correct_lenient', 0)} times. Commits per configuration: "
            f"{rep['commits']}.", ""]
    if rep["failed_models"]:
        out += [f"Children that exited non-zero (run_log.jsonl): "
                f"{rep['failed_models']}", ""]
    v = rep["decision"]["validity"]
    out += ["## Rule 1, validity (amended 2026-10-06)", "",
            f"{v['cells_checked']} closed-book and blank cells checked. A cell "
            f"fails when Holm's procedure at family-wise {v['alpha']} rejects "
            f"the exact probability that readers at each item's floor plus "
            f"{v['slack']} get at least its count. {len(v['failures'])} fail. "
            f"Smallest p {_g(v['smallest_p'])}.", ""]
    if v["failures"]:
        out.append(tbl(["model", "think", "cell", "cond", "n", "k", "acc",
                        "floor", "p (floor+slack)", "p (floor)"],
                       [[f["model"], int(f["thinking"]), f["cell"], f["condition"],
                         f["n"], f["k"], _f(f["acc"]), _f(f["floor"], 4),
                         _g(f["p_amended"]), _g(f["p_at_or_above_floor"])]
                        for f in v["failures"]]))
        out.append("")
    reg = v["as_registered"]
    out += [f"As first registered (Wilson upper bound at most floor + "
            f"{v['slack']}, not gating since the amendment): "
            f"{reg['cells_failing']} of {v['cells_checked']} cells fail.", ""]
    for title, g in [("Rule 2, " + m, rep["decision"]["go"][m])
                     for m in BASE_CANDIDATES] + \
            [("Rule 3, " + FALLBACK, rep["decision"]["fallback"])]:
        out += [f"## {title}", "",
                f"complete {g['complete']}; qualifying cells "
                f"{len(g['qualifying_cells'])} {g['qualifying_cells']}"
                f"{' (lookup families only)' if g['qualifying_cells_all_lookup'] else ''}; "
                f"PopQA acc {_f(g['popqa_acc'])} margin {_f(g['popqa_margin'])} "
                f"(subject masked {_f(g['popqa_acc_masked'])}); "
                f"passes {g['passes']}", ""]
        if g["cells"]:
            out.append(tbl(["cell", "n", "oracle", "sibling", "gap", "McNemar p"],
                           [[c["cell"], c["n"], _f(c["acc_a"]), _f(c["acc_b"]),
                             _f(c["gap"]), c["p"]] for c in g["cells"]]))
            out.append("")
    out += ["## Recorded, not gating", ""]
    for name, g in rep["recorded"].items():
        if name == "gated":
            continue
        out.append(f"{name}: macro {_f(g['macro_mean_of_level_gains'])} "
                   f"({g['macro_formula']})")
        out.append(tbl(["level", "n", "acc_a", "acc_b", "gain", "p"],
                       [[p["level"], p["n"], _f(p.get("acc_a")), _f(p.get("acc_b")),
                         _f(p["gain"]), p.get("p", "-")] for p in g["per_level"]]))
        out.append("")
    out += ["## PopQA forced choice", "",
            "masked is the same item with the subject replaced by X: what the "
            "relation and the options give without the entity.", "",
            tbl(["model", "band", "n", "acc", "wilson", "floor", "margin",
                 "masked", "acc (summed NLL, old rule)"],
                [[c["model"], c["band"], c["n"], _f(c["acc"]),
                  f"[{_f(c['wilson_lo'])}, {_f(c['wilson_hi'])}]", _f(c["floor"], 2),
                  _f(c["margin"]), _f(c["acc_masked"]), _f(c["acc_summed_nll"])]
                 for c in sorted(rep["popqa"], key=lambda c: (c["model"], c["band"]))]),
            "", "## Every generation cell", "",
            "acc is the strict forced-choice score; lenient is beside it, never "
            "instead of it. floor is the mean per-item floor in that condition; "
            "best_const is the share of the cell's commonest gold. answered is "
            "the rate of replies naming any candidate; ans_line the rate with "
            "an explicit answer line.", ""]
    rows = sorted(rep["cells"], key=lambda c: (c["model"], c["thinking"],
                                               c["family"], c["level"] or 0,
                                               c["condition"]))
    out.append(tbl(["model", "think", "cell", "cond", "n", "acc", "wilson",
                    "floor", "best_const", "hedge", "lenient", "answered",
                    "ans_line", "trunc"],
                   [[c["model"], int(c["thinking"]), c["cell"], c["condition"],
                     c["n"], _f(c["acc"]),
                     f"[{_f(c['wilson_lo'])}, {_f(c['wilson_hi'])}]",
                     _f(c["floor"], 4), _f(c["majority"]), _f(c["hedge"]),
                     _f(c["lenient"]), _f(c["answered"]), _f(c["answer_found"]),
                     _f(c["think_truncated"])] for c in rows]))
    out.append("")
    return "\n".join(out)


def build(items_path, popqa_path, records_dir, conditions=None,
          allow_mixed_commits: bool = False) -> dict:
    from src.pilot.items import CONDITIONS

    started = time.time()
    data = load_records(records_dir, items_path, popqa_path, started,
                        allow_mixed_commits)
    canary = canary_check(data["items"])
    cells = gen_cells(data["gen"], data["items"])
    pqc = popqa_cells(data["pq"])
    complete = completeness(data["gen"], data["items"], conditions or CONDITIONS)
    pq_complete = popqa_completeness(data["pq"], data["popqa"])
    failed = run_log_failures(records_dir)
    cell_rows = [{k: v for k, v in c.items() if k != "item_floors"}
                 for c in cells.values()]
    return {
        "freshness": data["freshness"],
        "regrade": data["regrade"],
        "commits": data["commits"],
        "canary": canary,
        "completeness": complete,
        "popqa_completeness": pq_complete,
        "failed_models": failed,
        "decision": decide(cells, data["gen"], pqc, complete, pq_complete,
                           failed),
        "recorded": recorded_gains(data["gen"]),
        "cells": cell_rows,
        "popqa": list(pqc.values()),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="build the pilot report")
    ap.add_argument("--items", required=True)
    ap.add_argument("--popqa", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-mixed-commits", action="store_true",
                    help="accept a configuration whose records were written "
                         "at more than one git commit")
    args = ap.parse_args(argv)
    try:
        rep = build(args.items, args.popqa, args.records,
                    allow_mixed_commits=args.allow_mixed_commits)
    except Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    os.makedirs(args.out, exist_ok=True)
    for name, body in (("report.json", json.dumps(rep, indent=1, default=str)),
                       ("report.md", render_md(rep))):
        tmp = os.path.join(args.out, name + ".tmp")
        with open(tmp, "w") as fh:
            fh.write(body)
        os.replace(tmp, os.path.join(args.out, name))
    print(rep["decision"]["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
