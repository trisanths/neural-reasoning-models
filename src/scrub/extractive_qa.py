"""Extractive question-answer pairs over a scrubbed passage.

Every question is built by string operations on the passage alone, so no
world knowledge enters the trace and every answer is verifiable by string
operations. Three question types:

  span_cloze       an informative span (a scrubbed entity run, a perturbed
                   number, or a determiner-anchored noun phrase) is cut out
                   of its sentence and replaced by a wh-phrase chosen by
                   span type; the answer is the span verbatim.
  sentence_select  "Which sentence mentions X?" with the full sentence as
                   the answer.
  existence        "Does the passage mention X?" answered yes for a present
                   span and no for a generated absent name.

The type mix is configurable and defaults to 70/15/15. Question type order
follows the same deficit rule as the renderer source mixes, so the realized
mix tracks the target deterministically. Candidate spans are required to
occur exactly once in the passage, which makes cloze reconstruction and
sentence selection unambiguous.

check_qa re-derives every answer from the passage with substring operations
only. generate_qa runs it on every pair before returning, and the tests run
it again on rendered-and-decoded traces.

Wh-phrase by span type: a multi-word entity asks who, a single-word entity
after a location preposition asks where and otherwise what, a year-like
number asks when, any other number asks how many, a noun phrase asks what.

render_qa_trace lays the pair list out with the same special tokens as
worldgen episodes: <|world|> with a domain marker line, <|doc|> with the
passage, then <|q|> question <|a|> answer <|eot|> per pair, so the C-style
elicitation format applies unchanged.
"""

import re
from bisect import bisect_right

import numpy as np

from src.scrub.scrubber import (FUNCTION_WORDS, entity_runs, number_literals,
                                _YEAR_RANGE)
from src.worldgen.names import make_word

DEFAULT_TYPE_MIX = {
    "span_cloze": 0.70,
    "sentence_select": 0.15,
    "existence": 0.15,
}

QA_DOMAIN = "extractive_qa"

_SENT_END_RE = re.compile(r"[.!?](?=\s|$)")
_TERMINALS = (".", "!", "?", "")

# Noun phrase heuristic: a lowercase determiner anchors the phrase, which
# rules out sentence-initial position by capitalization, followed by one to
# three lowercase words. The last word carries the phrase, so it must not be
# a function word.
_NP_RE = re.compile(r"\b(?:the|a|an)\s((?:[a-z]+ ){0,2}[a-z]{4,})\b")

_LOC_PREP_RE = re.compile(r"(?:\b(?:in|at|near|from|to)\s+)\Z")


def split_sentences(text: str) -> list:
    """(start, end) spans of sentences, terminal punctuation included and
    surrounding whitespace excluded."""
    spans = []

    def add(seg_start: int, seg_end: int) -> None:
        seg = text[seg_start:seg_end]
        stripped = seg.strip()
        if stripped:
            s = seg_start + (len(seg) - len(seg.lstrip()))
            spans.append((s, s + len(stripped)))

    pos = 0
    for m in _SENT_END_RE.finditer(text):
        add(pos, m.end())
        pos = m.end()
    add(pos, len(text))
    return spans


def _wh_for_span(text: str, start: int, end: int, kind: str) -> str:
    surface = text[start:end]
    if kind == "entity":
        if " " in surface:
            return "who"
        if _LOC_PREP_RE.search(text[max(0, start - 8):start]):
            return "where"
        return "what"
    if kind == "number":
        digits = surface.replace(",", "")
        if (len(digits) == 4 and "." not in digits
                and _YEAR_RANGE[0] <= int(digits) <= _YEAR_RANGE[1]):
            return "when"
        return "how many"
    return "what"


def find_spans(text: str) -> list:
    """Candidate answer spans of a scrubbed passage, in passage order.

    Each entry is a dict with start, end, text, kind, wh. Kinds are entity,
    number, and noun_phrase; overlapping noun phrases lose to entity and
    number spans."""
    spans = []
    taken = []
    for kind, pairs in (("entity", entity_runs(text)),
                        ("number", number_literals(text))):
        for s, e in pairs:
            spans.append({"start": s, "end": e, "text": text[s:e],
                          "kind": kind,
                          "wh": _wh_for_span(text, s, e, kind)})
            taken.append((s, e))
    for m in _NP_RE.finditer(text):
        s, e = m.start(1), m.end(1)
        words = m.group(1).split()
        if words[-1] in FUNCTION_WORDS:
            continue
        if any(s < te and ts < e for ts, te in taken):
            continue
        spans.append({"start": s, "end": e, "text": text[s:e],
                      "kind": "noun_phrase", "wh": "what"})
    spans.sort(key=lambda d: (d["start"], d["end"]))
    return spans


def _sentence_of(sents: list, span: dict):
    """Index of the sentence fully containing the span, or None."""
    starts = [s for s, _ in sents]
    i = bisect_right(starts, span["start"]) - 1
    if i < 0:
        return None
    s, e = sents[i]
    if span["start"] >= s and span["end"] <= e:
        return i
    return None


def _make_cloze(text: str, sents: list, span: dict):
    i = _sentence_of(sents, span)
    if i is None:
        return None
    s, e = sents[i]
    sent = text[s:e]
    rel = span["start"] - s
    wh = span["wh"]
    if rel == 0:
        wh = wh[0].upper() + wh[1:]
    body = sent[:rel] + wh + sent[rel + len(span["text"]):]
    if body and body[-1] in ".!?":
        body = body[:-1]
    return {
        "type": "span_cloze",
        "question": body + "?",
        "answer": span["text"],
        "wh": wh,
        "wh_pos": rel,
    }


def _make_sentence_select(text: str, sents: list, span: dict):
    i = _sentence_of(sents, span)
    if i is None:
        return None
    s, e = sents[i]
    return {
        "type": "sentence_select",
        "question": f'Which sentence mentions "{span["text"]}"?',
        "answer": text[s:e],
        "subject": span["text"],
    }


def _make_existence(subject: str, present: bool):
    return {
        "type": "existence",
        "question": f'Does the passage mention "{subject}"?',
        "answer": "yes" if present else "no",
        "subject": subject,
    }


def _absent_name(text: str, rng) -> str | None:
    lower = text.lower()
    for _ in range(20):
        word = make_word(rng)
        if word.lower() not in lower:
            return word
    return None


def check_qa(passage: str, qa: dict) -> bool:
    """Verify one pair against the passage with string operations only."""
    kind = qa.get("type")
    if kind == "span_cloze":
        answer = qa["answer"]
        if answer not in passage:
            return False
        q, wh, pos = qa["question"], qa["wh"], qa["wh_pos"]
        if q[pos:pos + len(wh)] != wh or not q.endswith("?"):
            return False
        base = q[:pos] + answer + q[pos + len(wh):-1]
        return any(base + t in passage for t in _TERMINALS)
    if kind == "sentence_select":
        return (qa["answer"] in passage
                and qa["subject"] in qa["answer"]
                and qa["subject"] in qa["question"])
    if kind == "existence":
        present = qa["subject"] in passage
        return (qa["answer"] == ("yes" if present else "no")
                and qa["subject"] in qa["question"])
    return False


def generate_qa(scrubbed_text: str, seed, n: int,
                mix: dict | None = None) -> list:
    """Generate up to n verified pairs over one scrubbed passage.

    Deterministic in (scrubbed_text, seed, n, mix); seed is an int or a
    tuple of ints. When a type runs out of candidate spans it falls through
    to the next viable type, ending at existence questions over generated
    absent names, so a nonempty passage almost always yields exactly n
    pairs."""
    if mix is None:
        mix = DEFAULT_TYPE_MIX
    if not scrubbed_text.strip() or n <= 0:
        return []
    weights = {k: float(v) for k, v in mix.items() if float(v) > 0}
    if not weights or any(v < 0 for v in mix.values()):
        raise ValueError(f"bad type mix {mix}")
    unknown = set(weights) - set(DEFAULT_TYPE_MIX)
    if unknown:
        raise ValueError(f"unknown question types {sorted(unknown)}")
    total = sum(weights.values())
    weights = {k: v / total for k, v in weights.items()}

    rng = np.random.default_rng(
        tuple(int(s) for s in seed) if isinstance(seed, (tuple, list))
        else int(seed))
    sents = split_sentences(scrubbed_text)
    unique = [sp for sp in find_spans(scrubbed_text)
              if scrubbed_text.count(sp["text"]) == 1]
    order = list(rng.permutation(len(unique)))
    pools = {
        "span_cloze": [unique[i] for i in order],
        "sentence_select": [unique[i] for i in reversed(order)],
        "existence": [unique[i] for i in order],
    }

    def take(kind: str):
        if kind == "existence":
            pool = pools[kind]
            if pool and rng.random() < 0.5:
                return _make_existence(pool.pop(0)["text"], present=True)
            subject = _absent_name(scrubbed_text, rng)
            if subject is None:
                return None
            return _make_existence(subject, present=False)
        makers = {"span_cloze": _make_cloze,
                  "sentence_select": _make_sentence_select}
        pool = pools[kind]
        while pool:
            span = pool.pop(0)
            qa = makers[kind](scrubbed_text, sents, span)
            if qa is not None and check_qa(scrubbed_text, qa):
                return qa
        return None

    fallback = ["span_cloze", "sentence_select", "existence"]
    counts = {k: 0 for k in weights}
    out = []
    while len(out) < n:
        first = min(weights, key=lambda k: (counts[k] / weights[k], k))
        qa = None
        for kind in [first] + [k for k in fallback if k != first]:
            qa = take(kind)
            if qa is not None:
                break
        if qa is None or not check_qa(scrubbed_text, qa):
            break
        if qa["type"] in counts:
            counts[qa["type"]] += 1
        else:
            counts[first] += 1
        out.append(qa)
    return out


def render_qa_trace(passage: str, qas: list, tokenizer,
                    domain: str = QA_DOMAIN) -> list:
    """Token stream for one QA trace, in the worldgen episode layout:
    <|world|> domain marker, <|doc|> passage, then per pair <|q|> question
    <|a|> answer <|eot|>."""
    sid = tokenizer.special_ids
    tokens = [sid["<|world|>"]]
    tokens.extend(tokenizer.encode(f"domain: {domain}"))
    tokens.append(sid["<|doc|>"])
    tokens.extend(tokenizer.encode(passage))
    for qa in qas:
        tokens.append(sid["<|q|>"])
        tokens.extend(tokenizer.encode(qa["question"]))
        tokens.append(sid["<|a|>"])
        tokens.extend(tokenizer.encode(qa["answer"]))
        tokens.append(sid["<|eot|>"])
    return tokens
