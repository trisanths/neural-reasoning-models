"""Rescore dumped rollouts under a grader that disallows hedging.

The shipped environment grader accepts any prediction CONTAINING the gold
answer with six tokens of slack, so a policy that names both candidates is
scored correct either way. This recomputes, per renderer and per family:

  acc_shipped     the shipped grader, as recorded
  acc_forced      exactly one distinct candidate named, and it is the gold
  acc_first       the first candidate named is the gold (lenient tie-break)
  hedge_rate      more than one distinct candidate named
  none_rate       no candidate named at all
  chance_cand     uniform over the episode's candidate set
  chance_page     uniform over the invented words visible on the served pages

In the twin condition a second system of the same family shares the store, so
the candidate set for forced choice is the union of both systems' labels, and
two extra columns report how often each system's words are named.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
from collections import defaultdict

WORD = re.compile(r"[a-z]{4,}")


def parse_name(path: str) -> tuple[str, str]:
    base = os.path.basename(path)
    for suf in (".rolls.jsonl", ".jsonl"):
        if base.endswith(suf):
            base = base[: -len(suf)]
    parts = base.split("-")
    return parts[1], "-".join(parts[2:])


def load(paths: list[str]) -> list[dict]:
    rows = []
    for p in paths:
        rend, cond = parse_name(p)
        with open(p) as fh:
            for line in fh:
                r = json.loads(line)
                r["renderer"] = rend
                r["condition"] = cond
                rows.append(r)
    return rows


def nonce_vocab(rows: list[dict]) -> set[str]:
    """Invented words appear in one episode; template English in nearly all."""
    eps_with = defaultdict(set)
    all_eps = set()
    for r in rows:
        key = (r["renderer"], r["condition"], r["ep"])
        all_eps.add(key)
        for ch in r["chunks"]:
            for w in set(WORD.findall(ch.lower())):
                eps_with[w].add(key)
    n = max(1, len(all_eps))
    return {w for w, s in eps_with.items() if len(s) / n < 0.20}


def named(answer: str, cands: list[str]) -> list[str]:
    """Distinct candidates named, in order of first appearance."""
    a = answer.lower()
    hits = []
    for c in cands:
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


def summarize(rows: list[dict], vocab: set[str]) -> dict:
    n = len(rows)
    shipped = hedge = none = forced = first = 0
    hit_own = hit_twin = 0
    ch_cand = ch_page = 0.0
    any_twin = False
    for r in rows:
        own = list(r["candidates"] or [])
        twin = list(r.get("twin_candidates") or [])
        any_twin = any_twin or bool(twin)
        pool = own + [t for t in twin if t not in own]
        hits = named(r["answer"], pool)
        gold = r["gold"].lower()
        shipped += int(r["shipped_ok"])
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
    }
    if any_twin:
        out["named_own"] = hit_own / n
        out["named_twin"] = hit_twin / n
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--glob", required=True, nargs="+")
    ap.add_argument("--order", default="")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    paths = sorted({p for g in args.glob for p in glob.glob(g)})
    if not paths:
        raise SystemExit("no dump files matched")
    rows = load(paths)
    # Template English is constant within a renderer but differs between
    # renderers, so the invented-word vocabulary is built per renderer.
    by_rend = defaultdict(list)
    for r in rows:
        by_rend[r["renderer"]].append(r)
    vocabs = {k: nonce_vocab(v) for k, v in by_rend.items()}
    vocab = set().union(*vocabs.values()) if vocabs else set()

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        fam = r["family"] or "chain"
        groups[(r["renderer"], r["condition"], fam)].append(r)
        groups[(r["renderer"], r["condition"], "ALL(pooled)")].append(r)

    order = [x for x in args.order.split(",") if x]
    rends = sorted({k[0] for k in groups},
                   key=lambda x: (order.index(x) if x in order else 99, x))
    conds = sorted({k[1] for k in groups})
    fams = sorted({k[2] for k in groups if k[2] != "ALL(pooled)"})
    fams = fams + ["ALL(pooled)"]

    twin_cols = any(r.get("twin_candidates") for r in rows)
    out = {}
    hdr = ("%-19s %-18s %5s %8s %7s %7s %6s %6s %7s %7s"
           % ("renderer", "family", "n", "shipped", "forced", "first",
              "hedge", "none", "chance", "chncPg"))
    if twin_cols:
        hdr += " %6s %6s" % ("own", "twin")
    for cond in conds:
        print("\n== condition: %s ==" % cond)
        print(hdr)
        for rend in rends:
            for fam in fams:
                key = (rend, cond, fam)
                if key not in groups:
                    continue
                s = summarize(groups[key], vocabs[rend])
                out["|".join(key)] = s
                line = ("%-19s %-18s %5d %8.3f %7.3f %7.3f %6.3f %6.3f "
                        "%7.3f %7.3f" % (rend, fam, s["n"], s["acc_shipped"],
                                         s["acc_forced"], s["acc_first"],
                                         s["hedge_rate"], s["none_rate"],
                                         s["chance_cand"], s["chance_page"]))
                if twin_cols:
                    line += " %6.3f %6.3f" % (s.get("named_own", float("nan")),
                                              s.get("named_twin", float("nan")))
                print(line)
    print("\ninvented-word vocabulary per renderer: %s"
          % ", ".join("%s=%d" % (k, len(v)) for k, v in sorted(vocabs.items())))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
