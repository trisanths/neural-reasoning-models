"""Forced-choice scoring, chance floors, and the hedging canary.

The grading rule is stated as an exact single choice rather than as a
containment test, because three containment graders were found broken on this
project in one day.

  named(answer)   the distinct candidates that occur in the answer as whole
                  words, in order of first occurrence. The candidate set is
                  the episode's own, plus the twin system's where one is in
                  the store.
  forced          exactly one candidate named, and it is the gold. This is the
                  headline.
  first           the first candidate named is the gold. Lenient tie-break,
                  reported beside forced, never instead of it.
  hedge           more than one distinct candidate named.
  none            no candidate named at all.
  shipped         the environment grader as recorded, kept only so the two can
                  be compared.

Two chance floors travel with every accuracy. `chance_cand` is uniform over
the episode's own candidate set, computed from that set's size and not
assumed. `chance_page` is uniform over the invented words visible on the
served pages, which is the floor for a reader that picks a nonce word off the
page without reading the rule. The invented-word vocabulary is built PER
FRAME: each frame's English is constant within that frame and absent from the
others, so a pooled vocabulary would misclassify one frame's ordinary words as
invented. That bug was live in the first pass of the earlier ablation.

The canary is a stand-in policy that answers with every candidate on every
item. It must score exactly 0.0 forced. `tests/test_frames.py` pins it.
"""

from __future__ import annotations

import re
from collections import defaultdict

WORD = re.compile(r"[a-z]{4,}")


def named(answer: str, candidates: list[str]) -> list[str]:
    """Distinct candidates named in the answer, in order of first appearance."""
    a = answer.lower()
    hits = []
    for c in candidates:
        m = re.search(rf"(?<![a-z]){re.escape(c.lower())}(?![a-z])", a)
        if m:
            hits.append((m.start(), c.lower()))
    hits.sort()
    seen, out = set(), []
    for _, c in hits:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def nonce_vocab(rows: list[dict]) -> set[str]:
    """Invented words show up in one episode; frame English in nearly all."""
    eps_with = defaultdict(set)
    all_eps = set()
    for r in rows:
        key = r["ep"]
        all_eps.add(key)
        for ch in r["chunks"]:
            for w in set(WORD.findall(ch.lower())):
                eps_with[w].add(key)
    n = max(1, len(all_eps))
    return {w for w, s in eps_with.items() if len(s) / n < 0.20}


def summarize(rows: list[dict], vocab: set[str],
              answer_key: str = "answer") -> dict:
    """Score one cell. Never call this across families or frames."""
    n = len(rows)
    if not n:
        return {"n": 0}
    shipped = hedge = none = forced = first = 0
    hit_own = hit_twin = 0
    ch_cand = ch_page = 0.0
    any_twin = False
    for r in rows:
        own = list(r["candidates"] or [])
        twin = list(r.get("twin_candidates") or [])
        any_twin = any_twin or bool(twin)
        pool = own + [t for t in twin if t not in own]
        hits = named(r[answer_key], pool)
        gold = r["gold"].lower()
        shipped += int(r.get("shipped_ok", False))
        if not hits:
            none += 1
        elif len(hits) > 1:
            hedge += 1
        if len(hits) == 1 and hits[0] == gold:
            forced += 1
        if hits and hits[0] == gold:
            first += 1
        ownl = {c.lower() for c in own}
        twinl = {c.lower() for c in twin} - ownl
        hit_own += int(any(h in ownl for h in hits))
        hit_twin += int(any(h in twinl for h in hits))
        if pool:
            ch_cand += 1.0 / len(pool)
        page = set()
        for ch in r["chunks"]:
            page |= {w for w in WORD.findall(ch.lower()) if w in vocab}
        if page and gold in page:
            ch_page += 1.0 / len(page)
    out = {
        "n": n,
        "acc_shipped": shipped / n,
        "acc_forced": forced / n,
        "acc_first": first / n,
        "hedge_rate": hedge / n,
        "none_rate": none / n,
        "chance_cand": ch_cand / n,
        "chance_page": ch_page / n,
        "n_candidates_mean": sum(len(r["candidates"] or []) for r in rows) / n,
    }
    if any_twin:
        out["named_own"] = hit_own / n
        out["named_twin"] = hit_twin / n
    return out


def canary_rows(rows: list[dict]) -> list[dict]:
    """The hedging stand-in: name every candidate on every item."""
    out = []
    for r in rows:
        pool = list(r["candidates"] or []) + list(r.get("twin_candidates") or [])
        c = dict(r)
        c["answer"] = " ".join(pool) if pool else ""
        c["shipped_ok"] = True
        out.append(c)
    return out


def corrected(acc: float, chance: float) -> float:
    """Chance-corrected accuracy: (acc - c) / (1 - c). Negative below chance."""
    return (acc - chance) / (1.0 - chance) if chance < 1.0 else 0.0


def macro_both_orders(cells: list[tuple[float, float]]) -> dict:
    """Both aggregation orders over (accuracy, chance) cells, with formulas.

    order_A  correct the macro:  (mean_i acc_i - mean_i c_i) / (1 - mean_i c_i)
    order_B  macro the corrected: mean_i [ (acc_i - c_i) / (1 - c_i) ]

    They differ whenever the chance floors differ across cells, which is why
    both are reported. Never call this across families in a headline.
    """
    if not cells:
        return {"cells": 0}
    accs = [a for a, _ in cells]
    chs = [c for _, c in cells]
    ma = sum(accs) / len(accs)
    mc = sum(chs) / len(chs)
    order_a = corrected(ma, mc)
    order_b = sum(corrected(a, c) for a, c in cells) / len(cells)
    return {
        "cells": len(cells),
        "macro_accuracy": ma,
        "macro_chance": mc,
        "order_A_corrected_macro": order_a,
        "order_B_mean_of_corrected": order_b,
        "formula_A": "(mean_i acc_i - mean_i c_i) / (1 - mean_i c_i)",
        "formula_B": "mean_i [ (acc_i - c_i) / (1 - c_i) ]",
    }


HEADER = ("%-28s %-18s %5s %8s %7s %7s %6s %6s %7s %7s"
          % ("frame", "family", "n", "shipped", "forced", "first", "hedge",
             "none", "chance", "chncPg"))


def row_line(frame: str, family: str, s: dict) -> str:
    return ("%-28s %-18s %5d %8.3f %7.3f %7.3f %6.3f %6.3f %7.3f %7.3f"
            % (frame, family, s["n"], s["acc_shipped"], s["acc_forced"],
               s["acc_first"], s["hedge_rate"], s["none_rate"],
               s["chance_cand"], s["chance_page"]))
