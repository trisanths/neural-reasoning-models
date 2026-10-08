"""Query formulations for MMLU web retrieval.

Five, and the point of naming them is that the harness previously had
one and never said so. Every formulation is built from the question and
its options, never from the gold answer, so no formulation can plant the
answer in the query.

    question         the stem, trimmed. What the published cell used.
    question_options the stem followed by all four options.
    keywords         the stem's content words, stopwords dropped.
    subject_question the mmlu subject name in front of the stem.
    generated        a search query written for the stem in advance and
                     read from a json file. The writer saw the stem and
                     nothing else: no options, no gold, no page text.
                     Anything else would be writing the answer into the
                     query and calling the result retrieval.
"""
from __future__ import annotations

import json
import os

from src.extern.retpack import content_terms

_GEN: dict | None = None


def _gen(path):
    global _GEN
    if _GEN is None:
        _GEN = json.load(open(path)) if path and os.path.exists(path) else {}
    return _GEN


def formulate(kind: str, row, gen_path: str = "data/extern/gen_queries.json") -> str:
    q = " ".join(str(row["question"]).split())
    if kind == "question":
        return q[:300]
    if kind == "question_options":
        opts = " ".join(" ".join(str(c).split()) for c in row["choices"])
        return (q[:300] + " " + opts)[:450]
    if kind == "keywords":
        seen, out = set(), []
        for t in content_terms(q):
            if t not in seen:
                seen.add(t)
                out.append(t)
        return " ".join(out[:18])
    if kind == "subject_question":
        return (str(row["subject"]).replace("_", " ") + ": " + q)[:320]
    if kind == "generated":
        g = _gen(gen_path).get(row["id"])
        return (g or q)[:300]
    raise ValueError(kind)


FORMULATIONS = ("question", "question_options", "keywords",
                "subject_question", "generated")
