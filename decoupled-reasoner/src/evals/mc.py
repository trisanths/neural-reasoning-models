"""Multiple choice scoring by language model likelihood.

Each option is appended to the shared context and scored by the negative log
likelihood of the option tokens alone. Three rules decide the winner, and the
first two exist because the earlier version got them wrong:

  length    the score is the mean NLL per option token, not the sum. A summed
            NLL charges every extra token, so the shortest option wins
            whenever the model is unsure, and a forced-choice accuracy built
            on it partly measures option length.
  order     options are scored in an order shuffled by a seeded RNG, and the
            winner is mapped back to the caller's index.
  ties      exact ties are broken by the same seeded RNG. Breaking them toward
            index zero, as before, hands every tie to whichever option the
            item file happened to list first, which is often the gold.

The pure part (choose, shuffled_order) takes per-option NLL sums and token
counts and touches no model, so any backend that can produce those numbers,
the in-house TransformerLM here or vLLM prompt logprobs in src/pilot, scores
the same way.

legacy=True restores the old rule (summed NLL, listed order, ties to the
lowest index) for reproducing numbers recorded before the change. Nothing in
the repository passes it today.
"""

from __future__ import annotations

import random

import torch
import torch.nn.functional as F

TIE_REL = 1e-6


def shuffled_order(n: int, rng: random.Random) -> list[int]:
    """A permutation of range(n) drawn from rng."""
    order = list(range(n))
    rng.shuffle(order)
    return order


def option_scores(nll_sums, n_tokens, normalize: bool = True) -> list[float]:
    """Per-option score, lower is better: mean NLL per token, or the sum."""
    if len(nll_sums) != len(n_tokens):
        raise ValueError("nll_sums and n_tokens differ in length")
    out = []
    for s, n in zip(nll_sums, n_tokens):
        if n <= 0:
            raise ValueError("option has no tokens")
        out.append(s / n if normalize else s)
    return out


def choose(nll_sums, n_tokens, rng: random.Random | None = None,
           normalize: bool = True, legacy: bool = False) -> int:
    """Index of the winning option in the caller's order.

    rng drives both the scoring order and the tie break; pass a
    random.Random seeded per item so a rerun picks the same winner. With
    legacy=True the rule is the old one: summed NLL, ties to index zero.
    """
    if legacy:
        return min(range(len(nll_sums)), key=lambda i: (nll_sums[i], i))
    if rng is None:
        raise ValueError("choose needs a seeded rng unless legacy=True")
    scores = option_scores(nll_sums, n_tokens, normalize=normalize)
    order = shuffled_order(len(scores), rng)
    best = min(scores[i] for i in order)
    # Scores arrive from float32 sums, so two options the model rates equally
    # can differ in the last bits depending on summation order. Anything
    # within TIE_REL of the best counts as tied.
    tol = TIE_REL * max(1.0, abs(best))
    tied = [i for i in order if scores[i] - best <= tol]
    return tied[0] if len(tied) == 1 else rng.choice(tied)


def option_nll_stats(model, context_ids, option_ids, device) -> tuple[float, int]:
    """(summed NLL, number of option tokens scored) of option_ids given context."""
    if not option_ids:
        raise ValueError("option has no tokens")
    max_len = model.cfg.max_seq_len
    ids = list(context_ids) + list(option_ids)
    if len(ids) > max_len:
        # Keep the tail: the question and options sit at the end.
        ids = ids[-max_len:]
    n_opt = min(len(option_ids), len(ids) - 1)
    x = torch.tensor([ids], dtype=torch.long, device=device)
    with torch.no_grad():
        logits, _ = model(x)
    logprobs = F.log_softmax(logits[0, :-1].float(), dim=-1)
    targets = x[0, 1:]
    tail = logprobs[-n_opt:].gather(1, targets[-n_opt:].unsqueeze(1))
    return float(-tail.sum().item()), int(n_opt)


def option_nll(model, context_ids, option_ids, device) -> float:
    """Summed NLL of option_ids given context_ids under the model."""
    return option_nll_stats(model, context_ids, option_ids, device)[0]


def score_mc(model, tokenizer, context_ids, options, device, seed: int = 0,
             rng: random.Random | None = None, normalize: bool = True,
             legacy: bool = False):
    """Return (best_index, per option NLL list) for text options.

    The NLL list is summed NLL in the caller's option order, as before; the
    choice uses the mean per token unless normalize is False. rng, when
    given, overrides seed; either way the result is deterministic for fixed
    inputs.
    """
    if rng is None:
        rng = random.Random(seed)
    order = list(range(len(options))) if legacy else shuffled_order(len(options), rng)
    sums: list[float] = [0.0] * len(options)
    counts: list[int] = [0] * len(options)
    for i in order:
        ids = tokenizer.encode(options[i])
        if not ids:
            ids = tokenizer.encode(" " + options[i])
        sums[i], counts[i] = option_nll_stats(model, context_ids, ids, device)
    best = choose(sums, counts, rng=rng, normalize=normalize, legacy=legacy)
    return best, sums


def load_checkpoint_model(ckpt_path, device):
    """Rebuild the TransformerLM stored in a trainer checkpoint."""
    from src.train.model import ModelConfig, TransformerLM

    state = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    model.to(device).eval()
    return model, state
