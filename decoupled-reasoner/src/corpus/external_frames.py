"""The `src/frames/` generator, used as a second frame source.

`src/frames/` landed while this corpus was being built. It is a frame
generator over the three `src/skillacq/simple.py` rule families, sampling a
lexicon and a sentence shape and rendering through
`src/disc/renderers.SimpleRenderer`, so its frames are directly comparable
with the published hand written renderers.

It does not replace `src/corpus/frames_default.py` and the seam in
`src/corpus/frames.py` does not pick it up, for one reason: its `Frame`
renders three families through `pages_<family>` and `q_<family>` methods,
while the corpus renders sixteen relation structures from prose free records.
The two interfaces do not meet. What is worth having from it is the shapes
themselves, independently designed, so it is used here as its own corpus
component covering the three families it knows, and the internal bank covers
the other thirteen.

One constraint is inherited rather than decided here. `src/frames/generate.py`
defines `split_frames`, a train and test partition of its frame space by
lexicon and by shape. Training on its test frames would destroy that split, so
only the train side is written into the training band, and its test frames go
into the corpus held-out band and are named in the manifest.

Nothing in `src/frames/` is modified.
"""

from __future__ import annotations

import random


def available() -> bool:
    try:
        import src.frames.generate  # noqa: F401
    except Exception:  # noqa: BLE001
        return False
    return True


def frame_split(policy: str = "both") -> dict:
    from src.frames.generate import split_frames
    return split_frames(policy=policy)


def build_external_episode(frame_name: str, family: str, seed: int,
                           n_problems: int = 6) -> dict:
    """One episode in the corpus record shape, rendered by a src/frames frame.

    The episode itself comes from `src/disc/renderers.simple_episode`, which is
    the published builder: same draw order, same rejection, same distractor
    page, same candidate list. Only the axis fields are added on top.
    """
    from src.disc.renderers import simple_episode
    from src.frames.generate import FRAMES

    frame = FRAMES[frame_name]
    ep = simple_episode(seed, family, frame, n_problems=n_problems)
    docs = [d["text"] for d in ep["documents"]]
    from src.corpus import audit
    qs = []
    cands = [str(c) for c in ep.get("candidates") or []]
    for q in ep["questions"]:
        rec = dict(q)
        # A one step lookup has no starting stage. Recording the answer as its
        # own stage would make `answer_is_start` fire on every item, which is
        # an artefact of the record and not a property of the task, so the
        # stage list is left empty and the two stage exclusions are vacuous.
        rec["stages"] = []
        rec["candidates"] = cands
        rec["plan_len"] = 1
        rec["n_distinct_ops"] = 1
        rec["ops"] = ["lookup"]
        rec["answer_source"] = audit.answer_source(q["answer"], docs)
        rec["chance"] = audit.chance_floor(rec)
        rec["hash"] = audit.question_hash(q["text"], str(q["answer"]))
        qs.append(rec)
    lx, sh = frame_name.split("__", 1)
    out = dict(ep)
    out.update({
        "episode_id": f"cx-{family}-{frame_name}-{seed:09d}",
        "component": "external_frames",
        "family": family,
        "frame": frame_name,
        "frame_axes": {"lexicon": lx, "shape": sh, "source": "src.frames"},
        "depth": 1,
        "questions": qs,
    })
    return out


def cell(job):
    """One (frame, family) cell over a seed block."""
    frame_name, family, seed0, n_seeds, band = job
    from collections import Counter
    kept, rejects = [], Counter()
    rng = random.Random(seed0)
    for r in range(n_seeds):
        seed = seed0 + r
        try:
            ep = build_external_episode(frame_name, family, seed)
        except Exception as exc:  # noqa: BLE001
            rejects["generator_error:" + type(exc).__name__] += 1
            continue
        if len(ep["questions"]) < 2:
            rejects["too_few_questions"] += 1
            continue
        bad = 0
        docs = "\n".join(d["text"] for d in ep["documents"])
        from src.corpus import audit
        for q in ep["questions"]:
            v = audit.violations(q, docs)
            bad += sum(v.values())
        if bad:
            rejects["necessity_violation"] += 1
            continue
        ep["band"] = band
        kept.append(ep)
        rejects["kept"] += 1
    del rng
    return frame_name, family, kept, dict(rejects)
