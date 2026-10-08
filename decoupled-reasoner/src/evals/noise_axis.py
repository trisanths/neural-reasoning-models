"""Retrieval noise axis, SPEC.md section 6.

Corrupt the retrieved context at fixed rates and measure how accuracy
degrades. Corruption swaps chunks for chunks drawn from other episodes,
which models a retriever that returns plausible but wrong passages.

The harness is model agnostic. It takes an answering callable with
signature answer_fn(question, chunks) -> str and a list of examples,
each a dict with keys question, answer, chunks (list of strings), and
episode_id. Accuracy uses the same normalized exact match as the
naturalized suite. Everything is seeded and deterministic.

run_noise_axis_interactive plugs the emit-query-read decode loop from
src/evals/interactive.py in as the reader, so the corrupted chunks are
exactly the documents that loop serves through <|result|>.
"""

import random

from src.evals.naturalized import exact_match

DEFAULT_RATES = (0.0, 0.1, 0.25, 0.5)


def build_examples(episodes):
    """Turn worldgen episodes into noise axis examples.

    Each question becomes one example whose chunks are the full document
    list of its episode, in episode order.
    """
    examples = []
    for ep_idx, episode in enumerate(episodes):
        chunks = [doc["text"] for doc in episode["documents"]]
        for question in episode["questions"]:
            examples.append({
                "question": question["text"],
                "answer": question["answer"],
                "chunks": list(chunks),
                "episode_id": ep_idx,
            })
    return examples


def _donor_pools(examples):
    """Map each episode_id to the unique chunks of every other episode."""
    per_episode = {}
    for ex in examples:
        seen = per_episode.setdefault(ex["episode_id"], dict())
        for chunk in ex["chunks"]:
            seen[chunk] = None
    pools = {}
    for eid in per_episode:
        donors = []
        for other, chunks in per_episode.items():
            if other != eid:
                donors.extend(chunks)
        pools[eid] = donors
    return pools


def corrupt_examples(examples, rate: float, rng: random.Random):
    """Swap a rate fraction of each example's chunks for other-episode chunks.

    The number of swapped chunks is int(rate * n + 0.5) per example, so
    rate 0 changes nothing. Returns new example dicts with fresh chunk
    lists; the input is never mutated. Raises ValueError when corruption
    is requested but every chunk belongs to a single episode.
    """
    if not 0.0 <= rate <= 1.0:
        raise ValueError(f"rate must be in [0, 1], got {rate}")
    pools = _donor_pools(examples)
    out = []
    for ex in examples:
        chunks = list(ex["chunks"])
        k = int(rate * len(chunks) + 0.5)
        if k > 0:
            donors = pools[ex["episode_id"]]
            if not donors:
                raise ValueError(
                    "cannot corrupt: no chunks from other episodes exist")
            for pos in sorted(rng.sample(range(len(chunks)), k)):
                chunks[pos] = donors[rng.randrange(len(donors))]
        new = dict(ex)
        new["chunks"] = chunks
        out.append(new)
    return out


def _least_squares_slope(xs, ys) -> float:
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0.0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom


def run_noise_axis(answer_fn, examples, rates=DEFAULT_RATES, seed: int = 0) -> dict:
    """Measure accuracy per corruption rate and the degradation slope.

    The slope is the least squares fit of accuracy against rate, in
    accuracy per unit corruption rate, so a reader that degrades under
    noise reports a negative slope. Each rate uses its own RNG stream
    derived from the seed, so adding or removing rates does not change
    the corruption at the remaining rates.
    """
    if not examples:
        raise ValueError("no examples")
    if not rates:
        raise ValueError("no rates")
    rate_list = [float(r) for r in rates]
    accuracies = []
    for i, rate in enumerate(rate_list):
        rng = random.Random(seed * 1000003 + i)
        current = corrupt_examples(examples, rate, rng) if rate > 0 else examples
        n_ok = sum(
            1 for ex in current
            if exact_match(answer_fn(ex["question"], ex["chunks"]), ex["answer"]))
        accuracies.append(n_ok / len(current))
    lo = rate_list.index(min(rate_list))
    hi = rate_list.index(max(rate_list))
    return {
        "suite": "noise_axis",
        "n": len(examples),
        "seed": seed,
        "rates": rate_list,
        "accuracy_per_rate": {f"{r:g}": acc
                              for r, acc in zip(rate_list, accuracies)},
        "slope": _least_squares_slope(rate_list, accuracies),
        "clean_accuracy": accuracies[lo],
        "noisiest_accuracy": accuracies[hi],
        "degradation": accuracies[lo] - accuracies[hi],
    }


def run_noise_axis_interactive(step_fn, tokenizer, examples,
                               rates=DEFAULT_RATES, seed: int = 0,
                               max_rounds: int = 4,
                               max_new_tokens: int = 128) -> dict:
    """Run the noise axis with the interactive decode loop as the reader.

    Each example's chunks become the document set the loop retrieves
    from, so a corrupted chunk is served through <|result|> whenever
    BM25 selects it. step_fn is a next token scores callable as
    described in src/evals/interactive.py. The import stays inside this
    function so the module keeps no heavyweight dependencies for
    callers that bring their own answer_fn.
    """
    from src.evals.interactive import make_retrieval_answer_fn

    answer_fn = make_retrieval_answer_fn(
        step_fn, tokenizer, max_rounds=max_rounds,
        max_new_tokens=max_new_tokens, seed=seed)
    return run_noise_axis(answer_fn, examples, rates=rates, seed=seed)
