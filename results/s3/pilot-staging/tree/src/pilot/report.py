"""The pilot report: per-cell tables from stored records, and the preregistered decision.

Nothing here touches a model. Every number is recomputed from the records
written by src/pilot/runner.py, so a grading change costs a rerun of this
file and not of the GPU.

Freshness, after the rule FRAMES.md and RETRAIN.md enforce for the score
files (a report must never quote records it cannot vouch for). The builder
refuses, writes nothing and exits non-zero when:

  - RUNNING.lock is present in the records directory (a run is writing);
  - any records file is newer than the moment this build started, or
    changes while it is being read (records newer than the report);
  - any records file is older than the item file it claims to come from,
    or a record's items_sha or prompt_hash disagrees with the current item
    file (records from an earlier generation of the items);
  - a key (model, thinking, item, condition) appears twice;
  - the hedging canary scores above zero under the strict grader.

Every accuracy is printed with its denominator, its Wilson interval, the
mean per-item floor of the cell, the majority-answer rate of the cell, the
hedge rate and the lenient score. Nothing is pooled across families. The
decision follows the rules in PREREGISTERED.md, section "Acquisition pilot".

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
GO_GAP = 0.20
GO_CELLS = 2
POPQA_MARGIN = 0.15
POPQA_FLOOR = 0.25
BASE_CANDIDATES = ("lfm2.5-350m-base", "qwen3-0.6b-base")
FALLBACK = "qwen3-1.7b-base"
RECORDED_LEVELS = (4, 5, 6, 7, 8)


class Refusal(Exception):
    pass


# --------------------------------------------------------------------------
# loading, with the freshness rules
# --------------------------------------------------------------------------
def _read(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def load_records(records_dir: str, items_path: str, popqa_path: str | None,
                 started: float) -> dict:
    lock = os.path.join(records_dir, "RUNNING.lock")
    if os.path.exists(lock):
        raise Refusal(f"{lock} exists: a run is still writing records")
    items = {it["item_id"]: it for it in load_items(items_path)}
    items_sha = file_sha(items_path)
    items_mtime = os.path.getmtime(items_path)
    popqa = popqa_sha = popqa_mtime = None
    if popqa_path:
        popqa = {it["item_id"]: it for it in load_items(popqa_path)}
        popqa_sha = file_sha(popqa_path)
        popqa_mtime = os.path.getmtime(popqa_path)

    names = sorted(n for n in os.listdir(records_dir)
                   if n.endswith(".jsonl") and n.startswith(("gen__", "popqa__")))
    mtimes = {n: os.path.getmtime(os.path.join(records_dir, n)) for n in names}
    gen, pq = [], []
    for n in names:
        path = os.path.join(records_dir, n)
        if mtimes[n] > started:
            raise Refusal(f"{n} is newer than this report build "
                          f"({mtimes[n]:.0f} > {started:.0f})")
        is_pq = n.startswith("popqa__")
        source_mtime = popqa_mtime if is_pq else items_mtime
        if source_mtime is not None and mtimes[n] < source_mtime:
            raise Refusal(f"{n} is older than the item file it was scored "
                          f"from; it belongs to an earlier item set")
        rows = _read(path)
        if is_pq:
            if popqa is None:
                continue
            for r in rows:
                if r["popqa_sha"] != popqa_sha or r["item_id"] not in popqa:
                    raise Refusal(f"{n}: record {r['item_id']} is from another "
                                  f"PopQA item file")
            pq.extend(rows)
        else:
            for r in rows:
                it = items.get(r["item_id"])
                if (r["items_sha"] != items_sha or it is None or
                        it["prompt_hashes"][r["condition"]] != r["prompt_hash"]):
                    raise Refusal(f"{n}: record {r['item_id']}/{r['condition']} "
                                  f"is from another item file")
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

    return {"items": items, "popqa": popqa, "gen": gen, "pq": pq,
            "freshness": {"started_utc": _utc(started),
                          "items": {"path": items_path, "sha256": items_sha,
                                    "mtime_utc": _utc(items_mtime)},
                          "popqa": ({"path": popqa_path, "sha256": popqa_sha,
                                     "mtime_utc": _utc(popqa_mtime)}
                                    if popqa_path else None),
                          "records": {n: _utc(t) for n, t in mtimes.items()}}}


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


# --------------------------------------------------------------------------
# cells
# --------------------------------------------------------------------------
def binom_upper_p(k: int, n: int, p: float) -> float:
    """P[X >= k] for X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i)
                                       for i in range(k))))


def cell_name(family: str, level) -> str:
    return family if level is None else f"{family}/L{level}"


def majority_rates(items: dict) -> dict:
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
        floor = sum(r["floor"] for r in rows) / n
        out[key] = {
            "model": model, "thinking": thinking, "family": fam, "level": lv,
            "cell": cell_name(fam, lv), "condition": cond, "n": n, "k": k,
            "acc": k / n, "wilson_lo": lo, "wilson_hi": hi, "floor": floor,
            "majority": maj.get((fam, lv)),
            "hedge": sum(r["hedge"] for r in rows) / n,
            "lenient": sum(r["correct_lenient"] for r in rows) / n,
            "answer_found": sum(r["answer_found"] for r in rows) / n,
            "think_truncated": sum(r["think_truncated"] for r in rows) / n,
            "mean_think_tokens": sum(r["n_think_tokens"] for r in rows) / n,
            "p_at_or_above_floor": binom_upper_p(k, n, floor),
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
        out[(model, band)] = {
            "model": model, "band": band, "n": n, "k": k, "acc": k / n,
            "wilson_lo": lo, "wilson_hi": hi, "floor": POPQA_FLOOR,
            "margin": k / n - POPQA_FLOOR,
            "acc_summed_nll": sum(r["correct_summed_nll"] for r in rows) / n}
    return out


# --------------------------------------------------------------------------
# the preregistered decision
# --------------------------------------------------------------------------
def configs_present(gen: list[dict]) -> list[tuple]:
    return sorted({(r["model"], r["thinking"]) for r in gen})


def completeness(gen: list[dict], items: dict, conditions) -> dict:
    have: dict = defaultdict(set)
    for r in gen:
        have[(r["model"], r["thinking"])].add((r["item_id"], r["condition"]))
    want = len(items) * len(conditions)
    return {f"{m}|think{int(t)}": {"records": len(v), "expected": want,
                                   "complete": len(v) == want}
            for (m, t), v in sorted(have.items())}


def rule_validity(cells: dict) -> dict:
    fails = []
    checked = 0
    for c in cells.values():
        if c["condition"] not in ("closed_book", "blank"):
            continue
        checked += 1
        if c["wilson_hi"] > c["floor"] + VALIDITY_SLACK + 1e-12:
            fails.append({k: c[k] for k in ("model", "thinking", "cell",
                                            "condition", "n", "k", "acc",
                                            "wilson_hi", "floor",
                                            "p_at_or_above_floor")})
    return {"rule": "(1) validity", "cells_checked": checked,
            "passed": checked > 0 and not fails, "failures": fails}


def rule_go_for(model: str, cells: dict, gen: list[dict], pqc: dict,
                complete: dict) -> dict:
    key = f"{model}|think0"
    rows = []
    for c in cells.values():
        if (c["model"], c["thinking"], c["condition"]) != (model, False, "oracle"):
            continue
        g = paired_gap(gen, model, False, c["family"], c["level"],
                       "oracle", "sibling")
        if g["gap"] is None:
            continue
        rows.append({"cell": c["cell"], **g, "qualifies": g["gap"] >= GO_GAP})
    q = [r["cell"] for r in rows if r["qualifies"]]
    pq = pqc.get((model, "all"))
    pq_ok = pq is not None and pq["margin"] >= POPQA_MARGIN
    have_all = complete.get(key, {}).get("complete", False) and pq is not None
    return {"model": model, "complete": have_all, "cells": rows,
            "qualifying_cells": q, "cells_ok": len(q) >= GO_CELLS,
            "popqa_acc": pq["acc"] if pq else None,
            "popqa_margin": pq["margin"] if pq else None,
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


def decide(cells, gen, pqc, complete) -> dict:
    validity = rule_validity(cells)
    go = {m: rule_go_for(m, cells, gen, pqc, complete) for m in BASE_CANDIDATES}
    fallback = rule_go_for(FALLBACK, cells, gen, pqc, complete)
    needed = [f"{m}|think0" for m in BASE_CANDIDATES + (FALLBACK,)]
    missing = [k for k in needed if not complete.get(k, {}).get("complete")]
    if missing:
        verdict = (f"not reached: records incomplete for {missing}")
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
    return {"verdict": verdict, "validity": validity, "go": go,
            "fallback": fallback, "missing": missing}


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------
def _f(x, d=3):
    return "-" if x is None else f"{x:.{d}f}"


def render_md(rep: dict) -> str:
    from src.extern.stats import tbl

    out = ["# Acquisition pilot report", "",
           f"Built {rep['freshness']['started_utc']} from items "
           f"`{rep['freshness']['items']['sha256'][:16]}`.", "",
           f"Decision: {rep['decision']['verdict']}", ""]
    v = rep["decision"]["validity"]
    out += ["## Rule 1, validity", "",
            f"{v['cells_checked']} closed-book and blank cells checked; "
            f"{len(v['failures'])} fail (Wilson upper bound above floor + "
            f"{VALIDITY_SLACK}). The last column is the exact binomial "
            "probability of a count this high from a guesser at the floor.", ""]
    if v["failures"]:
        out.append(tbl(["model", "think", "cell", "cond", "n", "k", "acc",
                        "wilson_hi", "floor", "P[>=k|floor]"],
                       [[f["model"], int(f["thinking"]), f["cell"], f["condition"],
                         f["n"], f["k"], _f(f["acc"]), _f(f["wilson_hi"]),
                         _f(f["floor"], 4), _f(f["p_at_or_above_floor"], 4)]
                        for f in v["failures"]]))
        out.append("")
    for title, g in [("Rule 2, " + m, rep["decision"]["go"][m])
                     for m in BASE_CANDIDATES] + \
            [("Rule 3, " + FALLBACK, rep["decision"]["fallback"])]:
        out += [f"## {title}", "",
                f"complete {g['complete']}; qualifying cells "
                f"{len(g['qualifying_cells'])} {g['qualifying_cells']}; PopQA "
                f"acc {_f(g['popqa_acc'])} margin {_f(g['popqa_margin'])}; "
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
            tbl(["model", "band", "n", "acc", "wilson", "floor", "margin",
                 "acc (summed NLL, old rule)"],
                [[c["model"], c["band"], c["n"], _f(c["acc"]),
                  f"[{_f(c['wilson_lo'])}, {_f(c['wilson_hi'])}]", _f(c["floor"], 2),
                  _f(c["margin"]), _f(c["acc_summed_nll"])]
                 for c in sorted(rep["popqa"], key=lambda c: (c["model"], c["band"]))]),
            "", "## Every generation cell", "",
            "acc is the strict forced-choice score; lenient is beside it, never "
            "instead of it. floor is the mean per-item floor; majority is the "
            "rate of the most common gold answer in the cell.", ""]
    rows = sorted(rep["cells"], key=lambda c: (c["model"], c["thinking"],
                                               c["family"], c["level"] or 0,
                                               c["condition"]))
    out.append(tbl(["model", "think", "cell", "cond", "n", "acc", "wilson",
                    "floor", "majority", "hedge", "lenient", "ans_line", "trunc"],
                   [[c["model"], int(c["thinking"]), c["cell"], c["condition"],
                     c["n"], _f(c["acc"]),
                     f"[{_f(c['wilson_lo'])}, {_f(c['wilson_hi'])}]",
                     _f(c["floor"], 4), _f(c["majority"]), _f(c["hedge"]),
                     _f(c["lenient"]), _f(c["answer_found"]),
                     _f(c["think_truncated"])] for c in rows]))
    out.append("")
    return "\n".join(out)


def build(items_path, popqa_path, records_dir, conditions=None) -> dict:
    from src.pilot.items import CONDITIONS

    started = time.time()
    data = load_records(records_dir, items_path, popqa_path, started)
    canary = canary_check(data["items"])
    cells = gen_cells(data["gen"], data["items"])
    pqc = popqa_cells(data["pq"])
    complete = completeness(data["gen"], data["items"], conditions or CONDITIONS)
    pq_complete = {m: sum(1 for r in data["pq"] if r["model"] == m)
                   for m in sorted({r["model"] for r in data["pq"]})}
    return {
        "freshness": data["freshness"],
        "canary": canary,
        "completeness": complete,
        "popqa_completeness": {m: {"records": n,
                                   "expected": len(data["popqa"] or {})}
                               for m, n in pq_complete.items()},
        "decision": decide(cells, data["gen"], pqc, complete),
        "recorded": recorded_gains(data["gen"]),
        "cells": list(cells.values()),
        "popqa": list(pqc.values()),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="build the pilot report")
    ap.add_argument("--items", required=True)
    ap.add_argument("--popqa", default=None)
    ap.add_argument("--records", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    try:
        rep = build(args.items, args.popqa, args.records)
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
