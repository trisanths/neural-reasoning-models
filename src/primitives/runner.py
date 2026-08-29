"""Model-agnostic runner for the primitive suite.

The model enters through one callable:

    predict(question: str, chunks: list) -> str

which is the answer_fn shape src.evals.interactive.make_retrieval_answer_fn
returns, so a checkpoint already wired for the interactive loop can be
handed straight to this runner, and so can a scripted stand-in, an API
client, or a heuristic baseline. Nothing below imports torch.

chunks are the documents an item makes available. Most primitives put
their material in the question as well and pass the same text as chunks,
so an adapter is free to use whichever channel its model was trained on.
The acquisition primitive passes an empty chunk list on purpose: its whole
point is that the corpus is not visible and only the query is scored.

Two modes throughout. In isolated mode the other six faculties are
supplied by oracle around the one under test. In integrated mode those
oracles are withdrawn. Both are runnable at every size, which is what the
substrate sweep needs to produce the two curves the pre-registration asks
for.
"""

from __future__ import annotations

import time

from src.primitives import episode as ep
from src.primitives import (
    p1_intent, p2_gap, p3_acquisition, p4_abstraction, p5_composition,
    p6_memory, p7_verification,
)
from src.primitives.common import proportion

DEFAULT_N = 40
DEFAULT_KS = (1, 2, 3, 4, 5)


def followup_question(item) -> str:
    """The second turn of a recursive acquisition item.

    Built here so the runner and the scripted stand-ins agree on it byte
    for byte, rather than each assembling its own version.
    """
    return (item.question + "\n\n" + item.meta["followup"]
            + "\n\nReturned page.\n" + item.meta["served_text"])


def _call(predict, item, on_error="") -> str:
    try:
        return str(predict(item.question, list(item.chunks)))
    except Exception as exc:  # a model that crashes scores zero, loudly
        return f"{on_error}<<predict raised {type(exc).__name__}: {exc}>>"


def _run_items(predict, items, grade_fn, progress=None) -> tuple[list, list]:
    grades, records = [], []
    for i, item in enumerate(items):
        text = _call(predict, item)
        g = grade_fn(item, text)
        grades.append(g)
        records.append({"item_id": item.item_id, "primitive": item.primitive,
                        "variant": item.variant, "mode": item.mode,
                        "response": text[:2000],
                        "grade": {k: v for k, v in g.items()
                                  if isinstance(v, (int, float, bool, str))
                                  or v is None}})
        if progress and (i + 1) % 25 == 0:
            progress(f"    {i + 1}/{len(items)}")
    return grades, records


# ------------------------------------------------------------ per primitive

def run_intent(predict, n=DEFAULT_N, seed=0, mode="isolated", progress=None):
    items = p1_intent.generate_many(n, seed=seed, mode=mode)
    grades, rec = _run_items(predict, items, p1_intent.grade, progress)
    return p1_intent.aggregate(items, grades), rec


def run_gap(predict, n=DEFAULT_N, seed=0, mode="isolated", progress=None):
    items = p2_gap.generate_many(n, seed=seed, mode=mode)
    grades, rec = _run_items(predict, items, p2_gap.grade, progress)
    return p2_gap.aggregate(items, grades), rec


def run_acquisition(predict, n=DEFAULT_N, seed=0, mode="isolated",
                    progress=None):
    """Both variants. The recursive one costs a second call per item."""
    out, rec = {}, []
    for variant in ("direct", "recursive"):
        items = p3_acquisition.generate_many(n, seed=seed, mode=mode,
                                             variant=variant)
        grades = []
        for item in items:
            first = _call(predict, item)
            follow = None
            if variant == "recursive":
                follow = str(predict(followup_question(item), []))
            g = p3_acquisition.grade(item, first, followup=follow)
            grades.append(g)
            rec.append({"item_id": item.item_id, "primitive": item.primitive,
                        "variant": item.variant, "mode": item.mode,
                        "response": first[:2000],
                        "followup": (follow or "")[:2000],
                        "grade": {k: v for k, v in g.items()
                                  if isinstance(v, (int, float, bool))}})
        out[variant] = p3_acquisition.aggregate(items, grades)
        if progress:
            progress(f"    acquisition/{variant} done")
    out["headline"] = out["direct"]["headline"]
    out["primitive"] = "acquisition"
    out["mode"] = mode
    out["n"] = sum(out[v]["n"] for v in ("direct", "recursive"))
    return out, rec


def run_abstraction(predict, n=DEFAULT_N, seed=0, mode="isolated",
                    progress=None):
    """Transfer is the headline; same-surface is the control beside it."""
    out, rec = {}, []
    for condition in ("same_surface", "transfer"):
        items = p4_abstraction.generate_many(n, seed=seed, mode=mode,
                                             condition=condition)
        grades, r = _run_items(predict, items, p4_abstraction.grade, progress)
        out[condition] = p4_abstraction.aggregate(items, grades)
        rec.extend(r)
    out["primitive"] = "abstraction"
    out["mode"] = mode
    out["headline"] = out["transfer"]["headline"]
    out["transfer_cost"] = (out["same_surface"]["accuracy"]["acc"]
                            - out["transfer"]["accuracy"]["acc"])
    out["n"] = sum(out[c]["n"] for c in ("same_surface", "transfer"))
    return out, rec


def run_composition(predict, n=DEFAULT_N, seed=0, mode="isolated",
                    ks=DEFAULT_KS, progress=None, with_probes=True):
    """Three curves, never pooled, each raw and step-conditioned."""
    out, rec = {}, []
    for kind in p5_composition.KINDS:
        items = p5_composition.generate_curve(n, kind, ks, seed=seed, mode=mode)
        grades, r = _run_items(predict, items, p5_composition.grade, progress)
        rec.extend(r)
        probes, pgrades = None, None
        if with_probes:
            probes = p5_composition.probe_items(items)
            pgrades, pr = _run_items(predict, probes, p5_composition.grade,
                                     progress)
            rec.extend(pr)
        out[kind] = p5_composition.aggregate_curve(items, grades, probes,
                                                   pgrades)
        if progress:
            progress(f"    composition/{kind} k*={out[kind]['k_star']}")
    out["primitive"] = "composition"
    out["mode"] = mode
    out["headline"] = {k: out[k]["k_star"] for k in p5_composition.KINDS}
    out["n"] = sum(out[k]["n"] for k in p5_composition.KINDS)
    return out, rec


def run_memory(predict, n=DEFAULT_N, seed=0, mode="isolated", progress=None):
    items = p6_memory.generate_many(n, seed=seed, mode=mode)
    grades, rec = _run_items(predict, items, p6_memory.grade, progress)
    return p6_memory.aggregate(items, grades), rec


def run_verification(predict, n=DEFAULT_N, seed=0, mode="isolated",
                     progress=None):
    items = p7_verification.generate_many(n, seed=seed, mode=mode)
    grades, rec = _run_items(predict, items, p7_verification.grade, progress)
    return p7_verification.aggregate(items, grades), rec


def run_rescue_matrix(predict, n=20, seed=0, progress=None,
                      conditions=ep.CONDITIONS):
    """One episode per seed rendered under every intervention."""
    items = ep.generate_matrix(n, seed=seed, conditions=conditions)
    grades, rec = _run_items(predict, items, ep.grade, progress)
    return ep.aggregate(items, grades), rec


MODULES = {
    "intent": p1_intent, "gap": p2_gap, "acquisition": p3_acquisition,
    "abstraction": p4_abstraction, "composition": p5_composition,
    "memory": p6_memory, "verification": p7_verification,
}


def build_items(name: str, n=DEFAULT_N, seed=0, mode="isolated",
                ks=DEFAULT_KS) -> list:
    """Every item one primitive contributes, variants and probes included."""
    if name == "intent":
        return p1_intent.generate_many(n, seed=seed, mode=mode)
    if name == "gap":
        return p2_gap.generate_many(n, seed=seed, mode=mode)
    if name == "acquisition":
        return [i for v in ("direct", "recursive")
                for i in p3_acquisition.generate_many(n, seed=seed, mode=mode,
                                                      variant=v)]
    if name == "abstraction":
        return [i for c in ("same_surface", "transfer")
                for i in p4_abstraction.generate_many(n, seed=seed, mode=mode,
                                                      condition=c)]
    if name == "composition":
        out = []
        for kind in p5_composition.KINDS:
            items = p5_composition.generate_curve(n, kind, ks, seed=seed,
                                                  mode=mode)
            out.extend(items)
            out.extend(p5_composition.probe_items(items))
        return out
    if name == "memory":
        return p6_memory.generate_many(n, seed=seed, mode=mode)
    if name == "verification":
        return p7_verification.generate_many(n, seed=seed, mode=mode)
    raise KeyError(name)


def collect_choices(primitives=None, n=DEFAULT_N, seed=0, mode="isolated",
                    ks=DEFAULT_KS, rescue_n=0) -> list[tuple]:
    """(item, choice) pairs for every primitive that offers a forced choice.

    A checkpoint trained to emit a bare answer after the answer marker can
    fail every field format and still prefer the right reading. Scoring
    the option texts by likelihood asks the same question without asking
    the model to produce a format it never learned, which is the
    convention src/evals/heldout.py already uses. It is reported beside
    the generation channel and never instead of it: producing an answer
    and preferring one are different abilities, and the two columns say
    which one a size has lost.
    """
    names = list(primitives or RUNNERS)
    out: list[tuple] = []
    for name in names:
        mod = MODULES[name]
        for item in build_items(name, n=n, seed=seed, mode=mode, ks=ks):
            for choice in mod.choices(item):
                out.append((item, choice))
    if rescue_n:
        for item in ep.generate_matrix(rescue_n, seed=seed):
            for choice in ep.choices(item):
                out.append((item, choice))
    return out


HEADLINE_FIELD = {
    "intent": "goal", "gap": "detection", "acquisition": "source selection",
    "abstraction": "answer", "composition": "answer", "memory": "answer",
    "verification": "trap detection",
}


def hedging_report(records) -> dict:
    """Strict against lenient on each primitive's single-choice field.

    The shared environment grader accepts any reply containing the gold
    answer, so a policy that names two candidates is scored correct
    whenever either is right. This suite grades strictly instead, and
    reports the pair so the strictness is auditable rather than asserted:
    where lenient sits well above strict, that primitive was carried by
    hedging and only the strict column means anything. Fields with no
    label namespace to hedge across report no hedge rate rather than a
    zero they never measured.

    Never pooled. Every primitive keeps its own row, because one family
    scoring on the grader is exactly what a pooled mean would hide.
    """
    # Split by family, never pooled. A primitive whose families differ is
    # exactly where a pooled mean hides one family scoring on the grader,
    # so acquisition keeps its two variants apart, abstraction keeps
    # same-surface apart from transfer, composition keeps its three kinds
    # apart, and memory keeps its five arms apart.
    by: dict = {}
    for r in records:
        g = r.get("grade") or {}
        if "lenient_correct" not in g:
            continue
        variant = str(r.get("variant", ""))
        if variant.startswith("probe"):
            continue
        fam = r["primitive"]
        if variant and variant != fam:
            fam = f"{fam}/{variant}"
        by.setdefault(fam, []).append(g)
    strict_key = {"gap": "detected", "verification": "detected",
                  "acquisition": "source", "intent": "goal"}
    out: dict = {}
    for name, rows in sorted(by.items()):
        base = name.split("/")[0]
        key = strict_key.get(base, "correct")
        # The recorded strict verdict, not the primitive's own headline
        # field. gap and verification read their two-way field through a
        # cue list that takes the earliest cue, which is the lenient rule;
        # using it here would print a lenient number in a column labelled
        # strict, which is the exact confusion this table exists to end.
        key = "strict_correct" if all("strict_correct" in g for g in rows) else key
        rows = [g for g in rows if key in g]
        if not rows:
            continue
        n = len(rows)
        measurable = [g for g in rows if "hedged" in g]
        # The chance floor travels on the item, because the option count
        # is not the same on every item of every primitive and a floor
        # quoted from the module constant would be wrong wherever it varies.
        chance = sum(g.get("chance", 0.0) for g in rows) / n
        out[name] = {
            "field": HEADLINE_FIELD.get(base, key), "n": n,
            "chance": round(chance, 4),
            "strict": proportion(sum(int(g[key]) for g in rows), n, chance,
                                 f"{name}/strict"),
            "lenient": proportion(sum(int(g["lenient_correct"]) for g in rows),
                                  n, chance, f"{name}/lenient"),
            "hedge_rate": (proportion(sum(int(g["hedged"]) for g in measurable),
                                      len(measurable), 0.0, f"{name}/hedge")
                           if measurable else None),
        }
        out[name]["leniency_gap"] = round(
            out[name]["lenient"]["acc"] - out[name]["strict"]["acc"], 4)
    return out


def run_forced_choice(model, primitives=None, n=DEFAULT_N, seed=0,
                      mode="isolated", ks=DEFAULT_KS, rescue_n=0,
                      progress=None) -> dict:
    """Score every forced choice with model.choose, grouped and never pooled."""
    pairs = collect_choices(primitives, n=n, seed=seed, mode=mode, ks=ks,
                            rescue_n=rescue_n)
    both = hasattr(model, "choose_both")
    buckets: dict = {}
    raw: dict = {}
    episode_hits: list[dict] = []
    for i, (item, choice) in enumerate(pairs):
        args = (choice["question"], list(item.chunks), choice["options"])
        if both:
            pick, pick_sum = model.choose_both(*args)
        else:
            pick = pick_sum = model.choose(*args)
        chance = 1.0 / max(2, len(choice["options"]))
        key = item.primitive
        field = choice["field"]
        if item.primitive == "composition":
            field = f"{item.meta.get('kind', 'probe')}/k{item.meta.get('k', 0)}"
            if item.variant.startswith("probe"):
                field = f"{item.meta.get('kind')}/probe"
        elif item.primitive == "episode":
            field = item.meta["condition"]
            episode_hits.append({
                "condition": field, "seed": item.meta["seed"],
                "correct": float(int(pick) == choice["gold"]),
                "took_candidate": 0.0, "parsed": True})
        elif item.primitive in ("acquisition", "abstraction"):
            field = f"{item.variant}/{choice['field']}"
        b = buckets.setdefault((key, field), [0, 0, chance])
        b[0] += int(int(pick) == choice["gold"])
        b[1] += 1
        r = raw.setdefault((key, field), [0, 0, chance])
        r[0] += int(int(pick_sum) == choice["gold"])
        r[1] += 1
        if progress and (i + 1) % 400 == 0:
            progress(f"    forced choice {i + 1}/{len(pairs)}")

    def _fold(src):
        rep: dict = {}
        for (prim, field), (hits, total, chance) in sorted(src.items()):
            rep.setdefault(prim, {})[field] = proportion(
                hits, total, chance, f"{prim}/{field}")
        return rep

    out = _fold(buckets)
    if "composition" in out:
        # The same depth rule the generation curve uses, so the two channels
        # are read off the same threshold rather than eyeballed against each
        # other.
        depths = {}
        for kind in p5_composition.KINDS:
            best = 0
            for k in sorted(ks):
                stat = out["composition"].get(f"{kind}/k{k}")
                if stat and stat["adjusted_ci_lo"] > p5_composition.DEPTH_MARGIN:
                    best = k
                else:
                    break
            depths[kind] = best
        out["composition_k_star"] = depths
    if episode_hits:
        # The rescue matrix again, on the channel a model that cannot write
        # can actually answer. Same paired reading, same aggregator.
        out["rescue_matrix"] = ep.aggregate([], episode_hits)
    if both:
        out["_unnormalised"] = _fold(raw)
    return out


def plan_choices(primitives=None, n=DEFAULT_N, seed=0, mode="isolated",
                 ks=DEFAULT_KS, rescue_n=0) -> list[tuple]:
    """Every (question, chunks, options) the forced-choice channel needs."""
    return [(c["question"], list(i.chunks), c["options"])
            for i, c in collect_choices(primitives, n=n, seed=seed, mode=mode,
                                        ks=ks, rescue_n=rescue_n)]


def plan_pairs(primitives=None, n=DEFAULT_N, seed=0, mode="isolated",
               ks=DEFAULT_KS, rescue_n=0) -> list[tuple]:
    """Every (question, chunks) the suite will ask for, in one list.

    Generation is seeded, so this reproduces exactly what run_suite will
    put to the model. A batched adapter can decode all of it up front and
    then serve the runner's one-at-a-time calls from cache, which keeps
    the runner free of any batching concern.
    """
    names = list(primitives or RUNNERS)
    pairs: list[tuple] = []

    def add(items):
        for it in items:
            pairs.append((it.question, list(it.chunks)))

    if "intent" in names:
        add(p1_intent.generate_many(n, seed=seed, mode=mode))
    if "gap" in names:
        add(p2_gap.generate_many(n, seed=seed, mode=mode))
    if "acquisition" in names:
        for variant in ("direct", "recursive"):
            items = p3_acquisition.generate_many(n, seed=seed, mode=mode,
                                                 variant=variant)
            add(items)
            if variant == "recursive":
                pairs.extend((followup_question(i), []) for i in items)
    if "abstraction" in names:
        for condition in ("same_surface", "transfer"):
            add(p4_abstraction.generate_many(n, seed=seed, mode=mode,
                                             condition=condition))
    if "composition" in names:
        for kind in p5_composition.KINDS:
            items = p5_composition.generate_curve(n, kind, ks, seed=seed,
                                                  mode=mode)
            add(items)
            add(p5_composition.probe_items(items))
    if "memory" in names:
        add(p6_memory.generate_many(n, seed=seed, mode=mode))
    if "verification" in names:
        add(p7_verification.generate_many(n, seed=seed, mode=mode))
    if rescue_n:
        add(ep.generate_matrix(rescue_n, seed=seed))
    return pairs


RUNNERS = {
    "intent": run_intent,
    "gap": run_gap,
    "acquisition": run_acquisition,
    "abstraction": run_abstraction,
    "composition": run_composition,
    "memory": run_memory,
    "verification": run_verification,
}


def run_suite(predict, primitives=None, n=DEFAULT_N, seed=0, mode="isolated",
              ks=DEFAULT_KS, rescue_n=0, progress=None,
              keep_records=True) -> dict:
    """Every requested primitive, plus the rescue matrix when asked for.

    Returns a report dict keyed by primitive, with a meta block. Records
    are the raw responses, kept for auditing and written by the CLI to a
    jsonl beside the report.
    """
    names = list(primitives or RUNNERS)
    reports, records = {}, []
    t0 = time.time()
    for name in names:
        if progress:
            progress(f"  {name} ({mode})")
        kwargs = {"n": n, "seed": seed, "mode": mode, "progress": progress}
        if name == "composition":
            kwargs["ks"] = ks
        rep, rec = RUNNERS[name](predict, **kwargs)
        reports[name] = rep
        if keep_records:
            records.extend(rec)
    if rescue_n:
        if progress:
            progress("  rescue matrix")
        rep, rec = run_rescue_matrix(predict, n=rescue_n, seed=seed,
                                     progress=progress)
        reports["rescue_matrix"] = rep
        if keep_records:
            records.extend(rec)
    if hasattr(predict, "choose"):
        if progress:
            progress("  forced choice channel")
        reports["forced_choice"] = run_forced_choice(
            predict, primitives=names, n=n, seed=seed, mode=mode, ks=ks,
            rescue_n=rescue_n, progress=progress)
    # The contamination argument travels with the numbers. A profile read
    # without it is a table of scores whose independence nobody can check.
    reports["hedging"] = hedging_report(records)
    reports["contamination"] = {
        name: (MODULES[name].CONTAMINATION or "").split(
            "CONTAMINATION CONTROL, faculty by faculty.")[-1].strip()
        for name in names
    }
    reports["meta"] = {
        "mode": mode, "n_per_primitive": n, "seed": seed, "ks": list(ks),
        "rescue_episodes": rescue_n, "primitives": names,
        "seconds": round(time.time() - t0, 1),
        "n_items": len(records),
    }
    return {"report": reports, "records": records}
