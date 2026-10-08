"""Turn one generation into the span that gets graded, and say why when it cannot.

Grading the whole generation would be unfair to a model that reasons out loud,
because a reasoning trace names every candidate on its way to one of them and
`src/norm/cmpwork/grade.py` counts two named candidates as a hedge. So the
reasoning block is removed first and the answer span is taken after it.

The states a generation can be in are kept apart from a wrong answer, because
a model that never finished its reasoning inside the budget has not been
measured on the task at all.

    ok                     an answer span was found
    empty                  nothing but whitespace was generated
    unterminated_reasoning a reasoning block opened and never closed, so the
                           budget cut the model off before it answered
"""
from __future__ import annotations

import re

THINK_OPEN = re.compile(r"<\s*(think|thinking|reasoning)\s*>", re.I)
THINK_CLOSE = re.compile(r"<\s*/\s*(think|thinking|reasoning)\s*>", re.I)
ANSWER_LINE = re.compile(r"(?im)^[^\S\n]*(?:final\s+)?answer\s*[:\-–]\s*")


def split_reasoning(raw: str):
    """(reasoning, rest, state). Handles a closing tag with no opening tag,
    which is how a template that opens the block for the model comes back."""
    close = list(THINK_CLOSE.finditer(raw))
    if close:
        last = close[-1]
        return raw[:last.start()], raw[last.end():], "ok"
    if THINK_OPEN.search(raw):
        return raw, "", "unterminated_reasoning"
    return "", raw, "ok"


def answer_span(raw: str):
    """The part of a generation that is the model's answer."""
    reasoning, rest, state = split_reasoning(raw)
    if state == "unterminated_reasoning":
        return {"state": state, "span": "", "reasoning_chars": len(reasoning),
                "rest": ""}
    if not rest.strip():
        return {"state": "empty" if not raw.strip() else "reasoning_only",
                "span": "", "reasoning_chars": len(reasoning), "rest": rest}
    hits = list(ANSWER_LINE.finditer(rest))
    if hits:
        tail = rest[hits[-1].end():]
        # The answer usually sits on the marker's own line, but a model that
        # puts a newline after "Answer:" has still answered, so the first line
        # with anything on it is the one graded rather than the literal first.
        after = [l for l in tail.splitlines() if l.strip()]
        span = after[0] if after else ""
    else:
        lines = [l for l in rest.splitlines() if l.strip()]
        span = lines[-1] if lines else ""
    return {"state": "ok", "span": span, "reasoning_chars": len(reasoning),
            "rest": rest}
