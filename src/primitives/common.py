"""Shared machinery for the capability-primitive suite.

Every primitive in this package generates items the same way and is scored
the same way, so a profile across the seven faculties is comparable and
never pooled. This module holds the pieces they share.

The item contract. An Item carries a question string, a list of document
chunks, a gold dictionary the scorer reads, and metadata the report and the
guards read. Nothing else crosses the boundary between a generator and the
runner, so a generator can be rewritten without touching the runner.

The answer contract. Models reply in a line format, KEY: value, one field
per line. parse_fields reads that leniently: any order, any case, bullets
and numbering stripped, the first occurrence of a key winning. Format
compliance is therefore not silently folded into a content score; the
runner reports parse rates on their own.

The no-shortcut guard. Three heuristics stand in for the ways an item can
be answerable without the faculty it claims to test: answering from the
question stem alone, answering with the most frequent candidate in the
prompt, and answering with the candidate that shares the most words with
the stem. A generator that emits an item any of the three solves has
produced a broken item, and every generator here rejects those before the
item reaches a model.

Statistics. Proportions carry Wilson intervals, which stay inside [0, 1]
at the small counts and extreme rates this suite produces, where a normal
approximation would not.
"""

from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass, field

from src.skillacq.systems import GLYPHS, _word

__all__ = [
    "GLYPHS", "Item", "invented_word", "invented_words", "parse_fields",
    "parse_labels", "parse_one_label", "normalize", "token_set", "overlap",
    "wilson", "proportion", "mean_stat", "guard_report", "guard_ok",
    "render_menu", "LETTERS", "jaccard", "parse_binary", "field_or_whole",
]

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_KEY_LINE = re.compile(r"^[\s>*\-•\d.()]*([A-Za-z][A-Za-z0-9_ ]{0,30}?)\s*[:=]\s*(.*)$")
_WORD = re.compile(r"[a-z0-9]+")


def invented_word(rng: random.Random, n: int = 2) -> str:
    """A syllable-built nonce word, from the skillacq vocabulary."""
    return _word(rng, n)


def invented_words(rng: random.Random, k: int, n: int = 2) -> list[str]:
    """k distinct nonce words."""
    out: list[str] = []
    seen: set[str] = set()
    guard = 0
    while len(out) < k and guard < 4000:
        guard += 1
        w = _word(rng, n)
        if w in seen:
            continue
        seen.add(w)
        out.append(w)
    if len(out) < k:
        raise ValueError("could not draw enough distinct nonce words")
    return out


@dataclass
class Item:
    """One generated test item.

    primitive  which faculty this scores, one of the seven names.
    variant    the sub-condition inside that faculty, reported separately.
    mode       "isolated" when the other faculties are supplied by oracle,
               "integrated" when the model must produce those inputs itself.
    question   the text handed to predict as its first argument.
    chunks     documents handed to predict as its second argument. Empty
               when the item deliberately withholds the corpus.
    gold       everything the scorer needs.
    meta       everything the report and the guards need, never the scorer.
    """

    item_id: str
    primitive: str
    variant: str
    mode: str
    question: str
    chunks: list = field(default_factory=list)
    gold: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id, "primitive": self.primitive,
            "variant": self.variant, "mode": self.mode,
            "question": self.question, "chunks": list(self.chunks),
            "gold": dict(self.gold), "meta": dict(self.meta),
        }


def normalize(text: str) -> str:
    """Lower case, collapse whitespace, drop surrounding punctuation."""
    t = str(text).strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t.strip(" .,;:!?'\"()[]")


def token_set(text: str) -> set[str]:
    return set(_WORD.findall(str(text).lower()))


def overlap(a: str, b: str) -> float:
    """Fraction of a's word types that also occur in b."""
    ta, tb = token_set(a), token_set(b)
    if not ta:
        return 0.0
    return len(ta & tb) / len(ta)


def jaccard(a, b) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def parse_fields(text: str) -> dict:
    """Read KEY: value lines out of a free-form reply.

    Order does not matter, case does not matter, and leading bullets,
    numbering, quoting marks and stray punctuation are stripped. The first
    occurrence of a key wins, so a model that restates itself later cannot
    overwrite its own answer with a summary. Keys come back upper case with
    internal whitespace collapsed to single underscores.
    """
    out: dict = {}
    for raw in str(text).splitlines():
        m = _KEY_LINE.match(raw)
        if not m:
            continue
        key = re.sub(r"\s+", "_", m.group(1).strip()).upper()
        if key in out:
            continue
        out[key] = m.group(2).strip()
    return out


def parse_labels(value: str, allowed) -> list[str]:
    """Labels from an allowed set, in the order they appear, deduplicated.

    Matching is on word boundaries so C1 does not match C10, and is case
    insensitive so a model that lower-cases its labels is not punished for
    the wrong faculty.
    """
    allowed = list(allowed)
    if not allowed:
        return []
    pat = re.compile(r"(?<![A-Za-z0-9])(" + "|".join(
        re.escape(a) for a in sorted(allowed, key=len, reverse=True)
    ) + r")(?![A-Za-z0-9])", re.IGNORECASE)
    upper = {a.upper(): a for a in allowed}
    seen: list[str] = []
    for m in pat.finditer(str(value)):
        lab = upper.get(m.group(1).upper())
        if lab is not None and lab not in seen:
            seen.append(lab)
    return seen


def parse_one_label(value: str, allowed) -> str | None:
    """The single label a field names, or None when it names zero or many.

    Naming several options is not a correct answer to a single-choice
    field, so it is scored as a miss rather than as a lucky first mention.
    """
    labs = parse_labels(value, allowed)
    return labs[0] if len(labs) == 1 else None


def label_verdict(value, allowed, gold) -> dict:
    """One single-choice field under both grading rules, with the hedge flag.

    A grader that accepts a reply merely containing the gold answer scores
    a model that names every option as correct on every item. The two
    rules differ only in how they treat a hedge: strict counts naming more
    than one candidate as wrong, lenient takes the first candidate named.
    Reporting the pair and the hedge rate together is what makes a score
    that lives on the leniency visible instead of quietly banked.
    """
    labs = parse_labels(value, allowed)
    return {"strict": float(len(labs) == 1 and labs[0] == gold),
            "lenient": float(bool(labs) and labs[0] == gold),
            "hedged": float(len(labs) > 1),
            "named": float(len(labs))}


def binary_verdict(text, mapping: dict, gold) -> dict:
    """The same pair of rules for a two-way field read through cue words.

    A reply carrying cues for both sides is a hedge here too, even though
    the cue lists are generous about wording.
    """
    low = str(text).lower()
    hits = []
    for label, cues in mapping.items():
        for cue in cues:
            m = re.search(rf"(?<![a-z]){re.escape(cue)}(?![a-z])", low)
            if m:
                hits.append((m.start(), label))
                break
    hits.sort()
    sides = {lab for _, lab in hits}
    first = hits[0][1] if hits else None
    return {"strict": float(len(sides) == 1 and first == gold),
            "lenient": float(first is not None and first == gold),
            "hedged": float(len(sides) > 1),
            "named": float(len(sides))}


def parse_binary(text: str, mapping: dict) -> str | None:
    """A two-way choice read generously, or None when it is not there.

    A model that was never trained to write PASS still means something
    when it writes "no". Scoring that as a miss would measure format
    compliance and call the result a faculty, which is the failure mode
    this suite exists to avoid. The earliest cue in the text wins, and a
    text carrying cues for both sides at the same position is None.
    Strict field presence is reported separately as the parse rate, so
    nothing is hidden by the leniency.
    """
    low = str(text).lower()
    hits = []
    for label, cues in mapping.items():
        for cue in cues:
            m = re.search(rf"(?<![a-z]){re.escape(cue)}(?![a-z])", low)
            if m:
                hits.append((m.start(), label))
                break
    if not hits:
        return None
    hits.sort()
    if len(hits) > 1 and hits[0][0] == hits[1][0]:
        return None
    return hits[0][1]


def field_or_whole(fields: dict, key: str, response: str) -> str:
    """The named field, or the whole reply when the model wrote no fields.

    The label namespaces in this suite do not overlap, so scanning a
    formatless reply for one field's labels cannot pick up another's.
    """
    got = fields.get(key)
    return got if got else str(response)


def render_menu(options: list[str], prefix: str) -> tuple[str, list[str]]:
    """Render an enumerated option block and return (text, labels)."""
    labels = [f"{prefix}{i + 1}" for i in range(len(options))]
    lines = [f"  {lab}. {opt}" for lab, opt in zip(labels, options)]
    return "\n".join(lines), labels


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for k successes in n trials."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def proportion(k: int, n: int, chance: float = 0.0, label: str = "") -> dict:
    """A scored proportion with its interval and its chance adjustment.

    adjusted is (acc - chance) / (1 - chance), which is zero for a model at
    chance and one for a perfect model, so faculties whose items have
    different option counts stay comparable. above_chance is True only when
    the whole interval clears chance.
    """
    n = int(n)
    k = int(k)
    acc = k / n if n else 0.0
    lo, hi = wilson(k, n)
    denom = 1.0 - chance
    adj = (acc - chance) / denom if denom > 1e-9 else 0.0
    adj_lo = (lo - chance) / denom if denom > 1e-9 else 0.0
    return {
        "label": label, "n": n, "correct": k, "acc": acc,
        "ci_lo": lo, "ci_hi": hi, "chance": chance,
        "adjusted": adj, "adjusted_ci_lo": adj_lo,
        "above_chance": bool(n > 0 and lo > chance),
    }


def mean_stat(values, label: str = "") -> dict:
    """Mean of bounded scores with a normal interval on the mean."""
    vals = [float(v) for v in values]
    n = len(vals)
    if n == 0:
        return {"label": label, "n": 0, "mean": 0.0, "ci_lo": 0.0, "ci_hi": 0.0}
    m = sum(vals) / n
    if n > 1:
        var = sum((v - m) ** 2 for v in vals) / (n - 1)
        half = 1.96 * math.sqrt(var / n)
    else:
        half = 0.0
    return {"label": label, "n": n, "mean": m,
            "ci_lo": max(0.0, m - half), "ci_hi": min(1.0, m + half)}


def guard_report(stem: str, options: list[str], gold_index: int,
                 context: str = "") -> dict:
    """Run the three shortcut heuristics against one multiple choice item.

    stem is the question without the option block, options are the option
    texts in label order, context is anything else the model can see.

    prompt_only     the gold option's text occurs verbatim in the stem and
                    no other option's does, so echoing the stem wins.
    most_frequent   the gold option's text is the strict most frequent
                    option text across stem and context.
    keyword_nearest the gold option shares strictly more of the stem's
                    words than any other option.

    Returns which heuristics solve the item and the index each one picks.
    """
    haystack = (stem + "\n" + context).lower()
    norm = [normalize(o) for o in options]

    present = [i for i, o in enumerate(norm)
               if o and re.search(rf"(?<![\w]){re.escape(o)}(?![\w])", stem.lower())]
    prompt_only = present == [gold_index]

    counts = [haystack.count(o) if o else 0 for o in norm]
    best = max(counts) if counts else 0
    freq_winners = [i for i, c in enumerate(counts) if c == best]
    most_frequent = freq_winners == [gold_index] and best > 0

    scores = [overlap(o, stem) for o in options]
    top = max(scores) if scores else 0.0
    kw_winners = [i for i, s in enumerate(scores) if s >= top - 1e-9]
    keyword_nearest = kw_winners == [gold_index] and top > 0.0

    return {
        "prompt_only": prompt_only,
        "most_frequent": most_frequent,
        "keyword_nearest": keyword_nearest,
        "any": bool(prompt_only or most_frequent or keyword_nearest),
        "keyword_pick": kw_winners[0] if kw_winners else None,
        "frequent_pick": freq_winners[0] if freq_winners else None,
    }


def guard_ok(stem: str, options: list[str], gold_index: int,
             context: str = "") -> bool:
    """True when no shortcut heuristic solves the item."""
    return not guard_report(stem, options, gold_index, context)["any"]
