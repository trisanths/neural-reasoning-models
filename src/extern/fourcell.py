"""The four cell MMLU table, with intervals and the contamination split.

Two of the four cells are scored by log likelihood over the option letters and
two by generation, and they are not interchangeable. Cells 3 and 4 are both
log likelihood, so retrieval against closed book is a like for like move.
Cell 2 is generation, because this project's reader answers by writing, so its
paired control is its own no-index pass rather than cell 1. The table says
which scoring each row used and never subtracts across the two.

Intervals are Wilson at 95 percent, which is what makes an 0.275 against a
0.25 floor legible as "cannot distinguish" rather than as a result.
"""
from __future__ import annotations

import glob
import json
import math
import os


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def ci(acc, n):
    k = round(acc * n)
    lo, hi = wilson(k, n)
    return f"{acc:.4f} [{lo:.3f}, {hi:.3f}]"


def tbl(head, rows):
    w = [len(str(h)) for h in head]
    for r in rows:
        for i, c in enumerate(r):
            w[i] = max(w[i], len(str(c)))
    o = ["| " + " | ".join(str(h).ljust(w[i]) for i, h in enumerate(head)) + " |",
         "| " + " | ".join("-" * w[i] for i in range(len(head))) + " |"]
    for r in rows:
        o.append("| " + " | ".join(str(c).ljust(w[i])
                                   for i, c in enumerate(r)) + " |")
    return "\n".join(o)


SENTINEL = "<!-- appended sections follow; fourcell.py preserves everything below -->"


def adapt_cell2(c):
    """Fold the n=400 arm-per-decode record file into the shape this table
    reads.

    `src/extern/cell2.py` records one arm per decode setting rather than one
    pass per key, and it counts the emission of `<|retrieve|>` directly
    instead of inferring it from the stop reason. The two greedy arms are the
    web pass and its no-index control, so they map onto rows 2 and 1b. The
    contamination split is taken over the items that actually received text:
    an item served nothing has no pages to be contaminated by.
    """
    if not c or "arms" not in c:
        return c
    arms = c["arms"]

    def cell(recs):
        rs = [r for r in recs if "error" not in r]
        n = len(rs)
        if not n:
            return None
        return {"n": n,
                "strict": round(sum(r["strict"] for r in rs) / n, 4),
                "lenient": round(sum(r["lenient"] for r in rs) / n, 4),
                "named_none": round(sum(r["named_none"] for r in rs) / n, 4),
                "issued_query": round(sum(r["emitted_retrieve"]
                                          for r in rs) / n, 4),
                "query_returned": round(sum(r["query_returned"]
                                            for r in rs) / n, 4),
                "context_entered": round(sum(r["context_entered"]
                                             for r in rs) / n, 4),
                "mean_rounds": round(sum(r["n_rounds"] for r in rs) / n, 2),
                "mean_served_chars": round(sum(r["served_chars"]
                                               for r in rs) / n, 1)}

    web_recs = [r for r in arms["web_greedy"]["records"] if "error" not in r]
    served = [r for r in web_recs if r["context_entered"]]
    return {"n": c["n_items"], "floor": c["floor"],
            "live_searches": c["live_searches"],
            "cache_hits": c["cache_hits"], "seconds": c["seconds"],
            "web": cell(arms["web_greedy"]["records"]),
            "none": cell(arms["none_greedy"]["records"]),
            "by_contamination": {
                lab: cell([r for r in served
                           if r["contamination"] == lab])
                for lab in ("verbatim", "answer", "neither")}}


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


B = "results/extern/bench"
c1 = load(f"{B}/ours_corpus-v1-8k_mmlu.json")
c3 = load(f"{B}/lfm2_350m_mmlu_completion_bos.json")
# Cell 2 was cut to n=100 once its answer was clear: the reader issues
# essentially no queries, so the accuracy is predictable and the
# informative content is the per item decomposition. Whichever cell 2
# file is present is the one reported, and its n is in the table.
_c2 = sorted(glob.glob(f"{B}/cell2_ours_mmlu_retrieval_n*.json"))
c2 = adapt_cell2(load(_c2[-1]) if _c2 else None)
c4 = load(f"{B}/cell4_lfm2_mmlu_retrieval_n200.json")

rows = []
if c1:
    rows.append(["1", "ours corpus-v1-8k (375M)", "closed book",
                 "log likelihood", c1["n"], f"{c1['floor']:.4f}",
                 ci(c1["acc"], c1["n"]), "-"])
if c2 and c2.get("none"):
    d = c2["none"]
    rows.append(["1b", "ours corpus-v1-8k (375M)", "closed book (control)",
                 "generation", d["n"], f"{c2['floor']:.4f}",
                 ci(d["strict"], d["n"]), "-"])
if c2 and c2.get("web"):
    d = c2["web"]
    rows.append(["2", "ours corpus-v1-8k (375M)", "live web retrieval",
                 "generation", d["n"], f"{c2['floor']:.4f}",
                 ci(d["strict"], d["n"]), f"{c2['live_searches']} searches"])
if c3:
    rows.append(["3", "LFM2-350M", "closed book", "log likelihood",
                 c3["n"], f"{c3['floor']:.4f}", ci(c3["acc"], c3["n"]),
                 "published 43.43"])
if c4 and c4.get("all"):
    d = c4["all"]
    rows.append(["4", "LFM2-350M", "same pages in context", "log likelihood",
                 d["n"], f"{d['floor']:.4f}", ci(d["acc"], d["n"]),
                 f"{c4['live_searches']} searches"])

out = ["# The four cell MMLU table", "",
       "Every cell states its n, its measured chance floor and a Wilson 95 "
       "percent interval. Cells 3 and 4 share a scoring method and may be "
       "compared directly. Cell 2 is generation scored and its control is "
       "row 1b, the same model on the same items with retrieval unavailable.",
       "", tbl(["cell", "model", "condition", "scoring", "n", "floor",
                "accuracy [95% CI]", "note"], rows), ""]

for name, c in (("cell 2, ours", c2), ("cell 4, LFM2-350M", c4)):
    if not c:
        continue
    note = ("Never pooled. A page carrying the answer makes the item a "
            "lookup; the row that speaks to reasoning is `neither`.")
    if c is c2:
        note += (" The rows cover only the items that actually received "
                 "served text; an item served nothing has no pages to be "
                 "contaminated by and folding those in would inflate "
                 "`neither` with items retrieval never touched.")
    out += [f"## Contamination split, {name}", "", note, ""]
    r2 = []
    for lab in ("verbatim", "answer", "neither"):
        d = (c.get("by_contamination") or {}).get(lab)
        if not d:
            r2.append([lab, 0, "-", "-"])
            continue
        acc = d.get("acc", d.get("strict"))
        r2.append([lab, d["n"], f"{d.get('floor', 0.25):.4f}", ci(acc, d["n"])])
    out += [tbl(["retrieved pages contained", "n", "floor",
                 "accuracy [95% CI]"], r2), ""]

if c2 and c2.get("web"):
    w, nn = c2["web"], c2.get("none") or {}
    n_web = w["n"]
    k_iss = round(w["issued_query"] * n_web)
    lo, hi = wilson(k_iss, n_web)
    out += ["## Cell 2, the stages behind one flat accuracy", "",
            "The reader emitted `<|retrieve|>` on "
            f"**{k_iss} of {n_web}** passes, a rate of "
            f"{w['issued_query']:.4f} with a 95 percent interval of "
            f"[{lo:.3f}, {hi:.3f}]. That is the headline number and the "
            "accuracy is its shadow. The counter is the emission itself and "
            "is the same event with a serving surface attached and without "
            "one; an earlier counter inferred it from the stop reason and "
            "read low in the web pass. The section further down reconciles "
            "the two figures that produced.", "",
            "Four stages sit behind one flat accuracy and only the last is "
            "about comprehension.", "",
            tbl(["stage", "web pass", "no-index control"], [
                ["emitted the retrieve token", f"{w['issued_query']:.4f}",
                 f"{nn.get('issued_query', 0):.4f}"],
                ["query returned a chunk", f"{w['query_returned']:.4f}", "-"],
                ["chunk entered the trace", f"{w['context_entered']:.4f}", "-"],
                ["mean rounds served", f"{w['mean_rounds']:.2f}", "-"],
                ["mean served characters", f"{w['mean_served_chars']:.1f}", "-"],
                ["named no option at all", f"{w['named_none']:.4f}",
                 f"{nn.get('named_none', 0):.4f}"],
            ]), "",
            "A policy failure and a comprehension failure imply different "
            "fixes, and this table no longer picks one. The reader does ask, "
            "on one pass in four, and chunks do reach its trace. What does "
            "not follow is an answer: it names no option on the items where "
            "pages arrived, with them or without them. The paired control in "
            "the cell 2 section below is what settles that, not this split.",
            ""]

if c2 or c4:
    s2, s4 = (c2 or {}), (c4 or {})
    secs = s2.get("seconds", 0) + s4.get("seconds", 0)
    out += ["## Retrieval spend", "",
            f"Cell 2: {s2.get('live_searches', 0)} live Exa searches and "
            f"{s2.get('cache_hits', 0)} cache hits. Cell 4: "
            f"{s4.get('live_searches', 0)} live searches. Wall clock across "
            f"both retrieval cells: {secs / 60:.1f} minutes. Every retrieved "
            "page is cached on disk under `results/extern/exa_cache`, keyed "
            "by query, so a rerun replays without spending again, and every "
            "cache entry is checked for non-empty page text by "
            "`src/extern/cache_audit.py` before anything is scored against "
            "it.", ""]

os.makedirs("results/extern", exist_ok=True)
# Sections appended by src/extern/cell2report.py and src/extern/gsmreport.py
# live below the sentinel and are carried across a regeneration. Rewriting the
# whole file would silently drop measured results that this script never had
# the record files for.
DEST = "src/extern/FOURCELL.md"
tail = ""
if os.path.exists(DEST):
    prev = open(DEST).read()
    i = prev.find(SENTINEL)
    if i >= 0:
        tail = "\n" + prev[i:]
open(DEST, "w").write("\n".join(out) + "\n" + tail)
print("\n".join(out))
