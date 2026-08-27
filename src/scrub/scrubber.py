"""Scrub real-world anchors out of natural text.

scrub_text(text, seed) is a pure function. It removes three kinds of
anchor:

  entities  every capitalized token run that reads as a name is replaced.
            A run is a name when it has two or more tokens, or its one
            token is all-caps, or its one token sits mid-sentence, or its
            one token starts a sentence but the same word also appears
            capitalized mid-sentence elsewhere in the document. A lone
            capitalized frequent common noun or verb, and a lone
            sentence-starting word never seen mid-sentence, are ordinary
            words and stay. Two replacement policies exist. invent, the
            default, writes a synthetic name from the worldgen name
            grammar. shuffle writes another real entity surface form
            served by an EntityPool harvested from the corpus itself, so
            real name tokens keep training signal while the per-document
            random reassignment still kills the facts. Either way the
            replacement keeps the shape of the original: word count is
            preserved up to three words, and an all-caps token maps to an
            all-caps replacement token.
  numbers   numeric literals are perturbed inside their own digit count,
            so real figures are destroyed but magnitudes and formats
            survive. Year-like numbers shift by a small nonzero delta and
            stay in the year range. Single digit integers stay: counts
            that small are shape, not knowledge. Comma grouping, decimal
            places, and leading zeros are preserved.
  web       URLs, email addresses, and @handles are replaced whole by
            synthetic ones.

Consistency contract: within one call the same surface form always maps
to the same replacement, and the mapping is drawn from an rng keyed by
the seed, a hash of the whole document, and a hash of the surface form.
The same entity therefore reads consistently inside a document but maps
differently in every other document, so no global mapping of a real name
is learnable from a scrubbed corpus.

The returned spans mark every replacement in the output text. They are
the informative spans the extractive QA generator prefers as answers.
"""

import hashlib
import re
from bisect import bisect_right
from dataclasses import dataclass

import numpy as np

from src.scrub.common_words import COMMON_WORDS
from src.worldgen.names import make_word

FUNCTION_WORDS = frozenset("""
the a an this that these those
some any no none all both each every either neither few several many much
more most little less least enough such other another same own
i you he she it we they me him her us them my your his its our their
mine yours hers ours theirs myself yourself himself herself itself
ourselves yourselves themselves one ones
who whom whose which what whatever whoever whichever
anyone anybody anything everyone everybody everything someone somebody
something nobody nothing
when where why how
am is are was were be been being do does did doing done
have has had having will would shall should can could may might must
ought need
and or but nor so yet if because although though while whereas unless
until since whenever once
about above across after against along among around at before behind
below beneath beside between beyond by despite down during except for
from in inside into like near of off on onto out outside over past
through throughout to toward towards under underneath up upon with
within without
not never always often sometimes usually rarely seldom perhaps maybe
however therefore thus hence moreover furthermore meanwhile instead
otherwise nonetheless nevertheless also then now today soon later
earlier here there again still already just only even almost quite
rather very too first second third finally next last yes well indeed
according mr mrs ms dr
""".split())

_COMMON_WORD_SET = frozenset(COMMON_WORDS)

# Words whose trailing period does not end a sentence, for the
# sentence-start test on the following word.
_HONORIFICS = frozenset(["dr", "mr", "mrs", "ms", "prof", "st", "no",
                         "vs", "etc"])

# One token is either a capitalized word or a numeric literal. The two
# kinds never overlap because a capitalized word starts with a letter.
TOKEN_RE = re.compile(
    r"(?P<num>\d[\d,]*(?:\.\d+)?)|(?P<cap>[A-ZÀ-Þ][A-Za-z0-9À-ÿ]*)"
)

# Gap allowed between two capitalized tokens of one entity run: spaces and
# tabs only, no newlines, so runs never bridge line breaks.
_RUN_GAP_RE = re.compile(r"[ \t]+")

_URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"')\]]+")
_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
_HANDLE_RE = re.compile(r"(?<![\w@])@\w+")

_YEAR_RANGE = (1300, 2199)

# Characters skipped when scanning left for the sentence-start test:
# whitespace plus opening quotes and brackets.
_PRE_SKIP = " \t\n\r\"'([{"


@dataclass
class ScrubResult:
    """Scrubbed text plus the replacement spans inside it.

    spans entries are dicts with keys start, end, text, kind, where kind
    is "entity", "number", or "web" and text == scrubbed[start:end].
    replacements maps each replaced surface form, entities lowercased, to
    what replaced it.
    """

    text: str
    spans: list
    replacements: dict


def _seed_material(seed) -> tuple:
    if isinstance(seed, (tuple, list)):
        return tuple(int(s) for s in seed)
    return (int(seed),)


def _digest(payload: str) -> int:
    return int.from_bytes(
        hashlib.blake2b(payload.encode("utf-8"), digest_size=8).digest(),
        "little")


def _keyed_rng(material: tuple, doc_key: int, kind: str, key: str):
    return np.random.default_rng(
        material + (doc_key, _digest(f"{kind}\x00{key}")))


def _entity_base_words(surface_lower: str, rng) -> list:
    n_words = min(3, surface_lower.count(" ") + 1)
    return [make_word(rng, 2, 2) for _ in range(n_words)]


def _shape_entity(surface: str, base_words: list) -> str:
    orig_words = surface.split()
    out = []
    for i, base in enumerate(base_words):
        orig = orig_words[i] if i < len(orig_words) else orig_words[-1]
        if len(orig) >= 2 and orig.isupper():
            out.append(base.upper())
        else:
            out.append(base)
    return " ".join(out)


def _shape_pool_entity(surface: str, form: str) -> str:
    """Shape one pool form onto one occurrence: word count capped at
    three like the invented policy, and an all-caps original word maps to
    an all-caps replacement word."""
    orig_words = surface.split()
    form_words = form.split()
    out = []
    for i in range(min(3, len(orig_words))):
        base = form_words[i] if i < len(form_words) else form_words[-1]
        orig = orig_words[i]
        if len(orig) >= 2 and orig.isupper():
            out.append(base.upper())
        else:
            out.append(base)
    return " ".join(out)


def _perturb_int(digits: str, rng) -> str:
    length = len(digits)
    value = int(digits)
    factor = int(rng.integers(55, 180))
    new = value * factor // 100
    if digits[0] == "0":
        new %= 10 ** length
        if new == value:
            new = (new + 1) % 10 ** length
        return str(new).zfill(length)
    lo, hi = 10 ** (length - 1), 10 ** length - 1
    new = min(hi, max(lo, new))
    if new == value:
        new = value + 1 if value < hi else value - 1
    return str(new)


def _perturb_number(surface: str, rng) -> str:
    digits = surface.replace(",", "")
    if "." in digits:
        whole, frac = digits.split(".", 1)
        new_whole = _perturb_int(whole, rng) if len(whole) > 1 else whole
        # The offset stays below 10^len(frac), and the draw bound is capped
        # so absurdly long fractions cannot overflow the rng's int64 range.
        bound = min(9 ** len(frac) - 1, 10 ** 12)
        offset = 1 + int(rng.integers(bound)) if bound > 0 else 1
        new_frac = str((int(frac) + offset) % 10 ** len(frac)).zfill(
            len(frac))
        return f"{new_whole}.{new_frac}"
    if (len(digits) == 4 and "," not in surface
            and _YEAR_RANGE[0] <= int(digits) <= _YEAR_RANGE[1]):
        delta = int(rng.integers(-30, 31))
        if delta == 0:
            delta = 7
        year = int(digits) + delta
        if not _YEAR_RANGE[0] <= year <= _YEAR_RANGE[1]:
            year = int(digits) - delta
        return str(year)
    if len(digits) == 1:
        return surface
    out = _perturb_int(digits, rng)
    return f"{int(out):,d}" if "," in surface else out


def _web_replacement(kind: str, rng) -> str:
    if kind == "url":
        return f"https://{make_word(rng, 2, 2).lower()}.site/" \
               f"{make_word(rng, 2, 2).lower()}"
    if kind == "email":
        return f"{make_word(rng, 2, 2).lower()}@" \
               f"{make_word(rng, 2, 2).lower()}.net"
    return f"@{make_word(rng, 2, 2).lower()}"


def _sentence_initial(text: str, pos: int) -> bool:
    """True when the token at pos starts a sentence: only whitespace or
    opening punctuation to its left up to the document start or a sentence
    terminal, and the terminal is not an honorific's period."""
    i = pos - 1
    while i >= 0 and text[i] in _PRE_SKIP:
        i -= 1
    if i < 0:
        return True
    if text[i] not in ".!?":
        return False
    j = i - 1
    while j >= 0 and text[j].isalpha():
        j -= 1
    return text[j + 1:i].lower() not in _HONORIFICS


def _web_edits(text: str) -> list:
    """(start, end, kind, surface) for URLs, emails, and handles, longest
    kinds first so nothing nests."""
    edits = []
    covered = []
    for regex, kind in ((_URL_RE, "url"), (_EMAIL_RE, "email"),
                        (_HANDLE_RE, "handle")):
        for m in regex.finditer(text):
            if any(m.start() < e and s < m.end() for s, e in covered):
                continue
            edits.append((m.start(), m.end(), kind, m.group()))
            covered.append((m.start(), m.end()))
    return sorted(edits)


def _token_edits(text: str, covered: list) -> list:
    """(start, end, kind, surface) for entity runs and numbers outside the
    covered web ranges, applying the name heuristics."""
    starts = [s for s, _ in covered]
    ends = [e for _, e in covered]

    def in_covered(s: int, e: int) -> bool:
        i = bisect_right(starts, s) - 1
        if 0 <= i < len(ends) and s < ends[i]:
            return True
        i = bisect_right(starts, e - 1) - 1
        return 0 <= i < len(ends) and e - 1 < ends[i]

    numbers = []
    runs = []  # [start, end, n_tokens, first_initial]
    evidence = set()
    for m in TOKEN_RE.finditer(text):
        if in_covered(m.start(), m.end()):
            continue
        if m.lastgroup == "num":
            numbers.append((m.start(), m.end()))
            continue
        word = m.group()
        if word.lower() in FUNCTION_WORDS:
            continue
        if runs and _RUN_GAP_RE.fullmatch(text[runs[-1][1]:m.start()]):
            runs[-1][1] = m.end()
            runs[-1][2] += 1
            evidence.add(word.lower())
        else:
            initial = _sentence_initial(text, m.start())
            runs.append([m.start(), m.end(), 1, initial])
            if not initial:
                evidence.add(word.lower())

    edits = [(s, e, "number", text[s:e]) for s, e in numbers]
    for start, end, n_tokens, first_initial in runs:
        surface = text[start:end]
        if n_tokens == 1:
            if not (len(surface) >= 2 and surface.isupper()):
                if surface.lower() in _COMMON_WORD_SET:
                    continue
                if first_initial and surface.lower() not in evidence:
                    continue
        edits.append((start, end, "entity", surface))
    return edits


def scrub_text(text: str, seed, entity_policy: str = "invent",
               pool=None) -> ScrubResult:
    """Replace entity runs, perturb numbers, and rewrite web anchors,
    returning the new text with replacement spans. Deterministic in
    (text, seed, entity_policy, pool); seed is an int or a tuple of ints.

    entity_policy picks the entity replacement. invent, the default,
    writes synthetic names from the worldgen name grammar. shuffle
    writes other real entity surface forms served by pool, an
    EntityPool from src.scrub.name_pool; the same surface maps to one
    pool form inside a document and to unrelated forms in other
    documents."""
    if entity_policy not in ("invent", "shuffle"):
        raise ValueError(f"unknown entity policy {entity_policy!r}")
    if entity_policy == "shuffle" and pool is None:
        raise ValueError("the shuffle entity policy needs a harvested pool")
    material = _seed_material(seed)
    doc_key = _digest(text)

    web = _web_edits(text)
    covered = [(s, e) for s, e, _, _ in web]
    edits = sorted(web + _token_edits(text, covered))

    cache: dict = {}
    replacements: dict = {}

    def replace(kind: str, surface: str) -> str:
        key = (kind, surface.lower() if kind == "entity" else surface)
        if key not in cache:
            rng = _keyed_rng(material, doc_key, kind, key[1])
            if kind == "entity":
                if entity_policy == "shuffle":
                    cache[key] = pool.pick(surface, rng)
                else:
                    cache[key] = _entity_base_words(key[1], rng)
            elif kind == "number":
                cache[key] = _perturb_number(surface, rng)
            else:
                cache[key] = _web_replacement(kind, rng)
        if kind == "entity":
            if entity_policy == "shuffle":
                new = _shape_pool_entity(surface, cache[key])
            else:
                new = _shape_entity(surface, cache[key])
        else:
            new = cache[key]
        replacements[key[1]] = new
        return new

    parts = []
    spans = []
    pos = 0
    out_len = 0
    for start, end, kind, surface in edits:
        new = replace(kind, surface)
        parts.append(text[pos:start])
        out_len += start - pos
        spans.append({"start": out_len, "end": out_len + len(new),
                      "text": new,
                      "kind": kind if kind in ("entity", "number")
                      else "web"})
        parts.append(new)
        out_len += len(new)
        pos = end
    parts.append(text[pos:])
    return ScrubResult(text="".join(parts), spans=spans,
                       replacements=replacements)


def scrub_document(text: str, seed, entity_policy: str = "invent",
                   pool=None) -> str:
    """Scrubbed text only, for callers that do not need the spans."""
    return scrub_text(text, seed, entity_policy=entity_policy,
                      pool=pool).text


def entity_runs(text: str) -> list:
    """(start, end) pairs of the entity runs scrub_text would replace,
    ignoring web ranges. Used by the extractive QA span finder."""
    return [(s, e) for s, e, kind, _ in _token_edits(text, [])
            if kind == "entity"]


def number_literals(text: str) -> list:
    """(start, end) pairs of numeric literals in text."""
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)
            if m.lastgroup == "num"]
