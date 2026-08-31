"""Random structures, one per shape the frame grammar can write.

The shapes and their sizes follow `src/corpus/relations.py` so that a rendered
structure is the kind of page the corpus actually contains, rather than a
convenient one. Invented words come from `src/corpus/lexicon.py` bound to the
frame the structure will be rendered in, so a nonce word never collides with
that frame's own English, which is the collision the corpus lexicon exists to
prevent.
"""

from __future__ import annotations

import random

from src.corpus.frames import global_reserved
from src.corpus.lexicon import Lexicon, reserved_words
from src.norm.lang import Affine, Bands, Rule, Table, Weights
from src.norm.render import SHAPES, frame_by_id, frames
from src.norm.shapes import assemble

_RESERVED: dict = {}
_GLOBAL = None


def lexicon_for(fid: str, rng: random.Random) -> Lexicon:
    global _GLOBAL
    fr, _ = frames()
    if _GLOBAL is None:
        _GLOBAL = global_reserved(fr)
    if fid not in _RESERVED:
        _RESERVED[fid] = reserved_words(frame_by_id(fid))
    return Lexicon(rng, _RESERVED[fid], _GLOBAL)


def _cuts(rng: random.Random, n_bands: int):
    cuts = []
    v = rng.choice([25, 30, 35, 40])
    for _ in range(n_bands - 1):
        cuts.append(v)
        v += rng.choice([25, 30, 35])
    top = cuts[-1] + rng.choice([25, 30, 35])
    lows = [1] + [c + 3 for c in cuts]
    highs = [c - 3 for c in cuts] + [top]
    return cuts, lows, highs


def _reading(rng, lows, highs, idx):
    return rng.randint(lows[idx], max(lows[idx], highs[idx]))


def make(shape: str, rng: random.Random, lex: Lexicon):
    """One structure of the named shape."""
    if shape == "lookup":
        name = lex.name()
        keys = lex.words(4)
        vals = lex.words(4)
        default = lex.word()
        t = Table(name, tuple(zip(keys, vals)), default)
        key = rng.choice(keys) if rng.random() < 0.8 else lex.word()
        return assemble("lookup", tables=[t], inputs=(("x", key),))

    if shape == "lookup_general":
        name = lex.name()
        general, sk, sp = lex.word(), lex.word(), lex.word()
        r = Rule(name, general, ((sk, sp),))
        key = sk if rng.random() < 0.5 else lex.word()
        return assemble("lookup_general", rule=r, inputs=(("x", key),))

    if shape == "classify":
        n_bands = rng.choice([2, 3, 3, 4])
        name, attr = lex.name(), lex.word()
        labels = lex.words(n_bands)
        cuts, lows, highs = _cuts(rng, n_bands)
        b = Bands(name, attr, tuple(cuts), tuple(labels))
        idx = rng.randrange(n_bands)
        return assemble("classify", bands=b,
                        inputs=(("x", _reading(rng, lows, highs, idx)),))

    if shape == "inverse":
        name = lex.name()
        keys, vals = lex.words(4), lex.words(4)
        t = Table(name, tuple(zip(keys, vals)))
        return assemble("inverse", tables=[t],
                        inputs=(("x", rng.choice(vals)),))

    if shape == "exclusion":
        name = lex.name()
        keys = lex.words(4)
        v0, v1 = lex.words(2)
        odd = rng.choice(keys)
        t = Table(name, tuple((k, v1 if k == odd else v0) for k in keys))
        return assemble("exclusion", tables=[t], inputs=(("x", v0),))

    if shape == "priority":
        name = lex.name()
        n_rules = rng.choice([3, 4, 4, 5])
        groups, vals = lex.words(n_rules), lex.words(n_rules)
        t = Table(name, tuple(zip(groups, vals)), vals[0], ordered=True)
        hits = sorted(rng.sample(range(n_rules), rng.choice([2, 2, 3])))
        memb = tuple(groups[h] for h in hits)
        return assemble("priority", tables=[t], inputs=(("x", memb),))

    if shape == "pair":
        name = lex.name()
        rows, cols = lex.words(3), lex.words(3)
        cells = lex.words(9)
        entries = []
        t = 0
        for r in rows:
            for c in cols:
                entries.append(((r, c), cells[t]))
                t += 1
        tbl = Table(name, tuple(entries))
        return assemble("pair", tables=[tbl],
                        inputs=(("x", rng.choice(rows)),
                                ("y", rng.choice(cols))))

    if shape == "precedence":
        primary, secondary = lex.name(), lex.name()
        keys = lex.words(4)
        good, bad = lex.words(4), lex.words(4)
        a = Table(primary, tuple(zip(keys, good)))
        b = Table(secondary, tuple(zip(keys, bad)))
        return assemble("precedence", tables=[a, b],
                        inputs=(("x", rng.choice(keys)),))

    if shape == "compose":
        depth = rng.randint(1, 6)
        width = 4
        levels = [lex.words(width) for _ in range(depth + 1)]
        tables = []
        for i in range(depth):
            dst = list(levels[i + 1])
            rng.shuffle(dst)
            tables.append(Table(lex.name(), tuple(zip(levels[i], dst))))
        return assemble("compose", tables=tables,
                        inputs=(("x", rng.choice(levels[0])),))

    if shape == "iterate":
        n = rng.randint(1, 8)
        width = max(4, n + 2)
        name = lex.name()
        ring = lex.words(width)
        rng.shuffle(ring)
        t = Table(name, tuple((ring[i], ring[(i + 1) % width])
                              for i in range(width)))
        return assemble("iterate", tables=[t],
                        inputs=(("x", rng.choice(ring)),), n=n)

    if shape == "apply_n":
        n = rng.randint(1, 8)
        name = lex.name()
        a = rng.choice([2, 3, 4, 5])
        b = rng.choice([1, 3, 7, 9, 11])
        m = rng.choice([97, 101, 199, 251])
        af = Affine(name, a, b, m)
        return assemble("apply_n", affine=af,
                        inputs=(("x", rng.randint(2, m - 2)),), n=n)

    if shape == "lookup_then_band":
        wname, bname = lex.name(), lex.name()
        n_bands = rng.choice([2, 3, 3])
        n_keys = n_bands * 2
        keys = lex.words(n_keys)
        labels = lex.words(n_bands)
        cuts, lows, highs = _cuts(rng, n_bands)
        ws = []
        for j, k in enumerate(keys):
            ws.append((k, _reading(rng, lows, highs, j % n_bands)))
        w = Weights(wname, tuple(ws))
        # The corpus names the weights page as the band's attribute, which is
        # what makes the attribute recoverable in the two modes whose band
        # sentence does not state it.
        b = Bands(bname, wname, tuple(cuts), tuple(labels))
        return assemble("lookup_then_band", weights=[w], bands=b,
                        inputs=(("x", rng.choice(keys)),))

    if shape == "band_then_lookup":
        bname, tname = lex.name(), lex.name()
        n_bands = rng.choice([2, 3, 3])
        attr = lex.word()
        labels, vals = lex.words(n_bands), lex.words(n_bands)
        cuts, lows, highs = _cuts(rng, n_bands)
        b = Bands(bname, attr, tuple(cuts), tuple(labels))
        t = Table(tname, tuple(zip(labels, vals)))
        idx = rng.randrange(n_bands)
        return assemble("band_then_lookup", bands=b, tables=[t],
                        inputs=(("x", _reading(rng, lows, highs, idx)),))

    if shape == "sum_chain":
        depth = rng.randint(2, 5)
        width = 4
        levels = [lex.words(width) for _ in range(depth + 1)]
        tables, ws = [], []
        for i in range(depth):
            dst = list(levels[i + 1])
            rng.shuffle(dst)
            page = lex.name()
            tables.append(Table(page, tuple(zip(levels[i], dst))))
            ws.append(Weights(page, tuple((k, rng.randint(2, 40))
                                          for k in levels[i])))
        return assemble("sum_chain", tables=tables, weights=ws,
                        inputs=(("x", rng.choice(levels[0])),))

    raise ValueError(f"no generator for shape {shape!r}")


def make_for(fid: str, shape: str, seed: int):
    """One structure for one frame and shape, reproducible from the seed."""
    rng = random.Random(seed)
    return make(shape, rng, lexicon_for(fid, rng))
