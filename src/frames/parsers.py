"""Trivial programs that read the same pages, as a baseline for the model.

Two of them, and they answer different questions.

`frame_aware` is handed the frame the page was written in and reads the rule
with that frame's own regex. It is a solvability check: if it scores 1.000 in
every frame then every frame states its rule just as mechanically as the
native one does, and a model that collapses off-frame is not being defeated by
a harder task.

`native_tuned` is the same fifty lines of regex with the training frame baked
in: it reads `src/skillacq/simple.py`'s wording and nothing else. It is the
program-shaped version of the hypothesis under test, and it collapses off
frame by construction. Reporting it keeps the model's collapse honest: a
reader that only knows one surface behaves exactly this way.

Both parsers are handed the question's key for free rather than parsing it out
of the question text. That makes them stronger than a text-only program, which
is the conservative direction for `native_tuned`: if it still names nothing off
frame, the collapse is not an artifact of a weak parser.
"""

from __future__ import annotations

import random
import re

from src.disc.renderers import _simple_problems
from src.frames.generate import FRAMES, NATIVE_FRAME, Frame
from src.skillacq.simple import SIMPLE_FAMILIES


def system_and_problems(seed: int, family: str, n_problems: int = 6):
    """Rebuild the system and its problems exactly as `simple_episode` did."""
    rng = random.Random(seed)
    s = SIMPLE_FAMILIES[family](rng)
    return s, _simple_problems(s, family, rng, n_problems)


def read_substitution(frame: Frame, s, key: str, pages: str) -> str:
    m = re.search(frame.row_regex(s, key), pages)
    if m:
        return m.group(1)
    m = re.search(frame.fallback_regex(s), pages)
    return m.group(1) if m else ""


def read_exception(frame: Frame, s, key: str, pages: str) -> str:
    rx, order = frame.special_regex(s)
    sk = sp = None
    m = re.search(rx, pages)
    if m:
        a, b = m.group(1), m.group(2)
        sk, sp = (a, b) if order[0] == "key" else (b, a)
    gm = re.search(frame.general_regex(s), pages)
    general = gm.group(1) if gm else ""
    if sk is not None and key == sk:
        return sp
    return general


def parse_answer(frame: Frame, s, family: str, key: str, pages: str) -> str:
    if family == "substitution_rule":
        return read_substitution(frame, s, key, pages)
    if family == "exception_rule":
        return read_exception(frame, s, key, pages)
    return ""


def run_parsers(episodes: list[dict], family: str, frame_name: str,
                n_problems: int) -> list[dict]:
    """One row per question, with both parsers' answers beside the gold."""
    frame = FRAMES[frame_name]
    native = FRAMES[NATIVE_FRAME]
    rows = []
    for i, ep in enumerate(episodes):
        s, problems = system_and_problems(ep["seed"], family, n_problems)
        pages = "\n\n".join(d["text"] for d in ep["documents"])
        by_qid = {p["qid"]: p for p in problems}
        for q in ep["questions"]:
            p = by_qid.get(q["qid"])
            if p is None:
                continue
            key = p["key"]
            rows.append({
                "ep": i, "qid": q["qid"], "family": family,
                "gold": q["answer"],
                "candidates": ep["candidates"],
                "twin_candidates": ep.get("twin_candidates", []),
                "chunks": [d["text"] for d in ep["documents"]],
                # A parser reads the store directly, so the answering page is
                # served by construction.
                "served": True,
                "answer_frame_aware": parse_answer(frame, s, family, key,
                                                   pages),
                "answer_native_tuned": parse_answer(native, s, family, key,
                                                    pages),
            })
    return rows
