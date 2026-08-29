"""The built in frame bank: sentence shape varied, not just vocabulary.

A renderer sharing no content word with the trained idiom scored 0.840 on the
single document chain task; one keeping every content word and changing only
the sentence frame scored 0.030 (`src/disc/TEMPLATE.md`). Swapping nouns costs
0.13 and swapping the sentence shape costs 0.94, so a frame bank that only
changes nouns would fix nothing.

A frame here is a point in a product of shape choices, crossed with a lexicon:

    statement_mode   how a rule line is written: a conditional, a mapping, a
                     table row, an imperative, a passive declarative, or a
                     relative clause
    key_position     whether the key precedes the value or follows it, in the
                     rule line and in the table header
    question_form    a wh question, an imperative, a cloze, or an inverted
                     noun phrase
    scope_position   whether the scope is named before the item or after it
    lexicon          the content words, which is the cheap axis and is varied
                     as well so the two are not confounded

Every frame renders the same `src/corpus/relations.py` records, so the gold
answer for a seed does not depend on which frame drew it. `parity` in the
builder holds token length approximately constant across frames by choosing
among preamble variants of different lengths.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass

SENTINEL = "SLOT"

# ------------------------------------------------------------------ lexicons

LEXICONS = {
    "routing": dict(system="referral system", container="office",
                    item="request", target="desk", vact="handles",
                    vpass="is handled by", attrnoun="reading",
                    spec="specimen", treatment="treatment", rel="referral",
                    verbing="routing", classword="classification"),
    "assembly": dict(system="assembly", container="stage", item="item",
                     target="unit", vact="processes", vpass="is processed by",
                     attrnoun="grade", spec="part", treatment="finish",
                     rel="transfer", verbing="processing",
                     classword="grading"),
    "transit": dict(system="network", container="junction", item="parcel",
                    target="lane", vact="carries", vpass="is carried by",
                    attrnoun="weight", spec="load", treatment="tariff",
                    rel="leg", verbing="dispatch", classword="banding"),
    "ledger": dict(system="registry", container="bureau", item="filing",
                   target="ledger", vact="records", vpass="is recorded in",
                   attrnoun="index", spec="entry", treatment="charge",
                   rel="posting", verbing="recording", classword="grading"),
    "signal": dict(system="notation", container="node", item="signal",
                   target="channel", vact="passes", vpass="is passed to",
                   attrnoun="level", spec="trace", treatment="gain",
                   rel="hop", verbing="switching", classword="banding"),
    "clinic": dict(system="protocol", container="ward", item="case",
                   target="team", vact="reviews", vpass="is reviewed by",
                   attrnoun="score", spec="sample", treatment="course",
                   rel="referral", verbing="triage", classword="grading"),
    "depot": dict(system="chain", container="depot", item="crate",
                  target="bay", vact="stores", vpass="is stored in",
                  attrnoun="count", spec="batch", treatment="handling",
                  rel="move", verbing="storage", classword="sorting"),
    "abstract": dict(system="notation", container="map", item="token",
                     target="value", vact="receives", vpass="is sent to",
                     attrnoun="measure", spec="element", treatment="image",
                     rel="application", verbing="sending",
                     classword="partition"),
}

MODES = ("passive_decl", "conditional", "mapping", "table_row", "imperative",
         "relative_clause")
KEY_POSITIONS = ("key_first", "value_first")
QUESTION_FORMS = ("wh", "imperative", "cloze", "inverted")
SCOPE_POSITIONS = ("scope_first", "scope_last")


# --------------------------------------------------------------- fact lines

ASSOC = {
    ("passive_decl", "key_first"):
        "A {k} {item} {vpass} the {v} {target}.",
    ("passive_decl", "value_first"):
        "The {v} {target} is what {vact} a {k} {item}.",
    ("conditional", "key_first"):
        "If an incoming {item} is {k}, then the {v} {target} takes it.",
    ("conditional", "value_first"):
        "The {v} {target} takes an incoming {item} if that {item} is {k}.",
    ("mapping", "key_first"):
        "{k} maps to {v}.",
    ("mapping", "value_first"):
        "{v} is the image of {k}.",
    ("table_row", "key_first"):
        "{k}    {v}",
    ("table_row", "value_first"):
        "{v}    {k}",
    ("imperative", "key_first"):
        "Send every {k} {item} to the {v} {target}.",
    ("imperative", "value_first"):
        "To the {v} {target}, send every {k} {item}.",
    ("relative_clause", "key_first"):
        "The {target} that {vact} a {k} {item} is the {v} {target}.",
    ("relative_clause", "value_first"):
        "The {v} {target} is the one that {vact} a {k} {item}.",
}

ASSOC2 = {
    "passive_decl": "A {k} {item} at the {kb} {container} {vpass} the {v} {target}.",
    "conditional": "If an incoming {item} is {k} and stands at the {kb} {container}, the {v} {target} takes it.",
    "mapping": "{k} with {kb} maps to {v}.",
    "table_row": "{k}    {kb}    {v}",
    "imperative": "Send every {k} {item} at the {kb} {container} to the {v} {target}.",
    "relative_clause": "The {target} that {vact} a {k} {item} at the {kb} {container} is the {v} {target}.",
}

BAND = {
    "passive_decl": "A {spec} whose {attr} {attrnoun} is {range} {vpass2} {v}.",
    "conditional": "If the {attr} {attrnoun} of a {spec} is {range}, then that {spec} is {v}.",
    "mapping": "{range_short} maps to {v}.",
    "table_row": "{range_short}    {v}",
    "imperative": "Call a {spec} {v} when its {attr} {attrnoun} is {range}.",
    "relative_clause": "The name for a {spec} whose {attr} {attrnoun} is {range} is {v}.",
}

DEFAULT = {
    "passive_decl": "Any {item} whose type is not listed {vpass} the {v} {target}.",
    "conditional": "If the type of an incoming {item} is not listed, the {v} {target} takes it.",
    "mapping": "Anything unlisted maps to {v}.",
    "table_row": "unlisted    {v}",
    "imperative": "Send any unlisted {item} to the {v} {target}.",
    "relative_clause": "The {target} that {vact} an unlisted {item} is the {v} {target}.",
}

GENERAL = {
    "passive_decl": "Every {item} is given the {v} {treatment}.",
    "conditional": "If any {item} arrives, then it is given the {v} {treatment}.",
    "mapping": "Everything maps to {v}.",
    "table_row": "every {item}    {v}",
    "imperative": "Give every {item} the {v} {treatment}.",
    "relative_clause": "The {treatment} that every {item} is given is the {v} {treatment}.",
}

EXCEPT = {
    "passive_decl": "There is one exception. Any {item} whose category is {k} is given the {v} {treatment} instead.",
    "conditional": "There is one exception. If the category of any {item} is {k}, then it is given the {v} {treatment} instead.",
    "mapping": "One exception. {k} maps to {v} instead.",
    "table_row": "exception: {k}    {v}",
    "imperative": "There is one exception. Give any {item} of category {k} the {v} {treatment} instead.",
    "relative_clause": "The one exception is that the {treatment} any {item} of category {k} is given is the {v} {treatment}.",
}

WEIGHT = {
    "passive_decl": "A {k} {item} carries a {attrnoun} of {v}.",
    "conditional": "If any {item} is {k}, then its {attrnoun} is {v}.",
    "mapping": "{k} has {attrnoun} {v}.",
    "table_row": "{k}    {v}",
    "imperative": "Record a {attrnoun} of {v} for every {k} {item}.",
    "relative_clause": "The {attrnoun} that a {k} {item} carries is {v}.",
}

STEP = {
    "passive_decl": "On one pass the {attrnoun} is multiplied by {a}, then {b} is added, then the remainder on division by {m} is taken.",
    "conditional": "If a pass is taken, then the {attrnoun} becomes {a} times itself plus {b}, reduced by the remainder on division by {m}.",
    "mapping": "one pass: x maps to ({a} x plus {b}) mod {m}.",
    "table_row": "pass    {a} x plus {b} mod {m}",
    "imperative": "On each pass multiply the {attrnoun} by {a}, add {b}, then take the remainder on division by {m}.",
    "relative_clause": "The {attrnoun} that one pass produces is {a} times the old {attrnoun} plus {b}, reduced by the remainder on division by {m}.",
}

# ---------------------------------------------------------------- questions

Q_LOOKUP = {
    "wh": ("A {k} {item} arrives at the {scope} {container}. "
           "Which {target} {vact} it?"),
    "imperative": ("Name the {target} that {vact} a {k} {item} at the "
                   "{scope} {container}."),
    "cloze": ("At the {scope} {container}, a {k} {item} {vpass} the ____ "
              "{target}. Give the missing word."),
    "inverted": "For a {k} {item} at the {scope} {container}: which {target}?",
}

Q_LOOKUP_LAST = {
    "wh": ("A {k} {item} arrives. Which {target} {vact} it at the "
           "{scope} {container}?"),
    "imperative": ("Name the {target} that {vact} a {k} {item}, taking the "
                   "{scope} {container}."),
    "cloze": ("A {k} {item} {vpass} the ____ {target} at the {scope} "
              "{container}. Give the missing word."),
    "inverted": "For a {k} {item}, at the {scope} {container}: which {target}?",
}

Q_GENERAL = {
    "wh": ("A {item} of category {k} reaches the {scope} {system}. "
           "Which {treatment} does it receive?"),
    "imperative": ("Name the {treatment} any {item} of category {k} receives at "
                   "the {scope} {system}."),
    "cloze": ("At the {scope} {system}, any {item} of category {k} is given the "
              "____ {treatment}. Give the missing word."),
    "inverted": ("For any {item} of category {k} at the {scope} {system}: "
                 "which {treatment}?"),
}

Q_INVERSE = {
    "wh": ("At the {scope} {container}, which {item} type does the {k} "
           "{target} {vact}?"),
    "imperative": ("Name the {item} type that the {k} {target} {vact} at the "
                   "{scope} {container}."),
    "cloze": ("At the {scope} {container}, a ____ {item} {vpass} the {k} "
              "{target}. Give the missing word."),
    "inverted": "For the {k} {target} at the {scope} {container}: which {item} type?",
}

Q_CLASSIFY = {
    "wh": ("A {spec} has a {attr} {attrnoun} of {k}. In the {scope} "
           "{classword}, what is it called?"),
    "imperative": ("Name what a {spec} with a {attr} {attrnoun} of {k} is "
                   "called in the {scope} {classword}."),
    "cloze": ("In the {scope} {classword}, a {spec} with a {attr} {attrnoun} "
              "of {k} is called ____. Give the missing word."),
    "inverted": ("For a {spec} with a {attr} {attrnoun} of {k}, in the {scope} "
                 "{classword}: what is it called?"),
}

Q_COMPOSE = {
    "wh": ("A {k} {item} arrives at the {first} {container}.{hops} "
           "Which {target} {vact} it at the {last} {container}?"),
    "imperative": ("Take a {k} {item} through the {first} {container}{hops2}. "
                   "Name the {target} it reaches."),
    "cloze": ("A {k} {item} passes through the {first} {container}{hops2} and "
              "{vpass} the ____ {target}. Give the missing word."),
    "inverted": ("For a {k} {item} sent through the {first} {container}{hops2}: "
                 "which {target}?"),
}

Q_ITERATE = {
    "wh": ("Start from {k} and apply the {scope} {rel} {n} times. "
           "Which {item} results?"),
    "imperative": ("Apply the {scope} {rel} {n} times to {k}. Name the {item} "
                   "that results."),
    "cloze": ("Applying the {scope} {rel} {n} times to {k} gives ____. "
              "Give the missing word."),
    "inverted": "For {k} after {n} applications of the {scope} {rel}: which {item}?",
}

Q_PAIR = {
    "wh": ("A {k} {item} stands at the {kb} {container} in the {scope} "
           "{system}. Which {target} {vact} it?"),
    "imperative": ("Name the {target} that {vact} a {k} {item} at the {kb} "
                   "{container} in the {scope} {system}."),
    "cloze": ("In the {scope} {system}, a {k} {item} at the {kb} {container} "
              "{vpass} the ____ {target}. Give the missing word."),
    "inverted": ("For a {k} {item} at the {kb} {container} in the {scope} "
                 "{system}: which {target}?"),
}

Q_PRIORITY = {
    "wh": ("A given {item} belongs to {k}. At the {scope} {container}, which "
           "{target} {vact} it?"),
    "imperative": ("A given {item} belongs to {k}. Name the {target} that {vact} it "
                   "at the {scope} {container}."),
    "cloze": ("Any {item} belonging to {k} {vpass} the ____ {target} at the "
              "{scope} {container}. Give the missing word."),
    "inverted": ("For any {item} belonging to {k} at the {scope} {container}: "
                 "which {target}?"),
}

Q_EXCLUSION = {
    "wh": ("Of the {item} types listed for the {scope} {container}, which one "
           "does the {k} {target} not {vact}?"),
    "imperative": ("Name the listed {item} type at the {scope} {container} "
                   "that the {k} {target} does not {vact}."),
    "cloze": ("At the {scope} {container} the {k} {target} {vact} every listed "
              "{item} type except ____. Give the missing word."),
    "inverted": ("For the {scope} {container}: which listed {item} type does "
                 "the {k} {target} not {vact}?"),
}

Q_LOOKUP_THEN_BAND = {
    "wh": ("A {k} {item} is submitted to the {first} {container}. In the "
           "{last} {classword}, what is it called?"),
    "imperative": ("Submit a {k} {item} to the {first} {container} and name "
                   "what the {last} {classword} calls it."),
    "cloze": ("A {k} {item} submitted to the {first} {container} is called "
              "____ in the {last} {classword}. Give the missing word."),
    "inverted": ("For a {k} {item} at the {first} {container}, in the {last} "
                 "{classword}: what is it called?"),
}

Q_BAND_THEN_LOOKUP = {
    "wh": ("A {spec} has a {attr} {attrnoun} of {k}. It is classified in the "
           "{first} {classword} and then sent through the {last} {container}. "
           "Which {target} {vact} it?"),
    "imperative": ("Classify a {spec} with a {attr} {attrnoun} of {k} in the "
                   "{first} {classword}, send it through the {last} "
                   "{container}, and name the {target}."),
    "cloze": ("A {spec} with a {attr} {attrnoun} of {k}, classified in the "
              "{first} {classword}, {vpass} the ____ {target} at the {last} "
              "{container}. Give the missing word."),
    "inverted": ("For a {spec} with a {attr} {attrnoun} of {k} through the "
                 "{first} {classword} and the {last} {container}: which "
                 "{target}?"),
}

Q_SUM_CHAIN = {
    "wh": ("A {k} {item} passes through the {first} {container}{hops2}. "
           "What total {attrnoun} does it accumulate?"),
    "imperative": ("Take a {k} {item} through the {first} {container}{hops2} "
                   "and give the total {attrnoun} accumulated."),
    "cloze": ("A {k} {item} through the {first} {container}{hops2} accumulates "
              "a total {attrnoun} of ____. Give the missing number."),
    "inverted": ("For a {k} {item} through the {first} {container}{hops2}: "
                 "what total {attrnoun}?"),
}

Q_APPLY_N = {
    "wh": ("The {attrnoun} starts at {k}. Apply the {scope} pass {n} times. "
           "What is the {attrnoun} then?"),
    "imperative": ("Apply the {scope} pass {n} times to a starting {attrnoun} "
                   "of {k} and give the result."),
    "cloze": ("Starting from a {attrnoun} of {k}, {n} passes of the {scope} "
              "rule give ____. Give the missing number."),
    "inverted": "For a starting {attrnoun} of {k} after {n} {scope} passes: what value?",
}

Q_PRECEDENCE = {
    "wh": ("A {k} {item} is listed at both the {first} {container} and the "
           "{last} {container}. Which {target} {vact} it?"),
    "imperative": ("A {k} {item} is listed at the {first} and the {last} "
                   "{container}. Name the {target} that {vact} it."),
    "cloze": ("A {k} {item}, listed at both the {first} and the {last} "
              "{container}, {vpass} the ____ {target}. Give the missing word."),
    "inverted": ("For a {k} {item} listed at the {first} and the {last} "
                 "{container}: which {target}?"),
}

QUESTION_TABLES = {
    "lookup": (Q_LOOKUP, Q_LOOKUP_LAST),
    "lookup_general": (Q_GENERAL, Q_GENERAL),
    "inverse": (Q_INVERSE, Q_INVERSE),
    "classify": (Q_CLASSIFY, Q_CLASSIFY),
    "compose": (Q_COMPOSE, Q_COMPOSE),
    "invert_chain": (Q_INVERSE, Q_INVERSE),
    "iterate": (Q_ITERATE, Q_ITERATE),
    "pair": (Q_PAIR, Q_PAIR),
    "priority": (Q_PRIORITY, Q_PRIORITY),
    "exclusion": (Q_EXCLUSION, Q_EXCLUSION),
    "lookup_then_band": (Q_LOOKUP_THEN_BAND, Q_LOOKUP_THEN_BAND),
    "band_then_lookup": (Q_BAND_THEN_LOOKUP, Q_BAND_THEN_LOOKUP),
    "sum_chain": (Q_SUM_CHAIN, Q_SUM_CHAIN),
    "apply_n": (Q_APPLY_N, Q_APPLY_N),
    "precedence": (Q_PRECEDENCE, Q_PRECEDENCE),
}

# Page padding, one neutral sentence at a time.
#
# A table row frame states a rule in three words and a relative clause frame
# states the same rule in twelve, so without padding the two would differ in
# page length by half again and page length would be a rival explanation for
# any frame effect. The notes are shared by every frame, say nothing a question
# turns on, and are appended in order until the page reaches the corpus target,
# which gives the builder a knob with one sentence of granularity.
PREAMBLE_HEAD = "The {scope} {container}."

NOTES = [
    "This page states the {verbing} for the {scope} {container}.",
    ("Every {item} reaching it is dealt with by the {verbing} given below and "
     "by nothing else."),
    ("The list is complete, and a {target} is never inferred from the name of "
     "the {item} type."),
    ("Where a {item} could be read as belonging to more than one type, the "
     "type written on the {item} itself is the one that counts."),
    ("Nothing stated elsewhere adds to this page and nothing stated elsewhere "
     "overrides it."),
    ("A {target} that is not named here handles no {item} at all, whatever "
     "another page may suggest."),
    ("The {verbing} was fixed when the {scope} {container} was set up and has "
     "not changed since."),
    ("A {item} presented today is dealt with exactly as one presented on the "
     "first day would have been."),
    ("A {item} arriving without a legible type is set aside rather than "
     "guessed at."),
    ("No {target} acts on a {item} whose type is in doubt, and none infers a "
     "type from the {item} it arrived beside."),
    ("The record of every {item} dealt with here is kept by the {scope} "
     "{container} and can be consulted."),
    ("Questions about a {item} are settled by this page and by the record, in "
     "that order."),
]

MAX_NOTES = len(NOTES)

HEADERS = {
    "key_first": "{item} type    {target}",
    "value_first": "{target}    {item} type",
}


@dataclass(frozen=True)
class Frame:
    """One point in the shape product, crossed with a lexicon."""

    fid: str
    lexicon: str
    mode: str
    key_pos: str
    qform: str
    scope_pos: str

    # ------------------------------------------------------------- rendering

    @property
    def lx(self) -> dict:
        return LEXICONS[self.lexicon]

    def _fmt(self, tmpl: str, **kw) -> str:
        d = dict(self.lx)
        d.update(kw)
        return tmpl.format(**d)

    def _range(self, lo, hi) -> str:
        if lo is None:
            return f"less than {hi}"
        if hi is None:
            return f"{lo} or more"
        return f"{lo} or more but less than {hi}"

    def _range_short(self, lo, hi) -> str:
        if lo is None:
            return f"under {hi}"
        if hi is None:
            return f"{lo} and over"
        return f"{lo} to {hi}"

    def fact_line(self, f) -> str:
        m = self.mode
        if f.kind == "assoc":
            return self._fmt(ASSOC[(m, self.key_pos)], k=f.key, v=f.value)
        if f.kind == "assoc2":
            ka, kb = f.key
            return self._fmt(ASSOC2[m], k=ka, kb=kb, v=f.value)
        if f.kind == "band":
            return self._fmt(BAND[m], attr=f.attr, v=f.value,
                             vpass2="is called",
                             range=self._range(f.lo, f.hi),
                             range_short=self._range_short(f.lo, f.hi))
        if f.kind == "default":
            return self._fmt(DEFAULT[m], v=f.value)
        if f.kind == "general":
            return self._fmt(GENERAL[m], v=f.value)
        if f.kind == "except_":
            return self._fmt(EXCEPT[m], k=f.key, v=f.value)
        if f.kind == "weight":
            return self._fmt(WEIGHT[m], k=f.key, v=f.value)
        if f.kind == "step":
            _, a, b, mod = f.key
            return self._fmt(STEP[m], a=a, b=b, m=mod)
        raise ValueError(f.kind)

    def page(self, scope: str, facts, preamble_level: int = 1) -> str:
        n = max(0, min(preamble_level, MAX_NOTES))
        head = self._fmt(PREAMBLE_HEAD, scope=scope)
        if n:
            body = " ".join(self._fmt(t, scope=scope) for t in NOTES[:n])
            head = head + "\n\n" + body
        lines = [self.fact_line(f) for f in facts]
        if self.mode == "table_row" and any(
                f.kind in ("assoc", "weight", "default") for f in facts):
            lines = [self._fmt(HEADERS[self.key_pos])] + lines
        return head + "\n\n" + "\n".join(lines)

    def _hops(self, scopes) -> tuple:
        rest = scopes[1:]
        if not rest:
            return "", ""
        joined = ", then the ".join(rest)
        return (f" It is then referred to the {joined} {self.lx['container']}.",
                f", then the {joined} {self.lx['container']}")

    def question(self, q) -> str:
        first_tbl, last_tbl = QUESTION_TABLES[q.kind]
        tbl = first_tbl if self.scope_pos == "scope_first" else last_tbl
        tmpl = tbl[self.qform]
        hops, hops2 = self._hops(q.scopes)
        key = q.start
        if isinstance(key, tuple):
            key = ", ".join(key[:-1]) + f" and {key[-1]}"
        return self._fmt(
            tmpl, k=key, kb=q.key_b, scope=q.scopes[0], first=q.scopes[0],
            last=q.scopes[-1], hops=hops, hops2=hops2,
            attr=q.attr if q.attr is not None else self.lx["attrnoun"],
            n=q.meta.get("n_applications", len(q.plan)))

    def lookup_regex(self, key: str) -> str:
        """The regex a keyword shortcut reader uses to read one rule line.

        The shortcut baseline has to be as strong in this frame as it is in the
        trained one, or a frame would look safe only because the attack was
        written for a different wording.
        """
        line = self.fact_line_pattern()
        return line.replace("__K__", re.escape(key)).replace("__V__", r"(\w+)")

    def fact_line_pattern(self) -> str:
        d = dict(self.lx)
        d.update(k="__K__", v="__V__")
        raw = ASSOC[(self.mode, self.key_pos)].format(**d)
        parts = raw.split("__K__")
        parts = [re.escape(p) if "__V__" not in p else p for p in parts]
        out = "__K__".join(parts)
        segs = out.split("__V__")
        segs = [s if "__K__" in s or s.startswith("\\") or not s else re.escape(s)
                for s in segs]
        return "__V__".join(segs)

    # --------------------------------------------------------- reserved words

    def template_corpus(self) -> list:
        """The templates THIS frame can emit, filled with sentinels.

        Only this frame's statement mode, key position, question form and
        scope position appear, so the reserved set is the English this frame
        actually writes and not the union over the bank. Two frames sharing a
        lexicon but differing in mode reserve different words, which is the
        distinction the per frame vocabulary exists to make.
        """
        d = dict(self.lx)
        fill = dict(k=SENTINEL, v=SENTINEL, kb=SENTINEL, attr=SENTINEL,
                    scope=SENTINEL, first=SENTINEL, last=SENTINEL,
                    hops=SENTINEL, hops2=SENTINEL, n=SENTINEL, a=SENTINEL,
                    b=SENTINEL, m=SENTINEL, vpass2="is called",
                    range="0 or more but less than 0", range_short="0 to 0")
        d.update(fill)
        out = [ASSOC[(self.mode, self.key_pos)].format(**d)]
        for tbl in (ASSOC2, BAND, DEFAULT, GENERAL, EXCEPT, WEIGHT, STEP):
            out.append(tbl[self.mode].format(**d))
        for first_tbl, last_tbl in QUESTION_TABLES.values():
            tbl = first_tbl if self.scope_pos == "scope_first" else last_tbl
            out.append(tbl[self.qform].format(**d))
        out.append(PREAMBLE_HEAD.format(**d))
        for t in NOTES:
            out.append(t.format(**d))
        out.append(HEADERS[self.key_pos].format(**d))
        out.extend(sorted(set(self.lx.values())))
        # The hop clause is built in code rather than from a template.
        out.append(f"It is then referred to the {SENTINEL} {self.lx['container']}.")
        return out


def build_frames() -> list:
    """Every frame in the bank, named by its shape and lexicon."""
    frames = []
    for lex, mode, kp, qf, sp in itertools.product(
            sorted(LEXICONS), MODES, KEY_POSITIONS, QUESTION_FORMS,
            SCOPE_POSITIONS):
        fid = f"{lex}.{mode}.{kp}.{qf}.{sp}"
        frames.append(Frame(fid, lex, mode, kp, qf, sp))
    return frames


FRAMES = build_frames()
FRAMES_BY_ID = {f.fid: f for f in FRAMES}
