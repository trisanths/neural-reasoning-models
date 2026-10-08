"""Supervised episodes where the page that answers the question is known.

Built on the three computation-free families in src/skillacq/simple.py, chosen
because reading the rule is the whole task there: a threshold to compare
against, a routing table to look up, a general rule with one stated exception.
Nothing stands between reading the page and giving the answer, so a failure is a
failure of retrieval or of injection and not of arithmetic, which this project
has already shown a 350M model does not learn over retrieved rules.

Each episode holds six pages: the three pages of the system the question is
about, and the three pages of a second instance of the same family with
different invented words. Same family on purpose. With a different family as the
distractor the retriever could win on template prose alone; with the same family
every page is near identical boilerplate and the only thing separating the gold
page from the other five is which invented words and numbers it carries.

Worth being precise about what a query has to match, because it is not the
system name. Every family puts the name on its title page and on no other, and
the gold page is never the title page, so the name word the question carries is
a lexical attractor toward a page that does not answer it. What separates the
gold page is the rule content the question also names:

    threshold_rule     the attribute word, which is on all three pages of the
                       gold system, so the attribute alone narrows six to three
                       and picking among those needs the limit and the reading.
                       This is the hard family.
    substitution_rule  the request type, which appears on the routing page and
                       nowhere else in the episode.
    exception_rule     the category word, which appears on the exception page
                       and nowhere else in the episode.

Chance is 1/6 = 0.167 in every family. Two distractor settings:

    easy    the distractor system keeps its own invented name, so the name in
            the question picks out exactly one page and it is the gold
            system's title page.
    hard    the distractor's name is rewritten to the gold system's name, so
            both title pages answer to it and the name carries no information
            about which system at all.

Hard is the default. The gap between them says how much the name was doing,
in either direction.

The gold page per family is the one page from which the answer follows given
the question, and only episodes with a unique such page are kept:

    threshold_rule     page 1, the rule with the limit and the two labels.
    substitution_rule  page 1, the routing table. Questions whose request type
                       is unlisted are dropped: their answer is the default,
                       which is on page 1 too, but the type itself appears
                       nowhere, so there is no content for a query to match and
                       the episode would measure guessing.
    exception_rule     page 2, the exception. Only questions naming the excepted
                       category are kept. For any other category the answer is
                       the general treatment on page 1, but ruling out the
                       exception needs page 2 as well, so those episodes have no
                       single gold page and would make the retrieval target
                       ambiguous.

Half the episodes are dealt in the in-context condition: the gold page is pasted
into the prompt ahead of the question. The document store is identical in both
conditions, so the only difference the gate can see is whether the answer is
already reachable from the state. That is the discrimination being measured.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import torch

from src.latentret.vocab import get_vocab
from src.skillacq.simple import SIMPLE_FAMILIES

N_DOCS = 6
PAGES_PER_SYSTEM = 3
GOLD_PAGE = {"threshold_rule": 1, "substitution_rule": 1, "exception_rule": 2}


@dataclass
class LatentRetEpisode:
    family: str
    docs: list[list[int]]
    gold_doc: int
    prompt: list[int]
    answer: int
    in_context: bool
    question: list[int]
    foil: int
    """The answer to the same question asked of the distractor system.

    A tiny model may retrieve the right page and still not manage to say a word
    it has never emitted before, and full vocabulary accuracy cannot tell that
    apart from retrieving nothing: both read zero against a chance rate of
    1/701. The foil gives a second readout with a chance rate of one half. It is
    the same kind of word, drawn from the same pool, sitting on the distractor's
    matching page inside the same document store, so preferring the answer over
    it means the content of the right page reached the output and not merely
    that something did.
    """


def _usable(family: str, system, problem: dict) -> bool:
    """True when this problem's answer follows from the family's gold page."""
    if family == "substitution_rule":
        return problem["answer"] in system.values
    if family == "exception_rule":
        return problem["answer"] == system.special
    return True


def _draw_problem(family: str, system, rng: random.Random) -> dict:
    for problem in system.problems(rng, 24):
        if _usable(family, system, problem):
            return problem
    # Only reachable if a system draws colliding invented words; take the last.
    return problem


def make_episode(seed: int, in_context: bool, hard: bool = True) -> LatentRetEpisode:
    vocab = get_vocab()
    rng = random.Random(seed)
    family = rng.choice(sorted(SIMPLE_FAMILIES))
    cls = SIMPLE_FAMILIES[family]
    system = cls(rng)
    other = cls(random.Random(seed ^ 0x5EED))

    problem = _draw_problem(family, system, rng)
    gold_local = GOLD_PAGE[family]
    other_pages = other.describe()
    if hard:
        other_pages = [p.replace(other.name, system.name) for p in other_pages]
    pages = system.describe() + other_pages

    order = list(range(len(pages)))
    rng.shuffle(order)
    docs = [vocab.encode(pages[i]) for i in order]
    gold_doc = order.index(gold_local)

    foil_problem = _draw_problem(family, other, random.Random(seed ^ 0xF011))

    question = vocab.encode(problem["text"])
    prompt = [vocab.q_id] + question + [vocab.a_id]
    if in_context:
        prompt = [vocab.doc_id] + vocab.encode(pages[gold_local]) + prompt
    return LatentRetEpisode(
        family=family,
        docs=docs,
        gold_doc=gold_doc,
        prompt=prompt,
        answer=vocab.encode_word(problem["answer"]),
        in_context=in_context,
        question=question,
        foil=vocab.encode_word(foil_problem["answer"]),
    )


def _pad(seq: list[int], length: int, pad_id: int) -> list[int]:
    return list(seq[:length]) + [pad_id] * max(0, length - len(seq))


@dataclass
class Batch:
    prompt: torch.Tensor       # (B, Tp) right padded, causal so padding is inert
    ans_pos: torch.Tensor      # (B,) index of the <a> token
    answer: torch.Tensor       # (B,) target token id
    question: torch.Tensor     # (B, Tq) for the question-mode query baseline
    question_mask: torch.Tensor
    docs: torch.Tensor         # (B, N, Ld)
    doc_mask: torch.Tensor     # (B, N, Ld) True on real tokens
    gold: torch.Tensor         # (B,)
    foil: torch.Tensor         # (B,) the distractor system's answer word
    in_context: torch.Tensor   # (B,) bool
    family: torch.Tensor       # (B,) index into sorted(SIMPLE_FAMILIES)

    def to(self, device) -> "Batch":
        return Batch(**{k: v.to(device) for k, v in self.__dict__.items()})


def collate(episodes: list[LatentRetEpisode], prompt_len: int, doc_len: int,
            question_len: int) -> Batch:
    vocab = get_vocab()
    pad = vocab.pad_id
    fams = sorted(SIMPLE_FAMILIES)
    cols: dict[str, list] = {k: [] for k in
                             ("prompt", "ans_pos", "answer", "docs", "doc_mask",
                              "gold", "foil", "in_context", "question",
                              "question_mask", "family")}
    for ep in episodes:
        p = ep.prompt[:prompt_len]
        cols["ans_pos"].append(len(p) - 1)
        cols["prompt"].append(_pad(p, prompt_len, pad))
        cols["answer"].append(ep.answer)
        cols["docs"].append([_pad(d, doc_len, pad) for d in ep.docs])
        cols["doc_mask"].append(
            [[1] * min(len(d), doc_len) + [0] * max(0, doc_len - len(d))
             for d in ep.docs])
        cols["gold"].append(ep.gold_doc)
        cols["foil"].append(ep.foil)
        cols["in_context"].append(ep.in_context)
        cols["question"].append(_pad(ep.question, question_len, pad))
        cols["question_mask"].append(
            [1] * min(len(ep.question), question_len)
            + [0] * max(0, question_len - len(ep.question)))
        cols["family"].append(fams.index(ep.family))
    long = ("prompt", "ans_pos", "answer", "question", "docs", "gold", "foil",
            "family")
    out = {k: torch.tensor(v, dtype=torch.long if k in long else torch.bool)
           for k, v in cols.items()}
    return Batch(**out)


class EpisodeStream:
    """Endless batches from a seed range, half in context by default.

    Episodes are materialized once into a pool and sampled from it, because
    building one costs more than the forward pass at this scale and the pool is
    already far larger than the number of distinct invented systems the model
    could plausibly memorize in a few thousand steps. Set pool_size to None to
    draw a fresh episode every time.
    """

    def __init__(self, seed_lo: int, seed_hi: int, batch_size: int,
                 prompt_len: int = 128, doc_len: int = 80, question_len: int = 40,
                 in_context_frac: float = 0.5, seed: int = 0, hard: bool = True,
                 force_in_context: bool | None = None, pool_size: int | None = 20_000):
        self.seed_lo, self.seed_hi = seed_lo, seed_hi
        self.batch_size = batch_size
        self.prompt_len, self.doc_len = prompt_len, doc_len
        self.question_len = question_len
        self.in_context_frac = in_context_frac
        self.force_in_context = force_in_context
        self.hard = hard
        self.rng = random.Random(seed)
        self.pool: list[LatentRetEpisode] | None = None
        if pool_size is not None:
            span = min(pool_size, seed_hi - seed_lo)
            build = random.Random(seed ^ 0xA11CE)
            self.pool = [self._draw(build) for _ in range(span)]

    def _draw(self, rng: random.Random) -> LatentRetEpisode:
        s = rng.randrange(self.seed_lo, self.seed_hi)
        if self.force_in_context is None:
            ctx = rng.random() < self.in_context_frac
        else:
            ctx = self.force_in_context
        return make_episode(s, ctx, self.hard)

    def batch(self, batch_size: int | None = None) -> Batch:
        n = batch_size or self.batch_size
        if self.pool is None:
            eps = [self._draw(self.rng) for _ in range(n)]
        else:
            eps = [self.pool[self.rng.randrange(len(self.pool))] for _ in range(n)]
        return collate(eps, self.prompt_len, self.doc_len, self.question_len)


def corrupted_store(batch: Batch, offset: int = 1) -> Batch:
    """The same episodes with the gold page overwritten by another page.

    The control for whether retrieved content is used at all: if task accuracy
    in the retrieval condition does not fall when the answer bearing page is
    replaced, nothing was flowing through the injection.
    """
    docs = batch.docs.clone()
    mask = batch.doc_mask.clone()
    b = torch.arange(docs.shape[0], device=docs.device)
    other = (batch.gold + offset) % docs.shape[1]
    docs[b, batch.gold] = batch.docs[b, other]
    mask[b, batch.gold] = batch.doc_mask[b, other]
    return Batch(**{**batch.__dict__, "docs": docs, "doc_mask": mask})
