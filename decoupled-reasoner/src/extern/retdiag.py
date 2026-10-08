"""Where the answer went: a cache only diagnosis of the MMLU retrieval cell.

Nothing here touches the network. It replays the cached Exa results for
the same 200 MMLU items cell 4 scored and asks, for every item whose
context did not carry the answer, which of four things happened:

    search    no returned page contains the answer at any rank
    rank      a returned page has it, but that page never reached the
              context because the packer spent the budget earlier
    window    the first page has it, past the character cut
    detector  the text is there and the strict test missed it

The four are exclusive and are assigned in that order, so the counts add
up to the miss total.

Three detectors run side by side. `chars` is the original raw substring
test that produced the published split, `token` is the same match at
token boundaries, `soft` accepts the gold answer's content words inside
one window. The token test is the one the failure modes are assigned
from, because the character test fires on a gold of "-19" inside the
year 1976 and on the single letter a gold of "~H" normalises to.

Cache entries are checked before they are scored against. An entry with
no page text is a failed search written to disk, and counting it as a
search failure would be reporting a bug as a finding.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.getcwd())

from src.extern.bench import TASKS
from src.extern.retpack import (contains_answer, contains_answer_chars,
                                contains_answer_soft, degenerate_gold, norm,
                                pack, stem_key)

DETECTORS = {"chars": contains_answer_chars, "token": contains_answer,
             "soft": contains_answer_soft}


def cache_path(root, q):
    return os.path.join(root, hashlib.sha256(q.encode()).hexdigest()[:32] + ".json")


def query_for(row):
    return " ".join(str(row["question"]).split())[:300]


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - h) / d, 3), round((c + h) / d, 3)]


def flags(text, question, gold, distractors):
    hay = norm(text)
    sk = stem_key(question)
    out = {d: fn(hay, gold) for d, fn in DETECTORS.items()}
    out["stem"] = bool(sk) and sk in hay
    out["n_distractors"] = sum(1 for c in distractors
                               if contains_answer(hay, c))
    out["chars_len"] = len(text)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--cache", default="results/extern/exa_cache")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--max-context-chars", type=int, default=6000)
    ap.add_argument("--out", default="results/extern/retdiag.json")
    a = ap.parse_args()

    rows = TASKS["mmlu"](a.root, a.n, a.seed)
    recs, missing_cache, empty_cache = [], 0, 0
    for row in rows:
        q = query_for(row)
        p = cache_path(a.cache, q)
        if not os.path.exists(p):
            missing_cache += 1
            recs.append({"id": row["id"], "cached": False})
            continue
        pages = json.load(open(p))
        live = [x for x in pages if (x.get("text") or "").strip()]
        if not live:
            empty_cache += 1
        gold = row["choices"][row["gold"]]
        others = [c for i, c in enumerate(row["choices"]) if i != row["gold"]]

        per_page = [flags(x.get("text") or "", row["question"], gold, others)
                    for x in pages]
        ctx = {k: flags(pack(k, pages, a.max_context_chars,
                             query=row["question"], options=row["choices"]),
                        row["question"], gold, others)
               for k in ("sequential", "even", "passages")}

        def rank_of(field):
            for i, pp in enumerate(per_page):
                if pp[field]:
                    return i + 1
            return None

        cur = ctx["sequential"]
        if cur["token"]:
            mode = "hit"
        elif cur["soft"]:
            mode = "detector"
        elif any(pp["token"] or pp["soft"] for pp in per_page):
            r = rank_of("token") or rank_of("soft")
            mode = "window" if r == 1 else "rank"
        else:
            mode = "search"
        recs.append({
            "id": row["id"], "subject": row["subject"], "cached": True,
            "n_pages": len(pages), "n_pages_text": len(live),
            "gold": gold, "question": row["question"],
            "choices": list(row["choices"]),
            "degenerate_gold": degenerate_gold(gold),
            "urls": [x.get("url", "") for x in pages],
            "per_page": per_page, "ctx": ctx, "mode": mode,
            "rank_token": rank_of("token"), "rank_soft": rank_of("soft"),
            "rank_chars": rank_of("chars"),
        })

    scored = [r for r in recs if r.get("cached")]
    n = len(scored)

    def frac(pred, sub=None):
        s = scored if sub is None else sub
        k = sum(1 for r in s if pred(r))
        return {"k": k, "n": len(s),
                "rate": round(k / len(s), 4) if s else None,
                "ci": wilson(k, len(s))}

    recall = {}
    for det in ("chars", "token", "soft"):
        for k in (1, 3, 5):
            recall[f"{det}@{k}"] = frac(
                lambda r, k=k, d=det: any(pp[d] for pp in r["per_page"][:k]))

    nondeg = [r for r in scored if not r["degenerate_gold"]]
    out = {
        "n_items": len(recs), "n_cached": n,
        "missing_cache": missing_cache, "empty_cache_entries": empty_cache,
        "degenerate_gold": sum(1 for r in scored if r["degenerate_gold"]),
        "recall_full_text": recall,
        "recall_full_text_nondegenerate": {
            f"token@{k}": frac(lambda r, k=k: any(pp["token"]
                                                  for pp in r["per_page"][:k]),
                               nondeg) for k in (1, 3, 5)},
        "context_hit": {
            kind: {det: frac(lambda r, k=kind, d=det: r["ctx"][k][d])
                   for det in ("chars", "token", "soft")}
            | {"stem": frac(lambda r, k=kind: r["ctx"][k]["stem"]),
               "all_distractors_too": frac(
                   lambda r, k=kind: r["ctx"][k]["token"]
                   and r["ctx"][k]["n_distractors"] == len(r["choices"]) - 1),
               "mean_chars": round(sum(r["ctx"][kind]["chars_len"]
                                       for r in scored) / max(1, n), 1)}
            for kind in ("sequential", "even", "passages")},
        "failure_modes": {m: sum(1 for r in scored if r["mode"] == m)
                          for m in ("hit", "detector", "window", "rank",
                                    "search")},
        "page_chars": {
            "mean": round(sum(pp["chars_len"] for r in scored
                              for pp in r["per_page"])
                          / max(1, sum(len(r["per_page"]) for r in scored)), 1),
            "over_6000": sum(1 for r in scored for pp in r["per_page"]
                             if pp["chars_len"] > 6000),
            "total_pages": sum(len(r["per_page"]) for r in scored)},
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"summary": out, "records": recs}, open(a.out, "w"), indent=1)
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
