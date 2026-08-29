"""How far apart two frames are, split into words and skeleton.

The ablation in `src/disc/TEMPLATE.md` found that swapping every content word
while holding the sentence geometry fixed cost 0.13, and holding every content
word fixed while moving the geometry cost 0.94. A single scalar "distance"
would mix those two, so this module reports them separately.

Both are computed from rendered text, not from the generator's own templates,
so the same measurement applies to a generated frame and to a hand-written
renderer that knows nothing about this module. That is what makes the
calibration in `cmd_distance --calibrate` meaningful: it runs the metric over
the four hand-written chain renderers whose accuracies are already known.

  delexicalise   invented words become role tags (NAME, KEY, VAL, ...),
                 digits become NUM, closed-class words stay as themselves,
                 and every remaining open-class word becomes W.
  shape_distance Levenshtein over that tag sequence, divided by the length of
                 the longer sequence. Two frames that differ only in which
                 nouns and verbs fill the slots score 0.
  lex_distance   1 minus the Jaccard overlap of the open-class words that were
                 replaced by W. Two frames that differ only in clause order
                 score 0.

The skeleton does not depend on the seed, because every seed-dependent string
is replaced by a tag. `tests/test_frames.py` pins that.
"""

from __future__ import annotations

import random
import re

from src.frames.generate import FRAMES, Frame
from src.skillacq.simple import SIMPLE_FAMILIES

TOKEN = re.compile(r"[a-z]+|[0-9]+|[^\sa-z0-9]")

# Closed-class English. These carry the sentence geometry, so they survive
# delexicalisation; everything else open-class collapses to W. Comparatives
# and the conditional vocabulary are kept because the threshold and
# conditional shapes are built out of them.
CLOSED = set("""
a an the this that these those each every any all no some other another one
it its they them he she we you i who whom whose which what
of in on at to from by for with without into onto over under above below
before after through during against between among about across around than
as per via upon within
and or but if then else when while whereas unless until because so though
although however
is are was were be been being am do does did done has have had
will would can could may might must shall should
not never always only also instead here there now still yet just even
otherwise more less most least greater fewer many few several
""".split())


def _sub_nonce(s) -> dict[str, str]:
    m = {s.name.lower(): "NAME", s.rng_default.lower(): "VAL"}
    m.update({k.lower(): "KEY" for k in s.keys})
    m.update({v.lower(): "VAL" for v in s.values})
    return m


def _exc_nonce(s) -> dict[str, str]:
    return {s.name.lower(): "NAME", s.special_key.lower(): "KEY",
            s.general.lower(): "VAL", s.special.lower(): "VAL"}


def _thr_nonce(s) -> dict[str, str]:
    return {s.name.lower(): "NAME", s.attr.lower(): "KEY",
            s.high.lower(): "VAL", s.low.lower(): "VAL"}


NONCE = {"substitution_rule": _sub_nonce, "exception_rule": _exc_nonce,
         "threshold_rule": _thr_nonce}


def delexicalise(text: str, nonce: dict[str, str]) -> tuple[list[str], set[str]]:
    """Return the skeleton token sequence and the open-class words removed."""
    skeleton: list[str] = []
    words: set[str] = set()
    for t in TOKEN.findall(text.lower()):
        if t in nonce:
            skeleton.append(nonce[t])
        elif t.isdigit():
            skeleton.append("NUM")
        elif t.isalpha():
            if t in CLOSED:
                skeleton.append(t)
            else:
                skeleton.append("W")
                words.add(t)
        else:
            skeleton.append(t)
    return skeleton, words


def levenshtein(a: list[str], b: list[str]) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def surface(frame: Frame, family: str, seed: int) -> tuple[list[str], set[str]]:
    """The frame's whole rendered surface for one seed: pages then question."""
    from src.disc.renderers import _simple_problems
    rng = random.Random(seed)
    s = SIMPLE_FAMILIES[family](rng)
    problems = _simple_problems(s, family, rng, 6)
    pages = frame.describe(family, s)
    q = frame.question(family, s, problems[0])
    nonce = NONCE[family](s)
    # The question's key is sometimes a word the page never lists, which is
    # still a key and must be tagged as one or the skeleton would depend on
    # which problem the seed happened to draw.
    if problems[0].get("key"):
        nonce[str(problems[0]["key"]).lower()] = "KEY"
    return delexicalise("\n".join(pages) + "\n||\n" + q, nonce)


def signature(frame: Frame, family: str, seed: int = 4242) -> dict:
    sk, wd = surface(frame, family, seed)
    return {"skeleton": sk, "words": sorted(wd)}


def shape_distance(a: list[str], b: list[str]) -> float:
    n = max(len(a), len(b))
    return levenshtein(a, b) / n if n else 0.0


def lex_distance(a: set[str], b: set[str]) -> float:
    u = a | b
    return 1.0 - (len(a & b) / len(u)) if u else 0.0


def frame_signatures(names: list[str], family: str,
                     seed: int = 4242) -> dict[str, dict]:
    return {n: signature(FRAMES[n], family, seed) for n in names}


def pairwise(sigs: dict[str, dict]) -> dict[tuple[str, str], dict]:
    names = sorted(sigs)
    out = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sa, sb = sigs[a], sigs[b]
            sd = shape_distance(sa["skeleton"], sb["skeleton"])
            ld = lex_distance(set(sa["words"]), set(sb["words"]))
            out[(a, b)] = {"shape": sd, "lex": ld, "mean": (sd + ld) / 2}
    return out


def distances_to(sigs: dict[str, dict], anchor: str) -> dict[str, dict]:
    sa = sigs[anchor]
    out = {}
    for n, sb in sigs.items():
        sd = shape_distance(sa["skeleton"], sb["skeleton"])
        ld = lex_distance(set(sa["words"]), set(sb["words"]))
        out[n] = {"shape": sd, "lex": ld, "mean": (sd + ld) / 2}
    return out


def describe_distribution(vals: list[float]) -> dict:
    if not vals:
        return {"n": 0}
    v = sorted(vals)
    def q(p):
        return v[min(len(v) - 1, int(p * (len(v) - 1) + 0.5))]
    return {"n": len(v), "min": v[0], "p25": q(0.25), "median": q(0.50),
            "p75": q(0.75), "max": v[-1],
            "mean": sum(v) / len(v)}


# --------------------------------------------------- calibration on the 2x2


def chain_signatures(seed: int = 1000, depth: int = 1) -> dict[str, dict]:
    """The metric applied to the hand-written chain renderers.

    Those four form a two by two over lexicon and frame with known accuracies
    (`routing` 0.970, `processing` 0.840, `routing_frameb` 0.030, `abstract`
    0.010, table_only, forced choice). A distance metric that is any use has
    to put `processing` near `routing` in shape and far in words, and
    `routing_frameb` near in words and far in shape.
    """
    from src.disc.minrepro import MinSystem
    from src.disc.renderers import CHAIN_RENDERERS, chain_problems

    rng = random.Random(seed * 7919)
    sys = MinSystem(rng, alphabet_size=6, max_depth=4, typed=True)
    probs = chain_problems(sys, rng, depth, 8)
    nonce = {sys.name.lower(): "NAME"}
    nonce.update({m.lower(): "MAP" for m in sys.map_names})
    nonce.update({t.lower(): "TOK" for t in sys.universe})
    out = {}
    for name, r in CHAIN_RENDERERS.items():
        pages = r.pages(sys, depth)
        q = r.question(sys, probs[0]["start"], depth)
        sk, wd = delexicalise("\n".join(pages) + "\n||\n" + q, nonce)
        out[name] = {"skeleton": sk, "words": sorted(wd)}
    return out
