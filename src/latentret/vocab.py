"""A closed word level vocabulary for the latent retrieval sandbox.

The project tokenizer is a 32k byte level BPE, which is right for a 350M model
reading real text and wrong here. At this scale the answer has to be one token,
or the retrieval mechanism gets measured through the noise of a tiny model
trying to spell an invented word letter by letter.

The rule families in src/skillacq/simple.py draw their invented words from a
closed pool: two syllables from a list of twenty, so 400 words, and their
capitalized forms. Numbers are small. The template prose is fixed strings. So
the full set of types is enumerable, and this module enumerates it: every word
in the pool, every number in range, every glyph, and every function word that
appears in the templates, collected by generating the templates themselves.

Text is lowercased and split into words, whole numbers, and single punctuation
characters. Nothing outside the vocabulary should ever appear;
tests/test_vocab.py holds the unknown rate at zero over a thousand episodes.
"""

from __future__ import annotations

import random
import re

from src.skillacq.simple import SIMPLE_FAMILIES
from src.skillacq.systems import GLYPHS, NAME_SYLLABLES

TOKEN_RE = re.compile(r"[a-z]+|[0-9]+|[^\sa-z0-9]")

PAD, DOC, Q, A, EOT, UNK = "<pad>", "<doc>", "<q>", "<a>", "<eot>", "<unk>"
SPECIALS = [PAD, DOC, Q, A, EOT, UNK]

MAX_NUMBER = 199


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _template_types(n_seeds: int = 400) -> set[str]:
    """Every type the family templates can emit, by emitting them."""
    types: set[str] = set()
    for name, cls in sorted(SIMPLE_FAMILIES.items()):
        for seed in range(n_seeds):
            rng = random.Random(seed)
            system = cls(rng)
            for page in system.describe():
                types.update(tokenize(page))
            for problem in system.problems(rng, 6):
                types.update(tokenize(problem["text"]))
                types.update(tokenize(problem["answer"]))
    return types


class WordVocab:
    """Deterministic string to id map. Built once, identical across processes."""

    def __init__(self):
        words = {a + b for a in NAME_SYLLABLES for b in NAME_SYLLABLES}
        numbers = {str(i) for i in range(MAX_NUMBER + 1)}
        glyphs = set(GLYPHS)
        types = words | numbers | glyphs | _template_types()
        # Lowercased already, and the specials are angle bracketed so they can
        # never collide with a content type.
        self.itos = list(SPECIALS) + sorted(t for t in types if t not in SPECIALS)
        self.stoi = {t: i for i, t in enumerate(self.itos)}
        self.pad_id = self.stoi[PAD]
        self.doc_id = self.stoi[DOC]
        self.q_id = self.stoi[Q]
        self.a_id = self.stoi[A]
        self.eot_id = self.stoi[EOT]
        self.unk_id = self.stoi[UNK]

    def __len__(self) -> int:
        return len(self.itos)

    def encode(self, text: str) -> list[int]:
        return [self.stoi.get(t, self.unk_id) for t in tokenize(text)]

    def encode_word(self, word: str) -> int:
        return self.stoi.get(word.lower(), self.unk_id)

    def decode(self, ids) -> str:
        return " ".join(self.itos[int(i)] for i in ids)


_VOCAB: WordVocab | None = None


def get_vocab() -> WordVocab:
    global _VOCAB
    if _VOCAB is None:
        _VOCAB = WordVocab()
    return _VOCAB
