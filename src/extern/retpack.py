"""Packing and answer detection for the MMLU web retrieval cells.

Two jobs live here, and both were previously buried inside
`retrieval_mmlu.py` where no sweep could reach them.

Packing decides which characters of the retrieved pages reach the model.
The original packer walked the ranked pages in order and gave each one
whatever was left of a single character budget, so a first page longer
than the budget consumed all of it and pages two through five were never
seen. `pack_sequential` keeps that behaviour for comparison. `pack_even`
splits the budget across pages. `pack_passages` cuts every page into
overlapping windows, scores each window against the question and all of
its options with a bm25 style weighting, and fills the budget with the
best windows regardless of which page they came from.

Passage selection reads all options, never the gold one alone. Scoring a
window against the gold answer would plant the answer in the context by
construction and every hit rate after that would be an artefact.

Detection decides whether the text in front of the model states the
answer. `contains_answer` is the original exact normalised substring
test. `contains_answer_soft` also accepts the gold answer's content
words appearing together inside one short window, which catches a gold
string that the page paraphrases or splits across punctuation. Both are
reported; neither is silently substituted for the other.
"""
from __future__ import annotations

import math
import re

WORD = re.compile(r"[a-z0-9]+")

STOP = frozenset("""a an the of and or in on at to for with without by from as is are was
were be been being this that these those it its which who whom what when where why how
not no nor but if then than so such can could may might will would shall should do does
did done have has had having i you he she they we them his her their our your my me us
about into over under between among during before after above below up down out off
again further once here there all any both each few more most other some only own same
too very s t don now""".split())


def norm(s: str) -> str:
    return " ".join(WORD.findall(str(s).lower()))


def content_terms(s: str) -> list[str]:
    return [w for w in norm(s).split() if w not in STOP and len(w) > 1]


# ----------------------------------------------------------- detection
#
# Three tests, all reported, none substituted for another.
#
#   chars  the original: the normalised gold string as a raw character
#          substring. It fires on "19" inside "1976" and on the single
#          letter "h" that a gold of "~H" normalises to, so it counts
#          hits that are not hits.
#   token  the same match constrained to whole token boundaries, which
#          is what "the page states this answer" should mean.
#   soft   every content word of the gold answer inside one short
#          window, which catches a page that paraphrases or re-punctuates.
#
# A gold whose normalised form is one short token cannot be told from
# incidental text by any of them, so `degenerate_gold` marks those and
# they are reported apart rather than dropped.


def contains_answer_chars(hay_norm: str, gold: str) -> bool:
    """The original test. Kept so the published cell stays reproducible."""
    g = norm(gold)
    return bool(g) and g in hay_norm


def contains_answer(hay_norm: str, gold: str) -> bool:
    """Whole token match of the gold answer's normalised token sequence."""
    g = norm(gold)
    if not g:
        return False
    return (" " + g + " ") in (" " + hay_norm + " ")


def degenerate_gold(gold: str) -> bool:
    """A gold too short to distinguish a statement from a coincidence."""
    g = norm(gold)
    return len(g) <= 2 or (len(g.split()) == 1 and len(g) <= 3)


def contains_answer_soft(hay_norm: str, gold: str, window: int = 240) -> bool:
    """Every content word of the gold answer inside one short window.

    A single content word is required to appear as a whole token, which
    is the same as the token test for one word answers. Multi word
    answers pass when their content words co-occur closely, so a page
    that writes "the peripheral nervous system's ganglia" still counts
    for a gold of "ganglia of the peripheral nervous system".
    """
    terms = content_terms(gold)
    if not terms:
        return contains_answer(hay_norm, gold)
    if len(terms) == 1:
        return re.search(r"\b" + re.escape(terms[0]) + r"\b", hay_norm) is not None
    positions = []
    for t in terms:
        p = [m.start() for m in re.finditer(r"\b" + re.escape(t) + r"\b", hay_norm)]
        if not p:
            return False
        positions.append(p)
    # Any window of `window` characters that holds one occurrence of each term.
    anchors = positions[0]
    for a in anchors:
        lo, hi = a - window, a + window
        if all(any(lo <= p <= hi for p in ps) for ps in positions[1:]):
            return True
    return False


def stem_key(question: str, words: int = 12) -> str:
    return " ".join(norm(question).split()[:words])


def label_contamination(text: str, question: str, gold: str,
                        detector: str = "token") -> str:
    """verbatim / answer / neither, the original three way label shape."""
    hay = norm(text)
    sk = stem_key(question)
    if sk and sk in hay:
        return "verbatim"
    fn = {"chars": contains_answer_chars, "token": contains_answer,
          "soft": contains_answer_soft}[detector]
    return "answer" if fn(hay, gold) else "neither"


# ------------------------------------------------------------- packing

def _clean(t: str) -> str:
    return " ".join((t or "").split())


def pack_sequential(pages, max_chars: int) -> str:
    """The original packer. First page takes whatever it wants."""
    parts, used = [], 0
    for p in pages:
        t = _clean(p.get("text"))
        if not t:
            continue
        room = max_chars - used
        if room <= 0:
            break
        parts.append(f"[{p.get('title') or p.get('url')}] {t[:room]}")
        used += min(len(t), room)
    return "\n\n".join(parts)


def pack_even(pages, max_chars: int) -> str:
    """Equal share of the budget for every non empty page."""
    live = [p for p in pages if _clean(p.get("text"))]
    if not live:
        return ""
    share = max(400, max_chars // len(live))
    parts, used = [], 0
    for p in live:
        t = _clean(p.get("text"))
        room = min(share, max_chars - used)
        if room <= 0:
            break
        parts.append(f"[{p.get('title') or p.get('url')}] {t[:room]}")
        used += min(len(t), room)
    return "\n\n".join(parts)


def chunk(text: str, size: int = 900, overlap: int = 200) -> list[str]:
    t = _clean(text)
    if not t:
        return []
    step = max(1, size - overlap)
    return [t[i:i + size] for i in range(0, max(1, len(t) - overlap), step)]


def pack_passages(pages, max_chars: int, query: str, options,
                  size: int = 900, overlap: int = 200,
                  max_chunks_per_page: int = 400) -> str:
    """Fill the budget with the windows that best match question plus options.

    bm25 style: idf over the candidate window set, term frequency
    saturated at k1, length normalised at b. The query is the question
    and every option, so no option is favoured.
    """
    cands = []
    for p in pages:
        for c in chunk(p.get("text"), size, overlap)[:max_chunks_per_page]:
            cands.append((p.get("title") or p.get("url"), c))
    if not cands:
        return ""
    qterms = set(content_terms(query))
    for o in (options or []):
        qterms |= set(content_terms(o))
    if not qterms:
        return pack_even(pages, max_chars)
    toks = [content_terms(c) for _, c in cands]
    N = len(toks)
    df = {}
    for tk in toks:
        for t in set(tk):
            if t in qterms:
                df[t] = df.get(t, 0) + 1
    avgdl = sum(len(t) for t in toks) / max(1, N)
    k1, b = 1.4, 0.75
    scored = []
    for i, tk in enumerate(toks):
        dl = len(tk) or 1
        tf = {}
        for t in tk:
            if t in qterms:
                tf[t] = tf.get(t, 0) + 1
        s = 0.0
        for t, f in tf.items():
            idf = math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avgdl))
        scored.append((s, i))
    scored.sort(key=lambda x: (-x[0], x[1]))
    parts, used, seen = [], 0, set()
    for s, i in scored:
        if used >= max_chars or s <= 0:
            break
        title, c = cands[i]
        key = c[:120]
        if key in seen:
            continue
        seen.add(key)
        room = max_chars - used
        parts.append(f"[{title}] {c[:room]}")
        used += min(len(c), room)
    return "\n\n".join(parts)


PACKERS = {"sequential": pack_sequential, "even": pack_even,
           "passages": pack_passages}


def pack(kind: str, pages, max_chars: int, query: str = "", options=None) -> str:
    if kind == "passages":
        return pack_passages(pages, max_chars, query, options)
    return PACKERS[kind](pages, max_chars)
