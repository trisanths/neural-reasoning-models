"""The eight-level generator and the four-condition harness.

Two halves. The first builds a problem set and refuses to emit a problem it
cannot prove is unanswerable without the material it targets. The second runs
any model callable through four presentations of the same problem and reports
per level and per chapter, never pooled.

The guard, which exists because this project has already been fooled once by
scores that pooled a dead task family with a live one and by items whose
answer could be copied out of the question:

  closed_derivation   required_items already contains every dependency, so
                      the ablation below tests what it claims to test
  prompt_in_corpus    the question itself is not printed in the library, so
                      retrieval cannot be handed the target chapter for free
  answer_not_copyable the answer does not stand alone in the question
  not_corpus_mode     the answer is not the most frequent answer-shaped token
                      in the retrievable library
  keyword_nearest     a term-overlap retriever followed by "say the token
                      the retrieved text repeats most" does not land the
                      answer, and a composite answer does not appear whole in
                      what it retrieved
  ablation            the reference implementation returns nothing when the
                      target chapter is removed, once per target chapter
  level7_no_single_chunk  no chunk carries the answer next to the question's
                      own words, so retrieval alone cannot land it
  level8_absent       the answer occurs nowhere in the library

Every discard is counted by level and by which check refused it, and the
report carries the rate. A level whose discard rate is near one is a level
whose generator is broken, and that has to be visible rather than averaged
away.

Chance is reported alongside accuracy: the majority-answer rate over the
emitted problems of a level is what a model that has learned nothing but the
answer format can score, and closed book should sit near it.
"""

from __future__ import annotations

import math
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Callable

from src.mathgen.interface import LEVEL_NAMES, LEVELS, Problem, closure, load_universe

ModelFn = Callable[[str], str]

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
_INT_RE = re.compile(r"-?\d+")
_LIST_RE = re.compile(r"-?\d+(?:[,:]-?\d+)+")


# --------------------------------------------------------------------------
# retrieval
# --------------------------------------------------------------------------
def norm_terms(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RE.findall(text)]


class BM25:
    """A small term-overlap index over the library, also used by the guard."""

    def __init__(self, chunks: list[dict], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1, self.b = k1, b
        self.docs = [norm_terms(c["text"] + " " + c.get("title", "")) for c in chunks]
        self.lens = [len(d) for d in self.docs]
        self.avg = (sum(self.lens) / len(self.lens)) if self.lens else 1.0
        self.tf = [Counter(d) for d in self.docs]
        df: Counter = Counter()
        for d in self.docs:
            df.update(set(d))
        n = max(1, len(self.docs))
        self.idf = {t: math.log(1.0 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def score(self, terms: list[str], i: int) -> float:
        tf, dl = self.tf[i], self.lens[i] or 1
        s = 0.0
        for t in terms:
            f = tf.get(t, 0)
            if not f:
                continue
            denom = f + self.k1 * (1 - self.b + self.b * dl / self.avg)
            s += self.idf.get(t, 0.0) * f * (self.k1 + 1) / denom
        return s

    def top(self, query: str, k: int = 4) -> list[dict]:
        terms = norm_terms(query)
        scored = [(self.score(terms, i), i) for i in range(len(self.chunks))]
        scored.sort(key=lambda p: (-p[0], p[1]))
        return [self.chunks[i] for s, i in scored[:k]]


# --------------------------------------------------------------------------
# answer handling
# --------------------------------------------------------------------------
def answer_shape(answer: str) -> str:
    if _LIST_RE.fullmatch(answer.strip()):
        return "list"
    if _INT_RE.fullmatch(answer.strip()):
        return "int"
    return "word"


def shaped_tokens(text: str, shape: str) -> set[str]:
    if shape == "list":
        return set(_LIST_RE.findall(text))
    if shape == "int":
        return set(_INT_RE.findall(text))
    return {t.lower() for t in _WORD_RE.findall(text)}


def keyword_nearest_guess(chunks: list[dict], shape: str):
    """What a term-overlap baseline would answer from these chunks.

    Retrieve, then say the answer-shaped token the retrieved text repeats
    most, breaking ties by first appearance. This is the heuristic a problem
    has to beat: if it lands the answer, the problem is measuring retrieval
    and not understanding, and the guard throws it out. Returns the guess and
    the joined text the guess came from.
    """
    joined = "\n".join(c["text"] for c in chunks)
    if shape == "list":
        found = _LIST_RE.findall(re.sub(r"\s*([,:])\s*", r"\1", joined))
    elif shape == "int":
        found = _INT_RE.findall(joined)
    else:
        found = [t.lower() for t in _WORD_RE.findall(joined)]
    if not found:
        return None, joined
    counts = Counter(found)
    first = {}
    for i, tok in enumerate(found):
        first.setdefault(tok, i)
    best = max(counts, key=lambda t: (counts[t], -first[t]))
    return best, joined


def normalize(s: str) -> str:
    s = s.strip().lower()
    s = s.split("\n")[0].strip()
    s = re.sub(r"^(the\s+answer\s+is|answer\s*[:=]|is)\s*", "", s)
    s = s.strip().strip(".").strip()
    s = re.sub(r"\s*,\s*", ",", s)
    s = re.sub(r"\s*:\s*", ":", s)
    s = re.sub(r"\s+", " ", s)
    return s


def extract_answer(raw: str, shape: str) -> str:
    """Pull the answer out of free generation, in the shape the item expects."""
    text = raw.strip()
    m = re.search(r"(?i)answer\s*[:=]\s*(.+)", text)
    if m:
        text = m.group(1)
    text = text.split("\n")[0]
    if shape == "list":
        # A model that writes "17, 44" means the same list as "17,44", so the
        # spacing is closed up before the list pattern is looked for.
        found = _LIST_RE.findall(re.sub(r"\s*([,:])\s*", r"\1", text))
        if found:
            return normalize(found[0])
    if shape == "int":
        found = _INT_RE.findall(text)
        if found:
            return normalize(found[0])
    return normalize(text)


def is_correct(raw: str, answer: str) -> bool:
    return extract_answer(raw, answer_shape(answer)) == normalize(answer)


# --------------------------------------------------------------------------
# the guard
# --------------------------------------------------------------------------
GUARD_CHECKS = (
    "closed_derivation",
    "prompt_in_corpus",
    "answer_not_copyable",
    "not_corpus_mode",
    "keyword_nearest",
    "ablation",
    "level7_no_single_chunk",
    "level8_absent",
)


@dataclass
class GuardVerdict:
    ok: bool
    failed: str | None
    detail: dict = field(default_factory=dict)


class Guard:
    """Proof, per problem, that the target material is needed to answer it."""

    def __init__(self, universe, keyword_k: int = 3):
        self.u = universe
        self.library = universe.library()
        self.index = BM25(self.library)
        self.keyword_k = keyword_k
        self.all_chapters = [c.chapter_id for c in universe.chapters]
        self.corpus_text = "\n".join(c["text"] for c in self.library)
        self.corpus_flat = " ".join(self.corpus_text.split())
        self._mode: dict[str, str | None] = {}

    def corpus_mode(self, shape: str) -> str | None:
        if shape not in self._mode:
            counts = Counter()
            for chunk in self.library:
                counts.update(shaped_tokens(chunk["text"], shape))
            self._mode[shape] = counts.most_common(1)[0][0] if counts else None
        return self._mode[shape]

    def check(self, p: Problem) -> GuardVerdict:
        items = self.u.items
        if not p.closed_over(items):
            return GuardVerdict(False, "closed_derivation")

        # A corpus that prints the question hands retrieval the target
        # chapter without the model understanding anything, which empties out
        # the retrieval and agent conditions and level five in particular.
        if " ".join(p.text.split()) in self.corpus_flat:
            return GuardVerdict(False, "prompt_in_corpus")

        shape = answer_shape(p.answer)
        parts = [q for q in re.split(r"[,:]", p.answer) if q]
        in_q = shaped_tokens(p.text, shape)
        if normalize(p.answer) in {normalize(t) for t in in_q}:
            return GuardVerdict(False, "answer_not_copyable",
                                {"where": "whole"})
        if shape != "word" and parts and all(
                part in shaped_tokens(p.text, "int") for part in parts):
            return GuardVerdict(False, "answer_not_copyable", {"where": "parts"})

        if self.corpus_mode(shape) == normalize(p.answer):
            return GuardVerdict(False, "not_corpus_mode")

        near = self.index.top(p.text, self.keyword_k)
        guess, joined = keyword_nearest_guess(near, shape)
        if guess is not None and normalize(guess) == normalize(p.answer):
            return GuardVerdict(False, "keyword_nearest",
                                {"chunks": [c["chunk_id"] for c in near],
                                 "guess": guess})
        # A composite answer appearing whole in a retrieved chunk is leakage
        # whether or not the baseline would have picked it out.
        if shape == "list" and normalize(p.answer) in {
                normalize(t) for t in shaped_tokens(joined, shape)}:
            return GuardVerdict(False, "keyword_nearest",
                                {"chunks": [c["chunk_id"] for c in near],
                                 "verbatim": True})

        for target in p.target_chapters:
            allowed = [c for c in self.all_chapters if c != target]
            if self.u.reference_solve(p, allowed) is not None:
                return GuardVerdict(False, "ablation", {"chapter": target})

        if p.level == 7:
            qterms = {t for t in norm_terms(p.text) if len(t) > 4}
            for chunk in self.library:
                if normalize(p.answer) in {normalize(t) for t in
                                           shaped_tokens(chunk["text"], shape)}:
                    overlap = qterms & set(norm_terms(chunk["text"]))
                    if len(overlap) >= 2:
                        return GuardVerdict(False, "level7_no_single_chunk",
                                            {"chunk": chunk["chunk_id"]})

        if p.level == 8:
            if re.search(rf"(?<![\w.:]){re.escape(p.answer)}(?![\w.:])",
                         self.corpus_text):
                return GuardVerdict(False, "level8_absent")

        return GuardVerdict(True, None)


# --------------------------------------------------------------------------
# problem sets
# --------------------------------------------------------------------------
@dataclass
class ProblemSet:
    problems: list[Problem]
    universes: dict
    discards: dict
    baselines: dict

    def by_level(self) -> dict[int, list[Problem]]:
        out: dict[int, list[Problem]] = defaultdict(list)
        for p in self.problems:
            out[p.level].append(p)
        return dict(out)


def majority_baseline(problems: list[Problem]) -> dict:
    if not problems:
        return {"majority": 0.0, "n_distinct": 0}
    counts = Counter(normalize(p.answer) for p in problems)
    top = counts.most_common(1)[0][1]
    return {"majority": top / len(problems), "n_distinct": len(counts)}


# Levels 3, 7 and 8 ask about the universe rather than about an instance in
# it, so one universe holds only a handful of distinct problems at those
# levels. Asking for more would return the same question over and over, and a
# problem set thick with repeats would make a level look larger than it is.
# Breadth at those levels comes from more universes, not from more draws.
PER_UNIVERSE_CAP = {3: 2, 7: 1, 8: 1}


def build_problem_set(seeds, per_level: int = 4, levels=LEVELS,
                      universe_module: str | None = None,
                      oversample: int = 6, rng_seed: int = 0) -> ProblemSet:
    """Generate, guard, dedupe. Discards are counted, never hidden."""
    rng = random.Random(rng_seed)
    kept: list[Problem] = []
    universes: dict = {}
    discards = {lv: Counter() for lv in levels}
    emitted = {lv: 0 for lv in levels}
    duplicates = {lv: 0 for lv in levels}
    seen: set[tuple[str, str, str]] = set()

    for seed in seeds:
        u = load_universe(seed, module=universe_module)
        universes[u.universe_id] = u
        guard = Guard(u)
        for lv in levels:
            want = min(per_level, PER_UNIVERSE_CAP.get(lv, per_level))
            got = 0
            for cand in u.problems(lv, want * oversample, rng):
                key = (u.universe_id, str(lv), cand.text)
                if key in seen:
                    duplicates[lv] += 1
                    continue
                seen.add(key)
                emitted[lv] += 1
                verdict = guard.check(cand)
                if not verdict.ok:
                    discards[lv][verdict.failed] += 1
                    continue
                kept.append(cand)
                got += 1
                if got >= want:
                    break

    by_level: dict[int, list[Problem]] = defaultdict(list)
    for p in kept:
        by_level[p.level].append(p)

    report_discards = {}
    for lv in levels:
        total = emitted[lv]
        n_kept = len(by_level.get(lv, []))
        report_discards[LEVEL_NAMES[lv]] = {
            "level": lv,
            "distinct_emitted": total,
            "kept": n_kept,
            "discarded": total - n_kept,
            "discard_rate": (total - n_kept) / total if total else 0.0,
            "repeat_draws_skipped": duplicates[lv],
            "by_check": dict(discards[lv]),
        }
    baselines = {LEVEL_NAMES[lv]: majority_baseline(by_level.get(lv, []))
                 for lv in levels}
    return ProblemSet(kept, universes, report_discards, baselines)


# --------------------------------------------------------------------------
# the four conditions
# --------------------------------------------------------------------------
INSTRUCTION = ("Give only the answer, on one line, after the word Answer.")


def prompt_closed_book(p: Problem) -> str:
    return f"Problem.\n{p.text}\n\n{INSTRUCTION}\nAnswer:"


def required_chapters(p: Problem, universe) -> list[str]:
    """The chapters the derivation touches, in reading order."""
    return sorted(
        {universe.items[i].chapter_id for i in closure(p.required_items,
                                                       universe.items)},
        key=lambda cid: universe.by_id[cid].index)


def prompt_oracle(p: Problem, universe) -> str:
    # Each supplied chapter is labelled with its id, the same way a retrieved
    # chunk is, so a reader can tell what it has been given and the scripted
    # control can measure coverage the same way in every condition.
    parts = [f"[{cid}] {universe.chapter_text([cid])}"
             for cid in required_chapters(p, universe)]
    body = "\n\n".join(parts)
    return (f"Reference.\n{body}\n\nProblem.\n{p.text}\n\n{INSTRUCTION}\nAnswer:")


def prompt_rag(p: Problem, index: BM25, k: int = 4) -> str:
    chunks = index.top(p.text, k)
    body = "\n\n".join(f"[{c['chapter_id']}] [{c['chunk_id']}] {c['text']}"
                        for c in chunks)
    return (f"Retrieved.\n{body}\n\nProblem.\n{p.text}\n\n{INSTRUCTION}\nAnswer:")


ACQUISITION_PREAMBLE = (
    "You may read from a library before answering. Write a line beginning "
    "SEARCH: to read, or a line beginning ANSWER: to finish."
)


def run_acquisition(model: ModelFn, p: Problem, index: BM25,
                    max_rounds: int = 4, k: int = 2) -> tuple[str, list[str]]:
    """The agent condition: the whole library searchable, the model chooses."""
    transcript = [f"{ACQUISITION_PREAMBLE}\n\nProblem.\n{p.text}"]
    queries: list[str] = []
    for _ in range(max_rounds):
        out = model("\n\n".join(transcript) + "\n")
        line = out.strip().split("\n")[0].strip()
        m = re.match(r"(?i)^\s*search\s*:\s*(.+)", line)
        if m:
            q = m.group(1).strip()
            queries.append(q)
            chunks = index.top(q, k)
            served = "\n".join(f"[{c['chapter_id']}] [{c['chunk_id']}] {c['text']}"
                               for c in chunks)
            transcript.append(f"SEARCH: {q}")
            transcript.append(f"Library.\n{served}")
            continue
        return out, queries
    out = model("\n\n".join(transcript) + f"\n\n{INSTRUCTION}\nAnswer:")
    return out, queries


CONDITIONS = ("closed_book", "oracle", "rag", "acquisition")


def score(model: ModelFn, ps: ProblemSet, conditions=CONDITIONS,
          rag_k: int = 4, max_rounds: int = 4,
          record: list | None = None) -> dict:
    """Every problem through every condition. Reported per level and chapter."""
    indexes = {uid: BM25(u.library()) for uid, u in ps.universes.items()}
    hits: dict = {c: defaultdict(list) for c in conditions}
    chap: dict = {c: defaultdict(list) for c in conditions}
    # A zero in the agent condition means one of two different things, so the
    # report says whether the model ever issued a query at all.
    searched: dict = defaultdict(list)

    for p in ps.problems:
        u = ps.universes[p.universe_id]
        idx = indexes[p.universe_id]
        for cond in conditions:
            if cond == "closed_book":
                raw = model(prompt_closed_book(p))
                extra = {}
            elif cond == "oracle":
                raw = model(prompt_oracle(p, u))
                extra = {}
            elif cond == "rag":
                raw = model(prompt_rag(p, idx, rag_k))
                extra = {}
            else:
                raw, queries = run_acquisition(model, p, idx, max_rounds)
                extra = {"queries": queries}
            ok = is_correct(raw, p.answer)
            hits[cond][p.level].append(ok)
            if cond == "acquisition":
                searched[p.level].append(bool(extra.get("queries")))
            for cid in p.target_chapters:
                chap[cond][cid].append(ok)
            if record is not None:
                record.append({"problem_id": p.problem_id, "level": p.level,
                               "condition": cond, "answer": p.answer,
                               "raw": raw[:400], "correct": ok, **extra})

    def block(d):
        return {LEVEL_NAMES[lv]: {"level": lv, "n": len(v),
                                  "accuracy": sum(v) / len(v) if v else 0.0}
                for lv, v in sorted(d.items())}

    return {
        "per_level": {c: block(hits[c]) for c in conditions},
        "acquisition_search_rate": {
            LEVEL_NAMES[lv]: sum(v) / len(v) if v else 0.0
            for lv, v in sorted(searched.items())},
        "per_chapter": {c: {cid: {"n": len(v),
                                  "accuracy": sum(v) / len(v) if v else 0.0}
                            for cid, v in sorted(chap[c].items())}
                        for c in conditions},
        "baselines": ps.baselines,
        "discards": ps.discards,
    }


# --------------------------------------------------------------------------
# handing the problems to the RL environment
# --------------------------------------------------------------------------
def to_rl_episodes(ps: ProblemSet, n_context: int = 0) -> list[dict]:
    """Shape a problem set the way src/rl/env.py loads tasks.

    Same record shape src/skillacq/episodes.py produces, so the levels can be
    trained against as well as evaluated. One episode per universe, its pages
    the documents and its problems the questions. With n_context zero the
    pages arrive only through retrieval, which is the presentation the RL
    rollout already serves.
    """
    grouped: dict[str, list[Problem]] = defaultdict(list)
    for p in ps.problems:
        grouped[p.universe_id].append(p)
    out = []
    for uid, problems in grouped.items():
        u = ps.universes[uid]
        out.append({
            "episode_id": uid,
            "seed": u.seed,
            "world": {"domain": "mathgen_levels"},
            "n_context": n_context,
            "documents": [{"text": c["text"]} for c in u.library()],
            "questions": [
                {"qid": p.problem_id, "text": p.text, "answer": p.answer,
                 "plan": [p.problem_id], "type": LEVEL_NAMES[p.level],
                 "level": p.level, "target_chapters": list(p.target_chapters)}
                for p in problems
            ],
        })
    return out


def write_rl_jsonl(path: str, ps: ProblemSet, n_context: int = 0) -> dict:
    import json

    episodes = to_rl_episodes(ps, n_context=n_context)
    with open(path, "w") as fh:
        for rec in episodes:
            fh.write(json.dumps(rec) + "\n")
    return {"episodes": len(episodes),
            "questions": sum(len(e["questions"]) for e in episodes),
            "path": path}


# --------------------------------------------------------------------------
# scripted models, for wiring the harness up before a checkpoint is involved
# --------------------------------------------------------------------------
def scripted_reader(ps: ProblemSet, competence: float = 1.0, seed: int = 0) -> ModelFn:
    """A fake model that answers when the chapters it needs are in front of it.

    Every supplied chapter and every served chunk is labelled with its
    chapter id, so the reader can tell exactly what it has been given without
    reading it. It answers when the derivation's chapters are all present, and
    in the agent condition it searches by the title of a chapter it is still
    missing. With nothing supplied it guesses from the pool of answers. This is
    the plumbing check: oracle near one, closed book near the majority
    baseline, and the agent condition somewhere between depending on what its
    queries surface.
    """
    rng = random.Random(seed)
    lookup = {}
    for p in ps.problems:
        u = ps.universes[p.universe_id]
        # The query is the chapter's title together with the names of what it
        # states, because a title alone does not always retrieve its own
        # chapter out of a library written in invented words.
        needed = [(cid, " ".join([u.by_id[cid].title] +
                                 [u.items[i].name for i in u.by_id[cid].item_ids][:4]))
                  for cid in required_chapters(p, u)]
        lookup[p.text.strip()] = (p, needed)
    pool = [normalize(p.answer) for p in ps.problems]

    def present(chapter_id: str, supplied: str) -> bool:
        return f"[{chapter_id}]" in supplied

    def find(prompt: str):
        # A textbook can print its own exercises, so a problem's words can
        # turn up inside supplied chapter text. Only the segment that follows
        # the Problem marker counts as the question being asked.
        for segment in prompt.split("Problem.\n")[1:]:
            key = segment.split("\n\n")[0].strip()
            if key in lookup:
                return lookup[key]
        return None

    def model(prompt: str) -> str:
        entry = find(prompt)
        if entry is None:
            return "Answer: 0"
        p, needed = entry
        # Everything except the problem statement itself counts as supplied,
        # which keeps the reader from scoring off the question and works the
        # same whether the text arrived above the problem or below it.
        supplied = prompt.replace(p.text, " ")
        missing = [(cid, title) for cid, title in needed
                   if not present(cid, supplied)]
        if not missing and rng.random() < competence:
            return f"Answer: {p.answer}"
        if prompt.lstrip().startswith(ACQUISITION_PREAMBLE):
            fresh = [title for _, title in missing
                     if f"SEARCH: {title}" not in prompt]
            if fresh:
                return f"SEARCH: {fresh[0]}"
        return f"Answer: {rng.choice(pool)}"

    return model


def scripted_parrot(ps: ProblemSet, seed: int = 0) -> ModelFn:
    """A fake model that answers with the library's most frequent number.

    If the guard is doing its job this model scores zero everywhere, which is
    the check that the benchmark is not solvable by echoing the corpus.
    """
    counts: Counter = Counter()
    for u in ps.universes.values():
        for chunk in u.library():
            counts.update(shaped_tokens(chunk["text"], "int"))
    mode = counts.most_common(1)[0][0] if counts else "0"

    def model(prompt: str) -> str:
        return f"Answer: {mode}"

    return model
