"""The integrated episode and the causal rescue matrix.

Seven independent primitive tests are necessary and not sufficient. A
failed integrated episode smears its failure downstream: the model that
never parsed the brief also never found the chapter, so its retrieval
looks broken too. The fix is intervention. One episode is built that
needs all seven faculties, and then each faculty in turn is replaced by an
oracle. What rescues the episode locates the failure.

One episode, seven demands.

  intent        the brief is written the way a person writes one, with the
                goal buried under asides, and the question at the end
                refers back to it rather than restating it.
  acquisition   the chapter that teaches the procedure sits among eight
                chapters for other depots that are written identically.
  abstraction   the chapter states two tables and shows two worked runs of
                a procedure it never names. The order of operations exists
                only in those runs and has to be induced.
  gap           the second table is missing exactly the entry the chain
                needs. The brief's fine print says what to do when the
                archive is silent, so noticing the silence is the step,
                and no value has to be guessed.
  composition   three chained applications, the second of which is the one
                the gap sits under.
  memory        the consignment is named in the first paragraph of the
                brief and never again; the question refers to it as the
                one named at the top.
  verification  a candidate answer is supplied. It is the result of
                stopping one operation early, which is what a plausible
                first reading produces. It is always wrong, so the perfect
                verifier signal never carries the answer.

The interventions, one per faculty, exactly as pre-registered. Each one
supplies what that faculty would have produced and nothing further. The
composition oracle supplies intermediate results and never the final
answer, and generation asserts the final answer does not occur in any
injected block.

Reading the matrix. The condition with no oracle is the baseline. A
faculty whose oracle lifts the episode is where the episode was losing.
The lift is reported with a Wilson interval and with the paired
disagreement counts behind it, because at these sample sizes a raw
difference of means hides how many items actually changed.
"""

from __future__ import annotations

import random

from src.primitives.common import Item, invented_words, parse_one_label, proportion, wilson

PRIMITIVE = "episode"
N_NAMES = 8
CHANCE = 1.0 / N_NAMES

FACULTIES = ("intent", "gap", "acquisition", "abstraction", "composition",
             "verification", "memory")
CONDITIONS = ("none",) + tuple(f"oracle_{f}" for f in FACULTIES) + ("oracle_all",)

HEADER = """Read the brief and the archive, then answer the question at the end.
Answer with exactly this line:
ANSWER: one of the names listed under Names"""


def _cycle(rng: random.Random, names: list[str]) -> dict:
    order = list(names)
    rng.shuffle(order)
    return {order[i]: order[(i + 1) % len(order)] for i in range(len(order))}


def _table(mapping: dict, rng: random.Random, verb: str, omit=None) -> str:
    lines = [f"  {a} {verb} {b}." for a, b in mapping.items() if a != omit]
    rng.shuffle(lines)
    return "\n".join(lines)


def build(seed: int) -> dict:
    """One episode specification, independent of which oracles are applied."""
    rng = random.Random(seed * 9176 + 17)
    names = invented_words(rng, N_NAMES, 2)
    depot = invented_words(rng, 10, 2)
    step_a, step_b = depot[0].capitalize(), depot[1].capitalize()

    for _ in range(600):
        ma, mb = _cycle(rng, names), _cycle(rng, names)
        start = rng.choice(names)
        m1 = ma[start]
        # The gap: the second table is silent on m1, and the brief's fine
        # print says a name the archive is silent on passes through
        # unchanged. So the chain is a, then nothing, then a.
        m2 = m1
        final = ma[m2]
        candidate = m2  # where you stand if the third operation is forgotten
        chain = [start, m1, final]
        if len(set(chain)) == 3 and candidate != final:
            break
    else:
        raise RuntimeError("could not build an episode")

    # Two worked runs of the same three-operation procedure on other starts,
    # which is the only place the order of operations is stated. Neither run
    # passes through the name the second table is silent on, so the fine
    # print's fallback is never demonstrated and has to be applied fresh.
    worked = []
    for s0 in [n for n in names if n not in chain][:2]:
        w1 = ma[s0]
        w2 = mb[w1]
        w3 = ma[w2]
        worked.append(f"  Starting from {s0}, the depot reaches {w1}, then "
                      f"{w2}, and files it as {w3}.")

    gold_chapter = (
        f"Chapter {depot[2].upper()}. The {depot[3]} depot.\n\n"
        f"The {step_a} operation:\n{_table(ma, rng, 'goes to')}\n\n"
        f"The {step_b} operation:\n{_table(mb, rng, 'goes to', omit=m1)}\n\n"
        f"Two runs recorded by the {depot[3]} depot:\n" + "\n".join(worked))

    others = []
    for i in range(8):
        orng = random.Random(seed * 31 + i * 7 + 3)
        ow = invented_words(orng, N_NAMES, 2)
        od = invented_words(orng, 4, 2)
        oa, ob = _cycle(orng, ow), _cycle(orng, ow)
        s0 = orng.choice(ow)
        others.append(
            f"Chapter {od[0].upper()}. The {od[1]} depot.\n\n"
            f"The {od[2].capitalize()} operation:\n{_table(oa, orng, 'goes to')}\n\n"
            f"The {od[3].capitalize()} operation:\n{_table(ob, orng, 'goes to')}\n\n"
            f"Two runs recorded by the {od[1]} depot:\n"
            f"  Starting from {s0}, the depot reaches {oa[s0]}, then "
            f"{ob[oa[s0]]}, and files it as {oa[ob[oa[s0]]]}.")

    archive = [gold_chapter] + others
    rng.shuffle(archive)

    brief = (
        f"The consignment we are dealing with is {start}. I will not repeat "
        f"that.\n\n"
        f"Anyway. The {depot[3]} depot has a way of doing this and I want it "
        f"done their way, not ours. Do not use the {depot[4]} depot's method, "
        f"whatever anyone tells you, and ignore the {depot[5]} paperwork "
        f"entirely, that is a different job.\n\n"
        f"Fine print, and this matters: where the archive gives no entry for "
        f"a name under an operation, that name passes through the operation "
        f"unchanged. Do not invent an entry and do not skip the operation.\n\n"
        f"Somebody has already written an answer down. I do not trust it.")

    return {
        "seed": seed, "names": names, "start": start, "chain": chain,
        "final": final, "candidate": candidate, "m1": m1, "m2": m2,
        "step_a": step_a, "step_b": step_b, "depot": depot[3],
        "gold_chapter": gold_chapter, "archive": archive, "brief": brief,
    }


def _oracles(spec: dict) -> dict:
    """The block each intervention injects. Never the final answer."""
    return {
        "intent": (
            f"Structured goal, supplied.\n"
            f"  goal: report the name the {spec['depot']} depot's procedure "
            f"files the consignment under.\n"
            f"  subject: the consignment named at the top of the brief.\n"
            f"  method: the {spec['depot']} depot's procedure, from the "
            f"archive.\n"
            f"  rule when the archive is silent: the name passes through "
            f"unchanged.\n"
            f"  output: one name."),
        "gap": (
            f"Capability gap, supplied.\n"
            f"  The {spec['step_b']} operation table gives no entry for "
            f"{spec['m1']}. There is no way to look it up and none is "
            f"needed: the brief's fine print settles it, and {spec['m1']} "
            f"passes through {spec['step_b']} unchanged."),
        "abstraction": (
            f"Procedure, supplied.\n"
            f"  The {spec['depot']} depot's procedure is: apply "
            f"{spec['step_a']}, then apply {spec['step_b']}, then apply "
            f"{spec['step_a']} again. Three operations, in that order."),
        "composition": (
            f"Intermediate results, supplied.\n"
            f"  After the first operation the consignment is at "
            f"{spec['m1']}.\n"
            f"  After the second operation it is at {spec['m2']}.\n"
            f"  The third operation has not been carried out. Carry it out."),
        "verification": (
            f"Verifier signal, supplied.\n"
            f"  A checker has run the written answer, {spec['candidate']}, "
            f"against the procedure. It is wrong. Do not give it."),
        "memory": (
            f"Acquired state, re-injected.\n"
            f"  The consignment named at the top of the brief is "
            f"{spec['start']}."),
    }


def render(spec: dict, condition: str) -> Item:
    """One episode under one intervention."""
    oracles = _oracles(spec)
    if condition == "oracle_all":
        applied = list(FACULTIES)
    elif condition == "none":
        applied = []
    else:
        applied = [condition[len("oracle_"):]]

    archive = spec["archive"]
    if condition in ("oracle_acquisition", "oracle_all"):
        archive = [spec["gold_chapter"]]

    blocks = [oracles[f] for f in applied if f in oracles]
    injected = "\n\n".join(blocks)
    if injected and spec["final"] in injected:
        raise RuntimeError(f"oracle block for {condition} leaks the answer")

    question = (
        HEADER
        + "\n\nBrief.\n" + spec["brief"]
        + "\n\nArchive.\n" + "\n\n".join(archive)
        + "\n\nNames.\n  " + ", ".join(sorted(spec["names"]))
        + f"\n\nThe answer already written down.\n  {spec['candidate']}"
        + (("\n\n" + injected) if injected else "")
        + "\n\nQuestion.\nUnder which name does the "
        + f"{spec['depot']} depot file the consignment the brief names?")
    return Item(
        item_id=f"ep-{condition}-{spec['seed']:07d}",
        primitive=PRIMITIVE, variant=condition, mode="integrated",
        question=question, chunks=[{"text": c} for c in archive],
        gold={"answer": spec["final"], "labels": spec["names"]},
        meta={"seed": spec["seed"], "condition": condition,
              "candidate": spec["candidate"],
              "n_chapters": len(archive),
              "oracles": applied},
    )


def generate_matrix(n: int, seed: int = 0,
                    conditions=CONDITIONS) -> list[Item]:
    """The same n episodes rendered under every condition.

    The item set is identical across conditions by construction, so the
    lift a faculty's oracle produces is a paired quantity and the paired
    disagreement counts are meaningful.
    """
    out: list[Item] = []
    for i in range(n):
        spec = build(seed + i)
        for cond in conditions:
            out.append(render(spec, cond))
    return out


def grade(item: Item, response: str) -> dict:
    pick = parse_one_label(response, item.gold["labels"])
    return {"parsed": pick is not None,
            "correct": float(pick == item.gold["answer"]),
            "took_candidate": float(pick == item.meta["candidate"]),
            "condition": item.meta["condition"],
            "seed": item.meta["seed"]}


def aggregate(items: list[Item], grades: list[dict]) -> dict:
    """The rescue matrix: accuracy under each oracle and its paired lift."""
    by_cond: dict[str, list[dict]] = {}
    for g in grades:
        by_cond.setdefault(g["condition"], []).append(g)
    base = {g["seed"]: bool(g["correct"]) for g in by_cond.get("none", [])}

    rows = {}
    for cond, gs in by_cond.items():
        stat = proportion(sum(int(g["correct"]) for g in gs), len(gs), CHANCE,
                          cond)
        row = {"accuracy": stat,
               "took_candidate": proportion(
                   sum(int(g["took_candidate"]) for g in gs), len(gs), CHANCE,
                   cond + "/candidate")}
        if cond != "none" and base:
            b = sum(1 for g in gs
                    if g["correct"] and not base.get(g["seed"], False))
            c = sum(1 for g in gs
                    if not g["correct"] and base.get(g["seed"], False))
            row["lift"] = stat["acc"] - (
                sum(base.values()) / len(base) if base else 0.0)
            row["gained"] = b
            row["lost"] = c
            # Of the items the oracle changed, how many did it change for the
            # better. An interval that clears one half is a real rescue.
            if b + c:
                lo, hi = wilson(b, b + c)
                row["rescue_share"] = b / (b + c)
                row["rescue_ci"] = [lo, hi]
                row["rescued"] = bool(lo > 0.5)
            else:
                row["rescue_share"] = None
                row["rescued"] = False
        rows[cond] = row

    ranked = sorted(
        (c for c in rows if c not in ("none", "oracle_all")),
        key=lambda c: -(rows[c].get("lift") or 0.0))
    return {
        "primitive": PRIMITIVE, "n_episodes": len(base),
        "chance": CHANCE,
        "baseline": rows.get("none", {}).get("accuracy"),
        "ceiling": rows.get("oracle_all", {}).get("accuracy"),
        "rows": rows,
        "largest_rescue": ranked[0] if ranked else None,
        "ranking": ranked,
        "parse_rate": proportion(sum(int(g["parsed"]) for g in grades),
                                 len(grades), 0.0, "parse_rate"),
    }


CONTAMINATION = __doc__
