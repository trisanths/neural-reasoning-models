"""Training streams whose plan-length and symbol-count ceilings are settable.

The opgraph arm's training stream tops out at three plan steps and at one
distinct operator symbol per plan. Those are also the two ceilings the model
hits at evaluation. This module varies the training ceiling so the test
ceiling can be measured against it.

Only two things change relative to `src.opgraph.data.training_examples`:

  max_depth     the largest number of steps a training plan may have
  max_symbols   the largest number of distinct operator symbols one training
                plan may name

Everything else is held: the same base checkpoint, the same worlds from the
same seeds, four question items per world, the same induction half of the
stream, the same optimizer steps at the same batch size in sequences.

At max_depth=3 and max_symbols=1 the random draws are consumed in the same
order with the same candidate lists as the original, so the stream is
byte-identical to `build_stream(..., "opgraph")`. `check_parity` asserts it.
"""

from __future__ import annotations

import random

from src.opgraph.data import induce_prompt, plan_prompt, step_examples
from src.opgraph.invent import (Item, _reject_copyable, breadth_item,
                                make_world, seq_flat, seq_paren, units_item)
from src.opgraph.opdef import serialize_all
from src.opgraph.plan import Plan, Step, serialize_plan


def _depth_choices(max_depth: int, floor: int) -> list[int]:
    """The depths a training question of one family may be drawn from.

    `floor` is the smallest depth that family can express: one for a flat
    chain, two for the parenthesised form once it is above a bare application.
    A ceiling below the floor collapses the list to the ceiling itself.
    """
    lo = min(floor, max_depth)
    return list(range(lo, max_depth + 1))


def cross_item(world, rng: random.Random, n_symbols: int) -> Item:
    """A plan naming `n_symbols` distinct operators, drawn from two pages.

    The chain is a unit conversion feeding the assessment procedure, and at
    three symbols the procedure's decision on top of that. Two binary
    operators are never combined here, so the `novel` evaluation kind stays
    held out at every setting of the symbol ceiling: what the model is shown
    is that a plan may name more than one symbol, not which pair to combine.
    """
    return _reject_copyable(lambda r: _cross_item(world, r, n_symbols), rng)


def _cross_item(world, rng: random.Random, n_symbols: int) -> Item:
    upage = next(p for p in world.pages if p.key == "units")
    ppage = world.page_of("score")
    unit = rng.choice([upage.mid, upage.big])
    q = rng.randint(2, 15)
    ops = world.ops
    flags = ppage.flags
    bits = [rng.random() < 0.5 for _ in flags]
    desc = " ".join(
        f"It is {'marked' if b else 'not marked'} {flags[i][0]}."
        for i, b in enumerate(bits))
    head = (f"An application has a {ppage.attr} value equal to the number of "
            f"{upage.base} in {q} {unit}. {desc} ")
    base = ops[unit](q)
    steps = [Step("t1", unit, (q,)),
             Step("t2", "score", ("t1",) + tuple(bits))]
    if n_symbols >= 3:
        steps.append(Step("t3", "decide", ("t2",)))
        gold = ops["decide"](ops["score"](base, *bits))
        text = head + "Is it accepted or refused?"
        kind = "cross3"
    else:
        gold = ops["score"](base, *bits)
        text = head + "What is its adjusted value?"
        kind = "cross2"
    plan = Plan(tuple(steps), steps[-1].target)
    return Item(world, kind, len(steps), text, str(gold), plan,
                [upage.key, ppage.key],
                sorted({s.symbol for s in steps}))


def ceiling_items(seed: int, rng: random.Random, max_depth: int,
                  max_symbols: int) -> tuple:
    """One world and the four training questions drawn from it."""
    breadth = rng.choice([1, 2, 3])
    w = make_world(seed, breadth=breadth)
    # The draws are consumed in the order the original comprehension consumes
    # them: the depth for a question is drawn immediately before that question
    # is built, so at the default ceiling the stream is unchanged.
    items = [seq_flat(w, rng, rng.choice(_depth_choices(max_depth, 1))),
             seq_paren(w, rng, rng.choice(_depth_choices(max_depth, 2))),
             breadth_item(w, rng, breadth)]
    if max_symbols >= 2:
        items.append(cross_item(w, rng, max_symbols))
    else:
        items.append(units_item(w, rng))
    return w, items


def ceiling_examples(seed: int, arm: str, max_depth: int,
                     max_symbols: int) -> list[tuple[str, str]]:
    rng = random.Random(seed * 104729 + 7)
    w, items = ceiling_items(seed, rng, max_depth, max_symbols)
    out: list[tuple[str, str]] = []
    for p in w.shuffled_pages():
        out.append((induce_prompt(p.text), serialize_all(p.ops)))
    for it in items:
        if arm == "opgraph":
            out.append((plan_prompt(w.ops, it.text), serialize_plan(it.plan)))
        elif arm == "opgraph_step":
            out.extend(step_examples(w.ops, it.text, it.plan))
        else:
            raise ValueError(f"ceiling sweep covers the plan arms only, got {arm}")
    return out


def build_ceiling_stream(seeds, arm: str, rng_seed: int = 0, max_depth: int = 3,
                         max_symbols: int = 1):
    pool: list[tuple[str, str]] = []
    for s in seeds:
        pool.extend(ceiling_examples(s, arm, max_depth, max_symbols))
    random.Random(rng_seed).shuffle(pool)
    return pool


def stream_stats(pool) -> dict:
    """Plan-half statistics of a built stream, for the record."""
    from src.opgraph.plan import parse_plan
    lens: list[int] = []
    syms: list[int] = []
    induce = 0
    for prompt, target in pool:
        if " plan " not in prompt:
            induce += 1
            continue
        try:
            p = parse_plan(target)
        except Exception:
            continue
        lens.append(len(p.steps))
        syms.append(len({s.symbol for s in p.steps}))
    hist: dict[str, int] = {}
    for n in lens:
        hist[str(n)] = hist.get(str(n), 0) + 1
    shist: dict[str, int] = {}
    for n in syms:
        shist[str(n)] = shist.get(str(n), 0) + 1
    return {"induction_examples": induce, "plan_examples": len(lens),
            "plan_len_hist": hist, "plan_len_max": max(lens) if lens else 0,
            "plan_len_mean": round(sum(lens) / len(lens), 4) if lens else 0.0,
            "distinct_symbol_hist": shist,
            "distinct_symbol_max": max(syms) if syms else 0}


def check_parity(n: int = 200) -> bool:
    """The default ceiling must rebuild the original stream exactly."""
    from src.opgraph.data import build_stream
    a = build_ceiling_stream(range(n), "opgraph", rng_seed=17,
                             max_depth=3, max_symbols=1)
    b = build_stream(range(n), "opgraph", rng_seed=17)
    return a == b
