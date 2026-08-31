"""One grader for all three systems.

Forced choice over the item's own option set. The option set is the values the
plan's last step could have returned, so its size is the chance floor for that
item and floors are averaged, never assumed.

Matching is on word tokens, not substrings. An invented word is alphabetic and
a candidate can be a prefix of another candidate, so `answer.contains(option)`
would score `emb` correct on a page whose answer is `embqen`. Every candidate
is tokenized the same way the answer is and matched token for token, with a
multi-token candidate matched as a contiguous run.

    strict    exactly one distinct option is named and it is the gold one.
              Naming two options is wrong however the first one falls.
    lenient   the first option named is the gold one, whatever follows.
    hedged    two or more distinct options are named.
    none      no option is named at all.

`strict` is the headline. `lenient` travels beside it.
"""
from __future__ import annotations
import re

TOKEN = re.compile(r"[A-Za-z]+|[0-9]+|[^\sA-Za-z0-9]")


def _toks(s: str):
    return [t.lower() for t in TOKEN.findall(str(s))]


def _find_all(hay, needle):
    """Start positions where needle occurs as a contiguous run in hay."""
    n, m = len(hay), len(needle)
    if m == 0 or m > n:
        return []
    return [i for i in range(n - m + 1) if hay[i:i + m] == needle]


def forced(answer: str, options, gold: str) -> dict:
    hay = _toks(answer)
    first = {}
    for o in options:
        pos = _find_all(hay, _toks(o))
        if pos:
            first[o] = pos[0]
    named = sorted(first, key=lambda o: (first[o], -len(_toks(o))))
    # A candidate wholly inside a longer named candidate at the same position
    # is not a separate naming.
    keep = []
    for o in named:
        covered = any(first[o] >= first[q] and
                      first[o] + len(_toks(o)) <= first[q] + len(_toks(q)) and
                      o != q and len(_toks(q)) > len(_toks(o))
                      for q in named)
        if not covered:
            keep.append(o)
    named = keep
    return {
        "named": named,
        "named_none": int(not named),
        "hedged": int(len(named) > 1),
        "strict_correct": int(len(named) == 1 and named[0] == gold),
        "lenient_correct": int(bool(named) and named[0] == gold),
        "floor": 1.0 / len(options) if options else 0.0,
    }
