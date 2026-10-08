"""Naturalized reading suite, the kill-test gate from SPEC.md section 6.

Every item in this suite is answerable from its passage alone. The
passages describe fictional people, companies, machines, and events, so
no outside world knowledge beyond common vocabulary is required or even
usable. That property is the whole point: a fact-starved model that can
read should score well here, and a model that leans on memorized world
facts gets no help at all.

The suite ships as static JSON under src/evals/data/naturalized/. Each
item has a passage of 150 to 400 words in one of five registers (news
report, regulatory filing, technical manual, personal letter, meeting
transcript), one question, a short verifiable answer that appears in the
passage, and distractor content inside the passage that a careless
reader could mistake for the answer.

The harness functions ocr_noise, inject_contradiction, and
rhetorical_wrap corrupt or reframe passages deterministically so the
same seeds always produce the same evaluation text. Scoring reports
normalized exact match and a relaxed contains-answer rate.
"""

import json
import random
import re
from collections import Counter
from pathlib import Path

SUITE_VERSION = "DRAFT-1"

REGISTERS = ("news", "filing", "manual", "letter", "transcript")

_ARTICLES = {"a", "an", "the"}

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize(text: str) -> str:
    """Lowercase, strip punctuation, and drop leading articles everywhere."""
    tokens = _NON_ALNUM.sub(" ", text.lower()).split()
    return " ".join(t for t in tokens if t not in _ARTICLES)


def exact_match(prediction: str, gold: str) -> bool:
    """Normalized exact match."""
    return normalize(prediction) == normalize(gold)


def contains_answer(prediction: str, gold: str) -> bool:
    """True when the normalized gold tokens appear contiguously in the prediction."""
    pred = normalize(prediction).split()
    want = normalize(gold).split()
    if not want:
        return False
    n = len(want)
    return any(pred[i:i + n] == want for i in range(len(pred) - n + 1))


def default_data_dir() -> Path:
    return Path(__file__).parent / "data" / "naturalized"


def load_suite(data_dir=None) -> dict:
    """Load every JSON data file and return items plus suite metadata."""
    base = Path(data_dir) if data_dir is not None else default_data_dir()
    files = sorted(base.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"no naturalized data files under {base}")
    items = []
    for path in files:
        with open(path) as fh:
            items.extend(json.load(fh))
    counts = Counter(item["register"] for item in items)
    metadata = {
        "version": SUITE_VERSION,
        "n_items": len(items),
        "per_register": {reg: counts.get(reg, 0) for reg in REGISTERS},
    }
    return {"metadata": metadata, "items": items}


OCR_CONFUSIONS = {
    "a": ["o", "e"], "b": ["h", "lo"], "c": ["e", "o"], "d": ["cl", "ol"],
    "e": ["c", "o"], "f": ["t"], "g": ["q", "y"], "h": ["b", "li"],
    "i": ["l", "1"], "j": ["i"], "k": ["lc"], "l": ["1", "i"],
    "m": ["rn", "nn"], "n": ["ri", "u"], "o": ["0", "c"], "p": ["b"],
    "q": ["g"], "r": ["n"], "s": ["5", "z"], "t": ["f", "l"],
    "u": ["v", "ii"], "v": ["u", "y"], "w": ["vv"], "x": ["k"],
    "y": ["v"], "z": ["s", "2"],
    "0": ["o"], "1": ["l"], "5": ["s"], "8": ["3"],
}


def ocr_noise(text: str, rate: float, seed: int) -> str:
    """Corrupt characters the way cheap OCR does, deterministically.

    Each character is corrupted with probability rate using a fixed
    confusion table. Spaces are occasionally dropped or doubled.
    Characters with no confusion entry pass through unchanged. rate 0
    returns the text byte for byte.
    """
    if not 0.0 <= rate <= 1.0:
        raise ValueError(f"rate must be in [0, 1], got {rate}")
    rng = random.Random(seed)
    out = []
    for ch in text:
        if rng.random() >= rate:
            out.append(ch)
            continue
        low = ch.lower()
        if low in OCR_CONFUSIONS:
            rep = rng.choice(OCR_CONFUSIONS[low])
            out.append(rep.upper() if ch.isupper() else rep)
        elif ch == " ":
            out.append("" if rng.random() < 0.5 else "  ")
        else:
            out.append(ch)
    return "".join(out)


_CONTRADICTION_TEMPLATES = [
    " A margin note added to a later copy insists the correct value was"
    " {d}, though nothing else in the record supports that claim.",
    " An earlier circulated draft of this text gave the answer as {d}"
    " before the error was caught and corrected.",
    " One annotated copy claims it was really {d}, in direct conflict"
    " with the account above.",
]


def inject_contradiction(items, rate: float, seed: int):
    """Append a contradicting sentence to a fraction of the items.

    Returns new item dicts and never mutates the input. Each selected
    item gets one sentence asserting a distractor value, plus a
    contradicted flag. The gold answer is unchanged: the original
    passage remains the authoritative account and the injected sentence
    is marked as unsupported.
    """
    if not 0.0 <= rate <= 1.0:
        raise ValueError(f"rate must be in [0, 1], got {rate}")
    rng = random.Random(seed)
    out = []
    for item in items:
        new = dict(item)
        if rng.random() < rate:
            distractors = item.get("distractors") or ["something else"]
            d = distractors[rng.randrange(len(distractors))]
            template = _CONTRADICTION_TEMPLATES[
                rng.randrange(len(_CONTRADICTION_TEMPLATES))]
            new["passage"] = item["passage"] + template.format(d=d)
            new["contradicted"] = True
        else:
            new["contradicted"] = False
        out.append(new)
    return out


WRAP_STYLES = {
    "persuasive": [
        ("Read what follows closely, because it settles the question on"
         " its own.",
         "Anyone weighing this record honestly will reach the same"
         " conclusion it states."),
        ("The document below deserves your full attention before you"
         " form an opinion.",
         "Taken together, the details above leave little room for"
         " doubt."),
    ],
    "dismissive": [
        ("What follows is routine paperwork, reproduced only for"
         " completeness.",
         "Make of that what you will; few readers ever bother."),
        ("The next passage is the kind of text that rarely rewards a"
         " second reading.",
         "So ends another unremarkable entry in the file."),
    ],
    "sensational": [
        ("What this document reveals may surprise even careful"
         " readers.",
         "Every word of the above is drawn straight from the record."),
        ("Few people have seen the text below, and fewer still have"
         " read it to the end.",
         "The record speaks, and it is stranger than anyone guessed."),
    ],
    "academic": [
        ("The passage below is reproduced verbatim for close reading.",
         "Readers are invited to verify each claim against the text"
         " itself."),
        ("The following primary source is presented without"
         " commentary.",
         "All statements above should be checked against the source as"
         " given."),
    ],
}


def rhetorical_wrap(text: str, style: str, seed: int) -> str:
    """Frame a passage with rhetorical intro and outro text.

    The wrapping adds tone but no information, so the item stays
    answerable from the original passage. Deterministic in (style,
    seed).
    """
    if style not in WRAP_STYLES:
        raise ValueError(
            f"unknown style {style!r}, choose from {sorted(WRAP_STYLES)}")
    rng = random.Random(seed)
    intro, outro = WRAP_STYLES[style][rng.randrange(len(WRAP_STYLES[style]))]
    return f"{intro}\n\n{text}\n\n{outro}"


def evaluate(items, predict_fn) -> dict:
    """Score a suite. predict_fn(passage, question) returns an answer string.

    Reports normalized exact match and the relaxed contains-answer rate,
    overall and per register.
    """
    if not items:
        raise ValueError("no items to evaluate")
    per_register = {}
    n_em = 0
    n_contains = 0
    for item in items:
        pred = predict_fn(item["passage"], item["question"])
        em = exact_match(pred, item["answer"])
        contains = contains_answer(pred, item["answer"])
        n_em += int(em)
        n_contains += int(contains)
        stats = per_register.setdefault(
            item["register"], {"n": 0, "em": 0, "contains": 0})
        stats["n"] += 1
        stats["em"] += int(em)
        stats["contains"] += int(contains)
    for stats in per_register.values():
        stats["em"] = stats["em"] / stats["n"]
        stats["contains"] = stats["contains"] / stats["n"]
    n = len(items)
    return {
        "suite": "naturalized_reading",
        "version": SUITE_VERSION,
        "n": n,
        "em": n_em / n,
        "contains": n_contains / n,
        "per_register": per_register,
    }
