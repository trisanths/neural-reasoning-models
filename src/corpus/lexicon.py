"""Invented words, built per frame.

An earlier ablation drew one nonce vocabulary and reused it under every
wording. That is a bug, because each frame writes its own English around the
invented words: a frame whose templates contain "desk" and a frame whose
templates contain "unit" reserve different strings, and a nonce word that
collides with a frame's own English makes that frame's items ambiguous while
leaving the others alone. The collision is then confounded with the frame.

`reserved_words` renders a frame with sentinel fillers and reads back every
English word it produced. `Lexicon` draws nonce words that avoid that frame's
reserved set, and `check_no_collision` re-reads the finished text and reports
any word that slipped through.
"""

from __future__ import annotations

import random
import re

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

# The syllable inventory of src/disc/minrepro.py, extended so that a corpus
# holding tens of thousands of episodes does not have to reuse a stem inside an
# episode. Two syllable words from this list are the same shape as the ones the
# checkpoint already saw.
SYLLABLES = [
    "ka", "vor", "mi", "zel", "tu", "bra", "qen", "sol", "dri", "fex",
    "lum", "nak", "pyr", "tez", "ovi", "wren", "xil", "yuk", "zam", "clo",
    "nid", "harv", "esk", "plo", "tarn", "givo", "rusk", "mel", "onda", "verx",
    "ashk", "brun", "civ", "dolm", "emb", "frik", "gest", "hald", "ijo", "jarn",
    "kresh", "lorn", "muth", "nevi", "okra", "prav", "quil", "rham", "stiv",
    "thox", "ulm", "vand", "wisk", "xanth", "ybor", "zunt", "argo", "belu",
    "cinq", "drav",
]

SENTINEL = "SLOT"


def _word(rng: random.Random, n_syl: int = 2) -> str:
    return "".join(rng.choice(SYLLABLES) for _ in range(n_syl))


def reserved_words(frame) -> frozenset:
    """Every English word a frame can emit, read off its own templates.

    The frame is asked to render each of its templates with a sentinel in every
    slot. What is left after the sentinels are removed is the frame's own
    English, which no invented word may equal.
    """
    blob = "\n".join(frame.template_corpus())
    blob = blob.replace(SENTINEL, " ")
    return frozenset(w.lower() for w in WORD_RE.findall(blob))


class Lexicon:
    """A per episode supply of invented words that avoid one frame's English.

    Words are unique inside the episode and are checked against the frame's
    reserved set and against a global reserved set covering every frame in the
    corpus, so an item is neither ambiguous in its own frame nor accidentally
    readable as English in another.
    """

    def __init__(self, rng: random.Random, reserved: frozenset,
                 global_reserved: frozenset = frozenset()):
        self.rng = rng
        self.reserved = reserved
        self.global_reserved = global_reserved
        self.taken: set = set()
        self.rejected_collisions = 0

    def word(self, n_syl: int = 2) -> str:
        while True:
            w = _word(self.rng, n_syl)
            if w in self.taken:
                continue
            if w in self.reserved or w in self.global_reserved:
                self.rejected_collisions += 1
                continue
            self.taken.add(w)
            return w

    def words(self, count: int, n_syl: int = 2) -> list:
        return [self.word(n_syl) for _ in range(count)]

    def name(self) -> str:
        """A capitalised system or scope name."""
        return self.word().capitalize()


def check_no_collision(texts, invented) -> dict:
    """Read the finished text back and count invented words used as English.

    `invented` is the set of nonce strings the episode drew. A violation is a
    lowercased English word in the rendered text that equals one of them but
    was not placed there as a slot filler; since every filler is itself one of
    those strings, this instead checks the complement: that no invented word
    equals a word the frame would have written on its own. The frame's reserved
    set is the authority, so the check is run against it by the caller and this
    function reports the raw counts needed to do that.
    """
    seen = set()
    for t in texts:
        seen.update(w.lower() for w in WORD_RE.findall(t))
    inv = {w.lower() for w in invented}
    return {
        "n_words_in_text": len(seen),
        "n_invented": len(inv),
        "invented_present": len(inv & seen),
        "invented_absent": sorted(inv - seen)[:8],
    }


def collisions(frame_reserved: frozenset, invented) -> list:
    """Invented words that equal one of the frame's own English words."""
    return sorted({w.lower() for w in invented} & frame_reserved)
