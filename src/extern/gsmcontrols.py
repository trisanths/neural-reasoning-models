"""Two controls on the GSM8K contamination label, written to one record file.

The label says the gold number appears as a bare token somewhere in 4,000
characters of web text. GSM8K answers are small integers and 4,000 characters
of prose contains a lot of small integers, so the label could be mostly
coincidence, and a split built on a coincidental label would separate two
arbitrary subsets.

The permutation control estimates the coincidence rate: each item is scored
against another item's pages under a seeded derangement, which destroys any
relationship between problem and page while leaving the page lengths and the
number distribution alone. Whatever rate survives is the label's false
positive rate.

The copy control asks what our reader is doing when the label fires. It takes
the number the model emitted, right or wrong, and checks whether that number
is in the context block, against the same check on somebody else's block. A
model that computes an answer scores at the coincidence rate on both. A model
that copies a number off the page scores higher on its own.

Nothing live is spent. The pages come out of the same cache the runs read and
the client raises rather than fetching.
"""
from __future__ import annotations

import json
import os
import random
import re

from src.extern.bench_gsm import gold_of, load
from src.extern.gsm4 import fetch_block, label_contamination
from src.extern.retrieval_ours import CachedExa

OUT = "results/extern/bench/gsm4_controls.json"
LFM = "results/extern/bench/gsm4_lfm2_350m_bos_n200.json"
OURS = "results/extern/bench/gsm4_ours_native_a_n200.json"


class NoLive:
    """A search surface that cannot spend. A cache miss is an error here."""

    def search(self, *a, **k):
        raise RuntimeError("cache miss in a control that must not spend")


def present(num, text):
    if num is None or not text:
        return False
    return bool(re.search(r"(?<![\d.])" + re.escape(f"{num:g}") + r"(?![\d.])",
                          text.replace(",", "")))


def derangement(n, seed):
    rng = random.Random(seed)
    p = list(range(n))
    while True:
        rng.shuffle(p)
        if all(p[i] != i for i in range(n)):
            return p


d = json.load(open(LFM))
o = json.load(open(OURS))
test = load("data/extern", d["n"], d["seed"], "test")
gold = [gold_of(r["answer"]) for r in test]
client = CachedExa(NoLive(), "results/extern/exa_cache", 0)

res = {"n": len(test), "seed": d["seed"], "num_results": d["num_results"],
       "max_context_chars": d["max_context_chars"],
       "sources": {"lfm2": LFM, "ours": OURS},
       "label_permutation": {}, "copy": {}}

for cond in ("method", "problem"):
    blocks = [fetch_block(client, cond, r, d["num_results"],
                          d["max_context_chars"])[0] for r in test]
    p = derangement(len(test), 99)
    real = [label_contamination(blocks[i], test[i]["question"], gold[i])
            for i in range(len(test))]
    shuf = [label_contamination(blocks[p[i]], test[i]["question"], gold[i])
            for i in range(len(test))]
    res["label_permutation"][cond] = {
        lab: {"n": len(test),
              "real_k": sum(1 for x in real if x == lab),
              "permuted_k": sum(1 for x in shuf if x == lab)}
        for lab in ("verbatim", "answer", "neither")}

    q = derangement(len(test), 1717)
    recs = o["arms"][f"{cond}/greedy"]["records"]
    par = [i for i, r in enumerate(recs) if r["flexible"] is not None]
    corr = [i for i in par if recs[i]["flexible_correct"]]
    res["copy"][cond] = {
        "n_parseable": len(par),
        "own_k": sum(1 for i in par if present(recs[i]["flexible"], blocks[i])),
        "other_k": sum(1 for i in par
                       if present(recs[i]["flexible"], blocks[q[i]])),
        "n_correct": len(corr),
        "correct_with_gold_in_block": sum(
            1 for i in corr if present(recs[i]["flexible"], blocks[i]))}

res["live_searches"] = client.live
res["cache_hits"] = client.hits
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
