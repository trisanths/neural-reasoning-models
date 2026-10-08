"""Grade every prediction three ways and audit the generator.

Three graders, from the one the project reports to the one that admits no
hedging:

  lenient   what src.rl.env.EpisodeEnv.score uses: normalized exact match,
            then a contains fallback with six tokens of slack
  strict    normalized exact match only
  forced    the first invented word the answer names, compared to gold; an
            answer that names two candidates is wrong

The audit measures the regularities a shortcut could ride: how often the gold
answer is the shortest, the most frequent, the earliest, or the invented word
nearest a question word on the page the retriever serves.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

from src.evals.naturalized import contains_answer, exact_match, normalize
from src.falsify.probe import (WORD_RE, anchor_positions, bm25_top,
                               candidates as cand_of, nonce_words,
                               rank_documents, rebuild_system,
                               template_vocabulary)
from src.skillacq.simple import SIMPLE_FAMILIES
from src.skillacq.systems import generate_episode

SLACK = 6


def lenient(pred: str, gold: str) -> bool:
    if exact_match(pred, gold):
        return True
    gold_tokens = normalize(gold).split()
    if len(gold_tokens) == 1 and gold_tokens[0] in ("yes", "no"):
        return False
    pred_tokens = normalize(pred).split()
    if not pred_tokens:
        return False
    if len(pred_tokens) > len(gold_tokens) + SLACK:
        return False
    return contains_answer(pred, gold)


def strict(pred: str, gold: str) -> bool:
    return exact_match(pred, gold)


def first_candidate(pred: str, cands: list) -> str:
    low = [c.lower() for c in cands]
    for w in WORD_RE.findall(pred):
        if w.lower() in low:
            return w.lower()
    return ""


def forced(pred: str, gold: str, cands: list) -> bool:
    return first_candidate(pred, cands) == gold.lower()


def names_multiple(pred: str, cands: list) -> bool:
    low = {c.lower() for c in cands}
    seen = {w.lower() for w in WORD_RE.findall(pred) if w.lower() in low}
    return len(seen) > 1


def wilson(k: int, n: int) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    z, p = 1.96, k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def load(data_dir: str, pred_dir: str, cond: str):
    metas = [json.loads(l) for l in open(f"{data_dir}/meta_{cond}.jsonl")]
    preds = [json.loads(l) for l in open(f"{pred_dir}/pred_{cond}.jsonl")]
    for p in preds:
        p["meta"] = metas[p["episode_index"]]
    return preds


def score_condition(preds: list, gold_key: str = "gold") -> dict:
    """All graders, overall and per family, for the model and each baseline."""
    out: dict = {}
    fams = sorted({p["meta"]["family"] for p in preds})
    systems = ["model"] + sorted(preds[0]["baseline"])
    for sysname in systems:
        rows = {"overall": [0, 0, 0, 0, 0]}  # n, lenient, strict, forced, multi
        per = {f: [0, 0, 0, 0, 0] for f in fams}
        for p in preds:
            gold = p[gold_key]
            cands = p["meta"]["candidates"]
            answers = p["model"] if sysname == "model" else [p["baseline"][sysname]]
            for a in answers:
                for bucket in (rows["overall"], per[p["meta"]["family"]]):
                    bucket[0] += 1
                    bucket[1] += lenient(a, gold)
                    bucket[2] += strict(a, gold)
                    bucket[3] += forced(a, gold, cands)
                    bucket[4] += names_multiple(a, cands)
        def pack(b):
            n = max(1, b[0])
            lo, hi = wilson(b[1], b[0])
            return {"n": b[0], "lenient": b[1] / n, "strict": b[2] / n,
                    "forced": b[3] / n, "hedged": b[4] / n,
                    "lenient_ci": [round(lo, 4), round(hi, 4)]}
        out[sysname] = {"overall": pack(rows["overall"]),
                        **{f: pack(per[f]) for f in fams}}
    return out


def chance_floor(preds: list) -> dict:
    """Accuracy of picking uniformly from the answer set the page admits."""
    per = defaultdict(lambda: [0.0, 0])
    for p in preds:
        c = len(set(x.lower() for x in p["meta"]["candidates"]))
        per[p["meta"]["family"]][0] += 1.0 / c
        per[p["meta"]["family"]][1] += 1
        per["overall"][0] += 1.0 / c
        per["overall"][1] += 1
    return {k: v[0] / v[1] for k, v in per.items()}


def retrieval_split(preds: list) -> dict:
    """Did the rollout actually read the page that answers the question?

    A chunk counts as the answering page when it names at least two of the
    episode's candidate answers, which is true of the rule page and of no
    other page. Accuracy is then split on whether such a chunk was served.
    """
    got = [0, 0]
    miss = [0, 0]
    n_any = 0
    for p in preds:
        cands = [c.lower() for c in p["meta"]["candidates"]]
        chunks = p.get("retrieved") or []
        n_any += bool(chunks)
        served = any(sum(c in ch.lower() for c in cands) >= 2 for ch in chunks)
        bucket = got if served else miss
        bucket[0] += 1
        bucket[1] += lenient(p["model"][0], p["gold"])
    return {
        "any_retrieval": n_any / max(1, len(preds)),
        "answering_page_served": got[0] / max(1, len(preds)),
        "lenient_when_served": got[1] / max(1, got[0]),
        "lenient_when_not_served": miss[1] / max(1, miss[0]),
        "n_served": got[0], "n_not_served": miss[0],
    }


def audit_generator(n: int = 400, n_problems: int = 6) -> dict:
    """Measure the regularities a shortcut could ride, per family."""
    vocab = template_vocabulary(200)
    fams = sorted(SIMPLE_FAMILIES)
    stats = {f: defaultdict(list) for f in fams}
    label_counts = {f: Counter() for f in fams}
    for i in range(n):
        fam = fams[i % len(fams)]
        s = 6_000_000 + i
        ep = generate_episode(s, family=fam, n_problems=n_problems)
        sysobj = rebuild_system(s, fam)
        cands = [c.lower() for c in cand_of(sysobj)]
        docs = [{"text": t} for t in ep.textbook]
        for p in ep.problems:
            gold = p["answer"].lower()
            label_counts[fam][gold == cands[0]] += 1
            ranked = rank_documents(p["text"], docs, vocab)
            stats[fam]["rule_page_rank"].append(
                float(next((i for i, t in enumerate(ranked)
                            if sum(c in t.lower() for c in cands) >= 2), len(ranked))))
            stats[fam]["gold_on_bm25_top1"].append(
                float(gold in bm25_top(p["text"], docs).lower()))
            doc = "\n\n".join(ranked)
            page_words = [w.lower() for w in nonce_words(doc, vocab)]
            present = [c for c in cands if c in page_words]
            st = stats[fam]
            st["gold_on_top_page"].append(float(gold in page_words))
            if len(present) < 2:
                continue
            counts = Counter(page_words)
            first = {c: page_words.index(c) for c in present}

            def uniquely(key_of, better):
                """Gold wins outright, with no other candidate tied with it."""
                mine = key_of(gold)
                return float(all(better(mine, key_of(c))
                                 for c in present if c != gold))

            st["gold_len_minus_mean_candidate_len"].append(
                len(gold) - sum(len(c) for c in present) / len(present))
            st["gold_uniquely_shortest"].append(
                uniquely(len, lambda a, b: a < b))
            st["gold_uniquely_most_frequent"].append(
                uniquely(lambda c: counts[c], lambda a, b: a > b))
            st["gold_uniquely_earliest"].append(
                uniquely(lambda c: first.get(c, 10**9), lambda a, b: a < b))
            qn = {w.lower() for w in nonce_words(p["text"], vocab)}
            toks = [w.lower() for w in WORD_RE.findall(doc)]
            anchors = anchor_positions(toks, qn)
            if anchors:
                dist = {}
                for c in present:
                    pos = [j for j, w in enumerate(toks) if w == c]
                    if pos:
                        dist[c] = min(abs(j - a) for j in pos for a in anchors)
                if dist and gold in dist:
                    st["gold_uniquely_nearest_question_word"].append(
                        float(all(dist[gold] < d for c, d in dist.items() if c != gold)))
            st["n_candidates_on_page"].append(float(len(present)))
            st["chance_if_uniform"].append(1.0 / len(present))
    out = {}
    for f in fams:
        out[f] = {k: (sum(v) / len(v) if v else None) for k, v in stats[f].items()}
        tot = sum(label_counts[f].values())
        out[f]["p_first_candidate_is_gold"] = label_counts[f][True] / max(1, tot)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--conditions", default="textbook,wrong_textbook,no_documents,"
                                            "swapped,twin,twin_named,inverse_table,chain_rule,band_rule")
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args()

    report: dict = {"conditions": {}}
    for cond in args.conditions.split(","):
        if not os.path.exists(f"{args.pred}/pred_{cond}.jsonl"):
            continue
        preds = load(args.data, args.pred, cond)
        entry = {"n_items": len(preds), "scored": score_condition(preds),
                 "chance_floor": chance_floor(preds)}
        entry["mean_rounds"] = sum(sum(p["n_rounds"]) / len(p["n_rounds"])
                                   for p in preds) / len(preds)
        entry["retrieval"] = retrieval_split(preds)
        if cond.startswith("twin"):
            named_twin = 0
            named_right = 0
            for p in preds:
                tw = {c.lower() for c in p["meta"]["twin_candidates"]}
                mine = {c.lower() for c in p["meta"]["candidates"]}
                words = {w.lower() for w in WORD_RE.findall(p["model"][0])}
                named_twin += bool(words & tw)
                named_right += bool(words & mine)
            entry["named_twin_candidate"] = named_twin / len(preds)
            entry["named_own_candidate"] = named_right / len(preds)
        if cond == "swapped":
            for p in preds:
                p["page_gold"] = p["meta"]["alt_answers"][p["qid"]]
            entry["vs_page_implied_gold"] = score_condition(preds, "page_gold")
            inf = [p for p in preds if p["meta"]["informative"][p["qid"]]]
            entry["informative_only"] = {
                "n": len(inf),
                "vs_true_gold": score_condition(inf),
                "vs_page_gold": score_condition(
                    [dict(p, gold=p["meta"]["alt_answers"][p["qid"]]) for p in inf]),
            }
        report["conditions"][cond] = entry
        m = entry["scored"]["model"]["overall"]
        print(f"[{cond}] n={entry['n_items']} model lenient {m['lenient']:.4f} "
              f"strict {m['strict']:.4f} forced {m['forced']:.4f} "
              f"hedged {m['hedged']:.4f} chance {entry['chance_floor']['overall']:.4f}",
              flush=True)
        for b in sorted(entry["scored"]):
            if b == "model":
                continue
            r = entry["scored"][b]["overall"]
            print(f"    {b:18s} lenient {r['lenient']:.4f} strict {r['strict']:.4f}",
                  flush=True)

    if args.audit:
        report["generator_audit"] = audit_generator()
        print(json.dumps(report["generator_audit"], indent=1), flush=True)

    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
