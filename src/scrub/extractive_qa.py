"""Extractive question-answer pairs over a scrubbed passage.

Every question is built by string operations on the passage alone, so no
world knowledge enters the trace and every answer is verifiable by string
operations. Four trace item types:

  span_cloze       an informative span (a scrubbed entity run, a perturbed
                   number, or a determiner-anchored noun phrase) is cut out
                   of its sentence and replaced by a wh-phrase chosen by
                   span type; the answer is the span verbatim.
  sentence_select  "Which sentence mentions X?" with the full sentence as
                   the answer.
  existence        "Does the passage mention X?" answered yes for a present
                   span and no for a generated absent name.
  recap            a mechanical restatement of the sentence holding a
                   targeted span, plus an echo sentence repeating the span
                   ("The passage states that X did Y. The figure given is
                   N."), built by string operations alone. Recap items are
                   rendered directly after the document with no question
                   tokens, so plain next-token prediction on the recap
                   trains forward copying of specifics.

The type mix is configurable and defaults to 70/15/15 over the first three
types (regime E). E2_TYPE_MIX is 60/15/10/15 with recap. Question type
order follows the same deficit rule as the renderer source mixes, so the
realized mix tracks the target deterministically; passing a state dict
carries the deficit counters across passages so the aggregate mix over a
whole render tracks the target even at small per-passage counts. Candidate
spans are required to occur exactly once in the passage, which makes cloze
reconstruction and sentence selection unambiguous.

Span cloze selection is biased toward the specific span kinds a reader
model fabricates: entity runs and number literals (perturbed years
included). The bias holds cloze picks at CLOZE_SPECIFIC_SHARE specific at
every prefix while supply lasts, and recap items draw specific spans
first, so over a full render well over 60 percent of generated items
target a number or a name.

check_qa re-derives every answer from the passage with substring operations
only. generate_qa runs it on every item before returning, and the tests run
it again on rendered-and-decoded traces.

Wh-phrase by span type: a multi-word entity asks who, a single-word entity
after a location preposition asks where and otherwise what, a year-like
number asks when, any other number asks how many, a noun phrase asks what.

render_qa_trace lays the item list out with the same special tokens as
worldgen episodes: <|world|> with a domain marker line, <|doc|> with the
passage, then recap items as plain continuation text closed by <|eot|>,
then <|q|> question <|a|> answer <|eot|> per pair, so the C-style
elicitation format applies unchanged and the recap region carries no
question tokens.
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

E2_TYPE_MIX = {
    "span_cloze": 0.60,
    "sentence_select": 0.15,
    "existence": 0.10,
    "recap": 0.15,
}

QUESTION_TYPES = ("span_cloze", "sentence_select", "existence", "recap")

# Span kinds that carry a specific: entity runs and number literals
# (perturbed years included). These are the spans a reader model fabricates.
SPECIFIC_KINDS = ("entity", "number")

# Floor on the specific share of span cloze picks, held at every prefix.
# The task floor is 0.60 over generated questions; 0.75 inside the cloze
# share keeps the aggregate above 0.60 even when the other question types
# happen to draw noun phrases.
CLOZE_SPECIFIC_SHARE = 0.75

RECAP_LEAD = "The passage states that "
_RECAP_ECHO = {
    "number": "The figure given is ",
    "entity": "The name given is ",
    "noun_phrase": "The item given is ",
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
        "span_kind": span["kind"],
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
        "span_kind": span["kind"],
    }


def _make_existence(subject: str, present: bool, kind: str):
    return {
        "type": "existence",
        "question": f'Does the passage mention "{subject}"?',
        "answer": "yes" if present else "no",
        "subject": subject,
        "span_kind": kind,
    }


def _make_recap(text: str, sents: list, span: dict, protected: list):
    """One recap item: the span's sentence restated behind RECAP_LEAD plus
    an echo sentence repeating the span, all by string operations. The
    sentence's first character is lowered only when no candidate span
    covers it, so every span surface stays verbatim."""
    i = _sentence_of(sents, span)
    if i is None:
        return None
    s, e = sents[i]
    sent = text[s:e]
    core = sent[:-1] if sent and sent[-1] in ".!?" else sent
    if (core and core[0].isupper() and core[1:2].islower()
            and not any(ps <= s < pe for ps, pe in protected)):
        core = core[0].lower() + core[1:]
    echo = _RECAP_ECHO[span["kind"]]
    return {
        "type": "recap",
        "text": f"{RECAP_LEAD}{core}. {echo}{span['text']}.",
        "answer": span["text"],
        "sentence": sent,
        "span_kind": span["kind"],
    }


def _absent_name(text: str, rng) -> str | None:
    lower = text.lower()
    for _ in range(20):
        word = make_word(rng)
        if word.lower() not in lower:
            return word
    return None


def check_qa(passage: str, qa: dict) -> bool:
    """Verify one item against the passage with string operations only."""
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
    if kind == "recap":
        return (qa["answer"] in passage
                and qa["sentence"] in passage
                and qa["answer"] in qa["sentence"]
                and qa["answer"] in qa["text"]
                and qa["text"].startswith(RECAP_LEAD)
                and qa["text"].endswith(qa["answer"] + "."))
    return False


def generate_qa(scrubbed_text: str, seed, n: int,
                mix: dict | None = None, state: dict | None = None) -> list:
    """Generate up to n verified items over one scrubbed passage.

    Deterministic in (scrubbed_text, seed, n, mix, state); seed is an int
    or a tuple of ints. When a type runs out of candidate spans it falls
    through to the next viable type, ending at existence questions over
    generated absent names, so a nonempty passage almost always yields
    exactly n items. A caller-held state dict carries the type and cloze
    deficit counters across passages, so a stream of small per-passage
    batches still tracks the target mix in aggregate."""
    if mix is None:
        mix = DEFAULT_TYPE_MIX
    if not scrubbed_text.strip() or n <= 0:
        return []
    weights = {k: float(v) for k, v in mix.items() if float(v) > 0}
    if not weights or any(v < 0 for v in mix.values()):
        raise ValueError(f"bad type mix {mix}")
    unknown = set(weights) - set(QUESTION_TYPES)
    if unknown:
        raise ValueError(f"unknown question types {sorted(unknown)}")
    total = sum(weights.values())
    weights = {k: v / total for k, v in weights.items()}

    if state is None:
        state = {}
    counts = state.setdefault("types", {})
    for k in weights:
        counts.setdefault(k, 0)
    cloze_counts = state.setdefault("cloze", {"specific": 0, "other": 0})

    rng = np.random.default_rng(
        tuple(int(s) for s in seed) if isinstance(seed, (tuple, list))
        else int(seed))
    sents = split_sentences(scrubbed_text)
    all_spans = find_spans(scrubbed_text)
    protected = [(sp["start"], sp["end"]) for sp in all_spans]
    unique = [sp for sp in all_spans
              if scrubbed_text.count(sp["text"]) == 1]
    order = list(rng.permutation(len(unique)))
    shuffled = [unique[i] for i in order]
    specific = [sp for sp in shuffled if sp["kind"] in SPECIFIC_KINDS]
    other = [sp for sp in shuffled if sp["kind"] not in SPECIFIC_KINDS]
    pools = {
        "span_cloze": {"specific": list(specific), "other": list(other)},
        "recap": specific + other,
        "sentence_select": [unique[i] for i in reversed(order)],
        "existence": [unique[i] for i in order],
    }

    def take_cloze():
        sub = pools["span_cloze"]
        while sub["specific"] or sub["other"]:
            done = cloze_counts["specific"] + cloze_counts["other"]
            enough = (cloze_counts["specific"]
                      >= CLOZE_SPECIFIC_SHARE * (done + 1))
            pick = "other" if enough else "specific"
            if not sub[pick]:
                pick = "other" if pick == "specific" else "specific"
            span = sub[pick].pop(0)
            qa = _make_cloze(scrubbed_text, sents, span)
            if qa is not None and check_qa(scrubbed_text, qa):
                kind = ("specific" if span["kind"] in SPECIFIC_KINDS
                        else "other")
                cloze_counts[kind] += 1
                return qa
        return None

    def take(kind: str):
        if kind == "span_cloze":
            return take_cloze()
        if kind == "existence":
            pool = pools[kind]
            if pool and rng.random() < 0.5:
                span = pool.pop(0)
                return _make_existence(span["text"], True, span["kind"])
            subject = _absent_name(scrubbed_text, rng)
            if subject is None:
                return None
            return _make_existence(subject, False, "absent")
        makers = {"sentence_select": _make_sentence_select,
                  "recap": _make_recap}
        pool = pools[kind]
        while pool:
            span = pool.pop(0)
            if kind == "recap":
                qa = _make_recap(scrubbed_text, sents, span, protected)
            else:
                qa = makers[kind](scrubbed_text, sents, span)
            if qa is not None and check_qa(scrubbed_text, qa):
                return qa
        return None

    fallback = ["span_cloze", "sentence_select", "existence"]
    if "recap" in weights:
        fallback.insert(1, "recap")
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
    <|world|> domain marker, <|doc|> passage, recap items (when present) as
    plain continuation lines closed by one <|eot|>, then per pair <|q|>
    question <|a|> answer <|eot|>. The recap region carries no question
    tokens."""
    sid = tokenizer.special_ids
    recaps = [qa for qa in qas if qa["type"] == "recap"]
    pairs = [qa for qa in qas if qa["type"] != "recap"]
    tokens = [sid["<|world|>"]]
    tokens.extend(tokenizer.encode(f"domain: {domain}"))
    tokens.append(sid["<|doc|>"])
    tokens.extend(tokenizer.encode(passage))
    if recaps:
        recap_text = "\n" + "\n".join(qa["text"] for qa in recaps)
        tokens.extend(tokenizer.encode(recap_text))
        tokens.append(sid["<|eot|>"])
    for qa in pairs:
        tokens.append(sid["<|q|>"])
        tokens.extend(tokenizer.encode(qa["question"]))
        tokens.append(sid["<|a|>"])
        tokens.extend(tokenizer.encode(qa["answer"]))
        tokens.append(sid["<|eot|>"])
    return tokens
