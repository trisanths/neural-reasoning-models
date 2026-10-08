"""Prompt formats and supervised data for the three model tasks.

Three tasks, one format. Everything is written in the tokens the backbone was
pretrained on, so nothing here asks it to learn a new control vocabulary:

  direct   <|world|> opgraph <|doc|> page ... <|q|> question <|a|> answer <|eot|>
  induce   <|world|> opgraph <|doc|> page <|q|> induce <|a|> (defop ...) <|eot|>
  plan     <|world|> opgraph <|doc|> ops @/2 #/2 <|q|> plan question <|a|> t1 = ... <|eot|>

The direct condition is trained on the same questions from the same worlds as
the plan condition, with the pages in context, half the time all four pages and
half the time only the pages the question needs. It therefore gets the gold
source chapter rescue for free on half its training and on one of its two
evaluation conditions.

Loss covers the answer span and the closing <|eot|> only. The prompt is masked
out, so neither condition is scored for predicting pages it was handed.
"""

from __future__ import annotations

import random

from src.opgraph.invent import (breadth_item, decide_item, make_world, novel,
                                seq_flat, seq_paren, units_item)
from src.opgraph.opdef import serialize_all
from src.opgraph.plan import serialize_plan, signature_line, trace_text

IGNORE = -100


def direct_prompt(world, question: str, keys=None) -> str:
    return f"<|world|> opgraph{world.context(keys)} <|q|> {question} <|a|>"


def induce_prompt(page_text: str) -> str:
    return f"<|world|> opgraph <|doc|> {page_text} <|q|> induce <|a|>"


def trace_prompt(world, question: str, keys=None) -> str:
    return f"<|world|> opgraph{world.context(keys)} <|q|> trace {question} <|a|>"


def plan_prompt(ops, question: str) -> str:
    return (f"<|world|> opgraph <|doc|> ops {signature_line(ops)} "
            f"<|q|> plan {question} <|a|>")


def step_prompt(ops, question: str, prefix: str) -> str:
    """The scheduler asked for one step at a time, given the plan so far.

    Writing a whole plan in one generation makes the length of the plan
    something the decoder has to get right, and a decoder trained on plans of
    at most three steps has learned to stop at three. Asking for one step at a
    time removes that: a plan of any length is the same short decision, taken
    repeatedly, and the length prior has nothing to attach to.
    """
    return (f"<|world|> opgraph <|doc|> ops {signature_line(ops)} "
            f"<|q|> plan {question} <|result|> {prefix} <|a|>")


def plan_steps(plan) -> list[str]:
    """A plan as the chunks a stepwise scheduler emits, in order."""
    return [c.strip() for c in serialize_plan(plan).split(";")]


def step_examples(ops, question: str, plan) -> list[tuple[str, str]]:
    chunks = plan_steps(plan)
    out = []
    for k in range(len(chunks)):
        prefix = " ; ".join(chunks[:k]) + (" ;" if k else "")
        out.append((step_prompt(ops, question, prefix), chunks[k]))
    return out


def training_examples(seed: int, arm: str) -> list[tuple[str, str]]:
    """(prompt, target) pairs from one world, for the given arm.

    arm is "direct" or "opgraph". Both draw the same world and the same four
    questions, so the two arms are trained on identical episodes and differ
    only in what they are asked to produce.
    """
    rng = random.Random(seed * 104729 + 7)
    breadth = rng.choice([1, 2, 3])
    w = make_world(seed, breadth=breadth)
    items = [seq_flat(w, rng, rng.choice([1, 2, 3])),
             seq_paren(w, rng, rng.choice([2, 3])),
             breadth_item(w, rng, breadth),
             units_item(w, rng)]
    out: list[tuple[str, str]] = []
    if arm == "direct":
        for it in items:
            keys = None if rng.random() < 0.5 else set(it.pages)
            out.append((direct_prompt(w, it.text, keys), it.gold))
        return out
    if arm == "trace":
        for it in items:
            keys = None if rng.random() < 0.5 else set(it.pages)
            out.append((trace_prompt(w, it.text, keys), trace_text(it.plan, w.ops)))
        return out
    if arm in ("opgraph", "opgraph_step"):
        for p in w.shuffled_pages():
            out.append((induce_prompt(p.text), serialize_all(p.ops)))
        for it in items:
            if arm == "opgraph":
                out.append((plan_prompt(w.ops, it.text), serialize_plan(it.plan)))
            else:
                out.extend(step_examples(w.ops, it.text, it.plan))
        return out
    raise ValueError(arm)


def build_stream(seeds, arm: str, rng_seed: int = 0):
    """A shuffled stream of (prompt, target) for the arm, over the seed range."""
    pool: list[tuple[str, str]] = []
    for s in seeds:
        pool.extend(training_examples(s, arm))
    random.Random(rng_seed).shuffle(pool)
    return pool


def encode_example(tok, prompt: str, target: str, max_len: int):
    """Token ids and targets with the prompt masked, ready for the model."""
    p = tok.encode(prompt)
    t = tok.encode(" " + target) + [tok.token_id("<|eot|>")]
    ids = p + t
    if len(ids) > max_len:
        return None
    labels = [IGNORE] * len(p) + t
    return ids, labels


# ------------------------------------------------------------- eval sets

# Eval worlds live in a seed range the training stream never touches, and the
# same worlds are reused across every depth of a kind so an induced operator
# table can be computed once and shared by the whole curve.
EVAL_SEED0 = 900_000_000
KIND_OFFSET = {"sequential": 0, "sequential_paren": 1, "breadth": 2,
               "novel": 3, "same_page_pair": 4, "units": 5}


def eval_worlds(kind: str, n: int, breadth: int = 3, style: int = 0):
    """`n` fresh worlds for one kind, keyed so no two kinds share a world.

    style 1 returns the same worlds with every page rewritten in different
    prose. Same seeds, same operators, different wording.
    """
    base = EVAL_SEED0 + 1_000_000 * KIND_OFFSET[kind] + 10_000 * breadth
    return [make_world(base + i, breadth=breadth, style=style) for i in range(n)]


def make_item(kind: str, world, depth: int, index: int):
    rng = random.Random(world.seed * 31 + depth * 1013 + index)
    if kind == "sequential":
        return seq_flat(world, rng, depth)
    if kind == "sequential_paren":
        return seq_paren(world, rng, depth)
    if kind == "breadth":
        return breadth_item(world, rng, depth)
    if kind == "novel":
        return novel(world, rng, depth)
    if kind == "same_page_pair":
        return decide_item(world, rng)
    if kind == "units":
        return units_item(world, rng)
    raise ValueError(kind)


def eval_items(kind: str, depth: int, n: int, style: int = 0):
    """One question per world, at the given depth."""
    breadth = depth if kind == "breadth" else 3
    ws = eval_worlds(kind, n, breadth=breadth, style=style)
    return [make_item(kind, w, depth, i) for i, w in enumerate(ws)]
