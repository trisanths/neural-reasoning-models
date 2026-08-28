"""Primitive 6: temporary knowledge.

Hold what was acquired across a long episode with no weight update, and do
not carry it into the next one. The episode is rendered as one segmented
transcript, which is what a stateless decoder actually sees, with the
segment boundaries and their meaning stated in the prompt.

Four arms, all scored against the same five-way answer menu so their
numbers are comparable.

retain, near and far. The fact is stated once, then one or six unrelated
work segments intervene, then it is asked for. The two distances differ in
nothing but the number of filler segments, so the gap between them is the
cost of distance and nothing else.

interfere. The fact is stated, then a second fact of the same shape about
a different entity states a different value for the same attribute, then
the first is asked for. Answering with the second entity's value is
counted as an intrusion and reported on its own line, because a model that
retains nothing and a model that retains the wrong thing are different
failures.

update. Two episodes with an explicit boundary between them, whose meaning
the prompt states. The same attribute of the same entity takes a new value
in the second episode and is asked for there. Answering with the first
episode's value is a leak.

absent. The same boundary, but the second episode never mentions the
entity. The answer is NOT STATED. Answering with the first episode's value
is a stale carry-over, which is the discard-after failure the primitive
names.

CONTAMINATION CONTROL, faculty by faculty.

Composition depth: the answer is one stated value, retrieved by one
lookup. Nothing is chained and nothing is computed.

Abstraction construction: nothing is induced. The fact is a literal
attribute of a literal entity in invented vocabulary.

Information acquisition: the whole transcript is in the context and in the
chunk list; there is no query to write and no source to pick.

Missing-capability recognition: only the absent arm involves saying that
something is not there, and it is a menu option rather than a structural
diagnosis, so it does not require the second primitive.

Intent understanding: the question is one literal sentence naming the
entity and the attribute.

Verification and action: no trap, no candidate to check, no revision.

Arithmetic: none. Values are three-digit tags that are never combined.

Shortcut control: the filler segments use their own attribute names and
their own numbers, so the answer is never the most frequent number in the
prompt; the menu always carries five options including NOT STATED, so the
option set does not signal which arm an item belongs to; the decoy values
are drawn from the same range as the true one; and the true value never
appears in the question.
"""

from __future__ import annotations

import random

from src.primitives.common import Item, invented_words, parse_one_label, proportion

PRIMITIVE = "memory"
VARIANTS = ("retain_near", "retain_far", "interfere", "update", "absent")
NOT_STATED = "NOT STATED"
N_OPTIONS = 5
CHANCE = 1.0 / N_OPTIONS

HEADER = """This is a transcript of one working session, split into segments.
A line reading ---- SEGMENT ---- separates two segments of the same session.
A line reading ---- SESSION ENDED, EVERYTHING ABOVE IS VOID ---- ends the
session; nothing stated before that line is in force after it.
Answer the question at the end from the transcript alone.
Answer with exactly this line:
ANSWER: one of the listed options"""

SEP = "---- SEGMENT ----"
END = "---- SESSION ENDED, EVERYTHING ABOVE IS VOID ----"


def _filler(rng: random.Random, n: int, sprinkle=()) -> list[str]:
    """Unrelated work segments.

    Every decoy option is planted in one of them, attached to some other
    entity and some other attribute. Without that, the only three-digit
    number anywhere in the transcript would be the answer, and picking the
    option that occurs at all would score one without any retention.
    """
    plant = list(sprinkle)
    out = []
    for i in range(n):
        w = invented_words(rng, 5, 2)
        a = plant.pop() if plant else rng.randrange(100, 999)
        b = plant.pop() if plant and rng.random() < 0.5 else rng.randrange(100, 999)
        out.append(
            f"The {w[0]} run was logged at bay {rng.randrange(2, 60)}. Its "
            f"{w[1]} count came to {a} and its {w[2]} count to {b}. The "
            f"{w[3]} sheet was signed by the {w[4]} desk and filed the same "
            f"afternoon. No exception was raised and the run closed on "
            f"schedule.")
    if plant:
        w = invented_words(rng, 3, 2)
        out.append(f"A later note on the {w[0]} file recorded its {w[1]} at "
                   + " and its ".join(f"{x}" for x in plant)
                   + f", under the {w[2]} heading.")
    return out


def generate(seed: int, variant: str, mode: str = "isolated") -> Item:
    rng = random.Random(seed * 6364136223846793005 % (2 ** 31) + 11)
    w = invented_words(rng, 6, 2)
    ent, ent2, attr = w[0], w[1], w[2]
    vals = rng.sample(range(100, 999), 4)
    v_true, v_other, d1, d2 = vals

    def state(e, a, val):
        if mode == "isolated":
            return f"Record this: the {a} of {e} is {val}."
        return (f"Work continued on {e} through the morning. Nothing unusual "
                f"came up. Its {a} came out at {val}, which the desk accepted "
                f"without comment, and the file was closed.")

    n_fill = 6 if variant in ("retain_far", "interfere") else 1
    plant = [d1, d2] + ([v_other] if variant in ("retain_near", "retain_far")
                        else [])
    fill = _filler(rng, n_fill, sprinkle=plant)
    segments: list[str] = []
    gold = str(v_true)

    if variant in ("retain_near", "retain_far"):
        segments = [state(ent, attr, v_true)] + fill
    elif variant == "interfere":
        segments = ([state(ent, attr, v_true)] + fill[:3]
                    + [state(ent2, attr, v_other)] + fill[3:])
    elif variant == "update":
        segments = [state(ent, attr, v_other)] + fill + [END] + \
                   [state(ent, attr, v_true)]
    elif variant == "absent":
        segments = [state(ent, attr, v_other)] + fill + [END] + \
                   _filler(rng, 1, sprinkle=[v_true])
        gold = NOT_STATED
    else:
        raise ValueError(variant)

    body = f"\n{SEP}\n".join(segments).replace(f"{SEP}\n{END}", END).replace(
        f"{END}\n{SEP}", END)
    if mode == "integrated":
        question = (f"What figure did the {attr} of {ent} come out at, "
                    f"as things stand now?")
    else:
        question = f"What is the {attr} of {ent} now?"

    options = [str(v_true), str(v_other), str(d1), str(d2), NOT_STATED]
    if variant == "absent":
        options = [str(v_other), str(d1), str(d2), str(vals[0]), NOT_STATED]
        options = list(dict.fromkeys(options))
        while len(options) < N_OPTIONS:
            options.insert(0, str(rng.randrange(100, 999)))
    rng.shuffle(options)

    prompt = (HEADER + "\n\nTranscript.\n" + body
              + "\n\nQuestion.\n" + question
              + "\n\nOptions.\n  " + "\n  ".join(options))
    return Item(
        item_id=f"p6-{variant}-{mode}-{seed:07d}",
        primitive=PRIMITIVE, variant=variant, mode=mode,
        question=prompt, chunks=[{"text": body}],
        gold={"answer": gold, "labels": options,
              "intrusion": str(v_other) if variant != "update" else None,
              "leak": str(v_other) if variant in ("update", "absent") else None},
        meta={"seed": seed, "n_segments": len(segments),
              "words": len(prompt.split())},
    )


def generate_many(n: int, seed: int = 0, mode: str = "isolated",
                  variants=VARIANTS) -> list[Item]:
    """n items per variant, guarded against the occurs-at-all shortcut.

    Every numeric option must occur somewhere in the transcript, so a model
    cannot score by naming the only option it can find, and the answer must
    occur exactly once, so it is never also the most frequent number.
    """
    out: list[Item] = []
    for var in variants:
        got, s, tried = 0, seed, 0
        while got < n and tried < n * 40:
            tried += 1
            item = generate(s, var, mode=mode)
            s += 1
            body = item.chunks[0]["text"]
            opts = [o for o in item.gold["labels"] if o != NOT_STATED]
            if not all(o in body for o in opts):
                continue
            g = item.gold["answer"]
            if g != NOT_STATED and body.count(g) != 1:
                continue
            out.append(item)
            got += 1
        if got < n:
            raise RuntimeError(f"only {got} of {n} memory items for {var}")
    return out


def grade(item: Item, response: str) -> dict:
    pick = parse_one_label(response, item.gold["labels"])
    g = item.gold
    return {"parsed": pick is not None,
            "correct": float(pick == g["answer"]),
            "intrusion": float(g["intrusion"] is not None
                               and pick == g["intrusion"]
                               and item.variant == "interfere"),
            "leak": float(g["leak"] is not None and pick == g["leak"]
                          and item.variant in ("update", "absent")),
            "variant": item.variant}


def aggregate(items: list[Item], grades: list[dict]) -> dict:
    if not items:
        return {"primitive": PRIMITIVE, "n": 0}
    per = {}
    for var in sorted({g["variant"] for g in grades}):
        sel = [g for g in grades if g["variant"] == var]
        per[var] = proportion(sum(int(g["correct"]) for g in sel), len(sel),
                              CHANCE, var)
    inter = [g for g in grades if g["variant"] == "interfere"]
    leaky = [g for g in grades if g["variant"] in ("update", "absent")]
    head = [per[v]["adjusted"] for v in ("retain_far", "interfere", "update")
            if v in per]
    return {
        "primitive": PRIMITIVE, "mode": items[0].mode, "n": len(grades),
        "chance": CHANCE,
        "headline": sum(head) / len(head) if head else 0.0,
        "per_variant": per,
        "distance_cost": (per["retain_near"]["acc"] - per["retain_far"]["acc"]
                          if "retain_near" in per and "retain_far" in per
                          else None),
        "intrusion_rate": proportion(sum(int(g["intrusion"]) for g in inter),
                                     len(inter), 0.0, "intrusion")
        if inter else None,
        "leak_rate": proportion(sum(int(g["leak"]) for g in leaky), len(leaky),
                                0.0, "leak") if leaky else None,
        "parse_rate": proportion(sum(int(g["parsed"]) for g in grades),
                                 len(grades), 0.0, "parse_rate"),
        "median_prompt_words": sorted(i.meta["words"] for i in items)[len(items) // 2],
    }


CONTAMINATION = __doc__
