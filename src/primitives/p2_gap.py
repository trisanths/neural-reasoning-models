"""Primitive 2: missing-capability recognition.

Not "I do not know fact X" but "I lack a procedure needed to continue". An
invented system arrives with a six-page manual and a problem. In half the
items every page the problem needs is present. In the other half exactly
one load-bearing page has been replaced by a filler page, and the model
has to say that it is blocked, classify the blockage structurally, and in
the isolated form say which step of a supplied plan first fails.

The structural answer never names the missing result. The gap menu is
fixed and describes kinds of absence, not values: a rule is not stated, a
constant the rule uses is not given, a conversion is not stated, a
precondition is not established, an ordering is not specified. Naming the
missing number would presume the knowledge, so the scorer never asks for
it and the report carries a leak counter that should stay at zero.

The calibration arm is the point of the design. Half the items are fully
answerable, so a model that always claims a gap scores at chance on
detection and shows a false-alarm rate of one. Detection, gap type and
step localisation are reported separately and never multiplied together.

CONTAMINATION CONTROL, faculty by faculty.

Composition depth: the plan is supplied, numbered, and at most five steps
long. The model never derives the plan and never executes it. In the
integrated form the plan is withheld, which is exactly the difference
between the two modes and is reported as its own curve rather than mixed
in.

Abstraction construction: no rule is induced, transferred or applied. The
model checks whether an ingredient a named step needs is present in the
manual, which is presence detection over stated text.

Information acquisition: every page is in the context, in a fixed order,
and the chunk list carries them; nothing is hidden behind a query.

Intent understanding: the problem statement is literal and short, with no
underspecification and no contradiction. There is no request to parse.

Temporary knowledge: single turn.

Verification and action: nothing is computed, so there is nothing to
check. A model that cannot do arithmetic can score one here.

Shortcut control: page count is held at six in both arms, so counting
pages cannot separate them; the filler pages reuse the same invented
entity names as the real pages, so a keyword-nearest reader cannot spot
the odd one out; the problem stem is byte-identical between the blocked
and unblocked version of the same seed, so nothing in the question
predicts the answer; and the five gap types are assigned round-robin over
seeds, so a constant reply scores one in five.
"""

from __future__ import annotations

import random

from src.primitives.common import (
    Item, field_or_whole, invented_words, parse_binary, parse_fields,
    parse_one_label, proportion,
)

PRIMITIVE = "gap"

GAP_MENU = [
    ("T1", "a rule relating two of the named quantities is not stated"),
    ("T2", "the value of a constant that a stated rule uses is not given"),
    ("T3", "a conversion between the unit given and the unit required is not stated"),
    ("T4", "the condition under which a stated procedure applies is not established"),
    ("T5", "the order in which two stated operations combine is not specified"),
]
GAP_LABELS = [g[0] for g in GAP_MENU] + ["NONE"]
GAP_STEP = {"T1": 3, "T2": 3, "T3": 1, "T4": 2, "T5": 4}
STEP_LABELS = ["1", "2", "3", "4", "5", "0"]

INSTRUCTIONS = """You are given a manual and a problem. Do not solve the problem.
Decide only whether the manual contains everything the problem needs.
Do not state, guess or name any value the manual does not contain.
Answer with exactly these three lines:
STATUS: BLOCKED or SOLVABLE
GAP: {gapopts}
STEP: {stepopts}"""

MENU_TEXT = "\n".join(f"  {lab}. {txt}" for lab, txt in GAP_MENU)


def _pages(v: dict) -> dict:
    """The five load-bearing pages, keyed by the gap type each one prevents."""
    return {
        "T1": (f"The {v['sys']} relation.\n\n"
               f"The {v['out']} of a consignment is obtained from its {v['inp']}. "
               f"Take the {v['inp']} in {v['small']}, multiply it by the "
               f"{v['const']} factor, and the product is the {v['out']}."),
        "T2": (f"The {v['const']} factor.\n\n"
               f"In the {v['sys']} the {v['const']} factor has the value "
               f"{v['kval']}. It is the same for every consignment and does not "
               f"change with the {v['inp']}."),
        "T3": (f"Measures in the {v['sys']}.\n\n"
               f"A {v['inp']} may be quoted in {v['big']} or in {v['small']}. "
               f"One {v['big']} is {v['conv']} {v['small']}."),
        "T4": (f"Scope of the {v['sys']} relation.\n\n"
               f"The relation applies to a consignment only once the consignment "
               f"has been marked {v['flag']}. A consignment that has not been "
               f"marked {v['flag']} is outside the relation entirely."),
        "T5": (f"Combining the {v['sys']} adjustments.\n\n"
               f"Two adjustments may apply to one {v['out']}: the {v['adj1']} "
               f"adjustment and the {v['adj2']} adjustment. When both apply the "
               f"{v['adj1']} adjustment is carried out first and the {v['adj2']} "
               f"adjustment is carried out on its result."),
    }


def _filler(v: dict, n: int) -> str:
    """A page in the same voice that no step of the plan needs.

    It reuses the invented entity names on purpose, so the blocked manual
    cannot be spotted by looking for the page that mentions unfamiliar
    words, and so a keyword-nearest reader has nothing to latch onto.
    """
    if n == 0:
        return (f"Filing the {v['sys']} record.\n\n"
                f"Every consignment carries a {v['sys']} record. The record "
                f"lists the {v['inp']}, the {v['out']} and the {v['flag']} "
                f"marking. Records are filed by consignment, never by "
                f"{v['const']} factor.")
    return (f"History of the {v['sys']}.\n\n"
            f"The {v['sys']} replaced an earlier convention in which the "
            f"{v['out']} was quoted without reference to the {v['inp']}. "
            f"The {v['adj1']} and {v['adj2']} adjustments date from that "
            f"convention and were carried over unchanged.")


def _plan(v: dict) -> str:
    return (f"  1. Express the consignment's {v['inp']} in {v['small']}.\n"
            f"  2. Confirm the consignment has been marked {v['flag']}.\n"
            f"  3. Obtain the {v['out']} from the {v['inp']}.\n"
            f"  4. Apply the {v['adj1']} and {v['adj2']} adjustments.\n"
            f"  5. Report the {v['out']}.")


def generate(seed: int, mode: str = "isolated",
             blocked: bool | None = None) -> Item:
    """One manual and one problem.

    Every draw that shapes the problem statement happens before the arm is
    decided, so generate(seed, blocked=True) and generate(seed,
    blocked=False) produce the same vocabulary and the same problem text.
    Nothing in the question predicts whether a page has been removed.
    """
    rng = random.Random(seed * 7919 + 13)
    w = invented_words(rng, 9)
    v = {"sys": w[0].capitalize() + " scheme", "inp": w[1], "out": w[2],
         "small": w[3], "big": w[4], "const": w[5], "flag": w[6],
         "adj1": w[7], "adj2": w[8],
         "kval": rng.randrange(3, 40), "conv": rng.randrange(4, 25)}
    quantity = rng.randrange(2, 12)
    problem = (f"A consignment has been marked {v['flag']} and its {v['inp']} "
               f"is {quantity} {v['big']}. The {v['adj1']} and {v['adj2']} "
               f"adjustments both apply. What is its {v['out']}?")

    if blocked is None:
        blocked = (seed % 2 == 0)
    gap = GAP_MENU[(seed // 2) % len(GAP_MENU)][0]

    pages = _pages(v)
    order = ["T3", "T4", "T1", "T2", "T5"]
    rng.shuffle(order)
    docs = [pages[t] for t in order if not (blocked and t == gap)]
    docs.append(_filler(v, 0))
    if blocked:
        docs.append(_filler(v, 1))
    rng.shuffle(docs)

    if mode == "isolated":
        head = (INSTRUCTIONS.format(
            gapopts="one label from the gap menu, or NONE",
            stepopts="the number of the first plan step that cannot be "
                     "carried out, or 0")
            + "\n\nGap menu.\n" + MENU_TEXT
            + "\n\nPlan.\n" + _plan(v))
    else:
        head = (INSTRUCTIONS.format(
            gapopts="one label from the gap menu, or NONE",
            stepopts="0")
            + "\n\nGap menu.\n" + MENU_TEXT)
    question = head + "\n\nProblem.\n" + problem

    chunks = [{"text": d} for d in docs]
    if mode == "integrated":
        # No plan, and the manual sits among manuals for other schemes, so
        # the model has to find the relevant pages before it can notice one
        # is absent. That is the acquisition load the isolated form removes.
        other = random.Random(seed ^ 0xB10C)
        ow = invented_words(other, 9)
        ov = {"sys": ow[0].capitalize() + " scheme", "inp": ow[1], "out": ow[2],
              "small": ow[3], "big": ow[4], "const": ow[5], "flag": ow[6],
              "adj1": ow[7], "adj2": ow[8],
              "kval": other.randrange(3, 40), "conv": other.randrange(4, 25)}
        chunks = chunks + [{"text": p} for p in _pages(ov).values()]
        other.shuffle(chunks)

    hidden = str(v["kval"]) if gap == "T2" else (
        str(v["conv"]) if gap == "T3" else "")

    return Item(
        item_id=f"p2-{mode}-{seed:07d}",
        primitive=PRIMITIVE,
        variant=(gap if blocked else "solvable"),
        mode=mode, question=question, chunks=chunks,
        gold={"status": "BLOCKED" if blocked else "SOLVABLE",
              "gap": gap if blocked else "NONE",
              "step": str(GAP_STEP[gap]) if blocked else "0",
              "hidden_value": hidden},
        meta={"seed": seed, "n_pages": len(docs), "blocked": blocked,
              "graded_step": mode == "isolated"},
    )


def generate_many(n: int, seed: int = 0, mode: str = "isolated") -> list[Item]:
    """n items, balanced blocked against solvable and round-robin over gaps."""
    items = [generate(seed + i, mode=mode) for i in range(n)]
    counts = {i.meta["n_pages"] for i in items}
    if len(counts) != 1:
        raise RuntimeError(f"page count leaks the answer: {sorted(counts)}")
    return items


STATUS_CUES = {
    "BLOCKED": ["blocked", "missing", "absent", "incomplete", "insufficient",
                "cannot", "not enough", "no"],
    "SOLVABLE": ["solvable", "complete", "sufficient", "enough", "answerable",
                 "can", "yes"],
}


def grade(item: Item, response: str) -> dict:
    """Read the answer generously and report the strict parse rate apart.

    A model that never learned to write STATUS still says something when
    it writes "no". Scoring that as a miss would turn a format failure
    into a faculty reading, which is the whole thing this suite is built
    to prevent.
    """
    f = parse_fields(response)
    status = parse_binary(field_or_whole(f, "STATUS", response), STATUS_CUES)
    gap = parse_one_label(field_or_whole(f, "GAP", response), GAP_LABELS)
    step = parse_one_label(f.get("STEP", ""), STEP_LABELS)
    g = item.gold
    detected = status == g["status"]
    hv = g["hidden_value"]
    return {
        "parsed": "STATUS" in f,
        "detected": float(detected),
        "false_alarm": float(g["status"] == "SOLVABLE" and status == "BLOCKED"),
        "miss": float(g["status"] == "BLOCKED" and status != "BLOCKED"),
        "gap": float(detected and gap == g["gap"]),
        "step": float(detected and step == g["step"]),
        "blocked_item": g["status"] == "BLOCKED",
        "leak_named": float(bool(hv) and hv in response),
    }


def aggregate(items: list[Item], grades: list[dict]) -> dict:
    if not items:
        return {"primitive": PRIMITIVE, "n": 0}
    n = len(grades)
    det = proportion(sum(int(g["detected"]) for g in grades), n, 0.5, "detection")
    solv = [g for g in grades if not g["blocked_item"]]
    blk = [g for g in grades if g["blocked_item"]]
    out = {
        "primitive": PRIMITIVE, "mode": items[0].mode, "n": n,
        "headline": det["adjusted"],
        "detection": det,
        "false_alarm": proportion(sum(int(g["false_alarm"]) for g in solv),
                                  len(solv), 0.0, "false_alarm"),
        "miss": proportion(sum(int(g["miss"]) for g in blk), len(blk), 0.0, "miss"),
        "gap_type": proportion(sum(int(g["gap"]) for g in blk), len(blk),
                               0.5 / len(GAP_MENU), "gap_type"),
        "leak_named": proportion(sum(int(g["leak_named"]) for g in grades), n,
                                 0.0, "leak_named"),
        "parse_rate": proportion(sum(int(g["parsed"]) for g in grades), n, 0.0,
                                 "parse_rate"),
    }
    if items[0].meta.get("graded_step"):
        out["step_localisation"] = proportion(
            sum(int(g["step"]) for g in blk), len(blk), 0.5 / 5, "step")
    out["per_variant"] = {
        var: proportion(
            sum(int(g["detected"]) for i, g in zip(items, grades) if i.variant == var),
            sum(1 for i in items if i.variant == var), 0.5, f"detection/{var}")
        for var in sorted({i.variant for i in items})
    }
    return out


CONTAMINATION = __doc__
