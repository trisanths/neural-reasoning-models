"""Building the episodes.

Three components, kept in separate files and never pooled in any count:

  relation   relation structures crossed with frames, carrying the relation
             type axis, the sentence frame axis, and plan lengths up to the
             depth the structure supports
  plan       operator worlds from `src/opgraph/invent.py`, carrying the plan
             length axis past the evaluation range and the distinct symbol
             axis past two
  mathgen    invented formal systems from `src/mathgen/cli.py`, carrying the
             answer source balance and its own verification

Every record is in the shape `src/rl/env.py:load_tasks` reads, plus the axis
fields the manifest counts. Extra keys on a question are ignored by the loader,
which is how the other generators in this repo carry their metadata.
"""

from __future__ import annotations

import random

from src.corpus import audit, relations
from src.corpus.lexicon import Lexicon, collisions, reserved_words

# Neutral lead-ins, shared by every frame, used only to bring an item's prompt
# length to the corpus target. Holding prompt length constant matters because
# `src/rl/env.py:load_tasks` drops any task over `max_prompt_tokens`, so a
# frame that ran long would silently lose its longest items and its sample
# would no longer match the other frames'.
LEADS = [
    "",
    "Answer from the pages.",
    "Answer using only what the pages state.",
    "Consider the pages before answering, then answer.",
    "Consider the pages before answering. Answer using only what they state.",
]

# One instance of a different structure sits in the same store, so a question
# has to find its page rather than being handed the only one there is.
DISTRACTOR_OFFSET = 61_000_000


def structurally_ok(q, inst) -> bool:
    """The frame independent exclusions, applied before any frame is chosen.

    `src/disc/renderers.py:chain_problems` makes the same move and says why:
    testing the rendered question would leave each frame with a different
    surviving question set, and then a frame comparison would no longer be
    comparing the same items. So the test runs on the tokens a question can
    name in any frame, and the per frame test on the rendered text is reported
    as a violation count rather than used to drop items.
    """
    stages = [str(s) for s in q.stages]
    gold = str(q.answer)
    if len(set(stages)) != len(stages):
        return False
    if gold == stages[0]:
        return False
    if gold in stages[:-1]:
        return False
    named = set(str(s) for s in q.scopes) | {inst.name, str(q.attr)}
    if gold in named:
        return False
    start = q.start if not isinstance(q.start, tuple) else " ".join(
        str(x) for x in q.start)
    if gold == str(start) or gold == str(q.key_b):
        return False
    return True


def _pick_level(options, cost, target):
    """The option whose cost is closest to the target, ties going to the shorter."""
    best, best_d = 0, None
    for i, o in enumerate(options):
        d = abs(cost(o) - target)
        if best_d is None or d < best_d:
            best, best_d = i, d
    return best


def build_relation_episode(seed: int, family: str, frame, encode,
                           depth: int = 1, n_problems: int = 6,
                           page_target: int = 420, prompt_target: int = 90,
                           with_distractor: bool = True,
                           global_reserved: frozenset = frozenset()) -> dict:
    """One episode: one relation instance, one frame, its questions audited.

    Two reserved sets, doing two different jobs. `reserved` is this frame's own
    English, read off this frame's templates and nothing else; it is what the
    collision check tests against, and it is what the earlier ablation got
    wrong by computing one set for every wording. `global_reserved` is the
    union over the whole bank and is what the draw avoids, which matters for a
    reason the per frame set cannot serve: a rejection that fired in one frame
    and not another would advance that frame's random stream by a different
    amount and the two frames would then draw different invented words for the
    same seed. Drawing against the union keeps the stream identical in every
    frame, so the gold answer for a seed is the same everywhere by
    construction rather than by luck, and the per frame check still bites
    because each frame's reserved set is a subset of the union.
    """
    reserved = reserved_words(frame)
    rng = random.Random(seed * 7919 + 13)
    lex = Lexicon(random.Random(seed * 104729 + 7), reserved, global_reserved)
    fn = relations.STRUCTURES[family]
    kw = {"n_problems": n_problems}
    if family in relations.DEPTH_STRUCTURES:
        kw["depth"] = depth
    inst = fn(rng, lex, **kw)
    n_proposed = len(inst.questions)
    inst.questions = [q for q in inst.questions if structurally_ok(q, inst)]
    n_structural_rejects = n_proposed - len(inst.questions)

    # The padding level is chosen on the whole document store, distractor
    # included, because that is what a retriever and a reader actually see.
    from src.corpus import frames_default as _fd
    n_levels = getattr(_fd, "MAX_NOTES", 8) + 1
    dfam = dinst = None
    if with_distractor:
        others = [f for f in relations.STRUCTURES if f != family]
        dfam = others[seed % len(others)]
        dkw = {"n_problems": 1}
        if dfam in relations.DEPTH_STRUCTURES:
            dkw["depth"] = min(depth, 2)
        dinst = fn_of(dfam)(
            random.Random(seed * 7919 + DISTRACTOR_OFFSET),
            Lexicon(random.Random(seed * 104729 + DISTRACTOR_OFFSET),
                    reserved, global_reserved), **dkw)
    all_pages = list(inst.pages) + (list(dinst.pages) if dinst else [])
    lvl = _pick_level(
        range(n_levels),
        lambda i: sum(len(encode(frame.page(sc, fs, i)))
                      for sc, fs in all_pages),
        page_target)
    pages = [frame.page(sc, fs, lvl) for sc, fs in inst.pages]

    dist_pages = ([frame.page(sc, fs, lvl) for sc, fs in dinst.pages]
                  if dinst else [])

    docs = pages + dist_pages
    random.Random(seed ^ 0x7317).shuffle(docs)
    invented = sorted(lex.taken)

    questions = []
    for q in inst.questions:
        base = frame.question(q)
        li = _pick_level(LEADS,
                         lambda s: len(encode((s + " " + base).strip())),
                         prompt_target)
        text = (LEADS[li] + " " + base).strip()
        plan_txt = [f"{s['op']} {s['scope']} -> {s['out']}" for s in q.plan]
        rec = {
            "qid": q.qid,
            "text": text,
            "answer": str(q.answer),
            "plan": plan_txt,
            "type": q.kind,
            "stages": [str(s) for s in q.stages],
            "candidates": [str(c) for c in inst.candidates],
            "plan_len": len(q.plan),
            "n_distinct_ops": relations.n_distinct_ops(q.plan),
            "ops": relations.plan_ops(q.plan),
            "lead_level": li,
            "lookup_key": str(q.start) if q.kind in
            ("lookup", "compose", "iterate") else None,
        }
        rec["answer_source"] = audit.answer_source(rec["answer"], docs)
        rec["chance"] = audit.chance_floor(rec)
        rec["hash"] = audit.question_hash(rec["text"], rec["answer"])
        questions.append(rec)

    return {
        "episode_id": f"cr-{family}-{frame.fid}-{seed:09d}",
        "seed": seed,
        "component": "relation",
        "family": family,
        "frame": frame.fid,
        "frame_axes": {"lexicon": frame.lexicon, "mode": frame.mode,
                       "key_pos": frame.key_pos, "qform": frame.qform,
                       "scope_pos": frame.scope_pos},
        "depth": depth,
        "preamble_level": lvl,
        "world": {"domain": f"corpus_{family}"},
        "n_context": 0,
        "documents": [{"text": t} for t in docs],
        "questions": questions,
        "invented_words": invented,
        "lexicon_collisions": collisions(reserved, invented),
        "lexicon_rejected_collisions": lex.rejected_collisions,
        "n_proposed_questions": n_proposed,
        "n_structural_rejects": n_structural_rejects,
    }


def fn_of(family):
    return relations.STRUCTURES[family]


def audit_relation_episode(ep, frame, rng) -> dict:
    """Necessity and shortcut counts for one episode."""
    docs = [d["text"] for d in ep["documents"]]
    viol = dict.fromkeys(audit.VIOLATIONS, 0)
    for q in ep["questions"]:
        v = audit.violations(q, "\n".join(docs))
        for k in viol:
            viol[k] += v[k]
    sc = audit.shortcut_hits(ep, frame, reserved_words(frame), rng)
    return {"violations": viol, "shortcuts": sc,
            "n_questions": len(ep["questions"])}


def keep_relation_episode(ep, rep) -> tuple:
    """Whether an episode survives the exclusions, and why not when it does not.

    An episode is discarded whole rather than trimmed, so a frame never ends up
    with a different question set than another frame drew from the same seed.
    """
    if len(ep["questions"]) < 2:
        return False, "too_few_questions"
    v = rep["violations"]
    for k in ("answer_in_question", "answer_is_start",
              "answer_is_intermediate", "stages_not_distinct"):
        if v[k]:
            return False, k
    if ep["lexicon_collisions"]:
        return False, "lexicon_collision"
    return True, "kept"


# ---------------------------------------------------------------- plan arm

def build_plan_records(seed: int, n_steps: int, n_symbols: int, qframe: str,
                       rng: random.Random, band: str = "train") -> tuple:
    """The whole plan target and the stepwise targets for one item.

    Both arms are emitted. The whole plan arm is what saturated at three steps;
    the stepwise arm is the form `src/opgraph/data.py:step_prompt` documents as
    removing the length prior, and a corpus meant to lift a length ceiling
    should carry the evidence for both.
    """
    from src.opgraph.data import plan_prompt, step_examples
    from src.opgraph.plan import signature_line
    from src.corpus.plans import plan_item

    item, reason = plan_item(seed, n_steps, n_symbols, qframe, rng)
    if item is None:
        return None, reason
    w = item["world"]
    whole = {
        "record": "plan_whole",
        "seed": seed,
        "component": "plan",
        "n_steps": n_steps,
        "n_symbols": n_symbols,
        "symbols": item["symbols"],
        "qframe": qframe,
        "prompt": plan_prompt(w.ops, item["text"]),
        "target": item["plan_text"],
        "answer": item["gold"],
        "signature": signature_line(w.ops),
        "hash": audit.question_hash(item["text"], item["gold"]),
        "rejects": item["rejects"],
    }
    steps = [{"record": "plan_step", "seed": seed, "component": "plan",
              "band": band, "n_steps": n_steps, "n_symbols": n_symbols,
              "qframe": qframe, "step_index": i, "prompt": p, "target": t}
             for i, (p, t) in enumerate(step_examples(w.ops, item["text"],
                                                      item["plan"]))]
    return (whole, steps), None


# ------------------------------------------------------------- mathgen arm

def build_mathgen_episode(seed: int, answer_source: str = "all") -> dict:
    """One invented formal system, in the shared episode shape.

    `src/mathgen/cli.py:build_universe` runs its own verification, so the
    assertion counts come back with the universe rather than being re-derived.
    Exercise sections are dropped from the served pages, per
    `src/mathgen/rlbridge.py:DROP_SECTION_KINDS`: leaving them in tells a term
    overlap retriever which chapter the answer is on.
    """
    from src.mathgen.cli import build_universe
    from src.mathgen.textbook import chunks

    u = build_universe(seed, answer_source=answer_source)
    ch = [c for c in chunks(u["book"])
          if c.get("section_kind") != "exercises"]
    docs = [{"text": c["text"], "chapter": c["chapter"],
             "section_kind": c["section_kind"]} for c in ch]
    page_texts = [d["text"] for d in docs]
    qs = []
    for ex in u["exercises"]:
        d = ex.to_dict()
        qs.append({
            "qid": d["exercise_id"],
            "text": d["prompt"],
            "answer": str(d["answer"]),
            "plan": list(d["required_chapters"]),
            "type": d["recipe"].get("kind", "unknown"),
            "stages": [str(d["answer"])],
            "candidates": [],
            "plan_len": len(d["required_chapters"]),
            "n_distinct_ops": 1,
            "level": d["level"],
            "answer_kind": d["answer_kind"],
            "generator_answer_source": d["answer_source"],
            "answer_source": audit.answer_source(d["answer"], page_texts),
            "necessity": d["necessity"],
            "chance": 0.0,
            "hash": audit.question_hash(d["prompt"], str(d["answer"])),
        })
    ver = u["verification"]
    return {
        "episode_id": f"cm-{seed:09d}",
        "seed": seed,
        "component": "mathgen",
        "family": f"mathgen_{answer_source}",
        "frame": "mathgen.native",
        "world": {"domain": "mathgen"},
        "n_context": 0,
        "documents": docs,
        "questions": qs,
        "verification": {
            "all_passed": ver["all_passed"],
            "assertions_checked": ver["assertions_checked"],
            "assertions_passed": ver["assertions_passed"],
        },
        "relation_kind": u["theory"].structure.rel_kind,
    }
