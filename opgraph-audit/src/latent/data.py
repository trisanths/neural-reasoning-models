"""Prompts, streams and encoding for the two latent conditions.

Condition D, latent_answer. The prompt is the direct arm's prompt with its
closing <|a|> replaced by <|result|>. Then R latent positions. Then <|a|>, then
the answer. The target is written `ans VALUE`, the same final chunk the trace
arm writes, so both are read back by src.opgraph.plan.trace_answer and graded
by the same comparison.

Condition E, latent_plan. The prompt is the opgraph arm's plan prompt with the
same substitution, and the target is the plan. The existing executor runs it.
The stream also carries the same induction examples the opgraph arm sees, with
no latent positions, so the plan half and the induction half stay in the same
proportion as in the arm it is being compared against.

Nothing in the latent segment is supervised. Labels are IGNORE at every latent
position and at the <|a|> that closes the segment, so no loss anywhere asks the
continuous state to reconstruct a deleted written step.

Worlds, questions and the page subset draw come from src.opgraph.data's own
generator, consumed in the same order, so a latent arm trained on seeds 0..N
sees exactly the episodes the direct, trace and opgraph arms saw on 0..N.

Two curricula are available and both are off by default.

  stage  the Coconut style replacement schedule, for latent_answer only. At
         stage k the first k written trace chunks are gone from the target and
         k * latents_per_step latent positions stand in their place. Stage 0 is
         the trace arm exactly. The chunks that remain are still written out,
         so what changes across the schedule is how much of the reasoning has
         left the token channel, not what the loss asks of the latent state.
  ramp   the latent segment grows from zero to R over the schedule and the
         target never changes. This is what latent_plan uses, because its
         prompt carries an operator signature line and no pages, so there is no
         written intermediate content between reading the question and writing
         the plan for a replacement schedule to replace.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.opgraph.data import (IGNORE, direct_prompt, induce_prompt,
                              plan_prompt)
from src.opgraph.invent import (breadth_item, make_world, seq_flat, seq_paren,
                                units_item)
from src.opgraph.opdef import serialize_all
from src.opgraph.plan import serialize_plan, trace_text

# A reserved procgen slot stands in for a latent position when the id tensor is
# built. Its embedding is never read: a slot that is not yet filled is dropped
# from the sequence entirely, and a slot that is filled has its embedding
# overwritten by the latent vector. The id is there so the tensor has a shape.
LATENT_TOKEN = "<|pg0|>"
RESULT = "<|result|>"
ANSWER = "<|a|>"
EOT = "<|eot|>"

ARMS = ("latent_answer", "latent_plan")


def latent_answer_prompt(world, question: str, keys=None) -> str:
    """The direct arm's prompt, ending at <|result|> instead of <|a|>."""
    head = direct_prompt(world, question, keys)
    assert head.endswith(ANSWER)
    return head[: -len(ANSWER)] + RESULT


def latent_plan_prompt(ops, question: str) -> str:
    """The opgraph arm's plan prompt, ending at <|result|> instead of <|a|>."""
    head = plan_prompt(ops, question)
    assert head.endswith(ANSWER)
    return head[: -len(ANSWER)] + RESULT


# ------------------------------------------------------------------ items

@dataclass
class Episode:
    """One training question, with everything both conditions need from it."""

    item: object
    keys: object          # the page subset the direct arm drew, or None
    kind: str


def training_episodes(seed: int) -> list[Episode]:
    """The four questions of one world, drawn exactly as the arms draw them.

    The random draws happen in the same order as src.opgraph.data's
    training_examples, so world, breadth, the four questions and the page
    subset per question are identical to what direct and trace were trained on.
    """
    rng = random.Random(seed * 104729 + 7)
    breadth = rng.choice([1, 2, 3])
    w = make_world(seed, breadth=breadth)
    items = [seq_flat(w, rng, rng.choice([1, 2, 3])),
             seq_paren(w, rng, rng.choice([2, 3])),
             breadth_item(w, rng, breadth),
             units_item(w, rng)]
    out = []
    for it in items:
        keys = None if rng.random() < 0.5 else set(it.pages)
        out.append(Episode(it, keys, it.kind))
    return out


def induction_examples(seed: int) -> list[tuple[str, str]]:
    """The induction half of the opgraph arm's stream, verbatim."""
    rng = random.Random(seed * 104729 + 7)
    breadth = rng.choice([1, 2, 3])
    w = make_world(seed, breadth=breadth)
    return [(induce_prompt(p.text), serialize_all(p.ops))
            for p in w.shuffled_pages()]


def chunks_of(text: str) -> tuple[list[str], str]:
    """A written decomposition split into its steps and its closing ans chunk."""
    parts = [c.strip() for c in text.split(";") if c.strip()]
    return parts[:-1], parts[-1]


def answer_target(ep: Episode, stage: int) -> str:
    """Condition D's target at curriculum stage k.

    Stage 0 is the whole written trace. Stage k drops the first k step chunks.
    Past the last chunk the target is the closing `ans VALUE` alone, which is
    what the no curriculum run trains on from step one.
    """
    steps, tail = chunks_of(trace_text(ep.item.plan, ep.item.world.ops))
    keep = steps[min(stage, len(steps)):]
    return " ; ".join(keep + [tail])


def plan_target(ep: Episode) -> str:
    return serialize_plan(ep.item.plan)


def max_chunks(episodes) -> int:
    return max(len(chunks_of(trace_text(e.item.plan, e.item.world.ops))[0])
               for e in episodes)


# ---------------------------------------------------------------- encoding

@dataclass
class Encoded:
    ids: list[int]
    labels: list[int]
    first_latent: int
    n_latent: int
    kind: str


def encode(tok, prompt: str, target: str, n_latent: int, max_len: int,
           kind: str = "", add_answer_token: bool = True) -> Encoded | None:
    """Token ids and labels for one latent example.

    The prompt is masked. The latent positions are masked. The <|a|> that
    closes the latent segment is masked, because it is written by the scaffold
    at inference rather than predicted, so asking the last latent state to
    predict it would put a token shaped constraint on the state for nothing.
    Supervision starts at the first target token and runs through <|eot|>.
    """
    p = tok.encode(prompt)
    lat = [tok.token_id(LATENT_TOKEN)] * n_latent
    tail = [tok.token_id(ANSWER)] if add_answer_token else []
    t = tok.encode(" " + target) + [tok.token_id(EOT)]
    ids = p + lat + tail + t
    if len(ids) > max_len:
        return None
    labels = [IGNORE] * (len(p) + n_latent + len(tail)) + t
    return Encoded(ids, labels, len(p), n_latent, kind)


def supervised_pairs(e: Encoded) -> tuple[list[int], list[int]]:
    """(source position, target token) for every supervised prediction.

    Position i predicts the token at i + 1, which is the convention the arms
    are trained under. Every supervised source position sits at or after the
    <|a|> that closes the latent segment, which is what lets a compressed pass
    shift them all by the same amount.
    """
    src, tgt = [], []
    for i in range(1, len(e.ids)):
        if e.labels[i] != IGNORE:
            src.append(i - 1)
            tgt.append(e.labels[i])
    return src, tgt


def collate(batch: list[Encoded], pad: int = 0):
    """Padded tensors for one homogeneous batch. Needs torch only here."""
    import torch

    n_latent = batch[0].n_latent
    if any(e.n_latent != n_latent for e in batch):
        raise ValueError("a batch must be homogeneous in n_latent")
    width = max(len(e.ids) for e in batch)
    k = max(len(supervised_pairs(e)[0]) for e in batch)
    ids = torch.full((len(batch), width), pad, dtype=torch.long)
    first = torch.zeros(len(batch), dtype=torch.long)
    sel = torch.zeros(len(batch), k, dtype=torch.long)
    tgt = torch.full((len(batch), k), IGNORE, dtype=torch.long)
    for i, e in enumerate(batch):
        ids[i, : len(e.ids)] = torch.tensor(e.ids)
        first[i] = e.first_latent
        s, t = supervised_pairs(e)
        # With no latent segment nothing shifts, and the position before the
        # prompt's own <|a|> is a legitimate source. With one, every supervised
        # source has to sit past the segment or the uniform shift is wrong.
        floor = e.first_latent + e.n_latent
        if e.n_latent and s and min(s) < floor:
            raise ValueError("a supervised position falls inside the latent "
                             "segment, which the compressed pass cannot shift")
        sel[i, : len(s)] = torch.tensor(s)
        tgt[i, : len(t)] = torch.tensor(t)
    return {"ids": ids, "first_latent": first, "n_latent": n_latent,
            "sel": sel, "tgt": tgt, "width": width}


# ------------------------------------------------------------------ stream

def build_episodes(seeds) -> list[Episode]:
    out: list[Episode] = []
    for s in seeds:
        out.extend(training_episodes(s))
    return out


def build_induction(seeds) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for s in seeds:
        out.extend(induction_examples(s))
    return out


def group_batches(pool: list, batch_size: int, key, rng_seed: int = 1234):
    """Endless batches of similar length, in shuffled group order.

    Same shape as src.opgraph's own batcher: sort by length, cut into groups of
    batch_size, then shuffle which group comes next. What is matched against
    the arms is the batch size in sequences and the number of optimizer steps.
    """
    order = sorted(range(len(pool)), key=lambda i: key(pool[i]))
    groups = [order[i:i + batch_size] for i in range(0, len(order), batch_size)]
    groups = [g for g in groups if len(g) == batch_size] or [order[:batch_size]]
    rng = random.Random(rng_seed)
    while True:
        perm = list(range(len(groups)))
        rng.shuffle(perm)
        for gi in perm:
            yield [pool[i] for i in groups[gi]]
