"""Primitive 5: composition depth, as three curves that are never pooled.

The pre-registration is explicit that the three kinds may scale
differently, so they are generated, scored and reported apart.

Sequential depth. One stated step relation, applied k times. The relation
is a single eight-cycle over eight invented names, so the k-step answer
differs from every j-step answer for j below k and from the start, and a
model that stops early lands on a name that is in the candidate set and is
wrong. This is carrying one computation through k chained transformations.

Relational breadth. One conclusion from k simultaneously relevant clues.
The roster is built so that all k clues together single out one entity and
so that dropping any one clue leaves at least two, which is checked at
generation and is what makes partial integration score at chance rather
than nearly right. This is breadth, not depth: no clue feeds another.

Novel composition. k procedures, each taught in its own lesson with its
own worked examples, never once shown combined, then required in
sequence. A model can memorise every part and still fail to build the
whole, which is why this is the acquisition test proper.

Every item ships with per-step probes: the same model is asked each
constituent step on its own, over the same tables, in the same format.
The curve is therefore reported twice. The raw curve is accuracy at depth
k. The conditional curve is accuracy at depth k restricted to items whose
every constituent step that model answered correctly on its own, which is
what isolates composition from step competence. A model whose steps are
weak shows a low raw curve and a conditional curve that stays high; a
model whose composition is weak shows the opposite.

CONTAMINATION CONTROL, faculty by faculty.

Step competence: the conditional curve exists for exactly this reason, and
the per-step probe accuracy is reported beside every curve.

Abstraction construction: every table, clue and procedure is stated
literally. Nothing is induced from examples and nothing transfers to a new
surface.

Information acquisition: all tables are in the context and in the chunk
list. Nothing is retrieved and no source is chosen.

Missing-capability recognition: nothing is missing and no gap is to be
reported.

Intent understanding: the instruction is literal, the candidate answers
are enumerated, and the number of steps is stated outright rather than
inferred.

Temporary knowledge: single turn, with the table immediately above the
question.

Verification and action: no trap. The first correct traversal is correct.

Arithmetic: none anywhere. Every step is a table lookup or one equality
test between stated words.

Chance control: the answer is one of eight enumerated names, so chance is
one eighth at every depth, and the chance-adjusted score is what the
depth threshold is read off.
"""

from __future__ import annotations

import random

from src.primitives.common import Item, invented_words, parse_one_label, proportion

PRIMITIVE = "composition"
KINDS = ("sequential", "relational", "novel")
N_NAMES = 8
CHANCE = 1.0 / N_NAMES

ANSWER_LINE = "Answer with exactly this line:\nANSWER: one of the names listed above"


def _cycle(rng: random.Random, names: list[str]) -> dict:
    """A single full cycle over names, so no element is its own image."""
    order = list(names)
    rng.shuffle(order)
    return {order[i]: order[(i + 1) % len(order)] for i in range(len(order))}


def _table_text(mapping: dict, rng: random.Random, rel: str) -> str:
    lines = [f"  {a} {rel} {b}." for a, b in mapping.items()]
    rng.shuffle(lines)
    return "\n".join(lines)


# --------------------------------------------------------------- sequential

def _sequential(seed: int, k: int, mode: str) -> Item:
    rng = random.Random(seed * 31 + k * 7919)
    names = invented_words(rng, N_NAMES, 2)
    rel = "hands to"
    mapping = _cycle(rng, names)
    start = rng.choice(names)
    cur = start
    steps = []
    for _ in range(k):
        steps.append((cur, mapping[cur]))
        cur = mapping[cur]
    table = _table_text(mapping, rng, rel)
    body = (
        f"Each name below hands to exactly one other name.\n\n"
        f"Table.\n{table}\n\n"
        f"Names.\n  {', '.join(sorted(names))}\n\n"
        f"Start at {start}. Follow the hands-to link {k} time"
        f"{'s' if k != 1 else ''} in a row. Which name do you finish on?\n"
        f"{ANSWER_LINE}")
    if mode == "integrated":
        body = _bury(body, table, rng, rel)
    return Item(
        item_id=f"p5-sequential-k{k}-{mode}-{seed:07d}",
        primitive=PRIMITIVE, variant=f"sequential/k{k}", mode=mode,
        question=body, chunks=[{"text": "Table.\n" + table}],
        gold={"answer": cur, "labels": names},
        meta={"seed": seed, "kind": "sequential", "k": k, "names": names,
              "table": table, "start": start,
              "steps": [{"question":
                         f"Each name below hands to exactly one other name.\n\n"
                         f"Table.\n{table}\n\nNames.\n  {', '.join(sorted(names))}\n\n"
                         f"Which name does {a} hand to?\n{ANSWER_LINE}",
                         "answer": b} for a, b in steps]},
    )


# --------------------------------------------------------------- relational

def _relational(seed: int, k: int, mode: str) -> Item:
    rng = random.Random(seed * 37 + k * 104729)
    names = invented_words(rng, N_NAMES, 2)
    attr_names = invented_words(rng, 6, 2)
    values = [invented_words(rng, 4, 2) for _ in attr_names]

    for _ in range(400):
        # The answer must not be predictable from its position in the
        # roster, so the target is drawn at random and the roster is
        # printed in an order that is shuffled again below.
        target = rng.choice(names)
        clue_attrs = rng.sample(range(len(attr_names)), k)
        rows = {n: [rng.choice(v) for v in values] for n in names}
        for j, ai in enumerate(clue_attrs):
            rows[target][ai] = values[ai][0]
        # One near miss per clue: matches every clue but that one, so
        # dropping any single clue leaves at least two candidates.
        pool = [n for n in names if n != target]
        rng.shuffle(pool)
        ok = len(pool) >= k
        for j, ai in enumerate(clue_attrs):
            if not ok:
                break
            other = pool[j]
            for aj in clue_attrs:
                rows[other][aj] = values[aj][0]
            alt = [x for x in values[ai] if x != values[ai][0]]
            rows[other][ai] = rng.choice(alt)
        if not ok:
            continue

        def matches(n):
            return all(rows[n][ai] == values[ai][0] for ai in clue_attrs)

        if sum(1 for n in names if matches(n)) != 1:
            continue
        bad = False
        for ai in clue_attrs:
            rest = [x for x in clue_attrs if x != ai]
            hits = [n for n in names
                    if all(rows[n][aj] == values[aj][0] for aj in rest)]
            if len(hits) < 2:
                bad = True
                break
        if bad:
            continue
        break
    else:
        raise RuntimeError(f"could not build a relational item at k={k}")

    shown = list(names)
    rng.shuffle(shown)
    roster = "\n".join(
        f"  {n}: " + ", ".join(f"{attr_names[i]} {rows[n][i]}"
                               for i in range(len(attr_names)))
        for n in shown)
    clues = [f"  {i + 1}. its {attr_names[ai]} is {values[ai][0]}."
             for i, ai in enumerate(clue_attrs)]
    body = (
        f"Exactly one entry in the roster satisfies every clue below.\n\n"
        f"Roster.\n{roster}\n\n"
        f"Clues.\n" + "\n".join(clues) + "\n\n"
        f"Which entry is it?\n{ANSWER_LINE}")
    if mode == "integrated":
        body = _bury(body, roster, rng, "roster")
    probes = []
    for i, ai in enumerate(clue_attrs):
        who = rng.choice(names)
        probes.append({
            "question": f"Roster.\n{roster}\n\nIs it true that {who} has "
                        f"{attr_names[ai]} {values[ai][0]}?\n"
                        f"Answer with exactly this line:\nANSWER: YES or NO",
            "answer": "YES" if rows[who][ai] == values[ai][0] else "NO",
            "labels": ["YES", "NO"]})
    return Item(
        item_id=f"p5-relational-k{k}-{mode}-{seed:07d}",
        primitive=PRIMITIVE, variant=f"relational/k{k}", mode=mode,
        question=body, chunks=[{"text": "Roster.\n" + roster}],
        gold={"answer": target, "labels": names},
        meta={"seed": seed, "kind": "relational", "k": k, "names": names,
              "steps": probes,
              # The structure behind the roster, so the property that makes
              # the item a breadth test (every clue load bearing) can be
              # checked directly rather than reparsed out of the prose.
              "rows": {n: list(rows[n]) for n in names},
              "clues": [(ai, values[ai][0]) for ai in clue_attrs]},
    )


# -------------------------------------------------------------------- novel

def _novel(seed: int, k: int, mode: str) -> Item:
    rng = random.Random(seed * 41 + k * 15485863)
    names = invented_words(rng, N_NAMES, 2)
    proc_names = [w.capitalize() for w in invented_words(rng, k + 2, 2)]

    # Every value along the chain must be distinct, so a model that applies
    # too few steps lands somewhere the candidate set contains and marks
    # wrong. The tables are redrawn on each attempt, not just the start,
    # because with a fixed set of tables there are only as many chains as
    # there are names.
    for _ in range(600):
        maps = [_cycle(rng, names) for _ in range(k + 2)]
        start = rng.choice(names)
        cur = start
        seen = [start]
        chain = []
        for i in range(k):
            nxt = maps[i][cur]
            chain.append({"proc": i, "inp": cur, "out": nxt})
            cur = nxt
            seen.append(cur)
        if len(set(seen)) == len(seen):
            break
    else:
        raise RuntimeError(f"could not build a novel item at k={k}")

    lessons = []
    for i in range(k + 2):
        ex = rng.sample(names, 2)
        lessons.append(
            f"The {proc_names[i]} step.\n"
            f"  Applying {proc_names[i]} to a name gives the name beside it "
            f"in this list:\n"
            + _table_text(maps[i], rng, "becomes")
            + f"\n  So {proc_names[i]} applied to {ex[0]} gives "
              f"{maps[i][ex[0]]}, and {proc_names[i]} applied to {ex[1]} "
              f"gives {maps[i][ex[1]]}.")
    order = list(range(k + 2))
    rng.shuffle(order)
    lesson_text = "\n\n".join(lessons[i] for i in order)
    sequence = ", then ".join(proc_names[i] for i in range(k))
    body = (
        f"Each step below was taught on its own. None of them has ever been "
        f"used together with another. Apply them in the order given.\n\n"
        f"Lessons.\n{lesson_text}\n\n"
        f"Names.\n  {', '.join(sorted(names))}\n\n"
        f"Start with {start}. Apply {sequence}. Which name do you end with?\n"
        f"{ANSWER_LINE}")
    if mode == "integrated":
        body = _bury(body, lesson_text, rng, "lessons")
    probes = []
    for st in chain:
        i = st["proc"]
        probes.append({
            "question": f"{lessons[i]}\n\nNames.\n  {', '.join(sorted(names))}\n\n"
                        f"Apply {proc_names[i]} to {st['inp']}. Which name do "
                        f"you get?\n{ANSWER_LINE}",
            "answer": st["out"]})
    return Item(
        item_id=f"p5-novel-k{k}-{mode}-{seed:07d}",
        primitive=PRIMITIVE, variant=f"novel/k{k}", mode=mode,
        question=body, chunks=[{"text": lesson_text}],
        gold={"answer": cur, "labels": names},
        meta={"seed": seed, "kind": "novel", "k": k, "names": names,
              "n_unused_procs": 2, "steps": probes,
              "proc_names": proc_names, "lessons": lessons,
              "start": start},
    )


def _bury(body: str, block: str, rng: random.Random, what: str) -> str:
    """Integrated mode: the material the task needs arrives among material
    for other tasks, so finding it is part of the work."""
    noise = []
    for _ in range(2):
        w = invented_words(rng, N_NAMES, 2)
        m = _cycle(rng, w)
        noise.append(f"Unrelated {what}.\n"
                     + "\n".join(f"  {a} hands to {b}." for a, b in m.items()))
    blocks = [block] + noise
    rng.shuffle(blocks)
    return body.replace(block, "\n\n".join(blocks))


_BUILDERS = {"sequential": _sequential, "relational": _relational,
             "novel": _novel}


def generate(seed: int, kind: str, k: int, mode: str = "isolated") -> Item:
    return _BUILDERS[kind](seed, k, mode)


def generate_curve(n: int, kind: str, ks, seed: int = 0,
                   mode: str = "isolated") -> list[Item]:
    """n items at every depth in ks, guarded against early-stop shortcuts."""
    out: list[Item] = []
    for k in ks:
        got, s, tried = 0, seed, 0
        while got < n and tried < n * 40:
            tried += 1
            item = generate(s * 1009 + k, kind, k, mode=mode)
            s += 1
            inter = [st["answer"] for st in item.meta["steps"][:-1]]
            if item.gold["answer"] in inter:
                continue
            out.append(item)
            got += 1
        if got < n:
            raise RuntimeError(f"only {got} of {n} {kind} items at k={k}")
    return out


def probe_items(items: list[Item]) -> list[Item]:
    """The per-step probes of a curve, as items in their own right.

    They carry the parent item id so the aggregator can restrict a depth to
    the items whose every step this model answered on its own.
    """
    out: list[Item] = []
    for parent in items:
        for j, st in enumerate(parent.meta["steps"]):
            out.append(Item(
                item_id=f"{parent.item_id}#s{j}",
                primitive=PRIMITIVE, variant=f"probe/{parent.meta['kind']}",
                mode=parent.mode, question=st["question"], chunks=[],
                gold={"answer": st["answer"],
                      "labels": st.get("labels", parent.gold["labels"])},
                meta={"parent": parent.item_id, "step": j,
                      "kind": parent.meta["kind"], "k": parent.meta["k"]}))
    return out


def grade(item: Item, response: str) -> dict:
    pick = parse_one_label(response, item.gold["labels"])
    return {"parsed": pick is not None,
            "correct": float(pick == item.gold["answer"]),
            "k": item.meta.get("k", 0),
            "kind": item.meta.get("kind", "probe"),
            "chance": 1.0 / max(2, len(item.gold["labels"]))}


def aggregate_curve(items: list[Item], grades: list[dict],
                    probes: list[Item] | None = None,
                    probe_grades: list[dict] | None = None) -> dict:
    """One kind's depth curve, raw and conditioned on per-step competence."""
    if not items:
        return {"primitive": PRIMITIVE, "n": 0}
    kind = items[0].meta["kind"]
    mode = items[0].mode

    step_ok: dict[str, list[bool]] = {}
    if probes and probe_grades:
        for p, g in zip(probes, probe_grades):
            step_ok.setdefault(p.meta["parent"], []).append(bool(g["correct"]))
    all_steps_ok = {pid: all(v) for pid, v in step_ok.items()}

    curve, cond = {}, {}
    for k in sorted({i.meta["k"] for i in items}):
        sel = [(i, g) for i, g in zip(items, grades) if i.meta["k"] == k]
        ch = sel[0][1]["chance"]
        curve[k] = proportion(sum(int(g["correct"]) for _, g in sel), len(sel),
                              ch, f"{kind}/k{k}")
        keep = [(i, g) for i, g in sel if all_steps_ok.get(i.item_id, False)]
        if keep:
            cond[k] = proportion(sum(int(g["correct"]) for _, g in keep),
                                 len(keep), ch, f"{kind}/k{k}/step-clean")

    def depth(c):
        best = 0
        for k in sorted(c):
            if c[k]["above_chance"]:
                best = k
            else:
                break
        return best

    out = {
        "primitive": PRIMITIVE, "kind": kind, "mode": mode, "n": len(items),
        "chance": CHANCE,
        "curve": {str(k): v for k, v in curve.items()},
        "k_star": depth(curve),
        "headline": depth(curve),
        "parse_rate": proportion(sum(int(g["parsed"]) for g in grades),
                                 len(grades), 0.0, "parse_rate"),
    }
    if cond:
        out["curve_step_clean"] = {str(k): v for k, v in cond.items()}
        out["k_star_step_clean"] = depth(cond)
    if probe_grades:
        out["step_probe_accuracy"] = proportion(
            sum(int(g["correct"]) for g in probe_grades), len(probe_grades),
            CHANCE, "step_probe")
        out["items_with_all_steps_correct"] = proportion(
            sum(1 for v in all_steps_ok.values() if v), len(all_steps_ok),
            0.0, "all_steps_correct")
    return out


CONTAMINATION = __doc__
