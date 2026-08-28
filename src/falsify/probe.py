"""Adversarial machinery for the simple rule families.

Everything here exists to attack the claim that a fact-free 350M reads an
invented rule page and applies it. Four attacks live in this module:

  candidates()      the answer set an episode admits, which fixes the chance
                    floor a score has to beat
  swap_pages()      a same-family page with identical vocabulary and identical
                    structure whose values are permuted, so a reader flips its
                    answer and a structure matcher does not
  NEW_FAMILIES      relation types the checkpoint never trained on
  baselines         non-neural programs that see exactly what the model sees

Nothing here imports torch. The model run and the analysis stay separable.
"""

from __future__ import annotations

import random
import re

from src.skillacq.simple import SIMPLE_FAMILIES
from src.skillacq.systems import _word, generate_episode
from src.train.retrieval import BM25Index

WORD_RE = re.compile(r"[A-Za-z]+")
INT_RE = re.compile(r"\d+")


# --------------------------------------------------------------- reconstruct

def rebuild_system(seed: int, family: str):
    """The system object generate_episode built for this seed.

    generate_episode seeds a Random with the seed and constructs the family
    class first, and short circuits past rng.choice when family is given, so
    a fresh Random(seed) reproduces the same attributes exactly.
    """
    return SIMPLE_FAMILIES[family](random.Random(seed))


def candidates(sysobj) -> list[str]:
    """Every answer the family's problems() can emit for this system."""
    fam = sysobj.family
    if fam == "threshold_rule":
        return [sysobj.high, sysobj.low]
    if fam == "substitution_rule":
        return list(sysobj.values) + [sysobj.rng_default]
    if fam == "exception_rule":
        return [sysobj.general, sysobj.special]
    if fam == "inverse_table":
        return list(sysobj.keys)
    if fam == "chain_rule":
        return list(sysobj.dests)
    if fam == "band_rule":
        return list(sysobj.words)
    raise ValueError(fam)


def _swap_words(text: str, mapping: dict) -> str:
    """Simultaneous whole-word substitution."""
    if not mapping:
        return text
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in mapping) + r")\b")
    return pattern.sub(lambda m: mapping[m.group(0)], text)


def swap_pages(seed: int, family: str, pages: list[str], problems: list[dict]):
    """Permute the values a page states without touching its wording.

    Returns (new_pages, alt_answers, informative_flags). alt_answers holds the
    answer the permuted page implies for each problem. An item is informative
    when the permuted page implies a different answer than the true one; the
    uninformative items are substitution questions about unlisted types, whose
    answer is the default desk either way.
    """
    sysobj = rebuild_system(seed, family)
    if family == "threshold_rule":
        pair = [sysobj.high, sysobj.low]
    elif family == "exception_rule":
        pair = [sysobj.general, sysobj.special]
    elif family == "substitution_rule":
        pair = list(sysobj.values)
    else:
        raise ValueError(family)
    if len(set(pair)) != len(pair):
        # A word collision would make the permutation ambiguous; leave the
        # page alone and let every item on it count as uninformative.
        return list(pages), [p["answer"] for p in problems], [False] * len(problems)
    mapping = {v: pair[(i + 1) % len(pair)] for i, v in enumerate(pair)}
    new_pages = [_swap_words(p, mapping) for p in pages]
    alt, informative = [], []
    for p in problems:
        a = mapping.get(p["answer"], p["answer"])
        alt.append(a)
        informative.append(a != p["answer"])
    return new_pages, alt, informative


def retitle(page: str, name: str) -> str:
    """Say which system a page belongs to, in its heading.

    The generator writes the page that states the rule without naming the
    system it belongs to: "The rule." then the sentence. With one rule page in
    the store that is harmless, and with two it makes the store ambiguous, so
    the attributable twin puts the name back into every heading.
    """
    head, sep, body = page.partition("\n\n")
    return f"{head.rstrip('.')} in the {name} system.{sep}{body}"


def twin_episode(seed: int, family: str, attributable: bool = False) -> tuple:
    """Put a second system of the same family in the same document store.

    The twin repeats whatever the question mentions, so the two pages match a
    query on every term but the system's name: same reading name and a
    different limit, same request types and different desks, same excepted
    category and a different treatment. Picking the right line is no longer
    enough; the page has to be picked too.

    Returns (documents, twin_candidates).
    """
    sysobj = rebuild_system(seed, family)
    twin = SIMPLE_FAMILIES[family](random.Random(seed + 424242))
    while twin.name == sysobj.name:
        twin = SIMPLE_FAMILIES[family](random.Random(seed + 424243))
    if family == "threshold_rule":
        twin.attr = sysobj.attr
        choices = [x for x in (20, 35, 50, 65, 80) if x != sysobj.limit]
        twin.limit = random.Random(seed).choice(choices)
    elif family == "substitution_rule":
        twin.keys = list(sysobj.keys)
    elif family == "exception_rule":
        twin.special_key = sysobj.special_key
    else:
        raise ValueError(family)
    mine, theirs = sysobj.describe(), twin.describe()
    if attributable:
        mine = [retitle(p, sysobj.name) for p in mine]
        theirs = [retitle(p, twin.name) for p in theirs]
    pages = mine + theirs
    random.Random(seed ^ 0x7317).shuffle(pages)
    return [{"text": p} for p in pages], candidates(twin)


# ------------------------------------------------------------- new families

class InverseTableRule:
    """The routing table read backwards. Same page shape, opposite direction."""

    family = "inverse_table"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.keys = [_word(rng) for _ in range(4)]
        self.values = [_word(rng) for _ in range(4)]

    def describe(self) -> list[str]:
        lines = "\n".join(f"A {k} is handled by the {v} desk."
                          for k, v in zip(self.keys, self.values))
        return [
            f"The {self.name} routing table.\n\n"
            f"Requests in the {self.name} office are routed by their type.",
            f"Routing.\n\n{lines}",
            f"A note on precedence.\n\n"
            f"The table above is complete. Each desk handles exactly one "
            f"request type and no desk is shared.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            idx = rng.randrange(len(self.keys))
            out.append({
                "qid": f"p{i}",
                "kind": "inverse",
                "text": (f"In the {self.name} office, which request type does "
                         f"the {self.values[idx]} desk handle?"),
                "answer": self.keys[idx],
            })
        return out


class ChainRule:
    """Two stated hops. The answer needs both pages, not one."""

    family = "chain_rule"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.keys = [_word(rng) for _ in range(3)]
        self.mids = [_word(rng) for _ in range(3)]
        self.dests = [_word(rng) for _ in range(3)]

    def describe(self) -> list[str]:
        l1 = "\n".join(f"A {k} is first sent to the {m} bench."
                       for k, m in zip(self.keys, self.mids))
        l2 = "\n".join(f"The {m} bench forwards everything to the {d} office."
                       for m, d in zip(self.mids, self.dests))
        return [
            f"The {self.name} pipeline.\n\n"
            f"Every request in the {self.name} pipeline passes through two stages.",
            f"The first stage.\n\n{l1}",
            f"The second stage.\n\n{l2}",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        out = []
        for i in range(n):
            idx = rng.randrange(len(self.keys))
            out.append({
                "qid": f"p{i}",
                "kind": "chain",
                "text": (f"A {self.keys[idx]} request enters the {self.name} "
                         f"pipeline. Which office finally handles it?"),
                "answer": self.dests[idx],
            })
        return out


class BandRule:
    """Three bands instead of two, which drops the chance floor to a third."""

    family = "band_rule"

    def __init__(self, rng: random.Random):
        self.name = _word(rng).capitalize()
        self.attr = _word(rng)
        self.lo = rng.choice([25, 30, 35])
        self.hi = self.lo + rng.choice([30, 35, 40])
        self.words = [_word(rng) for _ in range(3)]

    def describe(self) -> list[str]:
        w0, w1, w2 = self.words
        return [
            f"The {self.name} classification.\n\n"
            f"Every specimen in the {self.name} classification carries a "
            f"{self.attr} reading, which is a whole number.",
            f"The rule.\n\n"
            f"A specimen whose {self.attr} reading is less than {self.lo} is "
            f"called {w0}. A specimen whose {self.attr} reading is {self.lo} or "
            f"more but less than {self.hi} is called {w1}. A specimen whose "
            f"{self.attr} reading is {self.hi} or more is called {w2}.",
            f"A worked example.\n\n"
            f"A specimen with a {self.attr} reading of {self.hi + 6} is {w2}.",
        ]

    def problems(self, rng: random.Random, n: int) -> list[dict]:
        w0, w1, w2 = self.words
        out = []
        for i in range(n):
            v = rng.randint(1, 110)
            while abs(v - self.lo) < 3 or abs(v - self.hi) < 3:
                v = rng.randint(1, 110)
            ans = w0 if v < self.lo else (w1 if v < self.hi else w2)
            out.append({
                "qid": f"p{i}",
                "kind": "band",
                "text": (f"A specimen has a {self.attr} reading of {v}. "
                         f"In the {self.name} classification, what is it called?"),
                "answer": ans,
            })
        return out


NEW_FAMILIES = {
    "inverse_table": InverseTableRule,
    "chain_rule": ChainRule,
    "band_rule": BandRule,
}


def generate_new_episode(seed: int, family: str, n_problems: int = 6) -> dict:
    """An episode for an untrained family, shaped like the trained ones.

    Three pages of the new system plus three pages of a trained simple family
    as a distractor, shuffled, exactly the six document store the trained
    episodes present.
    """
    rng = random.Random(seed)
    system = NEW_FAMILIES[family](rng)
    pages = system.describe()
    problems = system.problems(rng, n_problems * 3)
    kept = [p for p in problems
            if not re.search(rf"(?<![\w.]){re.escape(p['answer'])}(?![\w.])", p["text"])]
    kept = kept[:n_problems]
    for i, p in enumerate(kept):
        p["qid"] = f"p{i}"
    other_fam = rng.choice(sorted(SIMPLE_FAMILIES))
    other = SIMPLE_FAMILIES[other_fam](random.Random(seed ^ 0x5EED))
    pages = pages + other.describe()
    rng.shuffle(pages)
    return {
        "episode_id": f"nf-{seed:09d}",
        "seed": seed,
        "world": {"domain": f"skill_{family}"},
        "n_context": 0,
        "documents": [{"text": p} for p in pages],
        "questions": [{"qid": p["qid"], "text": p["text"], "answer": p["answer"],
                       "plan": [p["qid"]], "type": p["kind"]} for p in kept],
        "_system": system,
    }


# ------------------------------------------------------------ nonce lexicon

def template_vocabulary(n_episodes: int = 200) -> set:
    """Words that recur across independently generated episodes.

    Learned rather than hand listed: sample episodes, count how many of them
    each lowercased word appears in, and keep the ones that show up in more
    than a twentieth. Every invented word is unique to its episode, so what
    survives is the prose scaffolding and nothing else. A baseline built on
    this set is using only what any attacker gets from reading the corpus.
    """
    fams = sorted(SIMPLE_FAMILIES)
    df: dict = {}
    for i in range(n_episodes):
        ep = generate_episode(5_000_000 + i, family=fams[i % len(fams)], n_problems=4)
        seen = set()
        for page in ep.textbook:
            seen.update(w.lower() for w in WORD_RE.findall(page))
        for p in ep.problems:
            seen.update(w.lower() for w in WORD_RE.findall(p["text"]))
        for w in seen:
            df[w] = df.get(w, 0) + 1
    new = sorted(NEW_FAMILIES)
    for i in range(n_episodes):
        ep = generate_new_episode(5_500_000 + i, new[i % len(new)], n_problems=4)
        ep.pop("_system")
        seen = set()
        for d in ep["documents"]:
            seen.update(w.lower() for w in WORD_RE.findall(d["text"]))
        for q in ep["questions"]:
            seen.update(w.lower() for w in WORD_RE.findall(q["text"]))
        for w in seen:
            df[w] = df.get(w, 0) + 1
    return {w for w, c in df.items() if c > 2 * n_episodes * 0.05}


def nonce_words(text: str, vocab: set) -> list[str]:
    """Invented words in a text, in order of appearance, with duplicates."""
    return [w for w in WORD_RE.findall(text) if w.lower() not in vocab]


# ---------------------------------------------------------------- baselines

def bm25_top(question: str, documents: list[dict]) -> str:
    texts = [d["text"] for d in documents]
    idx = BM25Index(texts).top(question)
    return texts[idx]


def rank_documents(question: str, documents: list[dict], vocab: set) -> list[str]:
    """Order the store best first.

    Plain BM25 on the question ranks the classification's title page above the
    page that states the rule, because the title page repeats the system's
    name. A program with fifty lines to spend can do better for free: prefer a
    page that shares an invented word with the question, then fall back to the
    BM25 score. Everything below reads the top k of this ordering.
    """
    texts = [d["text"] for d in documents]
    index = BM25Index(texts)
    qn = {w.lower() for w in nonce_words(question, vocab)}
    scored = []
    for i, t in enumerate(texts):
        shared = len(qn & {w.lower() for w in WORD_RE.findall(t)})
        scored.append((shared, index.score(question, i), -i, t))
    scored.sort(reverse=True)
    return [s[3] for s in scored]


def _q_nonce(question: str, vocab: set) -> set:
    return {w.lower() for w in nonce_words(question, vocab)}


def h_random_nonce(question, doc, vocab, rng):
    words = [w for w in nonce_words(doc, vocab)
             if w.lower() not in _q_nonce(question, vocab)]
    return rng.choice(words) if words else ""


def h_freq_nonce(question, doc, vocab, rng):
    words = [w.lower() for w in nonce_words(doc, vocab)
             if w.lower() not in _q_nonce(question, vocab)]
    if not words:
        return ""
    counts: dict = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return max(words, key=lambda w: (counts[w], -words.index(w)))


def h_last_nonce(question, doc, vocab, rng):
    words = [w for w in nonce_words(doc, vocab)
             if w.lower() not in _q_nonce(question, vocab)]
    return words[-1] if words else ""


def anchor_positions(toks: list, qn: set) -> list:
    """Where the page echoes the rarest invented word the question uses.

    The system's own name is the word a question repeats most, and anchoring
    on it points at the title page rather than at the line that answers the
    question. Anchoring on the rarest shared word points at the line.
    """
    low = [w.lower() for w in toks]
    counts: dict = {}
    for w in low:
        if w in qn:
            counts[w] = counts.get(w, 0) + 1
    if not counts:
        return []
    fewest = min(counts.values())
    keep = {w for w, c in counts.items() if c == fewest}
    return [i for i, w in enumerate(low) if w in keep]


def h_nearest_nonce(question, doc, vocab, rng):
    """The invented word closest to a question word that the page repeats.

    This is the generic proximity heuristic: find where the page mentions
    something the question mentions, and answer with the invented word that
    sits nearest to it.
    """
    toks = WORD_RE.findall(doc)
    qn = _q_nonce(question, vocab)
    anchors = anchor_positions(toks, qn)
    cands = [(i, w) for i, w in enumerate(toks)
             if w.lower() not in vocab and w.lower() not in qn]
    if not cands:
        return ""
    if not anchors:
        return cands[-1][1]
    return min(cands, key=lambda iw: min(abs(iw[0] - a) for a in anchors))[1]


def h_hedge(question, doc, vocab, rng):
    """Say every invented word on the page, up to the grader's slack.

    The environment accepts a prediction that contains the gold answer as long
    as it is no more than contains_slack_tokens longer, so a wrong answer can
    hide inside a list of right ones. This baseline tests the grader, not the
    task.
    """
    words, seen = [], set()
    for w in nonce_words(doc, vocab):
        if w.lower() in _q_nonce(question, vocab) or w.lower() in seen:
            continue
        seen.add(w.lower())
        words.append(w)
    return " ".join(words[:7])


def h_rule_parser(question, doc, vocab, rng):
    """Fifty lines of regex that know the three families by shape."""
    m = re.search(r"reading is greater than (\d+) is called (\w+)\. .*?"
                  r"reading is \d+ or less is called (\w+)", doc, re.S)
    if m:
        qv = INT_RE.search(question)
        if qv:
            return m.group(2) if int(qv.group(0)) > int(m.group(1)) else m.group(3)
    m = re.search(r"reading is less than (\d+) is called (\w+)\..*?"
                  r"is (\d+) or more but less than (\d+) is called (\w+)\..*?"
                  r"is \d+ or more is called (\w+)", doc, re.S)
    if m:
        qv = INT_RE.search(question)
        if qv:
            v = int(qv.group(0))
            if v < int(m.group(1)):
                return m.group(2)
            return m.group(5) if v < int(m.group(4)) else m.group(6)
    qm = re.search(r"^A (\w+) request arrives", question)
    if qm:
        key = qm.group(1)
        m = re.search(rf"\bA {re.escape(key)} is handled by the (\w+) desk", doc)
        if m:
            return m.group(1)
        m = re.search(r"is not listed goes to the (\w+) desk", doc)
        if m:
            return m.group(1)
    qm = re.search(r"^An item of category (\w+) reaches", question)
    if qm:
        cat = qm.group(1)
        m = re.search(rf"whose category is {re.escape(cat)} is given the (\w+) treatment", doc)
        if m:
            return m.group(1)
        m = re.search(r"Every item is given the (\w+) treatment", doc)
        if m:
            return m.group(1)
    qm = re.search(r"which request type does the (\w+) desk handle", question)
    if qm:
        m = re.search(rf"\bA (\w+) is handled by the {re.escape(qm.group(1))} desk", doc)
        if m:
            return m.group(1)
    qm = re.search(r"^A (\w+) request enters", question)
    if qm:
        m = re.search(rf"\bA {re.escape(qm.group(1))} is first sent to the (\w+) bench", doc)
        if m:
            m2 = re.search(rf"The {re.escape(m.group(1))} bench forwards everything "
                           rf"to the (\w+) office", doc)
            if m2:
                return m2.group(1)
    return ""


HEURISTICS = {
    "random_nonce": h_random_nonce,
    "freq_nonce": h_freq_nonce,
    "last_nonce": h_last_nonce,
    "nearest_nonce": h_nearest_nonce,
    "hedge_all_nonce": h_hedge,
    "rule_parser": h_rule_parser,
}


def run_baseline(name: str, question: str, documents: list[dict], vocab: set,
                 rng: random.Random, topk: int = 1) -> str:
    """One heuristic's answer, reading the top k pages of the store.

    k=1 is the hardest setting for the program and k=6 hands it the whole
    store, which is what a fifty-line script would really do with six short
    pages. The regex parser is tried page by page first, because a distractor
    page of the same shape would otherwise capture its match.
    """
    ranked = rank_documents(question, documents, vocab)[:topk]
    if name == "rule_parser":
        for page in ranked:
            got = h_rule_parser(question, page, vocab, rng)
            if got:
                return got
        return h_rule_parser(question, "\n\n".join(ranked), vocab, rng)
    return HEURISTICS[name](question, "\n\n".join(ranked), vocab, rng)
