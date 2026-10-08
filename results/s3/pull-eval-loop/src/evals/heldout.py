"""Held out worlds suite, SPEC.md section 6.

Fresh episodes come from seeds never used in training. Every question is
scored as multiple choice: the true answer against distractors drawn from
the answer pool of the same domain, or against the opposite polarity for
yes or no questions. This measures in regime reasoning on the generator
manifold and is never the headline number.
"""

import numpy as np

from src.evals.mc import score_mc
from src.train.data import render_world_preamble


def build_context_ids(episode, question, tokenizer, max_seq_len):
    """Render the episode context for one question.

    Documents supporting the question's derivation come first so the answer
    stays derivable after budget truncation, then the remaining documents in
    episode order until the token budget runs out.
    """
    sid = tokenizer.special_ids
    ids = [sid["<|world|>"]]
    ids.extend(tokenizer.encode(render_world_preamble(episode["world"])))
    tail = [sid["<|q|>"], *tokenizer.encode(question["text"]), sid["<|a|>"]]
    budget = max_seq_len - len(ids) - len(tail) - 48

    needed = set(question.get("derivation", []))
    first, rest = [], []
    for doc in episode["documents"]:
        if needed & set(doc.get("supports", [])):
            first.append(doc)
        else:
            rest.append(doc)
    for doc in first + rest:
        doc_ids = [sid["<|doc|>"], *tokenizer.encode(doc["text"])]
        if len(doc_ids) > budget:
            continue
        ids.extend(doc_ids)
        budget -= len(doc_ids)
    ids.extend(tail)
    return ids


def build_options(question, pool, episode, rng, n_options=4):
    """Return (options list, index of the true answer)."""
    answer = question["answer"]
    if answer in ("yes", "no"):
        options = ["yes", "no"]
        return options, options.index(answer)
    distractors = [a for a in pool if a != answer]
    if len(distractors) < n_options - 1:
        extras = [e["name"] for e in episode["world"]["entities"]
                  if e["name"] != answer]
        distractors = list(dict.fromkeys(distractors + extras))
    take = min(n_options - 1, len(distractors))
    picked = [distractors[int(i)]
              for i in rng.choice(len(distractors), size=take, replace=False)]
    options = [answer] + picked
    order = [int(i) for i in rng.permutation(len(options))]
    shuffled = [options[i] for i in order]
    return shuffled, order.index(0)


def answer_pools(episodes):
    """Collect candidate answers per domain, excluding yes and no."""
    pools = {}
    for ep in episodes:
        domain = ep["world"]["domain"]
        for q in ep["questions"]:
            if q["answer"] not in ("yes", "no"):
                pools.setdefault(domain, set()).add(q["answer"])
    return {d: sorted(v) for d, v in pools.items()}


def run_heldout(model, tokenizer, episodes, device, seed=0) -> dict:
    """Score every question in the given episodes."""
    episodes = list(episodes)
    pools = answer_pools(episodes)
    rng = np.random.default_rng(seed)
    max_seq_len = model.cfg.max_seq_len

    per_domain = {}
    per_type = {}
    n_correct = 0
    n_total = 0
    chance_sum = 0.0
    for ep in episodes:
        domain = ep["world"]["domain"]
        for q in ep["questions"]:
            options, true_idx = build_options(q, pools.get(domain, []), ep, rng)
            context = build_context_ids(ep, q, tokenizer, max_seq_len)
            best, _ = score_mc(model, tokenizer, context, options, device)
            correct = best == true_idx
            n_correct += int(correct)
            n_total += 1
            chance_sum += 1.0 / len(options)
            for bucket, key in ((per_domain, domain), (per_type, q["type"])):
                stats = bucket.setdefault(key, {"n": 0, "correct": 0})
                stats["n"] += 1
                stats["correct"] += int(correct)

    for bucket in (per_domain, per_type):
        for stats in bucket.values():
            stats["accuracy"] = round(stats["correct"] / stats["n"], 4)

    return {
        "suite": "heldout_worlds",
        "n_episodes": len(episodes),
        "n_questions": n_total,
        "accuracy": round(n_correct / n_total, 4) if n_total else 0.0,
        "chance": round(chance_sum / n_total, 4) if n_total else 0.0,
        "per_domain": per_domain,
        "per_type": per_type,
    }
