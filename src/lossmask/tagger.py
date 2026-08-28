"""Tag the factual spans of natural text, and carry the tags onto tokens.

The text is never altered. That is the whole difference between this
package and src/scrub: regime E destroyed the corpus so the forward pass
read mangled language, and reading paid for it. Here the forward pass sees
the original sentence and only the loss changes.

What is reused, and from where:

  entity runs   src.scrub.scrubber.anchor_spans, which is scrub_text's
                detection pass with the rewriting removed. It carries the
                whole capitalized-run heuristic: multi-token runs, all-caps
                singletons, mid-sentence singletons, and the common-word and
                sentence-start exemptions that keep ordinary words out.
  numbers       the same call. Numeric literals with comma grouping and
                decimals, from src.scrub.scrubber.TOKEN_RE.
  web           the same call. URLs, email addresses, and @handles, from
                src.scrub.scrubber._web_edits.

Only dates are new here. The scrubber has no date detector: it treats a
year as a four digit number and handles it inside _perturb_number, and it
has no notion of a month name at all. src.scrub.scrubber._YEAR_RANGE is
reused for the year test, and month names are matched here. A date span
wins over any entity or number span it overlaps, so "January 1987" is one
date rather than an entity followed by a number, and a bare year in the
year range is a date rather than a number. Separating dates out lets an
experiment suppress times without suppressing names.
"""

import re

import numpy as np

from src.lossmask.tags import TAG_DATE, TAG_ENTITY, TAG_NUMBER, TAG_WEB
from src.scrub.scrubber import _YEAR_RANGE, anchor_spans

_KIND_TAGS = {
    "entity": TAG_ENTITY,
    "number": TAG_NUMBER,
    "url": TAG_WEB,
    "email": TAG_WEB,
    "handle": TAG_WEB,
}

_MONTH = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May"
          r"|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?"
          r"|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)")
_DAY = r"(?:[12]\d|3[01]|0?[1-9])"
_YEAR = r"(?:1[3-9]\d{2}|20\d{2}|21\d{2})"
_ORD = r"(?:st|nd|rd|th)"

# Longest patterns first: the scan takes the first match at a position and
# never lets a later pattern nest inside an accepted span.
_DATE_RES = [
    # 12 March 1998, 12th March 1998
    re.compile(rf"\b{_DAY}{_ORD}?\s+(?:of\s+)?{_MONTH}\.?\s*,?\s*{_YEAR}\b"),
    # March 12, 1998 and March 12th 1998
    re.compile(rf"\b{_MONTH}\.?\s+{_DAY}{_ORD}?\s*,?\s*{_YEAR}\b"),
    # 1998-03-12, 1998/03/12
    re.compile(rf"\b{_YEAR}[-/](?:1[0-2]|0?[1-9])[-/]{_DAY}\b"),
    # 03/12/1998, 3-12-98
    re.compile(rf"\b(?:1[0-2]|0?[1-9])[-/]{_DAY}[-/](?:{_YEAR}|\d{{2}})\b"),
    # March 1998
    re.compile(rf"\b{_MONTH}\.?\s+{_YEAR}\b"),
    # March 12
    re.compile(rf"\b{_MONTH}\.?\s+{_DAY}{_ORD}?\b(?!\s*[-/]\d)"),
    # 1998, 1990s, mid-1990s handled as the bare year inside them
    re.compile(rf"\b{_YEAR}s?\b"),
]


def date_spans(text: str) -> list:
    """(start, end) of every date-like span, in order and non-overlapping.

    The year range is src.scrub.scrubber._YEAR_RANGE, so a four digit
    number counts as a year here exactly when the scrubber would have
    perturbed it as one.
    """
    found = []
    for regex in _DATE_RES:
        for m in regex.finditer(text):
            if any(m.start() < e and s < m.end() for s, e in found):
                continue
            year = re.search(r"\d{4}", m.group())
            if year and not _YEAR_RANGE[0] <= int(year.group()) <= _YEAR_RANGE[1]:
                continue
            found.append((m.start(), m.end()))
    return sorted(found)


def factual_spans(text: str) -> list:
    """(start, end, tag) over the whole document, ordered and disjoint.

    Dates are laid down first and win every overlap, then the scrubber's
    anchors fill in around them.
    """
    spans = [(s, e, TAG_DATE) for s, e in date_spans(text)]
    taken = [(s, e) for s, e, _ in spans]
    for start, end, kind in anchor_spans(text):
        if any(start < e and s < end for s, e in taken):
            continue
        spans.append((start, end, _KIND_TAGS[kind]))
        taken.append((start, end))
    spans.sort()
    return spans


def encode_with_tags(text: str, tokenizer, spans=None):
    """Tokenize text and return (ids, tags) as lists of the same length.

    A token is tagged when its character range touches a span at all, so
    the leading space a byte level BPE token carries rides with the span it
    introduces. Predicting " Paris" is the memorization event, not
    predicting "Paris" after a space nobody had to guess.
    """
    if spans is None:
        spans = factual_spans(text)
    encoding = tokenizer.tokenizer.encode(text)
    ids = encoding.ids
    tags = tag_offsets(encoding.offsets, spans)
    return ids, tags


def tag_offsets(offsets, spans) -> list:
    """Walk sorted token offsets against sorted disjoint spans, one pass."""
    tags = [0] * len(offsets)
    if not spans:
        return tags
    i = 0
    n = len(spans)
    for k, (start, end) in enumerate(offsets):
        if end <= start:  # zero width tokens touch nothing
            continue
        while i < n and spans[i][1] <= start:
            i += 1
        if i >= n:
            break
        span_start, span_end, tag = spans[i]
        if start < span_end and span_start < end:
            tags[k] = tag
    return tags


def tag_histogram(tags) -> dict:
    """Token counts per tag id, for build stats and sanity checks."""
    counts = np.bincount(np.asarray(tags, dtype=np.int64), minlength=8)
    return {int(tag): int(count) for tag, count in enumerate(counts) if count}
