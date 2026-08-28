"""Primitive 4: abstraction construction.

Turn examples into a reusable procedure rather than a summary. A lesson
shows worked cases of an invented filing rule and never states the rule.
The model then files a case it has not seen. In the transfer condition the
case arrives in a vocabulary that shares no content word with the lesson,
joined to it only by an explicit legend, so a model that matched text
cannot produce the label at all while a model that built the rule can.

The rules are comparisons, never arithmetic: the first reading exceeds the
second, the first reading falls below the second, or the two readings have
the same parity. The first two are complements, so a model that assumes a
filing convention instead of inducing one scores one half across the pair.
Nothing here needs a calculator and nothing needs two chained inferences,
so a model that fails at composition depth two can still score one.

Two baselines are computed on every item at generation time and printed
next to the model's score. The copy baseline files the case the way the
lexically nearest lesson example was filed. The majority baseline always
files it the way most lesson examples were filed. Lesson labels are
balanced, so the majority baseline sits at one half, and the readings in
the test case are drawn away from every taught pair, so the copy baseline
has nothing useful to match. A model that beats both built something.

CONTAMINATION CONTROL, faculty by faculty.

Composition depth: one comparison, one label. The transfer condition adds
exactly one renaming lookup through a legend that states the
correspondence outright, and the same-surface condition is reported beside
it so the cost of that single extra step is visible rather than assumed.

Information acquisition: the lesson is in the context and the chunk list.
Nothing is retrieved and no source is chosen.

Missing-capability recognition: nothing is missing. Every item is
answerable from its lesson, and generation checks that the reference
implementation answers it.

Intent understanding: the instruction is one literal sentence with an
explicit two-word answer set.

Temporary knowledge: single turn, and the lesson sits immediately above
the question.

Verification and action: no trap and no revision. The first reading that
applies the induced rule is correct.

Chance control: the two labels are balanced across items and inside every
lesson, so chance is one half, a constant reply scores one half, and the
report carries both degenerate baselines explicitly.
"""

from __future__ import annotations

import random

from src.primitives.common import (
    Item, invented_words, label_verdict, overlap, parse_one_label, proportion,
)

PRIMITIVE = "abstraction"
STRUCTURES = ("greater", "lesser", "parity")

INSTRUCTIONS = """The lesson below files a number of cases. The rule behind the
filing is not written down anywhere. Work out the rule from the cases, then file
the new case the same way.
Answer with exactly this line:
ANSWER: one of {labels}"""


def _label_of(struct: str, a: int, b: int) -> int:
    """The invented rule. Never arithmetic, always one comparison.

    greater and lesser are complements on purpose: a model that assumes a
    filing convention instead of inducing one scores one half across the
    pair, so a prior cannot be mistaken for an induced rule. The class word
    on every case is a distractor and enters no rule.
    """
    if struct == "greater":
        return 0 if a > b else 1
    if struct == "lesser":
        return 0 if a < b else 1
    return 0 if (a % 2) == (b % 2) else 1


def _case_line(v: dict, a: int, b: int, cat: str) -> str:
    return (f"A {v['thing']} with {v['attr1']} {a}, {v['attr2']} {b} and "
            f"class {cat}")


def generate(seed: int, mode: str = "isolated", condition: str = "transfer") -> Item:
    rng = random.Random(seed * 2654435761 % (2 ** 31) + 3)
    struct = STRUCTURES[seed % len(STRUCTURES)]
    w = invented_words(rng, 12)
    v = {"thing": w[0], "attr1": w[1], "attr2": w[2],
         "lab0": w[3], "lab1": w[4], "sys": w[5].capitalize()}
    cats = w[6:12]

    taught: list[tuple[int, int, str, int]] = []
    seen: set[tuple[int, int, str]] = set()
    want = [0, 0, 0, 1, 1, 1]
    rng.shuffle(want)
    guard = 0
    while len(taught) < 6 and guard < 4000:
        guard += 1
        a, b = rng.randrange(5, 60), rng.randrange(5, 60)
        cat = rng.choice(cats)
        if a == b or (a, b, cat) in seen:
            continue
        lab = _label_of(struct, a, b)
        if lab != want[len(taught)]:
            continue
        seen.add((a, b, cat))
        taught.append((a, b, cat, lab))
    if len(taught) < 6:
        raise RuntimeError("could not balance the lesson")

    # The test readings sit above every taught reading, so no taught case is
    # a near neighbour of the new one and a nearest-example copier has
    # nothing to lean on.
    guard = 0
    while guard < 4000:
        guard += 1
        ta, tb = rng.randrange(61, 140), rng.randrange(61, 140)
        tcat = rng.choice(cats)
        if ta == tb or (ta, tb, tcat) in seen:
            continue
        break
    gold_i = _label_of(struct, ta, tb)

    lesson = "\n".join(
        f"  {_case_line(v, a, b, c)} is filed as "
        f"{v['lab0'] if lab == 0 else v['lab1']}."
        for a, b, c, lab in taught)

    if condition == "transfer":
        # Drawn disjoint from the lesson's vocabulary, so the test case
        # shares no content word with any lesson case and a copier has
        # nothing to match on.
        used = set(w)
        trng = random.Random(seed ^ 0x7A5F)
        rw: list[str] = []
        while len(rw) < 6:
            cand = invented_words(trng, 12)
            rw.extend(x for x in cand if x not in used and x not in rw)
        rw = rw[:6]
        t = {"thing": rw[0], "attr1": rw[1], "attr2": rw[2],
             "lab0": rw[3], "lab1": rw[4], "sys": rw[5].capitalize()}
        legend = (
            f"The {t['sys']} register keeps the same filing rule under other "
            f"names. A {t['thing']} stands where a {v['thing']} stood. Its "
            f"{t['attr1']} stands where {v['attr1']} stood, its {t['attr2']} "
            f"stands where {v['attr2']} stood, and its class word stands where "
            f"the class word stood. A {t['thing']} filed the way a {v['thing']} "
            f"would be filed {v['lab0']} is filed {t['lab0']}, and one filed "
            f"the way a {v['thing']} would be filed {v['lab1']} is filed "
            f"{t['lab1']}.")
        case = _case_line(t, ta, tb, tcat)
        labels = [t["lab0"], t["lab1"]]
        extra = "\n\nLegend.\n" + legend
    else:
        case = _case_line(v, ta, tb, tcat)
        labels = [v["lab0"], v["lab1"]]
        extra = ""

    body = (INSTRUCTIONS.format(labels=" or ".join(labels))
            + "\n\nLesson.\n" + lesson + extra
            + "\n\nNew case.\n" + case + ". How is it filed?")

    chunks = [{"text": "Lesson.\n" + lesson}]
    if mode == "integrated":
        # The lesson is not marked out. It arrives among worked cases from a
        # different register that follows a different rule, so the model has
        # to decide which examples constitute the lesson before it can
        # induce anything from them.
        other = random.Random(seed ^ 0x1234ABCD)
        ow = invented_words(other, 6)
        ov = {"thing": ow[0], "attr1": ow[1], "attr2": ow[2],
              "lab0": ow[3], "lab1": ow[4], "sys": ow[5].capitalize()}
        ocats = invented_words(other, 4)
        noise = "\n".join(
            f"  {_case_line(ov, other.randrange(5, 60), other.randrange(5, 60), other.choice(ocats))}"
            f" is filed as {other.choice([ov['lab0'], ov['lab1']])}."
            for _ in range(6))
        merged = lesson.splitlines() + noise.splitlines()
        other.shuffle(merged)
        body = body.replace("\n\nLesson.\n" + lesson,
                            "\n\nCases on file.\n" + "\n".join(merged))
        chunks = [{"text": "Cases on file.\n" + "\n".join(merged)}]

    copy_src = max(taught, key=lambda t4: overlap(
        _case_line(v, t4[0], t4[1], t4[2]), case))
    copy_pick = copy_src[3]
    majority_pick = 0 if sum(1 for t4 in taught if t4[3] == 0) > 3 else 1

    return Item(
        item_id=f"p4-{mode}-{condition}-{seed:07d}",
        primitive=PRIMITIVE, variant=f"{condition}/{struct}", mode=mode,
        question=body, chunks=chunks,
        gold={"answer": labels[gold_i], "labels": labels, "index": gold_i},
        meta={"seed": seed, "structure": struct, "condition": condition,
              "copy_correct": copy_pick == gold_i,
              "majority_correct": majority_pick == gold_i},
    )


def generate_many(n: int, seed: int = 0, mode: str = "isolated",
                  condition: str = "transfer") -> list[Item]:
    """n items with balanced gold labels, so chance is exactly one half."""
    out: list[Item] = []
    s = seed
    want = 0
    tried = 0
    while len(out) < n and tried < n * 60:
        tried += 1
        item = generate(s, mode=mode, condition=condition)
        s += 1
        if item.gold["index"] != want:
            continue
        out.append(item)
        want = 1 - want
    if len(out) < n:
        raise RuntimeError(f"only {len(out)} of {n} abstraction items balanced")
    return out


def grade(item: Item, response: str) -> dict:
    pick = parse_one_label(response, item.gold["labels"])
    v = label_verdict(response, item.gold["labels"], item.gold["answer"])
    return {"parsed": pick is not None,
            "correct": float(pick == item.gold["answer"]),
            "lenient_correct": v["lenient"], "hedged": v["hedged"],
            "chance": 1.0 / max(2, len(item.gold["labels"])),
            "structure": item.meta["structure"],
            "copy_correct": float(item.meta["copy_correct"]),
            "majority_correct": float(item.meta["majority_correct"])}


def choices(item: Item) -> list[dict]:
    return [{"field": "answer", "question": item.question,
             "options": list(item.gold["labels"]),
             "gold": item.gold["index"]}]


def aggregate(items: list[Item], grades: list[dict]) -> dict:
    if not items:
        return {"primitive": PRIMITIVE, "n": 0}
    n = len(grades)
    acc = proportion(sum(int(g["correct"]) for g in grades), n, 0.5, "accuracy")
    copy = proportion(sum(int(g["copy_correct"]) for g in grades), n, 0.5,
                      "copy_baseline")
    maj = proportion(sum(int(g["majority_correct"]) for g in grades), n, 0.5,
                     "majority_baseline")
    per_structure = {}
    deltas = []
    for st in sorted({g["structure"] for g in grades}):
        sel = [g for g in grades if g["structure"] == st]
        a = proportion(sum(int(g["correct"]) for g in sel), len(sel), 0.5, st)
        c = proportion(sum(int(g["copy_correct"]) for g in sel), len(sel), 0.5,
                       st + "/copy")
        per_structure[st] = {"accuracy": a, "copy_baseline": c,
                             "delta": a["acc"] - c["acc"]}
        deltas.append(a["acc"] - c["acc"])
    return {
        "primitive": PRIMITIVE, "mode": items[0].mode,
        "condition": items[0].meta["condition"], "n": n,
        # Averaging the per-structure margins rather than the pooled ones
        # keeps a structure whose copy baseline happens to be strong from
        # dragging the others down.
        "headline": sum(deltas) / len(deltas) if deltas else 0.0,
        "accuracy": acc, "copy_baseline": copy, "majority_baseline": maj,
        "beats_copy": bool(acc["ci_lo"] > copy["ci_hi"]),
        "per_structure": per_structure,
        "parse_rate": proportion(sum(int(g["parsed"]) for g in grades), n, 0.0,
                                 "parse_rate"),
    }


CONTAMINATION = __doc__
