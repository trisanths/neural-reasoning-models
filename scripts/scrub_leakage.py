"""Leakage estimator for the fact scrubber, toolkit item 3.

Reads real FineWeb text from parquet, scrubs it with
src.scrub.scrub_document under the selected entity policy (invent or
shuffle), and reports collapse numbers against the unscrubbed baseline:

probe co-occurrence: the fraction of knowledge probes whose answer
string appears in the same document as one of the probe's question
entities, in at least one document of the sample.

bigram survival: for the 50 most frequent capitalized bigrams in the
raw sample, the fraction that still appear intact anywhere after
scrubbing. The raw baseline is 1.0 by construction.

entity-pair survival: among the most frequent detected entity forms,
the pairs that co-occur in at least one raw document of the sample; the
fraction still co-occurring in at least one scrubbed document. The raw
baseline is 1.0 by construction. Under the shuffle policy a pair can
survive by chance reassignment, so this is the criterion to watch
there.

top-form coverage: the fraction of the most frequent detected entity
forms appearing anywhere in the scrubbed output. Near zero under
invent; high under shuffle, which is the policy's purpose: real name
tokens keep training signal.

It also reports single core scrub throughput on the sampled text.

Usage: python scripts/scrub_leakage.py --data ~/data/regime_a/parquet \
    --mb 200 --seed 0 --policy shuffle
"""

import argparse
import glob
import json
import os
import re
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyarrow.parquet as pq

from src.evals.probes import PROBES
from src.scrub import scrub_document
from src.scrub.name_pool import harvest_counts, pool_from_counts

_RUN_RE = re.compile(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b")
_ACRO_RE = re.compile(r"\b[A-Z]{2,}\b")
_BIGRAM_RE = re.compile(r"\b([A-Z][a-z]+) (?=([A-Z][a-z]+)\b)")
_ARTICLES = ("The ", "A ", "An ")


def probe_entities(text):
    """Capitalized entity strings in a probe question.

    A run at position zero is kept only when, after stripping a leading
    article, it still has two or more words. A lone leading capital is
    usually just the sentence start. Acronyms count anywhere.
    """
    ents = []
    for m in _RUN_RE.finditer(text):
        run = m.group()
        if m.start() == 0:
            for a in _ARTICLES:
                if run.startswith(a):
                    run = run[len(a):]
                    break
            if " " not in run:
                continue
        if run:
            ents.append(run)
    for m in _ACRO_RE.finditer(text):
        ents.append(m.group())
    return ents


def _bounded(s):
    return re.compile(r"(?<![A-Za-z])" + re.escape(s) + r"(?![A-Za-z])")


def build_probe_checks():
    checks = []
    for p in PROBES:
        ents = probe_entities(p["text"])
        if not ents:
            continue
        answer = p["options"][p["answer_idx"]]
        checks.append({
            "ents": ents,
            "ent_res": [_bounded(e) for e in ents],
            "answer": answer,
            "answer_re": _bounded(answer),
        })
    return checks


def cooccurrence_fraction(docs, checks):
    """Fraction of probes whose entity and answer share a document."""
    unresolved = list(checks)
    hits = 0
    for doc in docs:
        still = []
        for c in unresolved:
            hit = False
            for e, er in zip(c["ents"], c["ent_res"]):
                if e in doc and er.search(doc):
                    if c["answer"] in doc and c["answer_re"].search(doc):
                        hit = True
                    break
            if hit:
                hits += 1
            else:
                still.append(c)
        unresolved = still
        if not unresolved:
            break
    return hits / len(checks)


def top_bigrams(docs, k=50):
    counts = Counter()
    for doc in docs:
        for m in _BIGRAM_RE.finditer(doc):
            counts[m.group(1) + " " + m.group(2)] += 1
    return [b for b, _ in counts.most_common(k)]


def survival_fraction(bigrams, docs):
    alive = 0
    for b in bigrams:
        for doc in docs:
            if b in doc:
                alive += 1
                break
    return alive / len(bigrams)


def form_coverage(forms, docs):
    """Fraction of forms appearing word-bounded anywhere in docs."""
    if not forms:
        return 0.0
    found = 0
    for f in forms:
        r = _bounded(f)
        for doc in docs:
            if f in doc and r.search(doc):
                found += 1
                break
    return found / len(forms)


def cooccurring_pairs(docs, forms, max_pairs=200):
    """The most frequent co-occurring (a, b) pairs of forms over docs,
    both matches word-bounded."""
    res = {f: _bounded(f) for f in forms}
    counts = Counter()
    for doc in docs:
        present = [f for f in forms if f in doc and res[f].search(doc)]
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                counts[(present[i], present[j])] += 1
    return [p for p, _ in counts.most_common(max_pairs)]


def pair_survival(pairs, docs):
    """Fraction of pairs whose two forms co-occur in at least one doc."""
    if not pairs:
        return 0.0
    res = {}
    for a, b in pairs:
        res.setdefault(a, _bounded(a))
        res.setdefault(b, _bounded(b))
    alive = 0
    for a, b in pairs:
        for doc in docs:
            if (a in doc and b in doc
                    and res[a].search(doc) and res[b].search(doc)):
                alive += 1
                break
    return alive / len(pairs)


def read_sample(data_dir, target_bytes):
    docs = []
    tokens = 0
    total = 0
    files = sorted(glob.glob(os.path.join(data_dir, "*.parquet")))
    for path in files:
        pf = pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=1024,
                                     columns=["text", "token_count"]):
            texts = batch.column("text").to_pylist()
            counts = batch.column("token_count").to_pylist()
            for text, count in zip(texts, counts):
                docs.append(text)
                tokens += count
                total += len(text)
            if total >= target_bytes:
                return docs, tokens, total
    return docs, tokens, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.expanduser(
        "~/data/regime_a/parquet"))
    ap.add_argument("--mb", type=float, default=200.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--policy", choices=("invent", "shuffle"),
                    default="invent")
    ap.add_argument("--pool-max-forms", type=int, default=20000)
    ap.add_argument("--pool-min-count", type=int, default=2)
    ap.add_argument("--top-forms", type=int, default=50)
    ap.add_argument("--max-pairs", type=int, default=200)
    args = ap.parse_args()

    docs, tokens, chars = read_sample(args.data, int(args.mb * 1e6))
    print(f"sample: {len(docs)} docs, {chars/1e6:.1f}M chars, "
          f"{tokens/1e6:.1f}M tokens, policy {args.policy}", flush=True)

    t0 = time.perf_counter()
    counts = harvest_counts(docs)
    forms = [f for f, _ in counts.most_common(args.top_forms)]
    pool = None
    if args.policy == "shuffle":
        pool = pool_from_counts(counts, max_forms=args.pool_max_forms,
                                min_count=args.pool_min_count)
    print(f"harvest: {time.perf_counter() - t0:.1f}s, "
          f"{len(counts)} distinct forms, "
          f"pool {len(pool) if pool else 0}", flush=True)

    t0 = time.perf_counter()
    scrubbed = [scrub_document(d, args.seed, entity_policy=args.policy,
                               pool=pool) for d in docs]
    dt = time.perf_counter() - t0
    rate = tokens / dt
    print(f"scrub: {dt:.1f}s, {rate/1e6:.2f}M tokens/s single core",
          flush=True)

    checks = build_probe_checks()
    print(f"probes with usable entities: {len(checks)} of {len(PROBES)}",
          flush=True)
    base_co = cooccurrence_fraction(docs, checks)
    print(f"baseline probe co-occurrence: {base_co:.3f}", flush=True)
    scrub_co = cooccurrence_fraction(scrubbed, checks)
    print(f"scrubbed probe co-occurrence: {scrub_co:.3f}", flush=True)

    bigrams = top_bigrams(docs)
    surv = survival_fraction(bigrams, scrubbed)
    print(f"top-50 bigram survival after scrub: {surv:.3f} "
          f"(baseline 1.0)", flush=True)

    coverage = form_coverage(forms, scrubbed)
    print(f"top-{len(forms)} form coverage in scrubbed output: "
          f"{coverage:.3f}", flush=True)
    pairs = cooccurring_pairs(docs, forms, args.max_pairs)
    pair_surv = pair_survival(pairs, scrubbed)
    print(f"entity-pair survival after scrub: {pair_surv:.3f} over "
          f"{len(pairs)} pairs (baseline 1.0)", flush=True)

    print(json.dumps({
        "policy": args.policy,
        "docs": len(docs),
        "chars": chars,
        "tokens": tokens,
        "scrub_seconds": round(dt, 2),
        "tokens_per_second": round(rate),
        "pool_forms": len(pool) if pool else 0,
        "probes_used": len(checks),
        "probe_cooccurrence_baseline": round(base_co, 4),
        "probe_cooccurrence_scrubbed": round(scrub_co, 4),
        "bigram_survival_scrubbed": round(surv, 4),
        "bigram_survival_baseline": 1.0,
        "top_form_coverage_scrubbed": round(coverage, 4),
        "entity_pairs_used": len(pairs),
        "entity_pair_survival_scrubbed": round(pair_surv, 4),
        "entity_pair_survival_baseline": 1.0,
        "top_bigrams": bigrams[:10],
        "top_forms": forms[:10],
    }))


if __name__ == "__main__":
    main()
