"""The seven faculties re-rendered in the checkpoint's native frame.

WHY THIS EXISTS.

The suite's own profile reads 0.000 strict parse rate on four of seven
primitives and format produced on 12% of items, and its rescue matrix
locates nothing because no oracle moves the episode off the floor. That
shape has two readings and the suite alone cannot separate them: the
faculties are absent, or the faculties exist and cannot be expressed in
the surface form this suite happens to use.

The wording ablation in `src/disc/` settled that the checkpoint's rule
result is sentence-frame matching rather than rule reading. On a chain
task with a single document in the store, so page identification cannot
fail, a renderer sharing no content word with the trained idiom scored
0.840 while a renderer keeping every content word and changing only the
sentence frame scored 0.030. Nouns cost 0.13; sentence shape costs 0.94.
Forced-choice substitution_rule reads 0.970 in the native idiom and 0.015
to 0.045 in three other ordinary English idioms against a 0.200 floor,
with 0.53 to 0.94 of answers in distant renderers naming no candidate at
all.

A 0.000 parse rate here and a 0.53 to 0.94 no-candidate rate there are
plausibly the same phenomenon. So every faculty is rendered again in the
native frame and measured against the identical chance floor, and the two
columns are reported side by side.

THE NATIVE FRAME.

Taken from `src.disc.renderers.NativeSimple.pages_substitution_rule` and
`q_substitution_rule`, which is the published wording of the surface the
RL stage trained on:

    pages     "A {k} is handled by the {v} desk."
              wrapped in a routing-table preamble, a listing page, and a
              precedence note.
    question  "A {k} request arrives at the {name} office.
               Which desk handles it?"
    answer    a bare desk name.

DESIGN RULE, AND THE ONE THING THIS MUST NOT DO.

A separate lane found that appending a sentence asking for nothing
collapses retrieval rounds from 0.98 to 0.01, matching the intervention
it was meant to control for. Interventions phrased as extra words on the
question are therefore untestable on this checkpoint, and no variant here
works that way.

So the question sentence stays in the native frame verbatim for all seven
faculties, and every faculty's own difficulty is carried by the pages
instead. That keeps the thing being varied to one thing: whether the task
is posed in the frame the checkpoint knows.

WHAT EACH FACULTY HAD TO GIVE UP.

Frame match is not all-or-nothing, and mislabelling a partial match would
waste the control, so each renderer records its own `deviation` string and
the report prints it beside the number.

    composition   exact. This is the chain task, and the `routing`
                  renderer in src/disc/renderers.py is asserted byte for
                  byte against minrepro, so it is the training surface
                  itself.
    memory        exact frame. Distance is created by filler offices
                  between the routing line and the question, which is
                  page content, not question wording.
    acquisition   exact frame. Four offices each carry their own routing
                  table and only one lists the arriving type, so source
                  selection survives as locating the office.
    intent        exact question frame. The messy request moves into the
                  pages as an office narrative naming several types of
                  which one actually arrives.
    gap           exact question frame, minus the native default line.
                  The native pages end "Any request whose type is not
                  listed goes to the {default} desk", which answers a gap
                  question outright, so that sentence is removed and a
                  not-listed desk becomes an option.
    verification  exact question frame, but the faculty is proxied. The
                  suite asks for a verdict on a candidate; the native
                  frame has no verdict question, so a wrong desk is
                  proposed in the pages and the score is whether the model
                  answers the correct desk instead of the proposed one.
                  That is resisting a bad suggestion, not detecting one.
    abstraction   exact question frame, minus the precedence note. The
                  native pages end "Do not infer a desk from the name of a
                  request type; use only the routing given here", which
                  forbids the induction this faculty is about, so that
                  page is removed. Of the seven this is the loosest match.

Chance floors are matched to the suite version item set by item set, by
giving each question the same number of options its suite counterpart
has, so the two columns are read against one floor.
"""

from __future__ import annotations

import random

from src.primitives.common import (
    Item, invented_words, label_verdict, parse_labels, proportion,
)

PRIMITIVE = "nativeframe"

# The frame, in one place. Every renderer below calls these and nothing
# else builds a sentence, so a drift in the surface form is a one-line
# change rather than seven.
LINE = "A {k} is handled by the {v} desk."
DEFAULT_LINE = "Any request whose type is not listed goes to the {d} desk."
PRECEDENCE = ("A note on precedence.\n\nThe table above is complete. Do not "
              "infer a desk from the name of a request type; use only the "
              "routing given here.")
QUESTION = ("A {k} request arrives at the {office} office. "
            "Which desk handles it?")


def _table(keys, values) -> str:
    return "\n".join(LINE.format(k=k, v=v) for k, v in zip(keys, values))


def _pages(office: str, keys, values, default=None, precedence=True) -> list:
    """The three native pages, with the two optional ones switchable.

    The default line and the precedence note are the two sentences that
    make a faculty untestable when kept, so gap drops the first and
    abstraction drops the second, and each says so in its deviation.
    """
    body = f"Routing.\n\n{_table(keys, values)}"
    if default is not None:
        body += "\n\n" + DEFAULT_LINE.format(d=default)
    out = [f"The {office} routing table.\n\nRequests in the {office} office "
           f"are routed by their type.", body]
    if precedence:
        out.append(PRECEDENCE)
    return out


def _item(item_id, variant, question, pages, labels, answer, deviation,
          mode="native", meta=None) -> Item:
    # `question` already carries the pages followed by the native question,
    # built by _ask. Concatenating the pages again here would show every
    # page twice and put the question in the middle of the prompt, which
    # is not the frame being tested.
    chunks = [{"id": f"p{i}", "text": t} for i, t in enumerate(pages)]
    full = question
    m = {"deviation": deviation, "office": meta.get("office") if meta else None}
    m.update(meta or {})
    return Item(item_id=item_id, primitive=PRIMITIVE, variant=variant,
                mode=mode, question=full, chunks=chunks,
                gold={"labels": list(labels), "answer": answer,
                      "index": list(labels).index(answer)},
                meta=m)


def _ask(pages: list, key: str, office: str) -> str:
    """Pages first, then the native question. Nothing is appended to it."""
    return "\n\n".join(pages) + "\n\n" + QUESTION.format(k=key, office=office)


# ------------------------------------------------------------------ faculties


def gen_intent(seed: int, n_opt: int = 4) -> Item:
    """Goal extraction: several types are discussed, one actually arrives.

    Suite counterpart scores which of four goal labels the request is
    really after. Here four desks are listed and the pages narrate an
    office in which three types are mentioned in passing and one arrives,
    so the model must pick the arriving type's desk rather than the most
    recently mentioned one.
    """
    rng = random.Random(("intent", seed).__hash__() & 0xFFFFFFF)
    keys = invented_words(rng, n_opt, 2)
    desks = invented_words(rng, n_opt, 2)
    office = invented_words(rng, 1, 2)[0]
    i = rng.randrange(n_opt)
    # The distractors are named later than the real one, so recency alone
    # is the wrong strategy and the score is not a position effect.
    others = [k for j, k in enumerate(keys) if j != i]
    narrative = (
        f"Yesterday's log.\n\n"
        f"The {office} office spent the morning on {others[0]} paperwork and "
        f"the afternoon discussing {others[1]} and {others[2]}. None of those "
        f"were filed. The request that actually arrived today is a {keys[i]}.")
    pages = _pages(office, keys, desks) + [narrative]
    return _item(f"nf-intent-{seed}", "intent",
                 _ask(pages, keys[i], office), pages, desks, desks[i],
                 "exact question frame; the messy request moved into the "
                 "pages as an office log", meta={"office": office})


def gen_gap(seed: int) -> Item:
    """Completeness: the arriving type is absent and no default is given.

    The native pages normally end with a line sending unlisted types to a
    default desk, which answers this question outright, so that sentence
    is dropped and a not-listed desk is offered instead. Two options, to
    hold the suite's 0.500 floor.
    """
    rng = random.Random(("gap", seed).__hash__() & 0xFFFFFFF)
    keys = invented_words(rng, 4, 2)
    desks = invented_words(rng, 4, 2)
    office = invented_words(rng, 1, 2)[0]
    missing = invented_words(rng, 1, 2)[0]
    blocked = seed % 2 == 0
    ask = missing if blocked else keys[0]
    unlisted = "unlisted"
    # Two options exactly, so the floor matches the suite's detection field.
    labels = [desks[0], unlisted]
    answer = unlisted if blocked else desks[0]
    pages = _pages(office, keys, desks, default=None)
    pages.append(f"The desks.\n\nThe {office} office has a {desks[0]} desk. "
                 f"A request whose type the table does not list is recorded "
                 f"as {unlisted}.")
    return _item(f"nf-gap-{seed}", "blocked" if blocked else "solvable",
                 _ask(pages, ask, office), pages, labels, answer,
                 "exact question frame; the native default line removed, "
                 "since it answers a gap question outright",
                 meta={"office": office, "blocked": blocked})


def gen_acquisition(seed: int, n_office: int = 4) -> Item:
    """Source selection: four offices, only one lists the arriving type.

    The suite scores choosing one of four archive tiers. Here the four
    tiers are four offices with their own routing tables, and naming the
    right desk requires finding the office that lists the type, so the
    same four-way choice is made without leaving the frame.
    """
    rng = random.Random(("acq", seed).__hash__() & 0xFFFFFFF)
    offices = invented_words(rng, n_office, 2)
    target = seed % n_office
    key = invented_words(rng, 1, 2)[0]
    desks = invented_words(rng, n_office, 2)
    pages = []
    for j, off in enumerate(offices):
        ks = invented_words(rng, 3, 2)
        vs = invented_words(rng, 3, 2)
        if j == target:
            ks = list(ks) + [key]
            vs = list(vs) + [desks[j]]
        pages += _pages(off, ks, vs, precedence=False)
    return _item(f"nf-acq-{seed}", "direct",
                 _ask(pages, key, offices[target]), pages, desks,
                 desks[target],
                 "exact question frame; the four archive tiers became four "
                 "offices, so the four-way source choice is unchanged",
                 meta={"office": offices[target]})


def gen_abstraction(seed: int) -> Item:
    """Induction: the arriving type is unlisted but the table shows a rule.

    Every listed type ending in one suffix goes to one desk and every type
    ending in the other suffix goes to the other. The arriving type is not
    in the table and carries one of the suffixes. The native precedence
    note forbids exactly this inference, so it is dropped, which makes
    this the loosest frame match of the seven.
    """
    rng = random.Random(("abs", seed).__hash__() & 0xFFFFFFF)
    stems = invented_words(rng, 7, 2)
    sa, sb = "ex", "ol"
    desks = invented_words(rng, 2, 2)
    office = invented_words(rng, 1, 2)[0]
    keys, vals = [], []
    for j, st in enumerate(stems[:6]):
        suf = sa if j % 2 == 0 else sb
        keys.append(st + suf)
        vals.append(desks[0] if suf == sa else desks[1])
    want_a = seed % 2 == 0
    ask = stems[6] + (sa if want_a else sb)
    answer = desks[0] if want_a else desks[1]
    pages = _pages(office, keys, vals, precedence=False)
    return _item(f"nf-abs-{seed}", "transfer",
                 _ask(pages, ask, office), pages, desks, answer,
                 "exact question frame; the precedence note removed, since "
                 "it forbids the induction this faculty is about. Loosest "
                 "match of the seven",
                 meta={"office": office})


def gen_memory(seed: int, distance: int = 6) -> Item:
    """Retention: the routing line is stated, then buried under filler.

    Distance is built from filler offices between the line and the
    question, so it is page content and never words on the question.
    Five options, to hold the suite's 0.200 floor.
    """
    rng = random.Random(("mem", seed).__hash__() & 0xFFFFFFF)
    desks = invented_words(rng, 5, 2)
    keys = invented_words(rng, 5, 2)
    office = invented_words(rng, 1, 2)[0]
    i = rng.randrange(5)
    pages = _pages(office, keys, desks, precedence=False)
    for _ in range(distance):
        off = invented_words(rng, 1, 2)[0]
        pages += _pages(off, invented_words(rng, 3, 2),
                        invented_words(rng, 3, 2), precedence=False)
    return _item(f"nf-mem-{seed}", "retain_far",
                 _ask(pages, keys[i], office), pages, desks, desks[i],
                 "exact frame; distance built from filler offices between "
                 "the line and the question, never from question wording",
                 meta={"office": office, "distance": distance})


def gen_verification(seed: int) -> Item:
    """A wrong desk is proposed in the pages; the answer should not take it.

    The suite asks for a verdict on a candidate. The native frame has no
    verdict question, so the candidate is proposed in the pages and the
    score is whether the model answers the correct desk rather than the
    proposed one. That measures resisting a bad suggestion, not detecting
    one, and it is the weakest of the seven mappings.
    """
    rng = random.Random(("ver", seed).__hash__() & 0xFFFFFFF)
    keys = invented_words(rng, 4, 2)
    desks = invented_words(rng, 2, 2)
    office = invented_words(rng, 1, 2)[0]
    vals = [desks[0], desks[1], desks[0], desks[1]]
    i = rng.randrange(4)
    trap = seed % 2 == 0
    proposed = (desks[1] if vals[i] == desks[0] else desks[0]) if trap \
        else vals[i]
    pages = _pages(office, keys, vals, precedence=False)
    pages.append(f"A clerk's note.\n\nA clerk has written that a {keys[i]} "
                 f"goes to the {proposed} desk.")
    return _item(f"nf-ver-{seed}", "trap" if trap else "control",
                 _ask(pages, keys[i], office), pages, desks, vals[i],
                 "exact question frame; the faculty is proxied as resisting "
                 "a wrong proposal rather than returning a verdict on it",
                 meta={"office": office, "trap": trap})


def gen_composition(seed: int, k: int = 2) -> Item:
    """A chain of k routings, which is the training surface itself.

    The desk a type reaches becomes the type routed at the next office, so
    k lookups compose. Eight options, to hold the suite's 0.125 floor.
    """
    rng = random.Random(("comp", seed, k).__hash__() & 0xFFFFFFF)
    names = invented_words(rng, 8, 2)
    offices = invented_words(rng, k, 2)
    start = names[rng.randrange(8)]
    cur = start
    pages = []
    for j in range(k):
        vals = list(names)
        rng.shuffle(vals)
        # A derangement on the hop, so no step can be passed by echoing.
        vals = [v if v != n else names[(names.index(v) + 1) % 8]
                for v, n in zip(vals, names)]
        pages += _pages(offices[j], names, vals, precedence=False)
        cur = vals[names.index(cur)]
    return _item(f"nf-comp-{seed}-k{k}", f"chain/k{k}",
                 _ask(pages, start, offices[0]), pages, names, cur,
                 "exact frame; this is the chain task the wording ablation "
                 "holds byte for byte against the training surface",
                 meta={"office": offices[0], "k": k})


GENERATORS = {
    "intent": gen_intent, "gap": gen_gap, "acquisition": gen_acquisition,
    "abstraction": gen_abstraction, "memory": gen_memory,
    "verification": gen_verification, "composition": gen_composition,
}


def generate_many(faculty: str, n: int, seed: int = 0, **kw) -> list[Item]:
    return [GENERATORS[faculty](seed + i, **kw) for i in range(n)]


def choices(item: Item) -> list[dict]:
    return [{"field": "answer", "question": item.question,
             "options": list(item.gold["labels"]),
             "gold": item.gold["index"]}]


def grade(item: Item, response: str) -> dict:
    v = label_verdict(response, item.gold["labels"], item.gold["answer"])
    named = parse_labels(response, item.gold["labels"])
    return {"parsed": len(named) == 1,
            "correct": v["strict"], "strict_correct": v["strict"],
            "lenient_correct": v["lenient"], "hedged": v["hedged"],
            "no_candidate": float(len(named) == 0),
            "chance": 1.0 / max(2, len(item.gold["labels"])),
            "variant": item.variant,
            "deviation": item.meta["deviation"]}


def aggregate(items: list[Item], grades: list[dict]) -> dict:
    if not grades:
        return {"primitive": PRIMITIVE, "n": 0}
    n = len(grades)
    chance = sum(g["chance"] for g in grades) / n
    return {
        "primitive": PRIMITIVE, "n": n, "chance": round(chance, 4),
        "deviation": grades[0]["deviation"],
        "strict": proportion(sum(int(g["strict_correct"]) for g in grades), n,
                             chance, "strict"),
        "lenient": proportion(sum(int(g["lenient_correct"]) for g in grades),
                              n, chance, "lenient"),
        "hedge_rate": proportion(sum(int(g["hedged"]) for g in grades), n, 0.0,
                                 "hedge"),
        "no_candidate": proportion(sum(int(g["no_candidate"]) for g in grades),
                                   n, 0.0, "no_candidate"),
        "parse_rate": proportion(sum(int(g["parsed"]) for g in grades), n, 0.0,
                                 "parse_rate"),
        "headline": proportion(sum(int(g["strict_correct"]) for g in grades),
                               n, chance, "headline")["adjusted"],
    }
