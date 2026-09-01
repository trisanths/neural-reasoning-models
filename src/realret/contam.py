"""Does any benchmark test item appear in the real-document training data?

The four benchmarks this project reports on are MMLU, GSM8K, ARC-Challenge
and WinoGrande. Their test items are read from the same parquet files
`src/extern/bench.py` scores against, so the thing checked is the thing
measured and not a re-download that might differ.

Two matches are counted, and they answer different questions.

  exact       the normalised benchmark stem appears verbatim inside a
              training question or one of its documents. This is the match
              that would make a benchmark number a lookup.

  near        the benchmark stem and a training question share a high
              fraction of their word 5-grams. A paraphrase or a reformatted
              copy survives exact matching and this catches it. Reported at
              a stated Jaccard threshold with the worst offenders listed, so
              the number can be argued with rather than trusted.

Both run over training questions and over every document in every training
bundle, because a page that states an MMLU answer contaminates just as much
as a question that repeats its stem.

Topical overlap is not contamination. TriviaQA asks about history and so
does MMLU; that is the point of the experiment. What is checked is whether
the literal test item is in the training data.
"""

from __future__ import annotations

import argparse
import json
import re
import time

_WORD = re.compile(r"[a-z0-9]+")
NGRAM = 5
NEAR_THRESHOLD = 0.5
# A stem shorter than this many words cannot be matched safely: "yes" or
# "which of the following" would collide with everything.
MIN_STEM_WORDS = 8


def norm(text: str) -> str:
    return " ".join(_WORD.findall(str(text).lower()))


def grams(words: list[str], n: int = NGRAM) -> set[str]:
    if len(words) < n:
        return set()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def bench_items(root: str) -> list[dict]:
    import pyarrow.parquet as pq

    out = []

    def add(task, text, extra=""):
        s = norm(text)
        if len(s.split()) >= MIN_STEM_WORDS:
            out.append({"task": task, "stem": s, "extra": extra})

    t = pq.read_table(f"{root}/mmlu/all/test-00000-of-00001.parquet").to_pylist()
    for r in t:
        add("mmlu", r["question"], r["subject"])
    t = pq.read_table(
        f"{root}/ai2_arc/ARC-Challenge/test-00000-of-00001.parquet").to_pylist()
    for r in t:
        add("arc", r["question"])
    t = pq.read_table(
        f"{root}/winogrande/winogrande_xl/validation-00000-of-00001.parquet"
    ).to_pylist()
    for r in t:
        add("winogrande", r["sentence"])
    t = pq.read_table(f"{root}/gsm8k/main/test-00000-of-00001.parquet").to_pylist()
    for r in t:
        add("gsm8k", r["question"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", nargs="+", required=True)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--out", required=True)
    ap.add_argument("--near-threshold", type=float, default=NEAR_THRESHOLD)
    a = ap.parse_args()

    t0 = time.time()
    items = bench_items(a.root)
    per_task: dict = {}
    for it in items:
        per_task[it["task"]] = per_task.get(it["task"], 0) + 1
    print(f"benchmark stems: {json.dumps(per_task)}", flush=True)

    # Inverted index over benchmark 5-grams. A training text only has to be
    # compared against benchmark items it shares a 5-gram with.
    post: dict = {}
    stems = []
    for i, it in enumerate(items):
        g = grams(it["stem"].split())
        stems.append((it, g))
        for x in g:
            post.setdefault(x, []).append(i)

    exact_hits: list = []
    near_hits: list = []
    n_q = 0
    n_doc = 0
    scanned_chars = 0
    for path in a.episodes:
        with open(path) as fh:
            for line in fh:
                ep = json.loads(line)
                q = ep["questions"][0]
                fields = [("question", q["text"])]
                for di, d in enumerate(ep["documents"]):
                    fields.append((f"doc{di}", d["text"]))
                n_q += 1
                n_doc += len(ep["documents"])
                for field, text in fields:
                    s = norm(text)
                    scanned_chars += len(s)
                    words = s.split()
                    g = grams(words)
                    if not g:
                        continue
                    cand: dict = {}
                    for x in g:
                        for i in post.get(x, ()):  # noqa: PERF
                            cand[i] = cand.get(i, 0) + 1
                    for i, shared in cand.items():
                        it, bg = stems[i]
                        if it["stem"] and it["stem"] in s:
                            exact_hits.append({
                                "task": it["task"], "stem": it["stem"][:200],
                                "source": ep["source"], "qid": ep.get("qid"),
                                "field": field, "file": path})
                            continue
                        j = shared / max(1, len(g | bg))
                        if j >= a.near_threshold:
                            near_hits.append({
                                "task": it["task"], "stem": it["stem"][:200],
                                "text": s[:200], "jaccard": round(j, 3),
                                "source": ep["source"], "qid": ep.get("qid"),
                                "field": field, "file": path})

    res = {
        "episodes": a.episodes,
        "benchmark_stems": per_task,
        "benchmark_stems_total": len(items),
        "min_stem_words": MIN_STEM_WORDS,
        "ngram": NGRAM,
        "near_threshold": a.near_threshold,
        "training_questions_scanned": n_q,
        "training_documents_scanned": n_doc,
        "training_chars_scanned": scanned_chars,
        "exact_matches": len(exact_hits),
        "near_matches": len(near_hits),
        "exact_by_task": {t: sum(1 for h in exact_hits if h["task"] == t)
                          for t in per_task},
        "near_by_task": {t: sum(1 for h in near_hits if h["task"] == t)
                         for t in per_task},
        "exact_examples": exact_hits[:50],
        "near_examples": sorted(near_hits, key=lambda h: -h["jaccard"])[:50],
        "seconds": round(time.time() - t0, 1),
    }
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: v for k, v in res.items()
                      if not k.endswith("examples")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
